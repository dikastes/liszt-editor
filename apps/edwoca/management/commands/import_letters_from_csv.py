from ...models.base import Letter, LetterMentioning
from bib.models import ZotItem
from django.core.management.base import BaseCommand, CommandError
from dmad_on_django.models import Person, Corporation, Place, Period
from pylobid.pylobid import GNDNotFoundError, GNDIdError
from csv import DictReader
import datetime

class Command(BaseCommand):
    help = "Sepcify a file to import works from."

    def add_arguments(self, parser):
        parser.add_argument(
                'file_name',
                nargs=1,
                type=str,
                help='Path to a file containing CSV encoded manifestation data.'
            )

    def handle(self, *args, **options):
        with open(options['file_name'][0]) as file:
            roman_literals = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI']
            reader = list(DictReader(file))
            total = len(reader)
            for i, row in enumerate(reader):
                print(f'{str(i+1)} von {total}')
                print(f'{row["Absender Person"]}{row["Absender Körperschaft"]} an {row["Adressat Person"]}{row["Adressat Körperschaft"]}')

                sender_person = None
                if (sender_person_id := row["GND Absender Person"]):
                    sender_person = Person.fetch_or_get(sender_person_id)
                sender_corporation = None
                if (sender_corporation_id := row["GND Absender Körperschaft"]):
                    sender_corporation = Corporation.fetch_or_get(sender_corporation_id)
                sender_place = None
                if (sender_place_id := row["Absendeort_GND"]):
                    sender_place = Place.fetch_or_get(sender_place_id)

                receiver_person = None
                if (receiver_person_id := row["GND Adressat Person"]):
                    receiver_person = Person.fetch_or_get(receiver_person_id)
                receiver_corporation = None
                if (receiver_corporation_id := row["GND Adressat Körperschaft"]):
                    receiver_corporation = Corporation.fetch_or_get(receiver_corporation_id)
                receiver_place = None
                if (receiver_place_id := row["Empfangsort_GND"]):
                    receiver_place = Place.fetch_or_get(receiver_place_id)

                display = row['Datierung (standardisiert)']
                not_before = row['Datierung maschinenlesbar Teil 1']
                if not_before:
                    parsed_not_before = datetime.datetime.strptime(not_before, '%d.%m.%Y')
                not_after = row['Datierung maschinenlesbar Teil 2']
                if not_after:
                    parsed_not_after = datetime.datetime.strptime(not_after, '%d.%m.%Y')
                inferred = False if 'Vorlage' in row['Datierung Checkbox'] else True

                work_comments = []
                for number in roman_literals:
                    if row[f'Werkerwähnung ({number})']:
                        work_comments += [' // '.join([
                                string for
                                string in [
                                    row[f'Werkerwähnung ({number})'],
                                    'Entstehung' if row[f'Entstehung ({number})'] else None,
                                    'Quellentransfer' if row[f'Quellentransfer ({number})'] else None,
                                    'Aufführungen' if row[f'Aufführungen ({number})'] else None,
                                    f'Seite {row[f"Seite ({number})"]}',
                                    row[f'WVZ (Raabe) ({number})'],
                                    row[f'Werktitel ({number})'],
                                    row[f'Kommentar (intern) ({number})'],
                                    row[f'Erwähnung auf Werk- oder Quellenebene ({number})'],
                                ]
                                if string
                            ])]
                comment = '\n'.join([
                        row['Kommentar (intern)'],
                        row['Bemerkungen'],
                        *work_comments
                        ])

                period = Period.objects.create(
                        not_before = parsed_not_before,
                        not_after = parsed_not_after,
                        display = display
                    )
                letter = Letter.objects.create(
                        receiver_person = receiver_person,
                        receiver_corporation = receiver_corporation,
                        receiver_place = receiver_place,
                        sender_person = sender_person,
                        sender_corporation = sender_corporation,
                        sender_place = sender_place,
                        period = period,
                        comment = comment
                    )

                for mentioning in row['Sigle / Kurztitel'].split(' / '):
                    proof_title, *proof_page = row['Sigle / Kurztitel'].split(', ')
                    proof = ZotItem.objects.filter(zot_short_title = proof_title).first()
                    if not proof:
                        print(f"{proof_title} not found")
                        continue
                    LetterMentioning.objects.create(
                            bib = proof,
                            pages = proof_page[0] if len(proof_page) else '',
                            letter = letter
                        )

