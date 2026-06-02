from ...models.letter import *
from liszt_util.tools import camel_to_snake_case
from bib.models import ZotItem
from django.core.management.base import BaseCommand, CommandError
from dmad_on_django.models import Person, Corporation, Place, Period
from slub_pylobid.pylobid import GNDNotFoundError, GNDIdError
from csv import DictReader
import datetime

class Command(BaseCommand):
    help = "Sepcify a file to import stadium information from."

    def add_arguments(self, parser):
        parser.add_argument(
                'file_name',
                nargs=1,
                type=str,
                help='Path to a file containing CSV encoded manifestation data.'
            )

    def handle(self, *args, **options):
        with open(options['file_name'][0]) as file:
            reader = DictReader(file)
            for row in reader:
                print(row['edwoca-ID'])
                if Manifestation.objects.filter(pk = int(row['edwoca-ID'])).count():
                    m = Manifestation.objects.get(pk = int(row['edwoca-ID']))
                    if row['Quellenform'].strip().lower() == 'entwurf':
                        m.manifestation_form = Manifestation.ManifestationForm.SKETCHES
                    if row['Quellenform'].strip().lower() == 'fragment':
                        m.manifestation_form = None
                        if m.private_comment:
                            m.private_comment += '\nFragment'
                        else:
                            m.private_comment = 'Fragment'
                        m.needs_review = True
                    if row['Quellenform'].strip().lower() == 'ausschnitt':
                        m.manifestation_form = None
                        m.completeness = Manifestation.Completeness.INCOMPLETE
                    m.save()
                else:
                    print(f'not found: {row["edwoca-ID"]}')
