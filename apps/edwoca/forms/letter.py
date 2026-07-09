from .base import *
from django import forms
from ..models.letter import *
from django.conf import settings
from django.forms import DateTimeField, CharField, TextInput, ModelForm, Textarea
from liszt_util.forms import SelectDateWidget
from django.utils.translation import gettext_lazy as _
from dmad_on_django.models import Period
from .base import SimpleFormMixin
from django.utils.safestring import mark_safe
from dominate.tags import div, label, span
from dominate.util import raw


class LetterEditionPeriodForm(DateFormMixin, ModelForm):
    class Meta:
        model = Letter
        fields = []

    kwargs = {
            'years': range(settings.EDWOCA_FIXED_DATES['birth']['year'], 1900),
            'attrs': {
                'class': SimpleFormMixin.select_classes,
                'form': 'form'
            }
        }
    imprecision = ChoiceField(
            choices = Period.Imprecision,
            label = _('imprecision'),
            widget = Select(attrs = {
                    'class': SimpleFormMixin.select_classes,
                    'form': 'form'
                }),
            required = False
        )
    time_mode = ChoiceField(
            choices = Period.TimeMode,
            label = _('time mode'),
            widget = Select(attrs = {'class': SimpleFormMixin.select_classes, 'form': 'form'}),
            required = False
        )
    start_qualifier = ChoiceField(
            label = _('not before mode'),
            choices = Period.StartQualifier,
            widget = Select(attrs = {'class': SimpleFormMixin.select_classes, 'form': 'form'}),
            required = False
        )
    end_qualifier = ChoiceField(
            label = _('not after mode'),
            choices = Period.EndQualifier,
            widget = Select(attrs = {'class': SimpleFormMixin.select_classes, 'form': 'form'}),
            required = False
        )
    not_before = DateField(
            label = _('start'),
            widget = SelectDateWidget(**kwargs),
            required = False
        )
    not_after = DateField(
            label = _('end'),
            widget = SelectDateWidget(**kwargs),
            required = False
        )
    display = CharField(
            label = _('display'),
            required=False,
            widget = TextInput( attrs = { 'class': SimpleFormMixin.text_input_classes , 'form': 'form'})
        )
    inferred = TypedChoiceField(
            choices = ((False, _('based on source')), (True, _('inferred'))),
            coerce = lambda x: x == 'True',
            widget = RadioSelect(
                    attrs = {
                        'class': 'radio', 'form': 'form',
                        'form': 'form'
                    }
                ),
            required = False
        )
    assumed = BooleanField(widget = CheckboxInput(attrs = { 'class': 'toggle', 'form': 'form'}), required = False)

    def __init__(self, *args, **kwargs):
        super().__init__(period_property = 'edition_period', *args, **kwargs)

    def as_daisy(self):
        form = div()

        with form:
            self.get_date_div()

        return mark_safe(str(form))


class LetterSourcePeriodForm(DateFormMixin, ModelForm):
    class Meta:
        model = Letter
        fields = []

    kwargs = {
            'years': range(settings.EDWOCA_FIXED_DATES['birth']['year'], 1900),
            'attrs': {
                'class': SimpleFormMixin.select_classes,
                'form': 'form'
            }
        }
    imprecision = ChoiceField(
            choices = Period.Imprecision,
            label = _('imprecision'),
            widget = Select(attrs = {
                    'class': SimpleFormMixin.select_classes,
                    'form': 'form'
                }),
            required = False
        )
    time_mode = ChoiceField(
            choices = Period.TimeMode,
            label = _('time mode'),
            widget = Select(attrs = {'class': SimpleFormMixin.select_classes, 'form': 'form'}),
            required = False
        )
    start_qualifier = ChoiceField(
            label = _('not before mode'),
            choices = Period.StartQualifier,
            widget = Select(attrs = {'class': SimpleFormMixin.select_classes, 'form': 'form'}),
            required = False
        )
    end_qualifier = ChoiceField(
            label = _('not after mode'),
            choices = Period.EndQualifier,
            widget = Select(attrs = {'class': SimpleFormMixin.select_classes, 'form': 'form'}),
            required = False
        )
    not_before = DateField(
            label = _('start'),
            widget = SelectDateWidget(**kwargs),
            required = False
        )
    not_after = DateField(
            label = _('end'),
            widget = SelectDateWidget(**kwargs),
            required = False
        )
    display = CharField(
            label = _('display'),
            required=False,
            widget = TextInput( attrs = { 'class': SimpleFormMixin.text_input_classes , 'form': 'form'})
        )
    inferred = TypedChoiceField(
            choices = ((False, _('based on source')), (True, _('inferred'))),
            coerce = lambda x: x == 'True',
            widget = RadioSelect(
                    attrs = {
                        'class': 'radio', 'form': 'form',
                        'form': 'form'
                    }
                ),
            required = False
        )
    assumed = BooleanField(widget = CheckboxInput(attrs = { 'class': 'toggle', 'form': 'form'}), required = False)

    def __init__(self, *args, **kwargs):
        super().__init__(period_property = 'source_period', *args, **kwargs)

    def as_daisy(self):
        form = div()

        with form:
            self.get_date_div(disable_inferred = True)

        return mark_safe(str(form))


class LetterForm(BaseTrackedModelForm, ModelForm, SimpleFormMixin):
    class Meta:
        model = Letter
        fields = BaseTrackedModelForm.Meta.fields + [
                'comment',
                'work_mentionings',
                'diplomatic_source_date'
            ]
        widgets = dict(BaseTrackedModelForm.Meta.widgets, **{
            'diplomatic_source_date': TextInput(attrs={
                'class': SimpleFormMixin.text_input_classes,
                'form': 'form',
                'disabled': 'true'
            }),
            'work_mentionings': Textarea(attrs={
                'class': SimpleFormMixin.text_area_classes + ' bg-white border-black',
                'form': 'form'
            }),
            'comment': Textarea(attrs={
                'class': SimpleFormMixin.text_area_classes + ' bg-white border-black',
                'form': 'form'
            }),
        })

    first_save = DateTimeField(
            label=_('first save') + '*',
            required = False,
            disabled = True,
            widget = SelectDateWidget( attrs = { 'class': SimpleFormMixin.select_classes + ' disabled:!bg-white disabled:!border-black disabled:!text-black' })
        )
    last_save = DateTimeField(
            label=_('last save'),
            required = False,
            disabled = True,
            widget = SelectDateWidget( attrs = { 'class': SimpleFormMixin.select_classes + ' disabled:!bg-white disabled:!border-black disabled:!text-black'})
        )

    def diplomatic_date_as_daisy(self):
        form = div()

        diplomatic_date_field = self['diplomatic_source_date']
        with form:
            with label(cls=SimpleFormMixin.form_control_classes):
                with div(cls=SimpleFormMixin.label_classes):
                    span(diplomatic_date_field.label, cls=SimpleFormMixin.label_text_classes)
                raw(str(diplomatic_date_field))

        return mark_safe(str(form))

    def work_mentionings_as_daisy(self):
        form = div(cls='mb-10')

        work_mentionings_field = self['work_mentionings']

        with form:
            with label(cls=SimpleFormMixin.form_control_classes):
                with div(cls=SimpleFormMixin.label_classes):
                    span(work_mentionings_field.label, cls=SimpleFormMixin.label_text_classes)
                raw(str(work_mentionings_field))

        return mark_safe(str(form))

    def comment_as_daisy(self):
        form = div(cls='mb-10')

        comment_field = self['comment']

        with form:
            with label(cls=SimpleFormMixin.form_control_classes):
                with div(cls=SimpleFormMixin.label_classes):
                    span(comment_field.label, cls=SimpleFormMixin.label_text_classes)
                raw(str(comment_field))
        #if comment_field.errors:
            #comment_container.add(div(span(comment_field.errors, cls='text-primary text-sm'), cls='label'))

        #form.add(comment_container)

        return mark_safe(str(form))

    def editing_history_as_daisy(self):
        return mark_safe(str(self.get_editing_history_div()))


class LetterMentioningForm(BaseBibForm):
    class Meta:
        model = LetterMentioning
        fields = BaseBibForm.Meta.fields + ['letter_number']
        widgets = dict(**BaseBibForm.Meta.widgets,
                letter_number = TextInput(attrs = {'form': 'form', 'class': SimpleFormMixin.text_input_classes})
            )

    def as_daisy(self):
        form = div(cls='my-5')

        location_field = self['location']
        location_type_field = self['location_type']
        letter_number_field = self['letter_number']

        with form:
            # palette
            with div(cls=SimpleFormMixin.palette_classes):
                with label(cls='flex-0 form-control'):
                    with div(cls=SimpleFormMixin.label_classes):
                        span(_(location_type_field.label), cls=SimpleFormMixin.label_text_classes)
                    raw(str(location_type_field))
                with label(cls=SimpleFormMixin.palette_form_control_classes):
                    with div(cls=SimpleFormMixin.label_classes):
                        span(_(location_field.label), cls=SimpleFormMixin.label_text_classes)
                    raw(str(location_field))
                with label(cls=SimpleFormMixin.palette_form_control_classes):
                    with div(cls=SimpleFormMixin.label_classes):
                        span(_(letter_number_field.label), cls=SimpleFormMixin.label_text_classes)
                    raw(str(letter_number_field))

        #for hidden in self.hidden_fields():
            #hidden.field.widget.attrs['form'] = 'form'
            #form.add(raw(str(hidden)))

        return mark_safe(str(form))

class BaseLetterContributorForm(ModelForm):
    class Meta:
        fields = [ 'inferred', 'assumed' ]
        widgets = {
                'inferred': CheckboxInput(attrs = {'form': 'form', 'class': SimpleFormMixin.toggle_classes}),
                'assumed': CheckboxInput(attrs = {'form': 'form', 'class': SimpleFormMixin.toggle_classes}),
                'edition_name': TextInput(attrs = {'form': 'form', 'class': SimpleFormMixin.text_input_classes}),
                'source_name': TextInput(attrs = {'form': 'form', 'class': SimpleFormMixin.text_input_classes}),
                'edition_name_inferred': RadioSelect(attrs = {'form': 'form', 'class': SimpleFormMixin.radio_classes}),
                'edition_name_assumed': CheckboxInput(attrs = {'form': 'form', 'class': SimpleFormMixin.toggle_classes}),
                'source_name_inferred': RadioSelect(attrs = {'form': 'form', 'class': SimpleFormMixin.radio_classes}),
                'source_name_assumed': CheckboxInput(attrs = {'form': 'form', 'class': SimpleFormMixin.toggle_classes})
            }

    source_name = CharField(
            required = False,
            widget = Meta.widgets['source_name'],
            label = _('source name')
        )
    edition_name = CharField(
            required = False,
            widget = Meta.widgets['edition_name'],
            label = _('edtion name')
        )
    source_name_inferred = BooleanField(
            widget = CheckboxInput(attrs = {
                    'class': SimpleFormMixin.toggle_classes,
                    'form': 'form'
                }),
            disabled = True,
            required = False,
            label = _('inferred')
        )
    source_name_assumed = BooleanField(
            widget = CheckboxInput(attrs = {
                    'class': SimpleFormMixin.toggle_classes,
                    'form': 'form'
                }),
            disabled = True,
            required = False,
            label = _('assumed')
        )
    edition_name_inferred = BooleanField(
            widget = CheckboxInput(attrs = {
                    'class': SimpleFormMixin.toggle_classes,
                    'form': 'form'
                }),
            required = False,
            label = _('attributed')
        )
    edition_name_assumed = BooleanField(
            widget = CheckboxInput(attrs = {
                    'class': SimpleFormMixin.toggle_classes,
                    'form': 'form'
                }),
            required = False,
            label = _('assumed')
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.is_bound:
            return

        if self.instance.edition_name:
            self.initial.update({
                'edition_name': self.instance.edition_name.name,
                'edition_name_inferred': self.instance.edition_name.inferred,
                'edition_name_assumed': self.instance.edition_name.assumed
            })
        if self.instance.source_name:
            self.initial.update({
                'source_name': self.instance.source_name.name,
                'source_name_inferred': self.instance.source_name.inferred,
                'source_name_assumed': self.instance.source_name.assumed
            })

        self.fields['source_name'].disabled = True

    def save(self, commit=True):
        instance = super().save(commit=False)

        if not self.instance.edition_name:
            self.instance.edition_name = DocumentedEntityName()
        if not self.instance.source_name:
            self.instance.source_name = DocumentedEntityName()

        self.instance.edition_name.name = self.cleaned_data['edition_name']
        self.instance.edition_name.inferred = self.cleaned_data['edition_name_inferred']
        self.instance.edition_name.assumed = self.cleaned_data['edition_name_assumed']
        self.instance.source_name.name = self.cleaned_data['source_name']
        self.instance.source_name.inferred = self.cleaned_data['source_name_inferred']
        self.instance.source_name.assumed = self.cleaned_data['source_name_assumed']

        self.instance.edition_name.save()
        self.instance.source_name.save()
        self.instance.save()

        return self.instance

    def as_daisy(self):
        form = div()

        inferred_field = self['inferred']
        assumed_field = self['assumed']
        edition_name_field = self['edition_name']
        source_name_field = self['source_name']
        edition_name_inferred_field = self['edition_name_inferred']
        source_name_inferred_field = self['source_name_inferred']
        edition_name_assumed_field = self['edition_name_assumed']
        source_name_assumed_field = self['source_name_assumed']

        palette_classes = 'flex gap-10 items-center mt-2'

        with form:
            # palette for contributor
            with tags.div(cls=palette_classes):
                tags.div(cls='flex-1')
                with tags.label(cls=SimpleFormMixin.toggle_label_classes):
                    tags.span(_(assumed_field.label.lower()), cls=SimpleFormMixin.label_text_classes)
                    raw(str(assumed_field))
                with tags.label(cls=SimpleFormMixin.toggle_label_classes):
                    tags.span(_(inferred_field.label.lower()), cls=SimpleFormMixin.label_text_classes)
                    raw(str(inferred_field))
            # name according to edition
            with label(cls=SimpleFormMixin.form_control_classes):
                with div(cls=SimpleFormMixin.label_classes):
                    span(edition_name_field.label, cls=SimpleFormMixin.label_text_classes)
                raw(str(edition_name_field))
            # palette for name according to edition
            with tags.div(cls=palette_classes):
                tags.div(cls='flex-1')
                with tags.label(cls=SimpleFormMixin.toggle_label_classes):
                    tags.span(_(edition_name_assumed_field.label.lower()), cls=SimpleFormMixin.label_text_classes)
                    raw(str(edition_name_assumed_field))
                with tags.label(cls=SimpleFormMixin.toggle_label_classes):
                    tags.span(_(edition_name_inferred_field.label.lower()), cls=SimpleFormMixin.label_text_classes)
                    raw(str(edition_name_inferred_field))
            # gray area for disabled inputs
            with div(cls='bg-base-100 p-5 my-5'):
                # name according to source
                with label(cls=SimpleFormMixin.form_control_classes):
                    with div(cls=SimpleFormMixin.label_classes):
                        span(source_name_field.label, cls=SimpleFormMixin.label_text_classes)
                    raw(str(source_name_field))
                # palette for name according to source
                with tags.div(cls=palette_classes):
                    tags.div(cls='flex-1')
                    with tags.label(cls=SimpleFormMixin.toggle_label_classes):
                        tags.span(_(source_name_assumed_field.label.lower()), cls=SimpleFormMixin.label_text_classes)
                        raw(str(source_name_assumed_field))
                    #with tags.label(cls=SimpleFormMixin.toggle_label_classes):
                        #tags.span(_(source_name_inferred_field.label.lower()), cls=SimpleFormMixin.label_text_classes)
                        #raw(str(source_name_inferred_field))

        return mark_safe(str(form))


class SenderPersonForm(BaseLetterContributorForm):
    class Meta:
        model = SenderPerson
        fields = BaseLetterContributorForm.Meta.fields
        widgets = BaseLetterContributorForm.Meta.widgets


class ReceiverPersonForm(BaseLetterContributorForm):
    class Meta:
        model = ReceiverPerson
        fields = BaseLetterContributorForm.Meta.fields
        widgets = BaseLetterContributorForm.Meta.widgets


class SenderCorporationForm(BaseLetterContributorForm):
    class Meta:
        model = SenderCorporation
        fields = BaseLetterContributorForm.Meta.fields
        widgets = BaseLetterContributorForm.Meta.widgets


class ReceiverCorporationForm(BaseLetterContributorForm):
    class Meta:
        model = ReceiverCorporation
        fields = BaseLetterContributorForm.Meta.fields
        widgets = BaseLetterContributorForm.Meta.widgets


class SenderPlaceForm(BaseLetterContributorForm):
    class Meta:
        model = SenderPlace
        fields = BaseLetterContributorForm.Meta.fields
        widgets = BaseLetterContributorForm.Meta.widgets


class ReceiverPlaceForm(BaseLetterContributorForm):
    class Meta:
        model = ReceiverPlace
        fields = BaseLetterContributorForm.Meta.fields
        widgets = BaseLetterContributorForm.Meta.widgets


class LetterSignatureForm(BaseSignatureForm):
    class Meta:
        model = LetterSignature
        fields = BaseSignatureForm.Meta.fields
        widgets = BaseSignatureForm.Meta.widgets


class LetterDigitizedCopyForm(BaseDigitizedCopyForm):
    class Meta:
        model = LetterDigitalCopy
        fields = BaseDigitizedCopyForm.Meta.fields
        widgets = BaseDigitizedCopyForm.Meta.widgets
