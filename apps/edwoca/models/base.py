from django.conf import settings
from django.db import models
from django.db.models import Q, UniqueConstraint
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from dmad_on_django.models import Status, Language, Person, Corporation, Place, Period
from dmrism.models import WemiBaseClass, TitleTypes, Library, ItemSignature, BaseHandwriting, ItemHandwriting, ManifestationTitle, ManifestationTitleHandwriting, ItemDigitalCopy, BaseDigitalCopy, BaseSignature, Publication
from dmrism.models import Manifestation as DmRismManifestation
from dmrism.models import ManifestationTitle as DmRismManifestationTitle
from dmrism.models import Item as DmRismItem
from re import compile, split


class EdwocaUpdateUrlMixin:
    def get_absolute_url(self):
        model = self.__class__.__name__.lower()
        if model == 'item' and self.manifestation.is_singleton:
            return reverse('edwoca:manifestation_update', kwargs={'pk': self.manifestation.id})
        return reverse(f'edwoca:{model}_update', kwargs={'pk': self.id})


class Manifestation(EdwocaUpdateUrlMixin, DmRismManifestation):
    RISM_ID_KEY = 'RISM ID no.'
    CURRENT_SIGNATURE_KEY = 'Signatur, neu'

    class Meta:
        proxy = True

    def parse_edition_type(csv_representation):
        match csv_representation:
            case 'Partitur':
                return Manifestation.EditionType.SCORE
            case 'Stimme':
                return Manifestation.EditionType.PART
            case 'Stimmen':
                return Manifestation.EditionType.PARTS
            case 'Particell':
                return Manifestation.EditionType.PARTICELL
            case 'Klavierauszug':
                return Manifestation.EditionType.PIANO_REDUCTION
            case 'Chorpartitur':
                return Manifestation.EditionType.CHOIR_SCORE

    def __str__(self):
        if self.is_singleton:
            return super().__str__()

        if self.missing_item:
            return f"{catalog_number} unbekannt {numerus_currens}"

        publisher_addition = self.period
        if self.publications.first() and self.publications.first().plate_number:
            publisher_addition = self.publications.first().plate_number

        if self.publications.first() and self.publications.first().publisher:
            return f"{self.publications.first().publisher.get_designator()} {publisher_addition}, {self.get_temp_title()}"
        return f"<< Verlag >> {publisher_addition}, {self.get_temp_title()}"

    def extract_gnd_id(string):
        ID_PATTERN = '[0-9]\w{4,}-?\w? *]'
        id_pattern = compile(ID_PATTERN)
        match = id_pattern.search(string)
        if match:
            return string[match.start():match.end()].replace(']', '').strip()
        return None

    def extract_medium(medium_string):
        MEDIUM_PATTERN = '\([\w ,]+\)?'
        medium_pattern= compile(MEDIUM_PATTERN)
        match = medium_pattern.search(medium_string)
        if match:
            return medium_string[match.start():match.end()].\
                replace('(', '').\
                replace(')', '').\
                strip()

    def parse_csv(self, raw_data, source_type, manifestation_form = None, function = None, singleton = True):
        # Head keys
        IDENTIFICATION_KEY = 'WVZ-Nr.'
        INSTITUTION_KEY = 'Bestandeshaltende Institution'
        FORMER_SIGNATURE_KEY = 'Signatur, vormalig'
        TITLE_KEY = 'Titel (normiert, nach MGG)'

        EDITION_TYPE_KEY = 'Ausgabeform (Typ)'
        FUNCTION_KEY = 'Funktion'
        FORMER_TYPE_KEY = 'interne Sicherung vormaliger "Typ"-Einträge'
        OWNER_NOTE_KEY = 'Besitzvermerk (intern)'

        ENVELOPE_TITLE_KEY = 'Titelei Umschlag oder Titelblatt'
        ENVELOPE_TITLE_WRITER_KEY = 'Schreiber Titelei' # Schreiber Umschlag/Titelblatt Bezug zu O
        ENVELOPE_TITLE_MEDIUM_KEY = 'Autor Titelei (Liszt egh.)'
        ENVELOPE_TITLE_COMMENT_KEY = 'Kommentarfeld zu: Titel (der Quelle) Titelblatt | Umschlag'

        HEAD_TITLE_KEY = 'Kopftitel'
        HEAD_TITLE_WRITER_KEY = 'Schreiber Kopftitel' # Schreiber Umschlag/Titelblatt Bezug zu O
        HEAD_TITLE_MEDIUM_KEY = 'Autor Kopftitel (Liszt egh.)'
        HEAD_TITLE_COMMENT_KEY = 'Kommentarfeld zu: Titel (der Quelle) Notentext'

        DEDICATION_KEY = 'Widmung (diplomatisch)'
        DEDICATION_COMMENT_KEY = 'Kommentar zur Widmung'

        MEDIUM_OF_PERFORMANCE_KEY = 'Besetzung (normiert)'
        TEMPO_KEY = 'Tempoangabe (normiert)'
        METRONOM_KEY = 'Metronomangabe'
        LANGUAGE_KEY = 'Sprachcode'
        TEXT_INCIPIT_KEY = 'Text-Incipit (diplomatisch)'

        LOCATION_KEY = 'GND-Nr. Ort'
        DIPLOMATIC_DATE_KEY = 'Datierung (diplomatisch)'
        MACHINE_READABLE_DATE_KEY = 'Datierung (maschinenlesbar)'
        DATE_COMMENT_KEY = 'Datierung Kommentar'

        RELATED_PRINT_PUBLISHER_KEY = 'Bezug zu Druck: Verlags-GND-Nr.'
        RELATED_PRINT_PLATE_NUMBER_KEY = 'Bezug zu Druck: Plattennr.'

        PUBLISHER_KEY = 'Verlags GND-Nr.'
        PLATE_NUMBER_KEY = 'Plattennummer'
        STITCHER_KEY = 'Stecherei GND-Nr.'
        FIGURE_KEY = 'Abbildung (figurativ)'
        PRINT_TYPE_KEY = 'Drucktyp'

        AUTOGRAPH_HANDWRITING_KEY = 'Schrift (Liszt egh.)'
        FOREIGN_HANDWRITING_KEY = 'Schrift (fremder Hand)'
        WRITING_KEY = 'Schreiber zu AB gehörig bitte mit Information in AC kombinieren'

        EXTENT_KEY = 'Umfang'
        MEASURE_KEY = 'Papiermaß'
        PHYSICAL_FEATURES_KEY = 'Beschreibung physischer Merkmale'
        CONTENT_KEY = 'Inhalt'

        DIGITAL_COPY_KEY = 'Digitalisat'

        FUNCTION_KEY = 'Funktion'

        DEDUCED_PLACE_NAME_KEY = 'Ort ermittelt (normiert)'
        DEDUCED_PLACE_ID_KEY = 'Ort ermittelt GND-Nr.'

        PROVENANCE_KEY = 'Provenienz'
        PROVSTATION_SUFFIX = ' Station '

        MANIFESTATION_NOTES_KEY = 'Notizen zur Quelle (vormals "Beschreibung", bleibt intern)'
        MANIFESTATION_COMMENT_KEY = 'Kommentar zur Quelle (intern)'
        COMMENT_QUESTION_KEY = 'Kommentar intern / Fragen (interne Kommunikation)'
        FURTHER_INFORMATION_KEY = 'Weiterführende Informationen (Ausgaben, Permalinks etc.) (intern)'

        self.manifestation_form = manifestation_form
        self.function = function

        taken_information = []
        if MANIFESTATION_NOTES_KEY in raw_data and (manifestation_notes := raw_data[MANIFESTATION_NOTES_KEY]):
            taken_information += [ 'Notizen zur Quelle: ' + manifestation_notes]
        if MANIFESTATION_COMMENT_KEY in raw_data and (manifestation_comment := raw_data[MANIFESTATION_COMMENT_KEY]):
            taken_information += [ 'Kommentar zur Quelle: ' + manifestation_comment]
        if COMMENT_QUESTION_KEY in raw_data and (comment_question := raw_data[COMMENT_QUESTION_KEY]):
            taken_information += [ 'Kommentar intern: ' + comment_question]
        if FURTHER_INFORMATION_KEY in raw_data and (further_information := raw_data[FURTHER_INFORMATION_KEY]):
            taken_information += [ 'Weiterführende Informationen: ' + further_information]
        if FORMER_TYPE_KEY in raw_data and (former_type := raw_data[FORMER_TYPE_KEY]):
            taken_information += [ 'Vormalige Typ-Einträge: ' + former_type ]
        if CONTENT_KEY in raw_data and (content := raw_data[CONTENT_KEY]):
            taken_information += [ 'Inhalt: ' + content ]

        self.taken_information = '\n'.join(taken_information)

        fixed_persons = settings.EDWOCA_FIXED_PERSONS

        for person in fixed_persons:
            if (gnd_id := fixed_persons[person]):
                Person.fetch_or_get(gnd_id)
            else:
                if Person.objects.filter(interim_designator = person).count() == 0:
                    Person.objects.create(interim_designator = person)

        # add stitch template flag to manifestation?

        self.source_type = source_type

        #only makes sense if doubles may be detected and overriding may be activated
        #self.titles.all().delete()

        private_head_comment = []
        if IDENTIFICATION_KEY in raw_data and (identification := raw_data[IDENTIFICATION_KEY]):
            private_head_comment += [ 'Identifikation: ' + identification ]
        if TEMPO_KEY in raw_data and (tempo := raw_data[TEMPO_KEY]):
            private_head_comment += [ 'Tempo: ' + tempo ]
        if LANGUAGE_KEY in raw_data and (language := raw_data[LANGUAGE_KEY]):
            private_head_comment += [ 'Sprache: ' + language ]
        if TEXT_INCIPIT_KEY in raw_data and (incipit := raw_data[TEXT_INCIPIT_KEY]):
            private_head_comment += [ 'Text-Incipit: ' + incipit ]
        if METRONOM_KEY in raw_data and (metronom := raw_data[METRONOM_KEY]):
            private_head_comment += [ 'Metronom: ' + metronom ]
        if MEDIUM_OF_PERFORMANCE_KEY in raw_data and (medium := raw_data[MEDIUM_OF_PERFORMANCE_KEY]):
            private_head_comment += [ 'Besetzung: ' + medium ]
        self.private_head_comment = '\n'.join(private_head_comment)

        if DEDUCED_PLACE_NAME_KEY in raw_data and raw_data[DEDUCED_PLACE_NAME_KEY]:
            self.private_history_comment = f"Ort ermittelt: {raw_data[DEDUCED_PLACE_NAME_KEY]}, {raw_data[DEDUCED_PLACE_ID_KEY]}"
        if DATE_COMMENT_KEY in raw_data and (comment := raw_data[DATE_COMMENT_KEY]):
            self.private_history_comment = f"Datierung Kommentar: {comment}"

        if FUNCTION_KEY in raw_data:
            self.function = Manifestation.Function.parse_from_german(raw_data[FUNCTION_KEY])

        if self.RISM_ID_KEY in raw_data and\
            raw_data[self.RISM_ID_KEY] and\
            raw_data[self.RISM_ID_KEY].isnumeric():
            self.rism_id = raw_data[self.RISM_ID_KEY]

        library = Library.objects.filter(siglum = raw_data[INSTITUTION_KEY]).first() or \
            Library.objects.create(siglum = raw_data[INSTITUTION_KEY])
        signature = ItemSignature.objects.create(
                library = library,
                status = BaseSignature.Status.CURRENT,
                signature = raw_data[Manifestation.CURRENT_SIGNATURE_KEY]
            )
        single_item = Item.objects.create(manifestation = self)
        single_item.signatures.add(signature)

        if raw_data[FORMER_SIGNATURE_KEY]:
            former_signature = ItemSignature.objects.create(
                    library = library,
                    status = BaseSignature.Status.FORMER,
                    signature = raw_data[FORMER_SIGNATURE_KEY]
                )
            single_item.signatures.add(former_signature)

        provenance_comment = []
        if PROVENANCE_KEY + PROVSTATION_SUFFIX + '1' in raw_data:
            provenance_comment = [
                    provenance_string for
                    station in
                    range(3)
                    if (
                        provenance_string := \
                        raw_data[PROVENANCE_KEY + PROVSTATION_SUFFIX + str(station + 1)]
                    )
                ]
            if PROVENANCE_KEY + PROVSTATION_SUFFIX + '4' in raw_data:
                provenance_comment += f'\n {raw_data[PROVENANCE_KEY + PROVSTATION_SUFFIX + "4"]}'

        if PROVENANCE_KEY in raw_data and (provenance := raw_data[PROVENANCE_KEY]):
            provenance_comment += [ provenance ]

        if OWNER_NOTE_KEY in raw_data and (owner := raw_data[OWNER_NOTE_KEY]):
            provenance_comment += [ f'Besitzvermerk: {owner}' ]

        self.is_singleton = True
        if not singleton:
            self.is_singleton = False
            single_item.is_template = True

        single_item.private_provenance_comment = '\n'.join(provenance_comment)
        single_item.save()

        if LOCATION_KEY in raw_data and raw_data[LOCATION_KEY]:
            for gnd_id in raw_data[LOCATION_KEY].split('|'):
                place = Place.fetch_or_get(gnd_id.strip())
                self.places.add(place)

        if raw_data[TITLE_KEY]:
            ManifestationTitle.objects.create(
                    title = raw_data[TITLE_KEY],
                    status = Status.TEMPORARY,
                    manifestation = self
                )

        if EDITION_TYPE_KEY in raw_data:
            self.edition_type = Manifestation.parse_edition_type(raw_data[EDITION_TYPE_KEY])

        self.dedication = raw_data[DEDICATION_KEY]
        if self.dedication:
            dedications = self.dedication.split('|')
            for dedication in dedications:
                if gnd_id := Manifestation.extract_gnd_id(dedication):
                    dedicatee = Person.fetch_or_get(gnd_id)
                    self.dedicatees.add(dedicatee)
                else:
                    for person in fixed_persons:
                        if (gnd_id := fixed_persons[person]):
                            if person in dedication:
                                dedicatee = Person.objects.get(gnd_id = gnd_id)
                                self.dedicatees.add(dedicatee)
                                break
                        else:
                            if person in dedication:
                                dedicatee = Person.objects.get(interim_designator = person)
                                self.dedicatees.add(dedicatee)
                                break

        self.date_diplomatic = raw_data[DIPLOMATIC_DATE_KEY].replace(' | ', '\n')
        if raw_data[MACHINE_READABLE_DATE_KEY]:
            self.period = Period.parse(raw_data[MACHINE_READABLE_DATE_KEY])

        if RELATED_PRINT_PUBLISHER_KEY in raw_data:
            if raw_data[RELATED_PRINT_PUBLISHER_KEY]:
                Publication.objects.create(
                        manifestation = self,
                        publisher = Corporation.fetch_or_get(raw_data[RELATED_PRINT_PUBLISHER_KEY]),
                        plate_number = raw_data[RELATED_PRINT_PLATE_NUMBER_KEY]
                    )

        if PUBLISHER_KEY in raw_data:
            if raw_data[PUBLISHER_KEY]:
                Publication.objects.create(
                        manifestation = self,
                        publisher = Corporation.fetch_or_get(raw_data[PUBLISHER_KEY]),
                        plate_number = raw_data[PLATE_NUMBER_KEY]
                    )
        if STITCHER_KEY in raw_data and (stitcher := raw_data[STITCHER_KEY]):
            self.stitcher = Corporation.fetch_or_get(stitcher)

        if FIGURE_KEY in raw_data and raw_data[FIGURE_KEY]:
            self.specific_figure = True

        if PRINT_TYPE_KEY in raw_data and (print_type := raw_data[PRINT_TYPE_KEY]):
            self.print_type = Manifestation.PrintType.parse_from_german(print_type)

        if AUTOGRAPH_HANDWRITING_KEY in raw_data and \
            raw_data[AUTOGRAPH_HANDWRITING_KEY]:
            ItemHandwriting.objects.create(
                    writer = Person.objects.get(gnd_id = list(fixed_persons.values())[0]),
                    item = single_item,
                    medium = raw_data[AUTOGRAPH_HANDWRITING_KEY]
                )

        if FOREIGN_HANDWRITING_KEY in raw_data\
            and raw_data[FOREIGN_HANDWRITING_KEY]:
            for entry in raw_data[FOREIGN_HANDWRITING_KEY].split('$'):
                dubious_writer = False
                if '?' in entry:
                    dubious_writer = True
                writer_gnd_id = Manifestation.extract_gnd_id(entry)
                medium = Manifestation.extract_medium(entry)
                if writer_gnd_id:
                    writer = Person.fetch_or_get(writer_gnd_id)
                    ItemHandwriting.objects.create(
                            writer = writer,
                            item = single_item,
                            medium = medium,
                            dubious_writer = dubious_writer
                        )
                else:
                    fixed_person_found = False
                    for person in fixed_persons:
                        if (gnd_id := fixed_persons[person]):
                            if person in entry:
                                ItemHandwriting.objects.create(
                                        writer = Person.objects.get(gnd_id = gnd_id),
                                        item = single_item,
                                        medium = medium,
                                        dubious_writer = dubious_writer
                                    )
                                fixed_person_found = True
                                break
                        else:
                            if person in entry:
                                ItemHandwriting.objects.create(
                                        writer = Person.objects.get(interim_designator = person),
                                        item = single_item,
                                        medium = medium,
                                        dubious_writer = dubious_writer
                                    )
                                fixed_person_found = True
                                break
                    if not fixed_person_found:
                        ItemHandwriting.objects.create(
                                item = single_item,
                                medium = medium,
                                dubious_writer = dubious_writer
                            )

        if ENVELOPE_TITLE_KEY in raw_data and\
            raw_data[ENVELOPE_TITLE_KEY]:
            writer_medium_list = []
            if ENVELOPE_TITLE_WRITER_KEY in raw_data:
                for entry in split('\$|\),', raw_data[ENVELOPE_TITLE_WRITER_KEY]):
                    writer_gnd_id = Manifestation.extract_gnd_id(etry)
                    if writer_gnd_id:
                        writer_medium_list += [{
                                'writer': Person.fetch_or_get(writer_gnd_id),
                                'medium': Manifestation.extract_medium(entry),
                                'dubious_writer': True if '?' in entry else False
                            }]
                    else:
                        fixed_person_found = False
                        for person in fixed_persons:
                            if (gnd_id := fixed_persons[person]):
                                if person in entry:
                                    writer_medium_list += [{
                                            'writer': Person.objects.get(gnd_id = gnd_id),
                                            'medium': Manifestation.extract_medium(entry),
                                            'dubious_writer': True if '?' in entry else False
                                        }]
                                    fixed_person_found = True
                                    break
                            else:
                                if person in entry:
                                    writer_medium_list += [{
                                            'writer': Person.objects.get(interim_designator = person),
                                            'medium': Manifestation.extract_medium(entry),
                                            'dubious_writer': True if '?' in entry else False
                                        }]
                                    fixed_person_found = True
                                    break
                        if not fixed_person_found:
                            print(f"no writer found for envelope title")

            if ENVELOPE_TITLE_MEDIUM_KEY in raw_data:
                writer_medium_list += [{
                        'writer': Person.objects.get(gnd_id = list(fixed_persons.values())[0]),
                        'medium': raw_data[ENVELOPE_TITLE_MEDIUM_KEY],
                        'dubious_writer': False
                    }]

            manifestation_title_list = []
            for i, title in enumerate(raw_data[ENVELOPE_TITLE_KEY].split('$')):
                manifestation_title_list += [ ManifestationTitle.objects.create(
                        title = '\n'.join(title_line.strip() for title_line in title.split('|')),
                        title_type = TitleTypes.ENVELOPE_OR_TITLE_PAGE,
                        manifestation = self
                    ) ]
                #manifestation_title_list += [ ManifestationTitle.parse_from_csv(
                        #title = title.strip(),
                        #title_type = TitleTypes.ENVELOPE_OR_TITLE_PAGE,
                        #manifestation = self
                    #).save() ]

            if len(manifestation_title_list) == 1 and len(writer_medium_list) == 1:
                ManifestationTitleHandwriting.objects.create(
                        writer = writer_medium_list[0]['writer'],
                        medium = writer_medium_list[0]['medium'],
                        dubious_writer = writer_medium_list[0]['dubious_writer'],
                        manifestation_title = manifestation_title_list[0]
                    )

            if len(manifestation_title_list) == 1 and len(writer_medium_list) > 1:
                for writer_medium in writer_medium_list:
                    ManifestationTitleHandwriting.objects.create(
                            writer = writer_medium['writer'],
                            medium = writer_medium['medium'],
                            dubious_writer = writer_medium['dubious_writer'],
                            manifestation_title = manifestation_title_list[0],
                        )

            if len(manifestation_title_list) > 1 and len(writer_medium_list) == 1:
                for manifestation_title in manifestation_title_list:
                    ManifestationTitleHandwriting.objects.create(
                            writer = writer_medium_list[0]['writer'],
                            medium = writer_medium_list[0]['medium'],
                            dubious_writer = writer_medium_list[0]['dubious_writer'],
                            manifestation_title = manifestation_title,
                        )

            if len(manifestation_title_list) > 1 and len(writer_medium_list) > 1:
                if len(manifestation_title_list) != len(writer_medium_list):
                    print('length of manifestation title list and writer medium list differ')
                for i, writer_medium in enumerate(writer_medium_list):
                    ManifestationTitleHandwriting.objects.create(
                            writer = writer_medium['writer'],
                            medium = writer_medium['medium'],
                            dubious_writer = writer_medium['dubious_writer'],
                            manifestation_title = manifestation_title_list[i],
                        )

        if HEAD_TITLE_KEY in raw_data and\
            raw_data[HEAD_TITLE_KEY]:
            writer_medium_list = []
            if HEAD_TITLE_WRITER_KEY in raw_data:
                for entry in split('\$|\),', raw_data[HEAD_TITLE_WRITER_KEY]):
                    writer_gnd_id = Manifestation.extract_gnd_id(entry)
                    if writer_gnd_id:
                        writer_medium_list += [{
                                'writer': Person.fetch_or_get(writer_gnd_id),
                                'medium': Manifestation.extract_medium(entry),
                                'dubious_writer': True if '?' in entry else False
                            }]
                    else:
                        fixed_person_found = False
                        for person in fixed_persons:
                            if (gnd_id := fixed_persons[person]):
                                if person in entry:
                                    writer_medium_list += [{
                                            'writer': Person.objects.get(gnd_id = gnd_id),
                                            'medium': Manifestation.extract_medium(entry),
                                            'dubious_writer': True if '?' in entry else False
                                        }]
                                    fixed_person_found = True
                                    break
                            else:
                                if person in entry:
                                    writer_medium_list += [{
                                            'writer': Person.objects.get(interim_designator = person),
                                            'medium': Manifestation.extract_medium(entry),
                                            'dubious_writer': True if '?' in entry else False
                                        }]
                                    fixed_person_found = True
                                    break
                        if not fixed_person_found:
                            print(f"no writer found for head title")

            if HEAD_TITLE_MEDIUM_KEY in raw_data:
                writer_medium_list += [{
                        'writer': Person.objects.get(gnd_id = list(fixed_persons.values())[0]),
                        'medium': raw_data[HEAD_TITLE_MEDIUM_KEY],
                        'dubious_writer': False
                    }]

            manifestation_title_list = []
            for i, title in enumerate(raw_data[HEAD_TITLE_KEY].split('$')):
                manifestation_title_list += [ ManifestationTitle.objects.create(
                        title = '\n'.join(title_line.strip() for title_line in title.split('|')),
                        title_type = TitleTypes.HEAD_TITLE,
                        manifestation = self
                    ) ]
                #manifestation_title_list += [ ManifestationTitle.parse_from_csv(
                        #title = title.strip(),
                        #title_type = TitleTypes.HEAD_TITLE,
                        #manifestation = self
                    #).save() ]

            if len(manifestation_title_list) == 1 and len(writer_medium_list) == 1:
                ManifestationTitleHandwriting.objects.create(
                        writer = writer_medium_list[0]['writer'],
                        medium = writer_medium_list[0]['medium'],
                        dubious_writer = writer_medium_list[0]['dubious_writer'],
                        manifestation_title = manifestation_title_list[0]
                    )

            if len(manifestation_title_list) == 1 and len(writer_medium_list) > 1:
                for writer_medium in writer_medium_list:
                    ManifestationTitleHandwriting.objects.create(
                            writer = writer_medium['writer'],
                            medium = writer_medium['medium'],
                            dubious_writer = writer_medium['dubious_writer'],
                            manifestation_title = manifestation_title_list[0]
                        )

            if len(manifestation_title_list) > 1 and len(writer_medium_list) == 1:
                for manifestation_title in manifestation_title_list:
                    ManifestationTitleHandwriting.objects.create(
                            writer = writer_medium_list[0]['writer'],
                            medium = writer_medium_list[0]['medium'],
                            dubious_writer = writer_medium_list[0]['dubious_writer'],
                            manifestation_title = manifestation_title
                        )

            if len(manifestation_title_list) > 1 and len(writer_medium_list) > 1:
                if len(manifestation_title_list) != len(writer_medium_list):
                    print('length of manifestation title list and writer medium list differ')
                for i, writer_medium in enumerate(writer_medium_list):
                    ManifestationTitleHandwriting.objects.create(
                            writer = writer_medium['writer'],
                            medium = writer_medium['medium'],
                            dubious_writer = writer_medium['dubious_writer'],
                            manifestation_title = manifestation_title_list[i]
                        )

        private_title_comments = []
        if ENVELOPE_TITLE_COMMENT_KEY in raw_data and (comment := raw_data[ENVELOPE_TITLE_COMMENT_KEY]):
            private_title_comments += ['Kommentar Umschlagstitel: ' + comment]
        if HEAD_TITLE_COMMENT_KEY in raw_data and (comment := raw_data[HEAD_TITLE_COMMENT_KEY]):
            private_title_comments += ['Kommentar Kopftitel: ' + comment]
        if DEDICATION_COMMENT_KEY in raw_data and (comment := raw_data[DEDICATION_COMMENT_KEY]):
            private_title_comments += ['Kommentar Widmung: ' + comment]

        self.private_title_comment = '\n'.join(private_title_comments)

        self.extent = raw_data[EXTENT_KEY]
        self.measure = raw_data[MEASURE_KEY]

        if PHYSICAL_FEATURES_KEY in raw_data and (phys_features := raw_data[PHYSICAL_FEATURES_KEY]):
            self.private_manuscript_comment = f'Beschreiung physischer Merkmale: {phys_features}'

        if raw_data[DIGITAL_COPY_KEY]:
            ItemDigitalCopy.objects.create(
                    item = single_item,
                    url = raw_data[DIGITAL_COPY_KEY]
                )


class ManifestationTitle(DmRismManifestationTitle):
    class Meta:
        proxy = True

    def parse_from_csv(title, title_type, manifestation, writer = None, medium = None):
        manifestation_title = ManifestationTitle.objects.create(
                title_type = title_type,
                manifestation = manifestation,
                writer = writer,
                medium = medium
            )
        manifestation_title.title = title.replace('|', '\n')

        return manifestation_title


class Item (EdwocaUpdateUrlMixin, DmRismItem):
    class Meta:
        proxy = True

    def get_manifestation_url(self):
        return reverse(f'edwoca:manifestation_update', kwargs={'pk': self.manifestation.id})


class WeBaseClass(EdwocaUpdateUrlMixin, WemiBaseClass):
    class Meta:
        abstract = True

    def get_alt_titles(self):
        return ', '.join(alt_title.title for alt_title in self.titles.filter(status=Status.ALTERNATIVE))

    def get_pref_title(self):
        # Fetch all titles related to this instance in one query
        titles = self.titles.all()

        primary_title = next((t.title for t in titles if t.status == Status.PRIMARY), None)
        if primary_title:
            return primary_title

        temporary_title = next((t.title for t in titles if t.status == Status.TEMPORARY), None)
        if temporary_title:
            return f"{temporary_title.title} (T)"

        alternative_title = next((t.title for t in titles if t.status == Status.ALTERNATIVE), None)
        if alternative_title:
            return f"{alternative_title.title} (A)"

        return '<ohne Titel>'


class EventContributor(models.Model):
    class Role(models.TextChoices):
        COMPOSER = 'CP', _('Composer')
        WRITER = 'WR', _('Writer')
        TRANSLATOR = 'TR', _('Translator')
        POET = 'PT', _('Poet')
        DEDICATEE = 'DD', _('Dedicatee')

    event = models.ForeignKey(
        'Event',
        on_delete=models.CASCADE
    )
    person = models.ForeignKey(
        'dmad.Person',
        on_delete=models.CASCADE
    )
    role = models.CharField(max_length=10, choices=Role, default=Role.COMPOSER)


class WemiTitle(models.Model):
    class Meta:
        ordering = ['title']
        abstract = True

    title = models.CharField(max_length=100)
    status = models.CharField(max_length=1,choices=Status,default=Status.PRIMARY)
    language = models.CharField(max_length=15, choices=Language, default=Language['DE'])

    def __str__(self):
        return self.title

    def to_mei(self):
        title = ET.Element('title')
        if self.status == Status.ALTERNATIVE:
            title.attrib['type'] = 'alternative'
        title.text = self.title
        title.attrib['lang'] = to_iso639_1(self.language)
        return title


class Event(models.Model):
    class Type(models.TextChoices):
        PUBLISHED = 'PUB', _('Published')

    period = models.OneToOneField(
            'dmad.Period',
            on_delete=models.SET_NULL,
            null = True,
            blank = True,
            related_name = 'event'
        )
    event_type = models.CharField(
            max_length=10,
            choices=Type,
            default=Type.PUBLISHED
        )
    contributors = models.ManyToManyField(
            'dmad.Person',
            through = 'EventContributor'
        )
    place = models.ForeignKey(
            'dmad.Place',
            on_delete=models.SET_NULL,
            null = True
        )


class LetterSignature(BaseSignature):
    letter = models.ForeignKey(
            'Letter',
            on_delete = models.CASCADE,
            related_name = 'signatures'
        )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['letter'],
                condition=Q(status='C'),
                name='unique_current_letter_signature'
            )
        ]


class LetterDigitalCopy(BaseDigitalCopy):
    letter = models.ForeignKey(
            'Letter',
            on_delete = models.CASCADE,
            related_name = 'digital_copies'
        )


class Letter(models.Model):
    class Category(models.TextChoices):
        SKETCH = 'S', _('Sketch')
        LETTER = 'L', _('Letter')
        POSTCARD = 'P', _('Postcard')
        COPY = 'C', _('Copy')

    receiver_person = models.ForeignKey(
            'dmad.Person',
            null = True,
            on_delete = models.SET_NULL,
            related_name = 'received_letters'
        )
    sender_person = models.ForeignKey(
            'dmad.Person',
            null = True,
            on_delete = models.SET_NULL,
            related_name = 'sent_letters'
        )
    receiver_corporation = models.ForeignKey(
            'dmad.Corporation',
            null = True,
            on_delete = models.SET_NULL,
            related_name = 'received_letters'
        )
    sender_corporation = models.ForeignKey(
            'dmad.Corporation',
            null = True,
            on_delete = models.SET_NULL,
            related_name = 'sent_letters'
        )
    receiver_place = models.ForeignKey(
            'dmad.Place',
            null = True,
            on_delete = models.SET_NULL,
            related_name = 'received_letters'
        )
    sender_place = models.ForeignKey(
            'dmad.Place',
            null = True,
            on_delete = models.SET_NULL,
            related_name = 'sent_letters'
        )
    period = models.OneToOneField(
            'dmad.Period',
            on_delete=models.SET_NULL,
            null = True,
            blank = True,
            related_name = 'letter'
        )
    edition = models.ManyToManyField(
            'bib.ZotItem',
            related_name = 'edited_letters'
        )
    category = models.CharField(
            max_length = 1,
            choices = Category,
            default = Category.LETTER
        )
    comment = models.TextField(
            null = True,
            blank = True
        )
    manifestation = models.ManyToManyField(
            'Manifestation',
            related_name = 'letters'
        )
    person_provenance = models.ManyToManyField(
            'dmrism.PersonProvenanceStation',
            related_name = 'letters'
        )
    corporation_provenance = models.ManyToManyField(
            'dmrism.CorporationProvenanceStation',
            related_name = 'letters'
        )

    def get_absolute_url(self):
        return reverse('edwoca:letter_update', kwargs={'pk': self.id})

    def __str__(self):
        if self.sender_person:
            if self.sender_corporation:
                sender = str(self.sender_person) + ' u. a.'
            else:
                sender = str(self.sender_person)
        else:
            if self.sender_corporation:
                sender = str(self.sender_corporation)
            else:
                sender = 'unbekannt'

        if self.receiver_person:
            if self.receiver_corporation:
                receiver = str(self.receiver_person) + ' u. a.'
            else:
                receiver = str(self.receiver_person)
        else:
            if self.receiver_corporation:
                receiver = str(self.receiver_corporation)
            else:
                receiver = 'unbekannt'

        return f'{sender} an {receiver}, {self.period}'


class ItemModification(models.Model):
    class ModificationType(models.TextChoices):
        ARRANGEMENT = 'AR', _('Arrangement')
        TRANSCRIPTION = 'TR', _('Transcription')
        REVISION = 'RV', _('Revision')

    item = models.ForeignKey(
            'dmrism.Item',
            related_name = 'modifications',
            on_delete = models.CASCADE
        )
    related_manifestation = models.ForeignKey(
            'dmrism.Manifestation',
            related_name = 'relating_modifications',
            on_delete = models.SET_NULL,
            null = True
        )
    related_expression = models.ForeignKey(
            'Expression',
            related_name = 'relating_modifications',
            on_delete = models.SET_NULL,
            null = True
        )
    related_work = models.ForeignKey(
            'Work',
            related_name = 'relating_modifications',
            on_delete = models.SET_NULL,
            null = True
        )
    period = models.ForeignKey(
            'dmad.Period',
            related_name = 'modification',
            on_delete = models.SET_NULL,
            null = True
        )
    note = models.TextField(
            null = True,
            blank = True
        )
    modification_type = models.CharField(
            max_length = 2,
            choices = ModificationType,
            default = None,
            null = True
        )


class ModificationHandwriting(BaseHandwriting):
    modification = models.ForeignKey(
            'ItemModification',
            related_name = 'handwritings',
            on_delete = models.CASCADE
        )
