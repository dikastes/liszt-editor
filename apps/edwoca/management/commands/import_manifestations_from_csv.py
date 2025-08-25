from django.core.management.base import BaseCommand, CommandError
from ...models import Manifestation
from csv import DictReader

class Command(BaseCommand):
    help = "Sepcify a file to import manifestations from."

    def add_arguments(self, parser):
        parser.add_argument('file_name', nargs=1, type=str)

    def handle(self, *args, **options):
        for file_name in options['file_name']:
            with open(file_name) as file:
                reader = DictReader(file)
                for row in reader:
                    if Manifestation.RISM_ID_KEY in row and \
                        row[Manifestation.RISM_ID_KEY] and \
                        Manifestation.objects.filter(rism_id = row[Manifestation.RISM_ID_KEY]).first():
                        manifestation = Manifestation.objects.get(rism_id = row[Manifestation.RISM_ID_KEY])
                    else:
                        manifestation = Manifestation.objects.create()

                    manifestation.parse_csv(row)
                    if manifestation.rism_id:
                        manifestation.pull_rism_data()
                    manifestation.save()
