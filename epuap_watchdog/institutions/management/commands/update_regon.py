from django.core.management.base import BaseCommand
from gusregon import GUS

from epuap_watchdog.institutions.models import Institution
from django.conf import settings

class Command(BaseCommand):
    help = "My shiny new management command."

    def add_arguments(self, parser):
        parser.add_argument('sample', nargs='+')

    def handle(self, *args, **options):
        gus = GUS(api_key=settings.GUSREGON_API_KEY, sandbox=settings.GUSREGON_SANDBOX)
        for institution in Institution.objects.exclude(regon=None).all():
            print(institution.regon)
