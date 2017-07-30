import argparse
import csv
from itertools import chain

import reversion
from django.core.management.base import BaseCommand
from django.db import transaction
from tqdm import tqdm

from epuap_watchdog.courts.models import Court


class Command(BaseCommand):
    help = "Command to import courts.csv files."
    REQUIRED_FIELDS = ['apelacja', 'sad_apelacyjny', 'okreg', 'sad_okregowy', 'nazwa_sadu',
                       'ulica', 'kod_pocztowy', 'telefon', 'fax', 'e_mail']

    def add_arguments(self, parser):
        parser.add_argument('--infile', required=True, type=argparse.FileType('r'),
                            help="Path to RESP.xml file to import")
        parser.add_argument('--comment', required=True, help="Description of changes eg. data source description")
        parser.add_argument('--no-progress', dest='no_progress', action='store_false')

    def generate_data(self, infile):
        fcsv = csv.DictReader(infile)
        # The 'fieldnames' attribute is initialized upon first access or when the first record is read from the file.
        row = next(fcsv)
        for field in self.REQUIRED_FIELDS:
            assert field in fcsv.fieldnames, "Invalid file format. Missing '{}' field.".format(field)

        for row in chain([row], fcsv):
            yield {key: value.strip() for key, value in row.items()}

    def get_iter(self, items, no_progress, **kwargs):
        return tqdm(items, **kwargs) if no_progress else items

    def handle(self, comment, no_progress, infile, *args, **options):
        self.updated, self.inserted, self.skipped, self.deactivated = 0, 0, 0, 0
        self.cached_courts = {}

        with transaction.atomic() and reversion.create_revision():
            reversion.set_comment(comment)
            for item in self.get_iter(self.generate_data(infile), no_progress):
                self.process_item(item)

            for obj in Court.objects.exclude(pk__in=self.cached_courts.values()).all():
                obj.active = False
                obj.save()

        self.stdout.write("There is {} courts, which {} skipped, {} updated, {} inserted and {} deactivated.".format(
            self.updated + self.inserted + self.skipped,
            self.skipped,
            self.updated,
            self.inserted,
            self.deactivated))

    def get_attributes(self, item):
        attrs = {'phone': item['telefon'],
                 'postcode': item['kod_pocztowy'],
                 'street': item['ulica'],
                 'fax': item['fax'],
                 'appeal': item['apelacja'],
                 'district': item['okreg'],
                 'email': item['e_mail'],
                 'name': item['nazwa_sadu']}
        if item['sad_okregowy']:
            attrs['parent_id'] = self.cached_courts[item['sad_okregowy']]
        elif item['sad_apelacyjny']:
            attrs['parent_id'] = self.cached_courts[item['sad_apelacyjny']]
        return attrs

    def process_item(self, item):
        attrs = self.get_attributes(item)
        try:
            obj = Court.objects.get(name=item['nazwa_sadu'])
            changed = False
            for key, value in attrs.items():
                if getattr(obj, key) != value:
                    setattr(obj, key, value)
                    changed = True
            if changed:
                obj.save()
                self.updated += 1
            else:
                self.skipped += 1
        except Court.DoesNotExist:
            obj = Court.objects.create(**attrs)
            self.inserted += 1
        self.cached_courts[item['nazwa_sadu']] = obj.pk
