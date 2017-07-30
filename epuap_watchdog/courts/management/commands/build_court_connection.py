import reversion
from django.core.management.base import BaseCommand
from django.db import transaction
from tqdm import tqdm

from epuap_watchdog.courts.models import Court, REGONGuest
from epuap_watchdog.institutions.models import REGON


class Command(BaseCommand):
    help = "Command to guest connection court to institution."

    def add_arguments(self, parser):
        parser.add_argument('--comment', required=True, help="Description of changes eg. data source description")
        parser.add_argument('--no-progress', dest='no_progress', action='store_false')
        parser.add_argument('--verbose', dest='verbose', action='store_true')
        parser.add_argument('--update', action="store_true")

    def get_queryset(self, update):
        qs = Court.objects.all()
        if not update:
            return qs.filter(regonguest=None)
        return qs

    def get_iter(self, items, no_progress, **kwargs):
        return tqdm(items, **kwargs) if no_progress else items

    def handle(self, comment, no_progress, verbose, update, *args, **options):
        self.updated, self.inserted, self.skipped, self.deleted, self.missing = 0, 0, 0, 0, 0
        print(update)
        with transaction.atomic() and reversion.create_revision():
            reversion.set_comment(comment)
            for court in self.get_iter(self.get_queryset(update), no_progress):
                self.process_item(court, verbose)

        self.stdout.write(
            "There is {} connection, which {} skipped, {} updated, {} deleted, {} inserted, {} missing.".format(
                self.updated + self.inserted + self.skipped,
                self.skipped,
                self.updated,
                self.deleted,
                self.inserted,
                self.missing))

    def process_item(self, court, verbose):
        regons = list(REGON.objects.guest_by_name(name=court.name, email=court.email, confidence=2))
        if not regons:
            if verbose:
                self.stdout.write("Not found for {}".format(court.name))
            self.missing += 1
            self.deleted += REGONGuest.objects.filter(court=court.id).all().delete()[0]
            return
        regon = regons[0]
        if verbose:
            self.stdout.write(
                "Found {} for {}. Selected {}".format(len(regons), court.name, regon.name))
        try:
            obj = REGONGuest.objects.get(court=court)
            if obj.regon_id != regon.id:
                obj.regon = regon
                obj.save()
                self.updated += 1
            else:
                self.skipped += 1
        except REGONGuest.DoesNotExist:
            REGONGuest.objects.create(court=court, regon=regon)
            self.inserted += 1
