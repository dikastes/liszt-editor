from ...models.letter import *
from liszt_util.tools import camel_to_snake_case
from bib.models import ZotItem
from django.core.management.base import BaseCommand, CommandError
from dmad_on_django.models import Person, Corporation, Place, Period
from slub_pylobid.pylobid import GNDNotFoundError, GNDIdError
from csv import DictReader
import datetime

class Command(BaseCommand):
    help = "Sepcify a file to import works from."

    def add_arguments(self, parser):
        parser.add_argument(
                '-f', '--start-from',
                dest = 'start_from',
                default = 0,
                help='Start dataset.'
            )
        parser.add_argument(
                'file_name',
                nargs=1,
                type=str,
                help='Path to a file containing CSV encoded manifestation data.'
            )

    def handle(self, *args, **options):
        start_from = 0
        if options['start_from'] != 0:
            start_from = int(options['start_from']) - 1
        with open(options['file_name'][0]) as file:
            roman_literals = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI']
            reader = list(DictReader(file))
            total = len(reader)
            for i, row in list(enumerate(reader))[start_from:]:
                print(f'{str(i+1)} von {total}')
                print(f'{row["Absender Person"]}{row["Absender Körperschaft"]} an {row["Adressat Person"]}{row["Adressat Körperschaft"]}')

                sender_persons_config = {
                        'gnd_ids': 'GND Absender Person',
                        'names': 'Absender Person',
                        'edition_names': 'Absender Person Edition',
                        'model': Person
                    }
                sender_persons = self.get_contributor_data(row, sender_persons_config)

                receiver_persons_config = {
                        'gnd_ids': 'GND Adressat Person',
                        'names': 'Adressat Person',
                        'edition_names': 'Adressat Person Edition',
                        'model': Person
                    }
                receiver_persons = self.get_contributor_data(row, receiver_persons_config)

                sender_corporations_config = {
                        'gnd_ids': 'GND Absender Körperschaft',
                        'names': 'Absender Körperschaft',
                        'edition_names': 'Absender Körperschaft Edition',
                        'model': Corporation
                    }
                sender_corporations = self.get_contributor_data(row, sender_corporations_config)

                receiver_corporations_config = {
                        'gnd_ids': 'GND Adressat Körperschaft',
                        'names': 'Adressat Körperschaft',
                        'edition_names': 'Adressat Körperschaft Edition',
                        'model': Corporation
                    }
                receiver_corporations = self.get_contributor_data(row, receiver_corporations_config)

                sender_places_config = {
                        'gnd_ids': 'Absendeort_GND',
                        'names': 'Absendeort',
                        'edition_names': 'Absendeort Edition',
                        'model': Place
                    }
                sender_places = self.get_contributor_data(row, sender_places_config)

                receiver_places_config = {
                        'gnd_ids': 'Empfangsort_GND',
                        'names': 'Empfangsort',
                        'edition_names': 'Empfangsort Edition',
                        'model': Place
                    }
                receiver_places = self.get_contributor_data(row, receiver_places_config)

                work_mentionings = []
                for number in roman_literals:
                    if row[f'Werkerwähnung ({number})']:
                        work_mentionings += [' // '.join([
                                string for
                                string in [
                                    row[f'Werkerwähnung ({number})'],
                                    'Entstehung' if row[f'Entstehung ({number})'] else None,
                                    'Quellentransfer' if row[f'Quellentransfer ({number})'] else None,
                                    'Aufführungen' if row[f'Aufführungen ({number})'] else None,
                                    #f'Seite {row[f"Seite ({number})"]}',
                                    row[f'WVZ (Raabe) ({number})'],
                                    row[f'Werktitel ({number})'],
                                    row[f'Kommentar (intern) ({number})'],
                                    row[f'Erwähnung auf Werk- oder Quellenebene ({number})'],
                                ]
                                if string
                            ])]
                work_mentionings = '\n'.join(work_mentionings)

                comment = '\n'.join(s for s in [
                        row['Kommentar (intern)'],
                        row['Bemerkungen']
                        ] if s)

                display = row['Datierung (standardisiert)']
                not_before = row['Datierung maschinenlesbar Teil 1']
                if not_before:
                    try:
                        parsed_not_before = datetime.datetime.strptime(not_before, '%d.%m.%Y')
                    except:
                        parsed_not_before = datetime.datetime.strptime(not_before, '%Y-%m-%d')
                not_after = row['Datierung maschinenlesbar Teil 2']
                if not_after:
                    try:
                        parsed_not_after = datetime.datetime.strptime(not_after, '%d.%m.%Y')
                    except:
                        parsed_not_after = datetime.datetime.strptime(not_after, '%Y-%m-%d')
                inferred = False if 'Edition' in row['Datierung Checkbox'] else True
                assumed = True if 'unsicher' in row['Datierung Checkbox'] else False

                edition_period = Period.objects.create(
                        not_before = parsed_not_before,
                        not_after = parsed_not_after,
                        display = display,
                        inferred = inferred,
                        assumed = assumed
                    )

                needs_review = False
                if row['zu überarbeiten']:
                    needs_review = True

                letter = Letter.objects.create(
                        edition_period = edition_period,
                        comment = comment,
                        work_mentionings = work_mentionings,
                        needs_review = needs_review,
                        first_editor = 'Excelimport'
                    )

                # contributors
                for sender_person in sender_persons:
                    self.create_contributor(sender_person, letter, SenderPerson, 'person')
                for receiver_person in receiver_persons:
                    self.create_contributor(receiver_person, letter, ReceiverPerson, 'person')

                for sender_corporation in sender_corporations:
                    self.create_contributor(sender_corporation, letter, SenderCorporation, 'corporation')
                for receiver_corporation in receiver_corporations:
                    self.create_contributor(receiver_corporation, letter, ReceiverCorporation, 'corporation')

                for sender_place in sender_places:
                    self.create_contributor(sender_place, letter, SenderPlace, 'place')
                for receiver_place in receiver_places:
                    self.create_contributor(receiver_place, letter, ReceiverPlace, 'place')

                #for mentioning in row['Sigle / Kurztitel'].split(' / '):
                proof_title, *proof_page = row['Sigle / Kurztitel'].split(', ')
                proof = ZotItem.objects.filter(zot_short_title = proof_title).first()
                if not proof:
                    print(f"{proof_title} not found")
                    continue
                LetterMentioning.objects.create(
                        bib = proof,
                        location = proof_page[0].replace('S.', '').strip() if len(proof_page) else '',
                        letter = letter
                    )

                #for mentioning in row['Weitere Editionen'].split(' / '):
                if row['Weitere Editionen']:
                    proof_title, *proof_page = row['Weitere Editionen'].split(', ')
                    proof = ZotItem.objects.filter(zot_short_title = proof_title).first()
                    if not proof:
                        print(f"{proof_title} not found")
                        continue
                    LetterMentioning.objects.create(
                            bib = proof,
                            location = proof_page[0] if len(proof_page) else '',
                            letter = letter
                        )

    def turn_name(name):
        return ' '.join(part.strip() for part in name.split(',')[::-1])

    def create_contributor(self, data, letter, model, target_property):
        den = DocumentedEntityName.objects.create(
                name = data['target_name'],
                inferred = data['target_inferred'],
                assumed = data['target_assumed']
            )
        model.objects.create(
                edition_name = den,
                letter = letter,
                **{ target_property: data['target'] }
            )

    def get_contributor_data(self, data, config):
        contributors = []
        if (ids := data[config['gnd_ids']]):
            for i, id in enumerate(ids.split('|')):
                name = data[config['names']].split('|')[i].strip()
                edition_name = data[config['edition_names']].split('|')[i].strip()

                if name.startswith('[') and name.endswith(']'):
                    inferred = True
                    name = name.replace('[', '').replace(']', '').strip()
                else:
                    inferred = False

                if '?' in name:
                    assumed = True
                    #name = name.replace('?', '').strip()
                else:
                    assumed = False

                if id.strip() == 'RD':
                    get_kwargs = {'interim_designator': Command.turn_name(name)}
                else:
                    get_kwargs = {'gnd_id': id.strip()}

                target = config['model'].objects.get(**get_kwargs)
                contributors.append({
                        'target': target,
                        'target_name': edition_name,
                        'target_inferred': inferred,
                        'target_assumed': assumed
                    })

        return contributors
