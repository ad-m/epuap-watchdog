import argparse

import reversion
from django.core.management.base import BaseCommand
from django.db import transaction
from lxml import etree
from tqdm import tqdm

from epuap_watchdog.institutions.models import Institution, ESP

"""
Example row:
    <esp>
        <name>SZKOŁA PODSTAWOWA NR 5 W PŁOCKU IM. WŁADYSŁAWA BRONIEWSKIEGO</name>
        <regon>000903529</regon>
        <adres>ul. Cicha 12 A</adres>
        <kod_pocztowy>09-401</kod_pocztowy>
        <miejscowosc>Płock</miejscowosc>
        <uri>/SP5Plock/domyslna</uri>
    </esp>
"""


class Command(BaseCommand):
    help = "Command to import RESP.xml files."

    FIELD_MAP = {'name': 'name',
                 'regon': 'regon',
                 'adres': 'address',
                 'kod_pocztowy': 'postal_code',
                 'miejscowosc': 'city'}

    def add_arguments(self, parser):
        parser.add_argument('--infile', nargs='?', type=argparse.FileType('r'),
                            help="Path to RESP.xml file to import")
        parser.add_argument('--source', help="Description of changes eg. data source description")

    def _append_to_dict_list(self, dict_values, key, value):
        values = dict_values.get(key, [])
        values.append(value)
        dict_values[key] = values

    def handle(self, infile, source, *args, **options):
        self.esp_cache = {}
        self.updated, self.inserted = 0, 0

        self.process_all_institutions(infile, source)
        self.process_all_esps()

    def generate_data(self, input):
        tree = etree.parse(input, etree.XMLParser(remove_blank_text=True))
        items = tree.iterfind('esp')
        # items = [next(items), next(items), next(items)]
        for i, esp in enumerate(items):
            yield {el.tag: el.text.strip() for el in esp.getchildren()}

    def process_all_institutions(self, infile, source):
        last_epuap_id = None

        with transaction.atomic():
            # Transaction usage means that the disk has been written to the disk only after commit,
            # which greatly influences the speed.
            for item in tqdm(self.generate_data(infile), desc="Institution update"):
                last_epuap_id = self._process_institution(item, last_epuap_id, source)
                esp_id = item['uri'].split('/')[2]
                self._append_to_dict_list(self.esp_cache, last_epuap_id, esp_id)
            self.stdout.write("There is {} institutions changed, which {} updated and {} inserted.".format(
                self.updated + self.inserted,
                self.updated,
                self.inserted))

    def _process_institution(self, item, last_epuap_id, source):
        with reversion.create_revision():
            epuap_id = item['uri'].split('/')[1]
            if epuap_id != last_epuap_id:  # Update institution data
                try:
                    institution = self.update_institution(epuap_id, item)
                    self.updated += 1
                except Institution.DoesNotExist:
                    institution = self.save_new_institution(epuap_id, item)
                    self.inserted += 1
            reversion.set_comment(source)
            return epuap_id

    def update_institution(self, epuap_id, item):
        institution = Institution.objects.get(epuap_id=epuap_id)
        self._update_values(institution, item, epuap_id)
        institution.save()

    def save_new_institution(self, epuap_id, item):
        institution = Institution(epuap_id=epuap_id)
        self._update_values(institution, item, epuap_id)
        institution.save()

    def _update_values(self, institution, item, epuap_id):
        institution.slug = epuap_id[:50]
        for resp_field, model_field in self.FIELD_MAP.items():
            old_value = getattr(institution, model_field)
            new_value = item[resp_field] if item[resp_field] != 'NULL' else None

            if new_value and old_value != new_value:  # New values
                setattr(institution, model_field, item[resp_field])

    def process_all_esps(self):
        with transaction.atomic():
            self.updated, self.inserted = 0, 0
            for epuap_id, esp_names in tqdm(self.esp_cache.items(), desc="ESP update"):
                esp_names = set(esp_names)
                esps = ESP.objects.filter(institution__epuap_id=epuap_id).all()

                # Activate or deactivate existing ESPs accordingly
                for esp in esps:
                    esp.active = esp.name in esp_names
                    esp.save()
                    self.updated += 1
                to_add = esp_names ^ {esp.name for esp in esps}

                # Add all missing ESPs
                if to_add:
                    institution = Institution.objects.get(epuap_id=epuap_id)
                    ESP.objects.bulk_create(ESP(institution=institution,
                                                name=name)
                                            for name in to_add)
                    self.inserted += len(to_add)
            self.stdout.write(("There is {} ESPs changed, which {} "
                               "updated and {} inserted.").format(self.updated + self.inserted,
                                                                  self.updated,
                                                                  self.inserted))
