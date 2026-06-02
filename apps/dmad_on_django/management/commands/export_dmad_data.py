from django.core.management.base import BaseCommand, CommandError
from csv import DictWriter
from ...models import Place, Corporation, Person, SubjectTerm, Work

class Command(BaseCommand):
    help = "Specify a file to import datasets from."

    #def add_arguments(self, parser):
        #parser.add_argument('file_name', nargs=1, type=str)

    def handle(self, *args, **options):
        fieldnames = ['gnd_id', 'name', 'interim_designator', 'rework_in_gnd']
        for model in [ Place, Corporation, Person, SubjectTerm, Work ]:
            file_name = f'{model.__name__.lower()}.csv'
            print(f'Writing all {model.__name__} instances to {file_name}.')
            with open(file_name, 'w') as f:
                writer = DictWriter(f, fieldnames = fieldnames)
                writer.writeheader()
                for entity in model.objects.all():
                    line = {}
                    for fieldname in fieldnames:
                        line[fieldname] = getattr(entity, fieldname)
                    writer.writerow(line)
