
from django.core.management.base import BaseCommand
from django.db import transaction
from teryt_tree.models import JednostkaAdministracyjna
from tqdm import tqdm

from epuap_watchdog.cityhalls.models import CityHall
from epuap_watchdog.institutions.models import REGON
from epuap_watchdog.institutions.utils import normalize


class Command(BaseCommand):
    help = "My shiny new management command."

    def add_arguments(self, parser):
        parser.add_argument('--no-progress', dest='no_progress', action='store_false')
        parser.add_argument('--update', dest='update', action='store_true')

    def get_queryset(self, update):
        qs = CityHall.objects.exclude(original_terc=None)
        if not update:
            qs = qs.filter(detected_regon=None)
        qs = qs.select_related('detected_regon', 'original_terc', 'original_terc__parent')
        return qs.order_by('original_name').all()

    def get_iter(self, queryset, no_progress):
        return tqdm(queryset) if no_progress else queryset

    def get_regon(self, data):
        return data.get('regon14', data.get('regon9', None))

    def handle(self, no_progress, update, *args, **options):
        standard, try_extended, extended = 0, 0, 0
        with transaction.atomic():
            for cityhall in self.get_iter(self.get_queryset(update), no_progress):
                guest_list = REGON.objects.filter(regonjst__jst=cityhall.original_terc).exclude(data=None).order_by('name').all()
                self.stdout.write(cityhall.original_name)
                for regon in guest_list:
                    regon_no = self.get_regon(regon.data)
                    self.stdout.write("** {} - {}".format(normalize(regon.name), regon_no))
                if guest_list:
                    standard += 1
                if not guest_list:
                    jst_list = JednostkaAdministracyjna.objects.area(cityhall.original_terc.parent).all()
                    subregon_list = REGON.objects.filter(regonjst__jst__in=jst_list).exclude(data=None).order_by('name').all()
                    try_extended += 1
                    if len(subregon_list) < 20:
                        extended += 1
                        for regon in subregon_list:
                            regon_no = self.get_regon(regon.data)
                            self.stdout.write("**** {} - {}".format(normalize(regon.name), regon_no))
                self.stdout.write("\n")

        print("Standard found {} time, extended {} times, no found {} times".format(standard, try_extended, extended))
