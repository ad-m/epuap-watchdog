import os

import requests_cache
import reversion
import time
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from gusregon import GUS
from tqdm import tqdm

from epuap_watchdog.institutions.models import Institution, REGON, REGONError
from epuap_watchdog.institutions.utils import normalize_regon

requests_cache.configure()


class Command(BaseCommand):
    help = "Command to import REGON database."

    def add_arguments(self, parser):
        parser.add_argument('--comment', required=True, help="Description of changes eg. data source description")
        parser.add_argument('--update', dest='update', action='store_true')
        parser.add_argument('--institutions_id', type=int, nargs='+', help="Institution IDs updated")
        parser.add_argument('--no-progress', dest='no_progress', action='store_false')

    def handle(self, comment, institutions_id, update, no_progress, *args, **options):
        gus = GUS(api_key=settings.GUSREGON_API_KEY, sandbox=settings.GUSREGON_SANDBOX)
        if settings.GUSREGON_SANDBOX is True:
            self.stderr.write("You are using sandbox mode for the REGON database. Data may be incorrect. "
                              "Set the environemnt variable GUSREGON_SANDBOX and GUSREGON_API_KEY correctly.")
        inserted, updated, errored, skipped = 0, 0, 0, 0
        qs = self.get_queryset(update, institutions_id)
        for institution in self.get_iter(qs, no_progress):
            with transaction.atomic() and reversion.create_revision():
                try:
                    data = gus.search(regon=normalize_regon(institution.regon))
                except TypeError as e:
                    regon_obj = REGON.objects.create(institution=institution, regon=institution.regon)
                    REGONError.objects.create(regon=regon_obj, exception=repr(e))
                    errored += 1
                    self.stderr.write("Errored for {} in {} as {}".format(institution.regon, institution.pk, repr(e)))
                    continue
                if hasattr(institution, 'regon_data'):
                    if institution.regon_data.data != data:
                        institution.regon_data.regon = institution.regon
                        institution.regon_data.data = data
                        institution.regon_data.save()
                        updated += 1
                    else:
                        skipped += 1
                else:
                    REGON.objects.create(institution=institution,
                                         regon=institution.regon,
                                         data=data)
                    inserted += 1
                reversion.set_comment(comment)
            time.sleep(2)
        total = updated + inserted + errored + skipped
        self.stdout.write(("There is {} REGON changed, which "
                           "{} updated, "
                           "{} skipped, "
                           "{} inserted and "
                           "{} errored.").format(total, updated, skipped, inserted, errored))

    def get_queryset(self, update, institutions_id):
        qs = Institution.objects.select_related('regon_data').exclude(regon=None)
        if not update:
            qs = qs.filter(regon_data=None)
        if institutions_id:
            qs = qs.filter(id__in=institutions_id)
        return qs.order_by('-modified').all()

    def get_iter(self, queryset, no_progress):
        return tqdm(queryset, smoothing=0) if no_progress else queryset
