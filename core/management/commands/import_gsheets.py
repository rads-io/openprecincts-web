import re
import csv
from django.db import transaction
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Locality
from contact.models import Official

FIX_MAPPING = {
    'Isle of Wight': 'Isle of Wight County',
    'Norfolk': 'Norfolk, City of',
    'Richmond': 'Richmond, City of',
    'Virginia Beach': 'Virginia Beach, City of',
}


@transaction.atomic
def import_contact_csv(state, filename):
    bot, _ = User.objects.get_or_create(username='migration-bot')

    with open(filename) as f:
        # skip a few lines
        for _ in range(3):
            f.readline()
        for line in csv.DictReader(f):
            locality_name = re.sub(' [cC]ity$', ', City of', line['Locality'])
            locality_name = FIX_MAPPING.get(locality_name, locality_name)
            print(locality_name)
            locality = Locality.objects.get(state=state, name=locality_name)
            Official.objects.create(
                locality=locality,
                first_name=line['First Name'],
                last_name=line['Last Name'],
                title=line['Title'],
                phone_number=line['Phone'],
                email=line['Email'],
                job_title=line['Job Title'],
                notes=line[''],
                created_by=bot,
            )


class Command(BaseCommand):
    help = 'Import data from Google Drive'

    def add_arguments(self, parser):
        parser.add_argument('--contact', type=str, help='path to contact CSV')

    def handle(self, *args, **options):
        import_contact_csv('Virginia', options['contact'])
