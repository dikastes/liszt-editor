import re
from .base import *
from ..rism_tools import get_rism_data
from .item import ItemDigitalCopy, BaseDigitalCopy, BaseSignature
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from .item import Item, ItemSignature, Library
from dmad_on_django.models import Language, Status, Period, Person, Corporation
from dmad_on_django.models.base import DocumentationStatus
from bib.models import ZotItem
from iso639 import find as lang_find
from liszt_util.tools import RenderRawJSONMixin
from liszt_util.models import Sortable


class TitleTypes(models.TextChoices):
    HEAD_TITLE = 'HT', _('Head Title')
    TITLE_PAGE = 'TP', _('Title Page')
    ENVELOPE = 'EN', _('Envelope')
    ENVELOPE_OR_TITLE_PAGE = 'ET', _('Envelope or Title Page')


class Manifestation(Sortable, RenderRawJSONMixin, WemiBaseClass):
    class Meta:
        ordering = ['-needs_review', 'order_index']

    class PartLabel(models.TextChoices):
        CONSTITUTING = 'c', _('constituting')
        BOUND_TOGETHER = 'b', _('bound together')
        SEPARATED = 's', _('separated')

    class ManifestationForm(models.TextChoices):
        EXCERPTS = 'EX', _('Excerpts')
        SKETCHES = 'SK', _('Sketches'),
        FRAGMENTS = 'FR', _('Fragments'),

        def parse(string):
            match string.lower():
                case 'sketch' | 'sketches': return Manifestation.ManifestationForm.SKETCHES
                case 'fragment' | 'fragments': return Manifestation.ManifestationForm.FRAGMENTS
                case 'excerpt' | 'excerpts': return Manifestation.ManifestationForm.EXCERPTS

    class PrintType(models.TextChoices):
        PLATE_PRINT = 'P', _('Plate Print')
        LITHOGRAPH = 'L', _('Lithograph')

        def parse_from_german(german_string):
            match german_string.lower():
                case 'plattendruck' | 'platte': return Manifestation.PrintType.PLATE_PRINT
                case 'lithographie': return Manifestation.PrintType.LITHOGRAPH

    class Edition(models.TextChoices):
        FIRST_EDITION = '1', _('first issue')
        FOLLOWING_EDITION = 'F', _('following issue')

    class SourceType(models.TextChoices):
        TRANSCRIPT = 'TSC', _('transcript')
        CORRECTED_TRANSCRIPT = 'CTS', _('transcript with autograph entries')
        AUTOGRAPH = 'AUT', _('autograph')
        QUESTIONABLE_AUTOGRAPH = 'QAU', _('questionable autograph')
        CORRECTED_PRINT = 'CPR', _('print with autograph entries')

        def parse_from_rism(rism_string):
            match rism_string:
                case 'Autograph manuscript': return Manifestation.SourceType.AUTOGRAPH
                case 'Manuscript copy': return Manifestation.SourceType.TRANSCRIPT

        def parse(string):
            match string.lower():
                case 'autograph': return Manifestation.SourceType.AUTOGRAPH
                case 'copy': return Manifestation.SourceType.TRANSCRIPT
                case 'correctedcopy': return Manifestation.SourceType.CORRECTED_TRANSCRIPT
                case 'print': return Manifestation.SourceType.PRINT
                case 'correctedprint': return Manifestation.SourceType.CORRECTED_PRINT

    class State(models.TextChoices):
        COMPLETE= 'CP', _('complete')
        INCOMPLETE= 'INC', _('incomplete')

    working_title = models.TextField(
            max_length = 200,
            blank = True,
            verbose_name = _('working title'),
            default = ''
        )
    source_title = models.TextField(
            max_length = 200,
            blank = True,
            verbose_name = _('source title'),
            default = ''
        )
    rism_id_unaligned = models.BooleanField(default=False)
    temporary = models.BooleanField(default=False)
    temporary_target = models.ForeignKey(
            'Manifestation',
            on_delete = models.SET_NULL,
            related_name = 'temporary_copy',
            null = True
        )
    # move to edwoca?
    period = models.OneToOneField(
            'dmad.Period',
            on_delete = models.SET_NULL,
            null = True,
            blank = True,
        )
    places = models.ManyToManyField(
            'dmad.Place',
            through = 'ManifestationPlace'
        )
    related_manifestations = models.ManyToManyField(
            'Manifestation',
            through = 'RelatedManifestation'
        )
    manifestation_form = models.CharField(
            max_length=10,
            choices = ManifestationForm.choices,
            default = None,
            blank = True,
            null = True,
            verbose_name = _('manifestation form')
        )
    source_type = models.CharField(
            max_length = 5,
            choices = SourceType.choices,
            default = SourceType.AUTOGRAPH,
            blank = True,
            verbose_name = _('source type')
        )
    print_type = models.CharField(
            max_length = 10,
            choices = PrintType,
            default = None,
            null = True,
            verbose_name = _('edition')
        )
    edition = models.CharField(
            max_length = 10,
            choices = Edition,
            default = Edition.FOLLOWING_EDITION,
            verbose_name = _('edition')
        )
    state = models.CharField(
            max_length = 10,
            choices = State,
            default = State.COMPLETE,
            verbose_name = _('state')
        )
    extent = models.TextField(
            blank = True,
            verbose_name = _('extent'),
            default = ''
        )
    history = models.TextField(
            blank = True,
            verbose_name = _('history'),
            default = ''
        )
    bib = models.ManyToManyField(
            'bib.ZotItem',
            through = 'ManifestationBib'
        )
    language = models.CharField(
            max_length = 15,
            choices = Language,
            default = None,
            null = True,
            verbose_name = _('language')
        )
    watermark = models.TextField(
            max_length = 100,
            blank = True,
            verbose_name = _('watermark'),
            default = ''
        )
    watermark_url = models.URLField(
            blank=True,
            verbose_name = _('watermark url'),
            null = True
        )
    is_singleton = models.BooleanField(default=False)
    is_collection = models.BooleanField(default=False)
    missing_item = models.BooleanField(default=False)
    # move to edwoca?
    numerus_currens = models.IntegerField(
            null = True,
            unique = True
        )
    rism_id = models.CharField(
            max_length=20,
            blank = True,
            verbose_name = _('RISM id'),
            default = ''
        )
    raw_data = models.TextField(
            blank = True,
            default = ''
        )
    date_diplomatic = models.TextField(
            blank = True,
            verbose_name = _('diplomatic date'),
            default = ''
        )
    print_extent = models.TextField(
            blank = True,
            verbose_name = _('print extent'),
            default = ''
        )
    private_head_comment = models.TextField(
            blank = True,
            verbose_name = _('private head comment'),
            default = ''
        )
    private_relations_comment = models.TextField(
            blank = True,
            verbose_name = _('private relations comment'),
            default = ''
        )
    private_title_comment = models.TextField(
            blank = True,
            verbose_name = _('private title comment'),
            default = ''
        )
    private_history_comment = models.TextField(
            blank = True,
            verbose_name = _('private history comment'),
            default = ''
        )
    private_dedication_comment = models.TextField(
            blank = True,
            verbose_name = _('private dedication comment'),
            default = ''
        )
    private_print_comment = models.TextField(
            blank = True,
            verbose_name = _('private print comment'),
            default = ''
        )
    taken_information = models.TextField(
            blank = True,
            verbose_name = _('taken information'),
            default = ''
        )
    stitcher = models.ForeignKey(
            'dmad.Corporation',
            related_name = 'stitched_manifestations',
            on_delete = models.SET_NULL,
            null = True,
        )
    specific_figure = models.BooleanField(
            default = False,
            verbose_name = 'specific figure'
        )
    plate_number = models.CharField(
            max_length=20,
            blank = True,
            verbose_name = _('plate number'),
            default = ''
        )
    album_page = models.BooleanField(
            default = False,
            verbose_name = _('album page')
        )
    performance_material = models.BooleanField(
            default = False,
            verbose_name = _('performance material')
        )
    authorized_edition = models.BooleanField(
            default = False,
            verbose_name = _('authorized edition')
        )
    first_edition = models.BooleanField(
            default = False,
            verbose_name = _('first edition')
        )
    proof = models.BooleanField(
            default = False,
            verbose_name = _('proof')
        )
    part = models.BooleanField(
            default = False,
            verbose_name = _('part')
        )
    further_edition = models.BooleanField(
            default = False,
            verbose_name = _('further edition')
        )
    correction_sheet = models.BooleanField(
            default = False,
            verbose_name = _('correction sheet')
        )
    stitch_template = models.BooleanField(
            default = False,
            verbose_name = _('stitch template')
        )
    dedication_item = models.BooleanField(
            default = False,
            verbose_name = _('dedication item')
        )
    choir_score = models.BooleanField(
            default = False,
            verbose_name = _('choir score')
        )
    piano_reduction = models.BooleanField(
            default = False,
            verbose_name = _('piano reduction')
        )
    particell = models.BooleanField(
            default = False,
            verbose_name = _('particell')
        )
    score = models.BooleanField(
            default = False,
            verbose_name = _('score')
        )
    part_of = models.ForeignKey(
            'Manifestation',
            related_name = 'collection_parts',
            on_delete = models.SET_NULL,
            null = True
        )
    part_label = models.CharField(
            max_length = 1,
            choices = PartLabel,
            default = None,
            null = True,
            verbose_name = _('part label')
        )
    component_of = models.ForeignKey(
            'Manifestation',
            related_name = 'collection_components',
            on_delete = models.SET_NULL,
            null = True
        )
    first_save = models.DateTimeField(
            auto_now_add = True,
            verbose_name = _('first save')
        )
    last_save = models.DateTimeField(
            auto_now = True,
            verbose_name = _('last save')
        )
    first_editor = models.CharField(
            max_length = 50,
            blank = True,
            verbose_name = _('first editor'),
            default = ''
        )
    editing_history = models.TextField(
            blank = True,
            verbose_name = _('editing history'),
            default = ''
        )
    needs_review = models.BooleanField(
            default = False,
            verbose_name = _('needs review')
        )
    is_lyrics = models.BooleanField(
            default = False,
            verbose_name = _('is lyrics')
        )
    is_program = models.BooleanField(
            default = False,
            verbose_name = _('is program')
        )
    is_explanation = models.BooleanField(
            default = False,
            verbose_name = _('is explanation')
        )
    is_text = models.BooleanField(
            default = False,
            verbose_name = _('is text')
        )
    _group_field_names = ['part_of', 'component_of']

    def get_absolute_url(self):
        return reverse('dmrism:manifestation_detail', kwargs={'pk': self.id})

    def template_item(self):
        return self.items.get(is_template=True)

    def get_pref_title(self):
        return self.__str__()

    def set_collection(self, is_collection = False):
        if is_collection:
            # set collection
            self.is_collection = True
            if self.working_title and not self.source_title:
                self.source_title = self.working_title
        else:
            # unset collection
            if self.source_title and not self.working_title:
                self.working_title = self.source_title
            self.is_collection = False

    def render_title(self, prefix):
        review_string = ''
        if self.needs_review:
            review_string = '!'

        if self.is_collection:
            collection = _('coll')
            title = self.source_title or _('empty')
            return f'{review_string}({collection}) {prefix} {title}'

        title = self.working_title or _('empty')
        source_typed_title = f'{prefix} {title} ({self.get_source_type_display()})'

        if self.part_of:
            part = _('pt')
            return f'{review_string}({part}) {source_typed_title}'
        if self.component_of:
            component = _('cmp')
            return f'{review_string}({component}) {source_typed_title}'

        return review_string + source_typed_title

    def standardized_search_entry(self):
        if self.items.count():
            prefix = self.items.first().get_current_signature()
            return self.render_title(prefix)
        return '<Fehler: keine Items>'

    def __str__(self):
        return self.standardized_search_entry()

    def save(self, *args, **kwargs):
        if not self.period:
            self.period = Period.objects.create()
        # chatgpt sagt das soll nach clean und nicht nach save
        if self.pk:
            old_manifestation = Manifestation.objects.filter(id = self.id).first()
            if old_manifestation:
                old_rism_id = old_manifestation.rism_id
                if old_rism_id != self.rism_id:
                    self.rism_id_unaligned = True
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
            target_manifestation.set_collection(True)
            target_manifestation.save()
            self.part_of = target_manifestation
            self.part_label = Manifestation.PartLabel.CONSTITUTING
            #RelatedManifestation.objects.create(
                    #source_manifestation = self,
                    #target_manifestation = target_manifestation,
                    #label = RelatedManifestation.Label.IS_PART_OF
                #)

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
        self.private_comment = '\n'.join(line for line in comment if line)

        if singleton != None:
            self.is_singleton = singleton

        self.rism_id_unaligned = False

        return self

    def get_or_create(rism_id, singleton):
        manifestation = Manifestation.objects.filter(rism_id = rism_id).first()
        if not manifestation:
            manifestation = Manifestation.objects.create(rism_id = rism_id)
            manifestation.pull_rism_data(singleton)
            manifestation.save()
        return manifestation

    def get_single_item(self):
        if self.is_singleton:
            if self.items.count():
                return self.items.first()
            raise Exception('You are trying to retrieve the single item of a singleton manifestation which has zero items.')
        raise Exception('You are trying to retrieve a single item from a non singleton manifestation.')

    def get_current_signature(self):
        if self.is_singleton and self.get_single_item():
            return self.get_single_item().get_current_signature()
        return ''

    def get_current_signature_normalized(self):
        try:
            single_item = self.get_single_item()
        except:
            return ''

        signature = single_item.signatures.filter(status = BaseSignature.Status.CURRENT).first()
        if signature:
            return re.sub(r'[^A-Za-z0-9]', '', signature.signature or '').lower()
        return ''


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
    place = models.ManyToManyField(
            'dmad.Place',
            related_name = 'published_manifestations'
        )
    inferred = models.BooleanField(
            default=False,
            verbose_name = _("inferred")
        )
    assumed = models.BooleanField(
            default=False,
            verbose_name = _("assumed")
        )


class ManifestationPlace(models.Model):
    manifestation = models.ForeignKey(
            'Manifestation',
            on_delete = models.CASCADE
        )
    place = models.ForeignKey(
            'dmad.Place',
            on_delete = models.CASCADE
        )
    inferred = models.BooleanField(
            default=False,
            verbose_name = _("inferred")
        )
    assumed = models.BooleanField(
            default=False,
            verbose_name = _("assumed")
        )


class ManifestationTitle(models.Model):
    title = models.TextField(
            null=True,
            blank=True,
            verbose_name = _('diplomatic title')
        )
    title_type = models.CharField(
            max_length = 2,
            choices = TitleTypes,
            default = None,
            null = True,
            blank = True,
            verbose_name = _('title type')
        )
    manifestation = models.ForeignKey(
            'Manifestation',
            on_delete=models.CASCADE,
            related_name='titles',
        )

    def render_handwritings(self):
        return ', '.join(handwriting.__str__() for handwriting in self.handwritings.all())

    def render_first_writer(self):
        if self.handwritings.count() and self.handwritings.first().writer:
            return f'({self.handwritings.first().writer.get_default_name()})'
        return ''

    def render_summary(self):
        if (title_type := self.get_title_type_display()):
            title_type += ':'
        else:
            title_type = ''

        title = self.title or _('<< new title >>')

        return f'{title_type} {title} {self.render_first_writer()}'


class ManifestationBib(BaseBib):
    manifestation = models.ForeignKey(
        'Manifestation',
        on_delete=models.CASCADE,
        related_name='bib_set'
    )


class RelatedManifestation(RelatedEntity):
    class Label(models.TextChoices):
        STITCH_TEMPLATE = 'SD', _('is stitch template (as documented)')
        STITCH_TEMPLATE_INFERRED = 'SI', _('is stitch template (inferred)')
        RELATED = 'R', _('is related to')

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
            max_length=2,
            choices=Label,
            verbose_name = _('label'),
            null = True
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
