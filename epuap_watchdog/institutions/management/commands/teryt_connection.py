from functools import lru_cache

import reversion
from django.core.management.base import BaseCommand
from django.db import transaction
from teryt_tree.models import JednostkaAdministracyjna, SIMC
from tqdm import tqdm

from epuap_watchdog.institutions.models import REGON, JSTConnection, REGONJST
from epuap_watchdog.institutions.utils import get_jst_id


class Command(BaseCommand):
    help = "A make connection between institution and TERYT database throught REGON"

    def add_arguments(self, parser):
        parser.add_argument('--comment', required=True, help="Description of changes eg. data source description")
        parser.add_argument('--update', dest='update', action='store_true')
        parser.add_argument('--no-progress', dest='no_progress', action='store_false')

    @lru_cache(maxsize=128)
    def get_jst(self, jst_id):
        try:
            return JednostkaAdministracyjna.objects.get(pk=jst_id)
        except JednostkaAdministracyjna.DoesNotExist:
            return None

    def handle(self, comment, no_progress, update, *args, **options):
        self.update_institution(no_progress, update)
        self.update_regon(no_progress, update)

    def update_institution(self, no_progress, update):
        self.updated, self.inserted, self.errored, self.skipped = 0, 0, 0, 0
        with transaction.atomic() and reversion.create_revision():
            for regon in self.get_iter(self.get_queryset(update), no_progress):
                item = self.insert_throguth_terc(regon)
                if not item:
                    item = self.insert_throught_simc(regon)
                if not item:
                    self.errored += 1
        self.stdout.write(
            "There is {} connection changed, which {} updated, {} skipped and {} inserted. but {} errored.".
                format(self.updated + self.inserted,
                       self.updated,
                       self.skipped,
                       self.inserted,
                       self.errored))

    def insert_throguth_terc(self, regon):
        jst_id = get_jst_id(regon.data)
        if not jst_id:
            return False
        jst = self.get_jst(jst_id)
        if not jst:
            return False
        return self.save_or_update(institution=regon.institution, terc=jst)

    def get_queryset(self, update):
        qs = REGON.objects.exclude(data=None).exclude(institution=None)
        if not update:
            qs = qs.filter(institution__jstconnection=None)
        qs = qs.select_related('institution__jstconnection')
        return qs.order_by('-modified').all()

    def get_iter(self, queryset, no_progress):
        return tqdm(queryset) if no_progress else queryset

    def insert_throught_simc(self, regon):
        sym = regon.data.get('adsiedzmiejscowosc_symbol', regon.data.get('adkormiejscowosc_symbol', None))
        if not sym:
            return False
        try:
            simc = SIMC.objects.get(id=sym)
        except SIMC.DoesNotExist:
            return False
        return self.save_or_update(regon.institution, simc.terc)

    def save_or_update(self, institution, terc):
        print(institution)
        try:
            jc = JSTConnection.objects.get(institution=institution)
            if jc.jst != terc:
                jc.jst = terc
                jc.save()
                self.updated += 1
            else:
                self.skipped += 1
            return jc
        except JSTConnection.DoesNotExist:
            jc = JSTConnection.objects.create(institution=institution, jst=terc)
            self.inserted += 1
            return jc

    def update_regon(self, no_progress, update):
        self.updated, self.inserted, self.errored, self.skipped = 0, 0, 0, 0
        with transaction.atomic() and reversion.create_revision():
            for regon in self.get_iter(self.get_queryset_regon(update), no_progress):
                jst_id = get_jst_id(regon.data)
                jst = self.get_jst(jst_id)
                if not jst:
                    self.stderr.write("Unable to find JST {} for {}".format(jst_id, regon))
                    self.errored +=1
                    continue
                if hasattr(regon, 'regonjst'):
                    if regon.regonjst.jst == jst:
                        self.skipped += 1
                    else:
                        self.updated += 1
                        regon.regonjst.jst = jst
                        regon.regonjst.save()
                else:
                    self.inserted += 1
                    REGONJST.objects.create(regon=regon, jst=jst)

        self.stdout.write(
            "There is {} connection changed, which {} updated, {} skipped and {} inserted. but {} errored.".
                format(self.updated + self.inserted,
                       self.updated,
                       self.skipped,
                       self.inserted,
                       self.errored))

    def get_queryset_regon(self, update):
        qs = REGON.objects.select_related('regonjst').exclude(data=None)
        if not update:
            qs = qs.filter(regonjst=None)
        qs = qs.select_related('regonjst')
        return qs.order_by('-modified').all()
