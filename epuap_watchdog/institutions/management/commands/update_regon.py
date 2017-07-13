import requests_cache
import reversion
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from gusregon import GUS
from tqdm import tqdm

from epuap_watchdog.institutions.models import Institution, REGON, REGONError

requests_cache.configure()


class Command(BaseCommand):
    help = "Command to import REGON database."

    def add_arguments(self, parser):
        parser.add_argument('--comment', help="Description of changes eg. data source description")
        parser.add_argument('--update', dest='update', action='store_true')
        parser.add_argument('--no-progress', dest='no_progress', action='store_false')

    def handle(self, comment, update, no_progress, *args, **options):
        gus = GUS(api_key=settings.GUSREGON_API_KEY, sandbox=settings.GUSREGON_SANDBOX)
        inserted, updated, errored = 0, 0, 0
        qs = self.get_queryset(update)
        for institution in self.get_iter(qs, no_progress):
            with transaction.atomic() and reversion.create_revision():
                try:
                    data = gus.search(regon=institution.regon)
                except TypeError as e:
                    regon_obj = REGON.objects.create(institution=institution, regon=institution.regon)
                    REGONError.objects.create(regon=regon_obj, exception=repr(e))
                    errored += 1
                    self.stderr.write("Errored for {} in {} as {}".format(institution.regon, institution.pk, repr(e)))
                    continue
                if hasattr(institution, 'regon_data'):
                    if institution.regon_data.regon != institution.regon and institution.regon_data.data != data:
                        institution.regon_data.regon = institution.regon
                        institution.regon_data.data = data
                        institution.regon_data.save()
                    updated += 1
                else:
                    REGON.objects.create(institution=institution,
                                         regon=institution.regon,
                                         data=data)
                    inserted += 1
                reversion.set_comment(comment)
        total = updated + inserted + errored
        self.stdout.write(("There is {} REGON changed, which "
                            "{} updated, "
                            "{} inserted and "
                            "{} errored.").format(total, updated, inserted, errored))

    def get_queryset(self, update):
        qs = Institution.objects.select_related('regon_data').exclude(regon=None)
        if not qs.update():
            qs = qs.filter(regon_data=None)
        return qs.all()

    def get_iter(self, queryset, no_progress):
        return tqdm(queryset, smoothing=0) if no_progress else queryset
