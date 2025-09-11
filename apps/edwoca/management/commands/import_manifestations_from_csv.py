from django.core.management.base import BaseCommand, CommandError
from pylobid.pylobid import GNDNotFoundError, GNDIdError
from ...models import Manifestation
from csv import DictReader

class Command(BaseCommand):
    help = "Sepcify a file to import manifestations from."

    def add_arguments(self, parser):
        parser.add_argument('file_name', nargs=1, type=str)
        parser.add_argument('source_type', nargs=1, type=str)

    def handle(self, *args, **options):
        with open(options['file_name'][0]) as file:
            reader = list(DictReader(file))
            total = len(reader)
            for i, row in enumerate(reader):
                print(f'{i} von {total}')
                print(f'{row[Manifestation.CURRENT_SIGNATURE_KEY]}, {row[Manifestation.RISM_ID_KEY]}')
                # reactivate when RISM IDs are unique
                #if Manifestation.RISM_ID_KEY in row and \
                    #row[Manifestation.RISM_ID_KEY] and \
                    #Manifestation.objects.filter(rism_id = row[Manifestation.RISM_ID_KEY]).first():
                    #manifestation = Manifestation.objects.get(rism_id = row[Manifestation.RISM_ID_KEY])
                #else:
                manifestation = Manifestation.objects.create()

                try:
                    manifestation.parse_csv(row, options['source_type'][0].upper())
                except (GNDNotFoundError, GNDIdError) as e:
                    manifestation.delete()
                    print(f"GND Error in {row[Manifestation.RISM_ID_KEY]}, {row[Manifestation.CURRENT_SIGNATURE_KEY]}")
                    print(e)
                    continue
                # reactivate when RISM IDs are unique
                #if manifestation.rism_id:
                    #manifestation.pull_rism_data()
                manifestation.save()
