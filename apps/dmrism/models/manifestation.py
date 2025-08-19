from .base import *
from ..rism_tools import get_rism_data
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from .item import Item, Signature, Library
from dmad_on_django.models import Language
from iso639 import find as lang_find
from liszt_util.tools import RenderRawJSONMixin


class TitleTypes(models.TextChoices):
    ENVELOPE = 'EN', _('Envelope')
    TITLE_PAGE = 'TP', _('Title Page')
    HEAD_TITLE = 'HT', _('Head Title')


class Manifestation(RenderRawJSONMixin, WemiBaseClass):
    class ManifestationForm(models.TextChoices):
        SKETCHES = 'SK', _('Sketches'),
        FRAGMENTS = 'FR', _('Fragments'),
        EXCERPTS = 'EX', _('Excerpts')

    class EditionType(models.TextChoices):
        SCORE = 'SCO', _('Score')
        PART = 'PRT', _('Part')
        PARTS = 'PTS', _('Parts')
        PARTICELL = 'PTC', _('Particell')
        PIANO_REDUCTION = 'PNR', _('Piano Reduction')
        CHOIR_SCORE = 'CSC', _('Choir Score')

    class State(models.TextChoices):
        COMPLETE= 'CP', _('complete')
        INCOMPLETE= 'INC', _('incomplete')

    rism_id_unaligned = models.BooleanField(default=False)
    temporary = models.BooleanField(default=False)
    temporary_target = models.ForeignKey(
            'Manifestation',
            on_delete = models.CASCADE,
            null = True,
            related_name = 'temporary_copy'
        )
    # move to edwoca?
    plate_number = models.CharField(
            max_length = 10,
            null = True,
            blank = True
        )
    period = models.OneToOneField(
            'dmad.Period',
            on_delete = models.SET_NULL,
            blank = True,
            null = True
        )
    place = models.ForeignKey(
            'dmad.Place',
            on_delete = models.SET_NULL,
            blank = True,
            null = True
        )
    contributors = models.ManyToManyField(
            'dmad.Person',
            through = 'ManifestationContributor'
        )
    related_manifestations = models.ManyToManyField(
            'Manifestation',
            through = 'RelatedManifestation'
        )
    manifestation_form = models.CharField(
            max_length=10,
            choices = ManifestationForm,
            default = None,
            null = True
        )
    edition_type = models.CharField(
            max_length = 10,
            choices = EditionType,
            default = None,
            null = True
        )
    state = models.CharField(
            max_length=10,
            choices=State,
            default=State.COMPLETE
        )
    history = models.TextField(
            blank = True,
            null = True
        )
    bib = models.ManyToManyField(
            'bib.ZotItem',
            through = 'ManifestationBib'
        )
    dedicatee = models.ForeignKey(
            'dmad.Person',
            on_delete=models.SET_NULL,
            related_name='dedicated_manifestations',
            blank=True,
            null=True
        )
    language = models.CharField(
            max_length=15,
            choices=Language,
            default=None,
            null=True
        )
    dedication = models.TextField(
            max_length=100,
            blank=True,
            null=True
        )
    watermark = models.TextField(
            max_length=100,
            blank=True,
            null=True
        )
    watermark_url = models.URLField(
            blank=True,
            null=True
        )
    is_singleton = models.BooleanField(default=False)
    missing_item = models.BooleanField(default=False)
    # move to edwoca?
    numerus_currens = models.IntegerField(
            null = True,
            unique = True
        )
    rism_id = models.CharField(
            max_length=20,
            null = True,
            blank = True
        )
    raw_data = models.TextField(
            blank = True,
            null = True
        )
    handwriting = models.TextField(
            blank = True,
            null = True
        )
    extent = models.TextField(
            blank = True,
            null = True
        )
    paper = models.TextField(
            blank = True,
            null = True
        )
    #publisher = models.ForeignKey(
            #'dmad.Corporation',
            #related_name = 'publishers',
            #null = True,
            #on_delete = models.SET_NULL
        #)

    def get_absolute_url(self):
        return reverse('dmrism:manifestation_detail', kwargs={'pk': self.id})

    def get_pref_title(self):
        #titles = self.titles.all()

        #envelope_title = next((t.title for t in titles if t.title_type == TitleTypes.ENVELOPE), None)
        #if envelope_title:
            #return envelope_title

        #title_page_title = next((t.title for t in titles if t.title_type == TitleTypes.TITLE_PAGE), None)
        #if title_page_title:
            #return title_page_title

        #head_title = next((t.title for t in titles if t.title_type == TitleTypes.HEAD_TITLE), None)
        #if head_title:
            #return head_title

        #return '<ohne Titel>'
        return self.__str__()

    def __str__(self):
        if self.items.count():
            return self.items.all()[0].__str__()
        return '<Fehler: keine Items>'

    def save(self, *args, **kwargs):
        if self.is_singleton and self.items.count() > 1:
            raise ValidationError("A singleton manifestation cannot have more than one item.")
        super().save(*args, **kwargs)

    def unset_singleton(self):
        self.is_singleton = False

    def set_singleton(self):
        if self.items.count() > 1:
            raise Exception('A print with more than one item was declared a manuscript.')

        self.is_singleton = True
        if self.items.count() == 0 and not self.missing_item:
            self.items.create()

    def set_missing(self):
        if self.items.count() > 1:
            raise Exception('A manifestation with more than one item was declared as missing items.')
        self.items.all().delete()

        self.missing_item = True
        max_numerus_currens_manifestation = Manifestation.objects.filter(missing_item = True).order_by('numerus_currens').last()
        if max_numerus_currens_manifestation:
            self.numerus_currens = max_numerus_currens_manifestation.numerus_currens + 1
        else:
            self.numerus_currens = 1

    def unset_missing(self):
        self.items.create()
        self.missing_item = False

    def pull_rism_data(self):
        EXTENT_MARKER = 'Umfang: '
        HANDWRITING_MARKER = 'Schrift: '
        PAPER_MARKER = 'Papier: '

        data = get_rism_data(self.rism_id)
        self.raw_data = data.as_json()

        location = data.get('852')
        siglum = location.get('a')
        library = Library.objects.filter(siglum = siglum).first() or \
            Library.objects.create(
                    siglum = siglum,
                    name = location.get('e')
                )
        if library.name == '':
            library.name = location.get('e')

        if self.items.count() == 0:
            signature = Signature.objects.create(
                    library = library,
                    status = Signature.Status.CURRENT,
                    signature = location.get('c')
                )
            item = Item.objects.create(
                    manifestation = self
                )
            item.signatures.add(signature)

        # 852$d vormalige signatur
        # Verhältnis zu vormaligem Besitzer/Provenienz klären

        if data.get('240') and data.get('240').get('k'):
            self.manifestation_form = getattr(Manifestation.ManifestationForm, data.get('240').get('k').upper())

        # beispiel für former owner: 1001340874
        personal_names = data.get_fields('700')
        corporate_names = data.get_fields('710')
        comment = [ self.private_comment or '' ]
        comment += [
                f"Widmungsträger:in (Person): {personal_name.get('a')}"
                for personal_name
                in personal_names
                if personal_name.get('4') == 'dte'
            ]
        comment += [
                f"Widmungsträger:in (Institution): {corporate_name.get('a')}"
                for corporate_name
                in corporate_names
                if corporate_name.get('4') == 'dte'
            ]
        comment += [
                f"Vormalige:r Besitzer:in (Person): {personal_name.get('a')}"
                for personal_name
                in personal_names
                if personal_name.get('4') == 'fmo'
            ]
        comment += [
                f"Vormalige:r Besitzer:in (Institution): {corporate_name.get('a')}"
                for corporate_name
                in corporate_names
                if corporate_name.get('4') == 'fmo'
            ]

        # 031$d tempo
        # 031$q metronom
        # 031$t textincipit
        # bsp 1001340874

        # musical_incipits_information = data.get('031')
        #self.tempo = musical_incipits_information.get('d')

        # bsp?
        # self.metronom = musical_incipits_information.get('q')

        # bsp?
        # self.textual_incipit = musical_incipits_information.get('t')

        # diese informationen werden teil der expressions-charakteristika; heir muss erst abgewartet werden

        # bsp 1001310759
        language_code = data.get('041')
        if language_code:
            self.language = Language[lang_find(language_code.get('a'))['iso639_1'].upper()]

        imprint = data.get_fields('260')
        comment += [
                f"Ort: {field.get('a')}"
                for field
                in imprint
                if field.get('a')
            ]

        # bsp 1001340032
        #breakpoint()
        for host_item_entry in data.get_fields('773'):
            target_rism_id = host_item_entry.get('w').replace('sources/', '')
            target_manifestation = Manifestation.get_or_create(target_rism_id)
            RelatedManifestation.objects.create(
                    source_manifestation = self,
                    target_manifestation = target_manifestation,
                    label = RelatedManifestation.Label.PARENT
                )

        for electronic_location in data.get_fields('856'):
            DigitalCopy.objects.create(
                    manifestation = self,
                    url = electronic_location.get('u'),
                    link_type = electronic_location.get('x')
                )

        general_notes = data.get_fields('500')
        self.extent = '\n'.join(
                note.get('a').replace(EXTENT_MARKER, '')
                for note
                in general_notes
                if note.get('a').startswith(EXTENT_MARKER)
            )

        self.paper = '\n'.join(
                note.get('a').replace(PAPER_MARKER, '')
                for note
                in general_notes
                if note.get('a').startswith(PAPER_MARKER)
            )

        comment += [
                general_note.get('a')
                for general_note
                in general_notes
                if general_note.get('a').startswith(HANDWRITING_MARKER)
            ]

        self.is_singleton = True
        self.private_comment = '\n'.join(comment)
        self.rism_id_unaligned = False
        self.save()

        return self

    def get_or_create(rism_id):
        return Manifestation.objects.filter(rism_id = rism_id).first() or \
            Manifestation.objects.create(rism_id = rism_id).pull_rism_data()



class ManifestationTitle(models.Model):

    title = models.CharField(
            max_length=100,
            null=True,
            blank=True
        )
    title_type = models.CharField(
            max_length=2,
            choices=TitleTypes,
            default=TitleTypes.ENVELOPE
        )
    writer = models.ForeignKey(
            'dmad.Person',
            on_delete=models.SET_NULL,
            related_name='written_manifestation_titles',
            blank=True,
            null=True
        )
    medium = models.CharField(
            max_length=100,
            null=True,
            blank=True
        )
    manifestation = models.ForeignKey(
            'Manifestation',
            on_delete=models.CASCADE,
            related_name='titles',
        )


class ManifestationBib(BaseBib):
    manifestation = models.ForeignKey(
        'Manifestation',
        on_delete=models.CASCADE,
        related_name='bib_set'
    )


class ManifestationContributor(BaseContributor):
    manifestation = models.ForeignKey(
        'Manifestation',
        on_delete=models.CASCADE,
        related_name='contributor_relations'
    )


class RelatedManifestation(RelatedEntity):
    class Label(models.TextChoices):
        PARENT = 'PA', _('Parent'),
        RELATED = 'RE', _('Related')

    source_manifestation = models.ForeignKey(
            'Manifestation',
            on_delete=models.CASCADE,
            related_name="source_manifestation_of"
        )
    target_manifestation = models.ForeignKey(
            'Manifestation',
            on_delete=models.CASCADE,
            related_name="target_manifestation_of"
        )
    label = models.CharField(
            max_length=10,
            choices=Label,
            default=Label.PARENT
        )


class DigitalCopy(models.Model):
    manifestation = models.ForeignKey(
            'Manifestation',
            on_delete = models.CASCADE,
            related_name = 'digital_copies'
        )
    url = models.URLField(
            blank=True,
            null=True
        )
    link_type = models.CharField(
            max_length = 10,
            null = True,
            blank = True
        )
