from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from dmad_on_django.models import Status, Language, Person, Corporation, Place, Period
from dmrism.models import WemiBaseClass, TitleTypes, Library, Signature, ManifestationHandwriting, ManifestationTitle, ManifestationTitleHandwriting, DigitalCopy
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

        catalog_number = 'o. N.'
        if self.expressions.count() > 0:
            catalog_number = self.expressions.all()[0].work_catalog_number
        if self.expressions.count() > 1:
            catalog_number += '+'

        if self.missing_item:
            return f"{catalog_number} unbekannt {numerus_currens}"

        publisher_addition = self.period
        if self.plate_number:
            publisher_addition = self.plate_number

        return f"{catalog_number}, {self.publisher.get_designator()} {publisher_addition}"

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

    def parse_csv(self, raw_data, source_type):
        INSTITUTION_KEY = 'Bestandeshaltende Institution'
        FORMER_SIGNATURE_KEY = 'Signatur, vormalig'
        IDENTIFICATION_KEY = 'WVZ-Nr.'
        TITLE_KEY = 'Titel (normiert, nach MGG)'
        EDITION_TYPE_KEY = 'Ausgabeform (Typ)'
        FUNCTION_KEY = 'Funktion'

        ENVELOPE_TITLE_KEY = 'Titelei Umschlag oder Titelblatt'
        ENVELOPE_TITLE_WRITER_KEY = 'Schreiber Titelei' # Schreiber Umschlag/Titelblatt Bezug zu O
        ENVELOPE_TITLE_MEDIUM_KEY = 'Autor Titelei (Liszt egh.)'

        HEAD_TITLE_KEY = 'Kopftitel'
        HEAD_TITLE_WRITER_KEY = 'Schreiber Kopftitel' # Schreiber Umschlag/Titelblatt Bezug zu O
        HEAD_TITLE_MEDIUM_KEY = 'Autor Kopftitel (Liszt egh.)'

        DEDICATION_KEY = 'Widmung (diplomatisch)'
        MEDIUM_OF_PERFORMANCE_KEY = 'Besetzung (normiert)'
        TEMPO_KEY = 'Tempoangabe (normiert)'
        METRONOM_KEY = 'Metronomangabe'
        LANGUAGE_KEY = 'Sprachcode'
        TEXT_INCIPIT_KEY = 'Text-Incipit (diplomatisch)'
        LOCATION_KEY = 'GND-Nr. Ort'
        DIPLOMATIC_DATE_KEY = 'Datierung (diplomatisch)'
        MACHINE_READABLE_DATE_KEY = 'Datierung (maschinenlesbar)'
        RELATED_PRINT_PUBLISHER_KEY = 'Bezug zu Druck: Verlags-GND-Nr.'
        RELATED_PRINT_PLATE_NUMBER_KEY = 'Bezug zu Druck: Plattennr.'

        AUTOGRAPH_HANDWRITING_KEY = 'Schrift (Liszt egh.)'
        FOREIGN_HANDWRITING_KEY = 'Schrift (fremder Hand)'
        WRITING_KEY = 'Schreiber zu AB gehörig bitte mit Information in AC kombinieren'

        EXTENT_KEY = 'Umfang'
        MEASURE_KEY = 'Papiermaß'

        DIGITAL_COPY_KEY = 'Digitalisat'

        LISZT_GND_ID = '118573527'

        ANONYMOUS_WRITERS = ['zS', 'Dr']

        FUNCTION_KEY = 'Funktion'

        DEDUCED_PLACE_NAME_KEY = 'Ort ermittelt (normiert)'
        DEDUCED_PLACE_ID_KEY = 'Ort ermittelt GND-Nr.'

        PROVENANCE_KEY1 = 'Provenienz Station 1'
        PROVENANCE_KEY2 = 'Provenienz Station 2'
        PROVENANCE_KEY3 = 'Provenienz Station 3'
        PROVENANCE_KEY4 = 'Provenienz Station 4'

        MANIFESTATION_NOTES_KEY = 'Notizen zur Quelle (vormals "Beschreibung", bleibt intern)'
        MANIFESTATION_COMMENT_KEY = 'Kommentar zur Quelle (intern)'
        COMMENT_QUESTION_KEY = 'Kommentar intern / Fragen (interne Kommunikation)'
        FURTHER_INFORMATION_KEY = 'Weiterführende Informationen (Ausgaben, Permalinks etc.) (intern)'

        self.taken_information = '\n'.join([
                'Notizen zur Quelle: ' + raw_data[MANIFESTATION_NOTES_KEY],
                'Kommentar zur Quelle: ' + raw_data[MANIFESTATION_COMMENT_KEY],
                'Kommentar intern: ' + raw_data[COMMENT_QUESTION_KEY],
                'Weiterführende Informationen: ' + raw_data[FURTHER_INFORMATION_KEY]
            ])

        self.private_provenance_comment = '\n'.join(
                provenance_string for
                provenance_key in
                [ PROVENANCE_KEY1, PROVENANCE_KEY2, PROVENANCE_KEY3, PROVENANCE_KEY4 ]
                if (provenance_string := raw_data[provenance_key])
            )

        for writer in ANONYMOUS_WRITERS:
            if Person.objects.filter(interim_designator = writer).count() == 0:
                Person.objects.create(interim_designator = writer)

        # add stitch template flag to manifestation?
        liszt = Person.fetch_or_get(LISZT_GND_ID)

        if not getattr(Manifestation.SourceType, source_type):
            raise Exception(f'Unknown source type {source_type}')

        self.source_type = getattr(Manifestation.SourceType, source_type)

        self.is_singleton = True
        self.titles.all().delete()

        self.private_head_comment = '\n'.join([
                'Identifikation: ' + raw_data[IDENTIFICATION_KEY],
                'Besetzung: ' + raw_data[MEDIUM_OF_PERFORMANCE_KEY],
                'Tempo: ' + raw_data[TEMPO_KEY],
                'Metronom:' + raw_data[METRONOM_KEY],
                'Sprache: ' + raw_data[LANGUAGE_KEY],
                'Textincipit: ' + raw_data[TEXT_INCIPIT_KEY]
            ])

        if raw_data[DEDUCED_PLACE_NAME_KEY]:
            self.private_history_comment = f"Ort ermittelt: {raw_data[DEDUCED_PLACE_NAME_KEY]}, {raw_data[DEDUCED_PLACE_ID_KEY]}"

        self.function = Manifestation.Function.parse_from_german(raw_data[FUNCTION_KEY])

        if self.RISM_ID_KEY in raw_data and\
            raw_data[self.RISM_ID_KEY] and\
            raw_data[self.RISM_ID_KEY].isnumeric():
            self.rism_id = raw_data[self.RISM_ID_KEY]

        library = Library.objects.filter(siglum = raw_data[INSTITUTION_KEY]).first() or \
            Library.objects.create(siglum = raw_data[INSTITUTION_KEY])
        signature = Signature.objects.create(
                library = library,
                status = Signature.Status.CURRENT,
                signature = raw_data[Manifestation.CURRENT_SIGNATURE_KEY]
            )
        single_item = Item.objects.create(manifestation = self)
        single_item.signatures.add(signature)

        if raw_data[FORMER_SIGNATURE_KEY]:
            former_signature = Signature.objects.create(
                    library = library,
                    status = Signature.Status.FORMER,
                    signature = raw_data[FORMER_SIGNATURE_KEY]
                )
            single_item.signatures.add(former_signature)

        if raw_data[LOCATION_KEY]:
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
                    for writer in ANONYMOUS_WRITERS:
                        if writer in dedication:
                            dedicatee = Person.objects.get(interim_designator = writer)
                            self.dedicatees.add(dedicatee)
                            break

        self.date_diplomatic = raw_data[DIPLOMATIC_DATE_KEY].replace(' | ', '\n')
        if raw_data[MACHINE_READABLE_DATE_KEY]:
            self.period = Period.parse(raw_data[MACHINE_READABLE_DATE_KEY])

        if raw_data[RELATED_PRINT_PUBLISHER_KEY]:
            self.publisher = Corporation.fetch_or_get(raw_data[RELATED_PRINT_PUBLISHER_KEY])
        self.plate_number = raw_data[RELATED_PRINT_PLATE_NUMBER_KEY]
        # machine readable key abklären

        if AUTOGRAPH_HANDWRITING_KEY in raw_data and \
            raw_data[AUTOGRAPH_HANDWRITING_KEY]:
            ManifestationHandwriting.objects.create(
                    writer = liszt,
                    manifestation = self,
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
                    ManifestationHandwriting.objects.create(
                            writer = writer,
                            manifestation = self,
                            medium = medium,
                            dubious_writer = dubious_writer
                        )
                else:
                    if 'Liszt' in entry:
                        ManifestationHandwriting.objects.create(
                                writer = liszt,
                                manifestation = self,
                                medium = medium,
                                dubious_writer = dubious_writer
                            )
                    else:
                        anonymous_writer_found = False
                        for designator in ANONYMOUS_WRITERS:
                            if designator in entry:
                                writer = Person.objects.get(interim_designator = designator)
                                ManifestationHandwriting.objects.create(
                                        writer = writer,
                                        manifestation = self,
                                        medium = medium,
                                        dubious_writer = dubious_writer
                                    )
                                anonymous_writer_found = True
                                break
                        if not anonymous_writer_found:
                            ManifestationHandwriting.objects.create(
                                    manifestation = self,
                                    medium = medium,
                                    dubious_writer = dubious_writer
                                )

        if ENVELOPE_TITLE_KEY in raw_data and\
            raw_data[ENVELOPE_TITLE_KEY]:
            writer_medium_list = []
            if ENVELOPE_TITLE_WRITER_KEY in raw_data:
                for entry in split('\$|\),', raw_data[ENVELOPE_TITLE_WRITER_KEY]):
                    writer_gnd_id = Manifestation.extract_gnd_id(entry)
                    if writer_gnd_id:
                        writer_medium_list += [{
                                'writer': Person.fetch_or_get(writer_gnd_id),
                                'medium': Manifestation.extract_medium(entry),
                                'dubious_writer': True if '?' in entry else False
                            }]
                    else:
                        if 'Liszt' in entry:
                            writer_medium_list += [{
                                    'writer': liszt,
                                    'medium': Manifestation.extract_medium(entry),
                                    'dubious_writer': True if '?' in entry else False
                                }]
                        else:
                            anonymous_writer_found = False
                            for anonymous_writer in ANONYMOUS_WRITERS:
                                if anonymous_writer in entry:
                                    writer_medium_list += [{
                                            'writer': Person.objects.get(interim_designator = anonymous_writer),
                                            'medium': Manifestation.extract_medium(entry),
                                            'dubious_writer': True if '?' in entry else False
                                        }]
                                    anonymous_writer_found = True
                                    break
                            if not anonymous_writer_found:
                                print(f"no writer found for envelope title")

            if ENVELOPE_TITLE_MEDIUM_KEY in raw_data:
                writer_medium_list += [{
                        'writer': liszt,
                        'medium': raw_data[HEAD_TITLE_MEDIUM_KEY],
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
                        if 'Liszt' in entry:
                            writer_medium_list += [{
                                    'writer': liszt,
                                    'medium': Manifestation.extract_medium(entry),
                                    'dubious_writer': True if '?' in entry else False
                                }]
                        else:
                            anonymous_writer_found = False
                            for anonymous_writer in ANONYMOUS_WRITERS:
                                if anonymous_writer in entry:
                                    writer_medium_list += [{
                                            'writer': Person.objects.get(interim_designator = anonymous_writer),
                                            'medium': Manifestation.extract_medium(entry),
                                            'dubious_writer': True if '?' in entry else False
                                        }]
                                    anonymous_writer_found = True
                                    break
                            if not anonymous_writer_found:
                                print(f"no writer found for envelope title")

            if HEAD_TITLE_MEDIUM_KEY in raw_data:
                writer_medium_list += [{
                        'writer': liszt,
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

        self.extent = raw_data[EXTENT_KEY]
        self.measure = raw_data[MEASURE_KEY]

        if raw_data[DIGITAL_COPY_KEY]:
            DigitalCopy.objects.create(
                    item = self.items.all()[0],
                    url = raw_data[DIGITAL_COPY_KEY]
                )

        # R -> medium of performance (leave open)

        # X/Y -> period

        # add handwriting model with writer/medium

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
