from .base import *
from ..rism_tools import get_rism_data
from .item import ItemDigitalCopy, BaseDigitalCopy
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from .item import Item, ItemSignature, Library
from dmad_on_django.models import Language, Status, Period, Person, Corporation
from bib.models import ZotItem
from iso639 import find as lang_find
from liszt_util.tools import RenderRawJSONMixin


class TitleTypes(models.TextChoices):
    ENVELOPE = 'EN', _('Envelope')
    TITLE_PAGE = 'TP', _('Title Page')
    ENVELOPE_OR_TITLE_PAGE = 'ET', _('Envelope or Title Page')
    HEAD_TITLE = 'HT', _('Head Title')


class Manifestation(RenderRawJSONMixin, WemiBaseClass):
    class ManifestationForm(models.TextChoices):
        SKETCHES = 'SK', _('Sketches'),
        FRAGMENTS = 'FR', _('Fragments'),
        EXCERPTS = 'EX', _('Excerpts')

        def parse(string):
            match string.lower():
                case 'sketch' | 'sketches': return Manifestation.ManifestationForm.SKETCHES
                case 'fragment' | 'fragments': return Manifestation.ManifestationForm.FRAGMENTS
                case 'excerpt' | 'excerpts': return Manifestation.ManifestationForm.EXCERPTS

    class EditionType(models.TextChoices):
        SCORE = 'SCO', _('Score')
        PART = 'PRT', _('Part')
        PARTS = 'PTS', _('Parts')
        PARTICELL = 'PTC', _('Particell')
        PIANO_REDUCTION = 'PNR', _('Piano Reduction')
        CHOIR_SCORE = 'CSC', _('Choir Score')

    class Function(models.TextChoices):
        COPY = 'COP', _('Copy')
        ALBUM_PAGE = 'ABP', _('Album Page')
        PART_EXCERPT = 'PTE', _('Part Excerpt')
        DEDICATION_ITEM = 'DDI', _('Dedication Item')
        STITCH_TEMPLATE = 'STT', _('Stitch Template')
        CORRECTED_STITCH_TEMPLATE = 'CST', _('Corrected Stitch Template')
        CORRECTION_SHEET = 'CRS', _('Correction Sheet')

        def parse(string):
            match string.lower():
                case 'copy': return Manifestation.Function.COPY
                case 'album' | 'albumpage': return Manifestation.Function.ALBUM_PAGE
                case 'excerpt' | 'partexcerpt': return Manifestation.Function.PART_EXCERPT
                case 'dedication' | 'dedicationitem': return Manifestation.Function.DEDICATION_ITEM
                case 'template' | 'stitchtemplate': return Manifestation.Function.STITCH_TEMPLATE
                case 'correctedtemplate' | 'correctedstitchtemplate': return Manifestation.Function.CORRECTED_STITCH_TEMPLATE
                case 'correction' | 'correctionsheet': return Manifestation.Function.CORRECTION_SHEET

        def parse_from_german(german_string):
            match german_string:
                case 'Abschrift': return Manifestation.Function.COPY
                case 'Albumblatt': return Manifestation.Function.ALBUM_PAGE
                case 'Chorstimmenauszug': return Manifestation.Function.PART_EXCERPT
                case 'Dedikationsexemplar': return Manifestation.Function.DEDICATION_ITEM
                case 'Stichvorlage': return Manifestation.Function.STITCH_TEMPLATE
                case 'korrigierte Stichvorlage': return Manifestation.Function.CORRECTED_STITCH_TEMPLATE
                case 'Korrekturblatt': return Manifestation.Function.CORRECTION_SHEET

    class PrintType(models.TextChoices):
        PLATE_PRINTING = 'P', _('Plate Print')
        LITHOGRAPH = 'L', _('Lithograph')

        def parse_from_german(german_string):
            match german_string.lower():
                case 'plattendruck' | 'platte': return Manifestation.PrintType.PLATE_PRINTING
                case 'lithographie': return Manifestation.PrintType.LITHOGRAPH

    class SourceType(models.TextChoices):
        AUTOGRAPH = 'AUT', _('Autograph')
        COPY = 'CPY', _('Abschrift')
        CORRECTED_COPY = 'CCP', _('Korrigierte Abschrift')
        PRINT = 'PRT', _('Print')
        CORRECTED_PRINT = 'CPR', _('Corrected Print')

        def parse_from_rism(rism_string):
            match rism_string:
                case 'Autograph manuscript': return Manifestation.SourceType.AUTOGRAPH
                case 'Manuscript copy': return Manifestation.SourceType.COPY

        def parse(string):
            match string.lower():
                case 'autograph': return Manifestation.SourceType.AUTOGRAPH
                case 'copy': return Manifestation.SourceType.COPY
                case 'correctedcopy': return Manifestation.SourceType.CORRECTED_COPY
                case 'print': return Manifestation.SourceType.PRINT
                case 'correctedprint': return Manifestation.SourceType.CORRECTED_PRINT

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
    period = models.OneToOneField(
            'dmad.Period',
            on_delete = models.SET_NULL,
            blank = True,
            null = True
        )
    places = models.ManyToManyField(
            'dmad.Place'
        )
    dedicatees = models.ManyToManyField(
            'dmad.Person'
        )
    related_manifestations = models.ManyToManyField(
            'Manifestation',
            through = 'RelatedManifestation'
        )
    manifestation_form = models.CharField(
            max_length=10,
            choices = ManifestationForm.choices,
            default = None,
            null = True,
            blank = True
        )
    edition_type = models.CharField(
            max_length = 10,
            choices = EditionType.choices,
            default = None,
            null = True,
            blank = True
        )
    source_type = models.CharField(
            max_length = 5,
            choices = SourceType.choices,
            default = None,
            null = True,
            blank = True
        )
    function = models.CharField(
            max_length = 5,
            choices = Function.choices,
            default = None,
            null = True,
            blank = True
        )
    print_type = models.CharField(
            max_length = 10,
            choices = PrintType,
            default = None,
            null = True,
            blank = True
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
    language = models.CharField(
            max_length=15,
            choices=Language,
            default=None,
            null=True
        )
    dedication = models.TextField(
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
    #handwriting = models.TextField(
            #blank = True,
            #null = True
        #)
    date_diplomatic = models.TextField(
            blank = True,
            null = True
        )
    print_extent = models.TextField(
            blank = True,
            null = True
        )
    private_head_comment = models.TextField(
            blank = True,
            null = True
        )
    private_relations_comment = models.TextField(
            blank = True,
            null = True
        )
    private_title_comment = models.TextField(
            blank = True,
            null = True
        )
    private_history_comment = models.TextField(
            blank = True,
            null = True
        )
    private_print_comment = models.TextField(
            blank = True,
            null = True
        )
    taken_information = models.TextField(
            blank = True,
            null = True
        )
    stitcher = models.ForeignKey(
            'dmad.Corporation',
            related_name = 'stitched_manifestations',
            null = True,
            on_delete = models.SET_NULL
        )
    specific_figure = models.BooleanField(
            default = False
        )

    def get_absolute_url(self):
        return reverse('dmrism:manifestation_detail', kwargs={'pk': self.id})

    def template_item(self):
        return self.items.get(is_template=True)

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

    def get_temp_title(self):
        if self.titles.filter(status = Status.TEMPORARY).first():
            return self.titles.filter(status = Status.TEMPORARY).first().title
        else:
            return ''

    def __str__(self):
        if self.titles.filter(status = Status.TEMPORARY).first():
            temporary_title = f", {self.titles.filter(status = Status.TEMPORARY).first().title}"
        else:
            temporary_title = ''

        if self.items.count():
            return f"{self.items.all()[0].get_current_signature()},  {self.get_temp_title()}"

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

    def pull_rism_data(self, singleton = None):
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
        if library.name == '' or not library.name:
            library.name = location.get('e')
            library.save()

        if self.items.count() == 0:
            signature = ItemSignature.objects.create(
                    library = library,
                    status = ItemSignature.Status.CURRENT,
                    signature = location.get('c')
                )
            item = Item.objects.create(
                    manifestation = self
                )
            item.signatures.add(signature)

            if location.get('d'):
                signature = ItemSignature.objects.create(
                        library = library,
                        status = ItemSignature.Status.FORMER,
                        signature = location.get('d')
                    )
                item.signatures.add(signature)

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

        if not self.private_head_comment:
            self.private_head_comment = ''

        private_head_comment = []
        if data.get('031'):
            if tempo := data.get('031').get('d'):
                private_head_comment += [ 'Tempo (RISM): ' + tempo ]
            if metronom := data.get('031').get('q'):
                private_head_comment += [ 'Metronom (RISM): ' + metronom ]
            if textincipit := data.get('031').get('t'):
                private_head_comment += [ 'Text-Incipit (RISM): ' + textincipit ]

        if data.get('774'):
            private_head_comment += [
                    'Untergeordnete Manifestationen (RISM-ID): ' +
                    ', '.join(
                        field.get('w').replace('sources/', '') for
                        field in
                        data.get_fields('774')
                    )
                ]

        self.private_head_comment = '\n'.join([self.private_head_comment] + private_head_comment)

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

        # - ascertain order from rism
        for host_item_entry in data.get_fields('773'):
            target_rism_id = host_item_entry.get('w').replace('sources/', '')
            target_manifestation = Manifestation.get_or_create(target_rism_id, singleton)
            RelatedManifestation.objects.create(
                    source_manifestation = self,
                    target_manifestation = target_manifestation,
                    label = RelatedManifestation.Label.PARENT
                )

        for electronic_location in data.get_fields('856'):
            ItemDigitalCopy.objects.create(
                    item = self.items.all()[0],
                    url = electronic_location.get('u'),
                    link_type = BaseDigitalCopy.LinkType.parse(electronic_location.get('x'))
                )

        general_notes = data.get_fields('500')
        #self.extent = '\n'.join(
                #note.get('a').replace(EXTENT_MARKER, '')
                #for note
                #in general_notes
                #if note.get('a').startswith(EXTENT_MARKER)
            #)

        self.measure = '\n'.join(
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
        self.private_comment = '\n'.join(comment)

        if singleton != None:
            self.is_singleton = singleton

        self.rism_id_unaligned = False

        return self

    def save(self, **kwargs):
        old_manifestation = Manifestation.objects.filter(id = self.id).first()
        if old_manifestation:
            old_rism_id = old_manifestation.rism_id
            if old_rism_id != self.rism_id:
                self.rism_id_unaligned = True
        super().save(**kwargs)

    def get_or_create(rism_id, singleton):
        manifestation = Manifestation.objects.filter(rism_id = rism_id).first()
        if not manifestation:
            manifestation = Manifestation.objects.create(rism_id = rism_id)
            manifestation.pull_rism_data(singleton)
            manifestation.save()
        return manifestation


class Publication(models.Model):
    manifestation = models.ForeignKey(
            'Manifestation',
            on_delete = models.CASCADE,
            related_name = 'publications'
        )
    publisher = models.ForeignKey(
            'dmad.Corporation',
            related_name = 'published_manifestations',
            null = True,
            on_delete = models.SET_NULL
        )
    plate_number = models.CharField(
            max_length = 50,
            null = True,
            blank = True
        )


class ManifestationTitle(models.Model):

    title = models.TextField(
            null=True,
            blank=True
        )
    title_type = models.CharField(
            max_length = 2,
            choices = TitleTypes,
            default = None,
            null = True
        )
    status = models.CharField(
            max_length=10,
            choices=Status,
            default=Status.PRIMARY
        )
    manifestation = models.ForeignKey(
            'Manifestation',
            on_delete=models.CASCADE,
            related_name='titles',
        )

    def render_handwritings(self):
        return ', '.join(handwriting.__str__() for handwriting in self.handwritings.all())

    def render_summary(self):
        if self.status == Status.TEMPORARY:
            return 'temporär'

        result = ''
        if self.title_type:
            result += self.title_type
            if self.handwritings.count():
                result += ', '
        if self.handwritings.count():
            result += self.render_handwritings()

        return result


class ManifestationBib(BaseBib):
    manifestation = models.ForeignKey(
        'Manifestation',
        on_delete=models.CASCADE,
        related_name='bib_set'
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
    order = models.IntegerField(
            default = 0
        )


class ManifestationTitleHandwriting(BaseHandwriting):
    manifestation_title = models.ForeignKey(
            'ManifestationTitle',
            related_name = 'handwritings',
            on_delete = models.CASCADE
        )


class ManifestationPersonDedication(BasePersonDedication):
    manifestation = models.ForeignKey(
            'Manifestation',
            on_delete = models.CASCADE,
            related_name = 'manifestation_person_dedications'
        )


class ManifestationCorporationDedication(BaseCorporationDedication):
    manifestation = models.ForeignKey(
            'Manifestation',
            on_delete = models.CASCADE,
            related_name = 'manifestation_corporation_dedications'
        )
