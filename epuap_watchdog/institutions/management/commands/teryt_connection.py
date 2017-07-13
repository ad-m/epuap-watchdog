from functools import lru_cache
from pprint import pprint

import reversion
from django.core.management.base import BaseCommand
from django.db import transaction
from teryt_tree.models import JednostkaAdministracyjna, SIMC
from tqdm import tqdm

from epuap_watchdog.institutions.models import REGON, JSTConnection


class Command(BaseCommand):
    help = "A make connection between institution and TERYT database throught REGON"
    JST_VOIVODESHIP_KEYS = ['adsiedzwojewodztwo_symbol', 'adkorwojewodztwo_symbol']
    JST_COUNTY_KEYS = ['adsiedzpowiat_symbol', 'adkorpowiat_symbol', ]
    JST_COMMUNITY_KEYS = ["adsiedzgmina_symbol", 'adkorgmina_symbol', ]

    def add_arguments(self, parser):
        parser.add_argument('--comment', help="Description of changes eg. data source description")
        parser.add_argument('--update', dest='update', action='store_true')
        parser.add_argument('--no-progress', dest='no_progress', action='store_false')

    def get_jst_id(self, data):
        for a, b, c in zip(self.JST_VOIVODESHIP_KEYS, self.JST_COUNTY_KEYS, self.JST_COMMUNITY_KEYS):
            if a in data and b in data and c in data:
                value = data[a] + data[b] + data[c]
                if value:
                    return value

    @lru_cache(maxsize=128)
    def get_jst(self, jst_id):
        try:
            return JednostkaAdministracyjna.objects.get(pk=jst_id)
        except JednostkaAdministracyjna.DoesNotExist:
            return None

    def handle(self, comment, no_progress, update, *args, **options):
        self.updated, self.inserted, self.errored = 0, 0, 0
        with transaction.atomic() and reversion.create_revision():
            for regon in self.get_iter(self.get_queryset(update), no_progress):
                item = self.insert_throguth_terc(regon)
                if not item:
                    item = self.insert_throught_simc(regon)
                if not item:
                    self.errored += 1

        self.stdout.write("There is {} connection changed, which {} updated and {} inserted. but {} errored.".format(
            self.updated + self.inserted,
            self.updated,
            self.inserted,
            self.errored))

    def insert_throguth_terc(self, regon):
        jst_id = self.get_jst_id(regon.data)
        if not jst_id:
            return False
        jst = self.get_jst(jst_id)
        if not jst:
            return False
        return self.save_or_update(institution=regon.institution, terc=jst)

    def get_queryset(self, update):
        qs = REGON.objects.exclude(data=None)
        if not update:
            qs = qs.filter(institution__jstconnection=None)
        return qs.select_related('institution__jstconnection').all()

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
        try:
            jc = JSTConnection.objects.get(institution=institution)
            jc.jst = terc
            jc.save()
            self.updated += 1
            return jc
        except JSTConnection.DoesNotExist:
            jc = JSTConnection.objects.create(institution=institution, jst=terc)
            self.inserted += 1
            return jc
