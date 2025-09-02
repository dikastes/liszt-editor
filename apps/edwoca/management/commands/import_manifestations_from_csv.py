from django.core.management.base import BaseCommand, CommandError
from pylobid.pylobid import GNDNotFoundError, GNDIdError
from ...models import Manifestation
from csv import DictReader

class Command(BaseCommand):
    help = "Sepcify a file to import manifestations from."

    def add_arguments(self, parser):
        parser.add_argument('file_name', nargs=1, type=str)

    def handle(self, *args, **options):
        with open(options['file_name'][0]) as file:
            reader = DictReader(file)
            for row in reader:
                print(row[Manifestation.RISM_ID_KEY])
                print(row[Manifestation.CURRENT_SIGNATURE_KEY])
                # reactivate when RISM IDs are unique
                #if Manifestation.RISM_ID_KEY in row and \
                    #row[Manifestation.RISM_ID_KEY] and \
                    #Manifestation.objects.filter(rism_id = row[Manifestation.RISM_ID_KEY]).first():
                    #manifestation = Manifestation.objects.get(rism_id = row[Manifestation.RISM_ID_KEY])
                #else:
                manifestation = Manifestation.objects.create()

                try:
                    manifestation.parse_csv(row)
                except (GNDNotFoundError, GNDIdError) as e:
                    manifestation.delete()
                    print(f"GND Error in {row[Manifestation.RISM_ID_KEY]}, {row[Manifestation.CURRENT_SIGNATURE_KEY]}")
                    print(e)
                    continue
                # reactivate when RISM IDs are unique
                #if manifestation.rism_id:
                    #manifestation.pull_rism_data()
                manifestation.save()
