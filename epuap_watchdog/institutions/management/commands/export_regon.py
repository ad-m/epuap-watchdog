import argparse
import csv
from functools import reduce
import sys
from django.core.management.base import BaseCommand
from django.db.models import Q

from epuap_watchdog.institutions.models import REGON
from epuap_watchdog.institutions.utils import normalize


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('query', nargs='+')
        parser.add_argument('-o', '--outfile', type=argparse.FileType('w'), default=sys.stdout)

    def handle(self, query, outfile, *args, **options):
        queries = [Q(name__icontains=x) | Q(regon__icontains=x) for x in query]
        q = reduce(lambda x, y: x | y, queries)

        f_csv = csv.writer(outfile)
        f_csv.writerow(['name', 'clean_name', 'regon14', 'regon9', 'region', 'terc'])
        for regon in REGON.objects.filter(q).select_related('regonjst', 'regonjst__jst').all():
            name = regon.name
            clean_name = normalize(regon.name)
            regon14 = regon.data.get('regon14', '')
            regon9 = regon.data.get('regon9', '')
            if hasattr(regon, 'regonjst'):
                region = " > ".join(x.name for x in regon.regonjst.jst.get_ancestors(ascending=False, include_self=True))
                teryt = regon.regonjst.jst_id
            else:
                region = ''
                teryt = ''
            f_csv.writerow((name, clean_name, regon14, regon9, region, teryt))
