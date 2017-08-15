from functools import lru_cache
from math import floor, ceil
from urllib.parse import urljoin

from django.core.management.base import BaseCommand

import requests
from django.db import transaction
from teryt_tree.models import JednostkaAdministracyjna, SIMC
from tqdm import tqdm, trange

from epuap_watchdog.cityhalls.models import CityHall


class Command(BaseCommand):
    help = "My shiny new management command."
    PER_PAGE = 100

    def add_arguments(self, parser):
        parser.add_argument('--host')
        parser.add_argument('--user')
        parser.add_argument('--password')
        parser.add_argument('--no-progress', dest='no_progress', action='store_false')

    def _get_url(self, resource):
        return urljoin(urljoin(self.host, '/api/'), resource)

    def post(self, resource, **kwargs):
        return self.s.post(self._get_url(resource), **kwargs).json()

    @lru_cache()
    def get(self, resource, **kwargs):
        return self.s.get(self._get_url(resource), **kwargs).json()

    def handle(self, host, user, password, no_progress, *args, **options):
        self.s = requests.Session()
        self.s.auth = (user, password)
        self.host = host
        self.updated, self.inserted, self.errored, self.skipped = 0, 0, 0, 0
        count = self.get('institutions/?tags=7')['count']
        with transaction.atomic() and tqdm(total=count) as t:
            page_num = int(ceil(count / self.PER_PAGE))
            for page in range(1, page_num + 1):
                t.set_description("Page {} of {}".format(page, page_num))
                result = self.get('institutions/?tags=7&page={}'.format(page))
                for row in result['results']:
                    self.update_row(row)
                    t.update(1)
        self.stdout.write(
            "Processed {} city halls, which {} updated, {} skipped and {} inserted. but {} errored.".
                format(self.updated + self.inserted,
                       self.updated,
                       self.skipped,
                       self.inserted,
                       self.errored))
        total_count = CityHall.objects.count()
        self.stdout.write("There is {} city halls in total".format(total_count))

    def update_row(self, row):
        updated = False
        try:
            item = CityHall.objects.get(original_pk=row['pk'])
            inserted = False
        except CityHall.DoesNotExist:
            updated = True
            inserted = True
            item = CityHall(original_pk=row['pk'])
        if item.original_name != row['name']:
            updated = True
            item.original_name = row['name']
        if item.original_terc_id != row['jst']:
            updated = True
            if JednostkaAdministracyjna.objects.filter(pk=row['jst']).exists():
                item.original_terc_id = row['jst']
            else:
                self.stderr.write("Unable to find JST ID: {}".format(row['jst']))
                self.errored += 1
                return
        if updated:
            item.save()
            if inserted:
                self.inserted += 1
            else:
                self.updated += 1
        else:
            self.skipped += 1
