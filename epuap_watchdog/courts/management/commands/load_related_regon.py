import reversion
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from gusregon import GUS
from tqdm import tqdm

from epuap_watchdog.institutions.models import REGON


class Command(BaseCommand):
    help = "My shiny new management command."

    def add_arguments(self, parser):
        parser.add_argument('--comment', required=True, help="Description of changes eg. data source description")
        parser.add_argument('--no-progress', dest='no_progress', action='store_false')
        parser.add_argument('--verbose', dest='verbose', action='store_true')

    def get_queryset(self):
        return REGON.objects.exclude(data__jednosteklokalnych="0").exclude(data=None).all()

    def get_iter(self, items, no_progress, **kwargs):
        return tqdm(items, **kwargs) if no_progress else items

    def handle(self, no_progress, verbose, comment, *args, **options):
        gus = GUS(api_key=settings.GUSREGON_API_KEY, sandbox=settings.GUSREGON_SANDBOX)
        if settings.GUSREGON_SANDBOX is True:
            self.stderr.write("You are using sandbox mode for the REGON database. Data may be incorrect. "
                              "Set the environemnt variable GUSREGON_SANDBOX and GUSREGON_API_KEY correctly.")
        self.inserted, self.updated, self.errored, self.skipped = 0, 0, 0, 0
        qs = self.get_queryset()
        for regon in self.get_iter(qs, no_progress):
            with transaction.atomic() and reversion.create_revision():
                data = gus.search(regon=regon.data['regon14'], report_type='PublDaneRaportLokalnePrawnej', list=True)
                for item in data:
                    # item_data = gus.search(regon=item['regon14'])
                    item_data = item
                    try:
                        obj = REGON.objects.get(regon=item['regon14'])
                        if obj.data != item_data:
                            obj.data = item_data
                            obj.save()
                            self.updated += 1
                        else:
                            self.skipped += 1
                    except REGON.DoesNotExist:
                        REGON.objects.create(regon=item['regon14'], data=item_data)
                        self.inserted += 1
        self.stdout.write("There is {} courts, which {} skipped, {} updated and {} inserted.".format(
            self.updated + self.inserted + self.skipped,
            self.skipped,
            self.updated,
            self.inserted))
