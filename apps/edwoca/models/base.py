from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from dmad_on_django.models import Status, Language
from dmrism.models import WemiBaseClass, TitleTypes, Library, Signature
from dmrism.models import Manifestation as DmRismManifestation
from dmrism.models import ManifestationTitle as DmRismManifestationTitle
from dmrism.models import Item as DmRismItem

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
                return EditionType.SCORE
            case 'Stimme':
                return EditionType.PART
            case 'Stimmen':
                return EditionType.PARTS
            case 'Particell':
                return EditionType.PARTICELL
            case 'Klavierauszug':
                return EditionType.PIANO_REDUCTION
            case 'Chorpartitur':
                return EditionType.CHOIR_SCORE

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

    def parse_csv(self, raw_data):
        INSTITUTION_KEY = 'Bestandeshaltende Institution'
        SIGNATURE_KEY = 'Signatur, neu'
        FORMER_SIGNATURE_KEY = 'Signatur, vormalig'
        IDENTIFICATION_KEY = 'WVZ-Nr.'
        EDITION_TYPE_KEY = 'Ausgabeform (Typ)'
        FUNCTION_KEY = 'Funktion'
        ENVELOPE_TITLE_KEY = 'Titelei Umschlag oder Titelblatt'
        HEAD_TITLE_KEY = 'Kopftitel'
        AUTHOR_TITLE_KEY = 'Autor Titelei (Liszt egh.)'
        FOREIGN_TITLE_KEY = 'Autor Kopftitel (Liszt egh.)'
        MEDIUM_OF_PERFORMANCE_KEY = 'Besetzung (normiert)'
        DIPLOMATIC_DATE_KEY = 'Datierung (diplomatisch)'
        MACHINE_READABLE_DATE_KEY = 'Datierung (maschinenlesbar)'
        RELATED_PRINT_PUBLISHER_KEY = 'Verlag (normiert)'
        RELATED_PRINT_PLATE_NUMBER_KEY = 'Bezug zu Druck: Plattennr.'

        # add stitch template flag to manifestation?

        self.private_comment = raw_data[IDENTIFICATION_KEY]
        self.is_singleton = True

        if self.RISM_ID_KEY in raw_data and\
            raw_data[self.RISM_ID_KEY] and\
            raw_data[self.RISM_ID_KEY].isnumeric():
            self.rism_id = raw_data[self.RISM_ID_KEY]
        else:
            library = Library.objects.filter(siglum = raw_data[INSTITUTION_KEY]).first() or \
                Library.objects.create(siglum = raw_data[INSTITUTION_KEY])
            signature = Signature.objects.create(
                    library = library,
                    status = Signature.Status.CURRENT,
                    signature = raw_data[SIGNATURE_KEY]
                )
            single_item = Item.objects.create(manifestation = self)
            single_item.signatures.add(signature)
            # former signature logic here

        if EDITION_TYPE_KEY in raw_data:
            self.edition_type = Manifestation.parse_edition_type(raw_data[EDITION_TYPE_KEY])

        # J -> function

        envelope_titles = raw_data[ENVELOPE_TITLE_KEY].split('$')
        if len(envelope_titles) > 1:
            ManifestationTitle.parse_from_csv(envelope_titles[0], TitleTypes.ENVELOPE, self).save()
            ManifestationTitle.parse_from_csv(envelope_titles[1], TitleTypes.TITLE_PAGE, self).save()
        if len(envelope_titles) == 1:
            ManifestationTitle.parse_from_csv(envelope_titles[0], TitleTypes.TITLE_PAGE, self).save()
        if raw_data[HEAD_TITLE_KEY]:
            ManifestationTitle.parse_from_csv(raw_data[HEAD_TITLE_KEY], TitleTypes.HEAD_TITLE, self).save()


        # remodel!! manifestationtitle needs the fields written_by_composer and writing_material
        # O/Q -> writing_material
        # if O/Q != '' -> written_by_composer = True

        # R -> medium of performance (leave open)

        # X/Y -> period

        # AG -> publisher

        # AI -> plate_number

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
