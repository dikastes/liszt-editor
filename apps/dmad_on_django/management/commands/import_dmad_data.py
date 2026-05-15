from slub_pylobid.pylobid import PyLobidClient, PyLobidPlace, PyLobidOrg, PyLobidPerson
from django.core.management.base import BaseCommand, CommandError
from csv import DictReader
from ...models import Place, Corporation, Person

class Command(BaseCommand):
    help = "Specify a file to import datasets from."

    def add_arguments(self, parser):
        parser.add_argument('file_name', nargs=1, type=str)

    def handle(self, *args, **options):
        TYPE = 'edwoca'
        INTERIM_DESIGNATOR = 'Name (RD)'
        ALTERNATIVE_NAME = 'Name (abweichend)'
        COMMENT = 'Infos'
        GND_ID = 'GND-ID'
        MODEL = 'Art'
        STUB = 'RD'
        MODEL_MAP = {
                'Person': Person,
                'Geografika': Place,
                'Körperschaft': Corporation
            }

        for file_name in options['file_name']:
            with open(file_name) as file:
                csv_reader = DictReader(file)
                contents = list(csv_reader)
                total = len(contents)

                for i, row in enumerate(contents):
                    model = MODEL_MAP[row[MODEL]]

                    if row[TYPE] == STUB:
                        interim_designator = row[INTERIM_DESIGNATOR]
                        print(f'{str(i+1)} von {total}: Rumpfdatensatz {interim_designator}')

                        if not model.objects.filter(interim_designator = interim_designator).first():
                            comment = ''
                            if (alt_name := row[ALTERNATIVE_NAME]):
                                comment += f'{ALTERNATIVE_NAME}: {alt_name}'
                                if row[COMMENT]:
                                    comment += '\n'
                            if (comment_text := row[COMMENT]):
                                comment += comment_text

                            model.objects.create(
                                    interim_designator = interim_designator,
                                    comment = comment
                                )
                        else:
                            print('existiert bereits')

                    else:
                        gnd_id = row[GND_ID]
                        print(f"{str(i+1)} von {total}: {gnd_id}")
                        if not model.objects.filter(gnd_id = gnd_id).first():
                            new_item = model.objects.create(gnd_id = gnd_id)
                            new_item.fetch_raw()
                            new_item.update_from_raw()
                            new_item.save()
                        else:
                            print('existiert bereits')
