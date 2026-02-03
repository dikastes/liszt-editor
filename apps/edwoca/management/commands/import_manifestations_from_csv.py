from django.core.management.base import BaseCommand, CommandError
from pylobid.pylobid import GNDNotFoundError, GNDIdError
from ...models import Manifestation
from csv import DictReader

class Command(BaseCommand):
    help = "Sepcify a file to import manifestations from."

    def add_arguments(self, parser):
        parser.add_argument(
                'file_name',
                nargs=1,
                type=str,
                help='Path to a file containing CSV encoded manifestation data.'
            )
        source_types = [ s.lower().replace('_', '') for s in Manifestation.SourceType._member_names_ ]
        parser.add_argument(
                '-st',
                '--source-type',
                nargs='?',
                type=str,
                help=' or '.join([', '.join(source_types[:-1]), source_types[-1]])
            )
        manifestation_forms = [ s.lower().replace('_', '') for s in Manifestation.ManifestationForm._member_names_ ]
        parser.add_argument(
                '-mf',
                '--manifestation-form',
                nargs='?',
                type=str,
                help=' or '.join([', '.join(manifestation_forms[:-1]), manifestation_forms[-1]])
            )
        functions = [
                'album page',
                'performance material',
                'correction sheet',
                'stitch template',
                'dedication item',
                'choir score',
                'piano reduction'
            ]
        parser.add_argument(
                '-f',
                '--function',
                nargs='?',
                type=str,
                help=' or '.join([', '.join(functions[:-1]), functions[-1]])
            )
        parser.add_argument(
                '-n',
                '--not-singleton',
                action='store_true',
                help='Specify if results shall be parsed as non singletons.'
            )

    def handle(self, *args, **options):
        function = None
        if (function_argument := options['function']):
            function = Manifestation.Function.parse(function_argument)

        manifestation_form = None
        if (form_argument := options['manifestation_form']):
            manifestation_form = Manifestation.ManifestationForm.parse(form_argument)

        source_type = None
        if (type_argument := options['source_type']):
            source_type = Manifestation.SourceType.parse(type_argument)

        singleton = True
        if options['not_singleton']:
            singleton = False

        with open(options['file_name'][0]) as file:
            reader = list(DictReader(file))
            total = len(reader)
            for i, row in enumerate(reader):
                print(f'{str(i+1)} von {total}')
                print(f'{row[Manifestation.CURRENT_SIGNATURE_KEY]}, {row[Manifestation.RISM_ID_KEY]}')
                # reactivate when RISM IDs are unique
                #if Manifestation.RISM_ID_KEY in row and \
                    #row[Manifestation.RISM_ID_KEY] and \
                    #Manifestation.objects.filter(rism_id = row[Manifestation.RISM_ID_KEY]).first():
                    #manifestation = Manifestation.objects.get(rism_id = row[Manifestation.RISM_ID_KEY])
                #else:
                manifestation = Manifestation.objects.create()

                try:
                    manifestation.parse_csv(row, source_type, manifestation_form, function, singleton)
                    manifestation.save()
                    if manifestation.rism_id:
                        manifestation.pull_rism_data(singleton)
                    manifestation.save()
                except (GNDNotFoundError, GNDIdError) as e:
                    manifestation.delete()
                    print(f"GND Error in {row[Manifestation.RISM_ID_KEY]}, {row[Manifestation.CURRENT_SIGNATURE_KEY]}")
                    print(e)
                    continue
