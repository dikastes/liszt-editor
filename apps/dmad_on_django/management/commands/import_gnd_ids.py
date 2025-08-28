from pylobid.pylobid import PyLobidClient, PyLobidPlace, PyLobidOrg, PyLobidPerson
from django.core.management.base import BaseCommand, CommandError
from csv import reader
from ...models import Place, Corporation, Person

class Command(BaseCommand):
    help = "Specify a file to import datasets from."

    def add_arguments(self, parser):
        parser.add_argument('file_name', nargs=1, type=str)

    def handle(self, *args, **options):
        #breakpoint()
        for file_name in options['file_name']:
            with open(file_name) as file:
                csv_reader = reader(file)
                contents = list(csv_reader)
                total = len(contents)
                for i, row in enumerate(contents):
                    gnd_id = row[0]
                    print(f"{i} von {total}: {gnd_id}")
                    py_ent = PyLobidClient(f"http://d-nb.info/gnd/{gnd_id}").factory()

                    match py_ent.__class__.__name__:
                        case 'PyLobidPlace':
                            model = Place
                        case 'PyLobidOrg':
                            model = Corporation
                        case 'PyLobidPerson':
                            model = Person

                    if not model.objects.filter(gnd_id = gnd_id).first():
                        new_item = model.objects.create(gnd_id = gnd_id)
                        new_item.fetch_raw()
                        new_item.update_from_raw()
                        new_item.save()
