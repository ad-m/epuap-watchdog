import argparse
from itertools import groupby

import reversion
from django.core.management.base import BaseCommand
from django.db import transaction
from lxml import etree
from tqdm import tqdm

from epuap_watchdog.institutions.models import Institution, ESP, RESP

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


#  Input file can be downloaded at https://epuap.gov.pl/ -> Strefa urzędnika -> Dla integratorów ->
#  Książka adresowa ESP -> XML ( https://s.jawne.info.pl/ksiazka-esp )


class Command(BaseCommand):
    help = "Command to import RESP.xml files."

    def add_arguments(self, parser):
        parser.add_argument('--infile', required=True, type=argparse.FileType('r'),
                            help="Path to RESP.xml file to import")
        parser.add_argument('--comment', required=True, help="Description of changes eg. data source description")
        parser.add_argument('--no-progress', dest='no_progress', action='store_false')

    def handle(self, infile, comment, no_progress, *args, **options):
        self.esp_cache = {}
        self.updated, self.inserted, self.skipped = 0, 0, 0
        self.regon_fixed = 0
        self.esp_updated, self.esp_inserted, self.esp_skipped = 0, 0, 0
        self.no_progress = no_progress
        with transaction.atomic() and reversion.create_revision():
            reversion.set_comment(comment)
            # Transaction usage means that the disk has been written to the disk only after commit,
            # which greatly influences the speed.
            for epuap_id, esps in self.get_iter(self.generate_data(infile)):
                items = list(esps)
                regon = items[0]['regon'] if items[0]['regon'] != 'NULL' else None
                institution = Institution.objects.get_or_create(epuap_id=epuap_id,
                                                                defaults={'regon': regon,
                                                                          'name': items[0]['name']})[0]
                self._process_resp(institution, items[0])
                self._process_esps(institution, items)

        self.stdout.write("There is {} RESPs {} skipped and changed, which {} updated and {} inserted.".format(
            self.updated + self.inserted + self.skipped,
            self.skipped,
            self.updated,
            self.inserted))
        self.stdout.write("There is {} REGON's fixed in institution".format(self.regon_fixed))
        self.stdout.write(("There is {} ESPs changed, which {} skipped, {} "
                           "updated and {} inserted.").format(self.esp_updated + self.esp_inserted + self.esp_skipped,
                                                              self.esp_skipped,
                                                              self.esp_updated,
                                                              self.esp_inserted))

    def get_iter(self, items, **kwargs):
        iter = tqdm(items, **kwargs) if self.no_progress else items
        return groupby(iter, key=lambda esp: esp['uri'].split('/')[1])

    def generate_data(self, input):
        tree = etree.parse(input, etree.XMLParser(remove_blank_text=True))
        items = tree.iterfind('esp')
        for i, esp in enumerate(items):
            yield {el.tag: el.text.strip() for el in esp.getchildren()}

    def _process_resp(self, institution, item):
        item = item.copy()
        del item['uri']
        try:
            resp = RESP.objects.get(institution=institution.id)
            if resp.data != item:
                resp.data = item
                resp.save()
                self.updated += 1
            else:
                self.skipped += 1
        except RESP.DoesNotExist:
            RESP.objects.create(institution=institution, data=item)
            self.inserted += 1
        if institution.regon != item['rego'] and item['regon'] != 'NULL':
            self.regon_fixed += 1
            Institution.objects.filter(pk=institution.pk).update(regon=item['regon'])

    def _process_esps(self, institution, items):
        esp_names = set(item['uri'].split('/', 3)[2] for item in items)

        esps = ESP.objects.filter(institution=institution).all()

        # Activate or deactivate existing ESPs accordingly
        for esp in esps:
            if esp.name in esp_names != esp.active:
                esp.active = esp.name in esp_names
                esp.save()
                self.esp_updated += 1
            else:
                self.esp_skipped += 1
        to_add = esp_names ^ {esp.name for esp in esps}

        # Add all missing ESPs
        if to_add:
            ESP.objects.bulk_create(ESP(institution=institution, name=name) for name in to_add)
            self.esp_inserted += len(to_add)
