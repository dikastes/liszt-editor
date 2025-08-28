from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from dmad_on_django.models import Status, Language, Person, Corporation, Place
from dmrism.models import WemiBaseClass, TitleTypes, Library, Signature, ManifestationHandwriting, ManifestationContributor, ManifestationTitle, ManifestationTitleHandwriting, DigitalCopy
from dmrism.models import Manifestation as DmRismManifestation
from dmrism.models import ManifestationTitle as DmRismManifestationTitle
from dmrism.models import Item as DmRismItem
from re import compile

class EdwocaUpdateUrlMixin:
    def get_absolute_url(self):
        model = self.__class__.__name__.lower()
        return reverse(f'edwoca:{model}_update', kwargs={'pk': self.id})


class Manifestation(EdwocaUpdateUrlMixin, DmRismManifestation):
    RISM_ID_KEY = 'RISM ID no.'

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

        #return f"{catalog_number}, {self.publisher} {self.publisher_addition}"
        return f"{catalog_number}, <<Verlag>> {publisher_addition}"

    def extract_gnd_id(dedicatee):
        ID_PATTERN = '[0-9]\w{4,}-?\w? *]'
        id_pattern = compile(ID_PATTERN)
        match = id_pattern.match(dedicatee)
        if match:
            return dedicatee[match.start():match.end()].replace(']', '').strip()
        return None

    def extract_medium(medium_string):
        MEDIUM_PATTERN = '\(\w*\)'
        medium_pattern= compile(MEDIUM_PATTERN)
        match = medium_pattern.match(medium_string)
        if match:
            return medium_string[match.start():match.end()].\
                replace('(', '').\
                replace(')', '').\
                strip()

    def parse_csv(self, raw_data):
        INSTITUTION_KEY = 'Bestandeshaltende Institution'
        CURRENT_SIGNATURE_KEY = 'Signatur, neu'
        FORMER_SIGNATURE_KEY = 'Signatur, vormalig'
        IDENTIFICATION_KEY = 'WVZ-Nr.'
        EDITION_TYPE_KEY = 'Ausgabeform (Typ)'
        FUNCTION_KEY = 'Funktion'
        ENVELOPE_TITLE_KEY = 'Titelei Umschlag oder Titelblatt'
        HEAD_TITLE_KEY = 'Kopftitel'
        TITLE_WRITER_KEY = 'Schreiber Titelei' # Schreiber Umschlag/Titelblatt Bezug zu O
        TITLE_MEDIUM_KEY = 'Autor Titelei (Liszt egh.)'
        FOREIGN_TITLE_MEDIUM_KEY = 'Autor Kopftitel (Liszt egh.)'
        DEDICATION_KEY = 'Widmung (diplomatisch)'
        MEDIUM_OF_PERFORMANCE_KEY = 'Besetzung (normiert)'
        TEMPO_KEY = 'Tempoangabe (normiert)'
        METRONOM_KEY = 'Metronomangabe'
        TEXT_INCIPIT_KEY = 'Text-Incipit (diplomatisch)'
        LOCATION_KEY = 'GND-Nr. Ort'
        DIPLOMATIC_DATE_KEY = 'Datierung (diplomatisch)'
        MACHINE_READABLE_DATE_KEY = 'Datierung (maschinenlesbar)'
        RELATED_PRINT_PUBLISHER_KEY = 'Bezug zu Druck: Verlags-GND-Nr.'
        RELATED_PRINT_PLATE_NUMBER_KEY = 'Bezug zu Druck: Plattennr.'
        TITLE_KEY = 'Titel (normiert, nach MGG)'

        AUTOGRAPH_HANDWRITING_KEY = 'Schrift (Liszt egh.)'
        FOREIGN_HANDWRITING_KEY = 'Schrift (fremder Hand)'
        WRITING_KEY = 'Schreiber zu AB gehörig bitte mit Information in AC kombinieren'

        EXTENT_KEY = 'Umfang'
        MEASURE_KEY = 'Papiermaß'

        DIGITAL_COPY_KEY = 'Digitalisat'

        LISZT_GND_ID = '118573527'

        # add stitch template flag to manifestation?
        liszt = Person.fetch_or_get(LISZT_GND_ID)

        self.private_comment = raw_data[IDENTIFICATION_KEY]
        self.is_singleton = True
        self.titles.all().delete()


        if self.RISM_ID_KEY in raw_data and\
            raw_data[self.RISM_ID_KEY] and\
            raw_data[self.RISM_ID_KEY].isnumeric():
            self.rism_id = raw_data[self.RISM_ID_KEY]

        library = Library.objects.filter(siglum = raw_data[INSTITUTION_KEY]).first() or \
            Library.objects.create(siglum = raw_data[INSTITUTION_KEY])
        signature = Signature.objects.create(
                library = library,
                status = Signature.Status.CURRENT,
                signature = raw_data[CURRENT_SIGNATURE_KEY]
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
        dedicatee_ids = [ 
                gnd_id for
                dedicatee in
                raw_data[DEDICATION_KEY].split('|')
                if (gnd_id := Manifestation.extract_gnd_id(dedicatee)) is not None
            ]
        for id in dedicatee_ids:
            dedicatee = Person.fetch_or_get(id)
            ManifestationContributor.create(
                    person = dedicatee,
                    role = ManifestationContributor.Role.DEDICATEE,
                    manifestation = self
                )

        self.function = raw_data[FUNCTION_KEY]

        self.date_diplomatic = raw_data[DIPLOMATIC_DATE_KEY].replace(' | ', '\n')

        if raw_data[RELATED_PRINT_PUBLISHER_KEY]:
            self.publisher = Corporation.fetch_or_get(raw_data[RELATED_PRINT_PUBLISHER_KEY])
        self.plate_number = raw_data[RELATED_PRINT_PLATE_NUMBER_KEY]
        # machine readable key abklären

        if raw_data[AUTOGRAPH_HANDWRITING_KEY]:
            ManifestationHandwriting.objects.create(
                    writer = liszt,
                    manifestation = self,
                    medium = raw_data[AUTOGRAPH_HANDWRITING_KEY]
                )

        if FOREIGN_HANDWRITING_KEY in raw_data:
            for entry in raw_data[FOREIGN_HANDWRITING_KEY].split('),'):
                writer_gnd_id = Manifestation.extract_gnd_id(entry)
                writer = Person.fetch_or_get(writer_gnd_id)
                medium = Manifestation.extract_medium(entry)
                ManifestationHandwriting.objects.create(
                        writer = writer,
                        manifestation = self,
                        medium = medium
                    )

        if ENVELOPE_TITLE_KEY in raw_data and\
            raw_data[ENVELOPE_TITLE_KEY]:
            envelope_titles = raw_data[ENVELOPE_TITLE_KEY].split('$')
            if len(envelope_titles) > 1:
                ManifestationTitle.parse_from_csv(envelope_titles[0], TitleTypes.ENVELOPE, self).save()
                ManifestationTitle.parse_from_csv(envelope_titles[1], TitleTypes.TITLE_PAGE, self).save()
            if len(envelope_titles) == 1:
                ManifestationTitle.parse_from_csv(envelope_titles[0], TitleTypes.TITLE_PAGE, self).save()
        if raw_data[HEAD_TITLE_KEY]:
            ManifestationTitle.parse_from_csv(raw_data[HEAD_TITLE_KEY], TitleTypes.HEAD_TITLE, self).save()

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

    def parse_from_csv(title, title_type, manifestation):
        manifestation_title = ManifestationTitle.objects.create( title_type = title_type, manifestation = manifestation )
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
