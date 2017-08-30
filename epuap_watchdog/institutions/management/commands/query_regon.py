import re

import html2text
import requests
import reversion
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from gusregon import GUS
from tqdm import tqdm

from epuap_watchdog.institutions.models import REGON

REGON_PATTERN = re.compile('([0-9]{9,14}|[0-9]{9}-[0-9]{5})')
NIP_PATTERN = re.compile('([0-9]{3}-[0-9]{3}-[0-9]{2}-[0-9]{2}|[0-9]{3}-[0-9]{2}-[0-9]{2}-[0-9]{3}|[0-9]{11})')


class Command(BaseCommand):
    help = "My shiny new management command."

    def add_arguments(self, parser):
        parser.add_argument('--krs', type=str, nargs='+', )
        parser.add_argument('--regon', type=str, nargs='+')
        parser.add_argument('--nip', type=str, nargs='+')
        parser.add_argument('--google', type=str, nargs='+', help="Use Google to guest REGON number")
        parser.add_argument('--comment', required=True, help="Description of changes eg. data source description")
        parser.add_argument('--no-progress', dest='no_progress', action='store_false')
        parser.add_argument('--no-regon', dest='no_regon', action='store_true')
        parser.add_argument('--no-nip', dest='no_nip', action='store_true')

    def handle(self, krs, regon, nip, comment, google, no_progress, no_regon, no_nip, *args, **options):
        gus = GUS(api_key=settings.GUSREGON_API_KEY, sandbox=settings.GUSREGON_SANDBOX)
        if settings.GUSREGON_SANDBOX is True:
            self.stderr.write("You are using sandbox mode for the REGON database. Data may be incorrect. "
                              "Set the environemnt variable GUSREGON_SANDBOX and GUSREGON_API_KEY correctly.")
        self.inserted, self.updated, self.errored, self.skipped = 0, 0, 0, 0

        if not any([krs, regon, nip, google]):
            raise CommandError("Provide at least one '--krs' or '--regon' or '--nip' or '--google' is required. ")

        queries = self.get_queryset(krs, nip, regon, google, no_regon, no_nip)

        with transaction.atomic() and reversion.create_revision():
            reversion.set_comment(comment)
            for query in self.get_iter(queries, no_progress):
                data = gus.search(**query)
                if data:
                    regon_id = query.get('regon', data.get('regon14', data.get('regon9')))
                    try:
                        regon = REGON.objects.regon(regon_id)
                        if regon.data != data:
                            regon.data = data
                            regon.save()
                            self.updated += 1
                        else:
                            self.skipped += 1
                    except REGON.DoesNotExist:
                        regon = REGON(regon=regon_id, data=data)
                        self.stdout.write("Added {}".format(regon.data.get('nazwa', '')))
                        regon.save()
                        self.inserted += 1
                else:
                    self.stderr.write("Unable to find {}".format(query))
                    self.errored += 1

        total = self.inserted + self.updated + self.errored
        self.stdout.write(("There is {} REGON changed, which "
                           "{} updated, "
                           "{} skipped, "
                           "{} inserted and "
                           "{} errored.").format(total, self.updated, self.skipped, self.inserted, self.errored))

    def get_queryset(self, krs, nip, regon, google, no_regon, no_nip):
        regon = regon or []
        nip = nip or []

        self.processor = html2text.HTML2Text()
        self.processor.ignore_emphasis = True
        self.processor.bypass_tables = True
        self.processor.ignore_links = True

        self.session = requests.Session()
        for keyword in tqdm(google or []):
            if not no_regon:
                result = self.search_google("{} REGON".format(keyword), REGON_PATTERN)
                print("For '{}' found {}".format(keyword, result))
                regon += result
            if not no_nip:
                result = self.search_google("{} NIP".format(keyword), NIP_PATTERN)
                print("For '{}' found {}".format(keyword, result))
                nip += [x.replace('-', '') for x in result if len(x.replace('-', '')) == 10]
        queries = [{'krs': v} for v in set(krs)] if krs else []
        queries += [{'nip': v} for v in set(nip)] if nip else []
        queries += [{'regon': v} for v in set(regon)] if regon else []

        return queries

    def search_google(self, query, pattern):
        content = self.session.get('https://www.google.pl/search', params={'q': query}).text
        text = self.processor.handle(content)
        result = pattern.findall(text)
        return result

    def get_iter(self, queryset, no_progress):
        return tqdm(queryset, smoothing=0) if no_progress else queryset
