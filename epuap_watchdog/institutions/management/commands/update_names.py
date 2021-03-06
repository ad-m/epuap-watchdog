from pprint import pprint

from django.core.management.base import BaseCommand
from django.db import transaction
from tqdm import tqdm

from epuap_watchdog.institutions.models import Institution
from epuap_watchdog.institutions.utils import normalize


class Command(BaseCommand):
    help = "Updated in order to determine the best name for the user.."

    def add_arguments(self, parser):
        parser.add_argument('--comment', required=True, help="Description of changes eg. data source description")
        parser.add_argument('--no-progress', dest='no_progress', action='store_false')
        parser.add_argument('--institutions_id', type=int, nargs='+', help="Institution IDs updated")
        parser.add_argument('--dry-run', dest="dry_run", action='store_true', help="Print changes, no save")

    def get_iter(self, items, no_progress, **kwargs):
        return tqdm(items, **kwargs) if no_progress else items

    def get_queryset(self, institutions_id):
        qs = Institution.objects.select_related('regon_data', 'resp').exclude(regon_data=None). \
            exclude(regon_data__data=None).order_by('-modified')
        if institutions_id:
            qs = qs.filter(id__in=institutions_id)
        return qs.all()

    def handle(self, comment, no_progress, dry_run, institutions_id, *args, **options):
        self.updated, self.skipped, self.errored = 0, 0, 0
        with transaction.atomic():
            for institution in self.get_iter(self.get_queryset(institutions_id), no_progress):
                name_resp = normalize(institution.resp.data.get('name'))
                name_regon = normalize(institution.regon_data.data.get('nazwa'))
                best_name = name_resp if len(name_resp) >= len(name_regon) else name_regon
                if institution.name != best_name:
                    if dry_run:
                        pprint({'id': institution.id,
                                'best_name': best_name,
                                'current_x': institution.name,
                                'resp_name': institution.resp.data.get('name'),
                                'regn_name': institution.regon_data.data.get('nazwa')
                                })
                    institution.name = best_name
                    if not dry_run:
                        institution.save(update_fields=['name'])
                    self.updated += 1
                else:
                    self.skipped += 1
        self.stdout.write(("There is {} institutions changed, which "
                           "{} updated and "
                           "{} skipped.").format(self.updated + self.skipped, self.updated, self.skipped))
