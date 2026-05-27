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
    not_before = DateField(widget = SelectDateWidget(**kwargs), required = False)
    not_after = DateField(widget = SelectDateWidget(**kwargs), required = False)
    display = CharField(required=False, widget = TextInput( attrs = { 'class': SimpleFormMixin.text_input_classes, 'form': 'form'}), label=_('date according to edition (standardized)'))
    inferred = TypedChoiceField(
            choices = ((False, _('based on edition')), (True, _('inferred'))),
            coerce = lambda x: x == 'True',
            widget = RadioSelect(
                    attrs = { 'class': 'radio', 'form': 'form'}
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
    not_before = DateField(widget = SelectDateWidget(**kwargs), required = False, disabled = True)
    not_after = DateField(widget = SelectDateWidget(**kwargs), required = False, disabled = True)
    display = CharField(required=False, widget = TextInput( attrs = { 'class': SimpleFormMixin.text_input_classes, 'form': 'form'}), label=_('date according to source (standardized)'), disabled = True)
    inferred = TypedChoiceField(
            choices = ((False, _('based on source')), (True, _('inferred'))),
            coerce = lambda x: x == 'True',
            widget = RadioSelect(
                    attrs = { 'class': 'radio', 'form': 'form'}
                ),
            required = False,
            disabled = True
        )
    assumed = BooleanField(widget = CheckboxInput(attrs = { 'class': 'toggle', 'form': 'form'}), required = False, disabled = True)

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


class LetterMentioningForm(ModelForm):
    class Meta:
        model = LetterMentioning
        fields = ['pages']
        widgets = {
                'pages': TextInput(attrs={'form': 'form', 'class': 'flex-1 min-w-0'})
        }


class BaseLetterContributorForm(ModelForm):
    class Meta:
        fields = [ ]
        widgets = {
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
    source_name_inferred = TypedChoiceField(
            choices = ((False, _('based on source')), (True, _('inferred'))),
            coerce = lambda x: x == 'True',
            required = False,
            empty_value = False
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
    edition_name_inferred = TypedChoiceField(
            choices = ((False, _('based on edition')), (True, _('attributed'))),
            coerce = lambda x: x == 'True',
            required = False,
            empty_value = False
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

        edition_name_field = self['edition_name']
        source_name_field = self['source_name']
        edition_name_inferred_field = self['edition_name_inferred']
        source_name_inferred_field = self['source_name_inferred']
        edition_name_assumed_field = self['edition_name_assumed']
        source_name_assumed_field = self['source_name_assumed']

        with form:
            with label(cls=SimpleFormMixin.form_control_classes):
                with div(cls=SimpleFormMixin.label_classes):
                    span(edition_name_field.label, cls=SimpleFormMixin.label_text_classes)
                raw(str(edition_name_field))
            with tags.div(cls=SimpleFormMixin.palette_classes + ' items-center'):
                tags.div(cls='flex-1')
                with tags.label(cls=SimpleFormMixin.toggle_label_classes):
                    tags.span(_(edition_name_assumed_field.label.lower()), cls=SimpleFormMixin.label_text_classes)
                    raw(str(edition_name_assumed_field))
                tags.div(cls='flex-1')
                for sw in edition_name_inferred_field.subwidgets:
                    with tags.div(cls=SimpleFormMixin.form_control_classes):
                        with tags.label(cls='label cursor-pointer gap-5'):
                            tags.span(_(sw.choice_label), cls=SimpleFormMixin.label_text_classes)
                            tags.input_(
                                    type='radio',
                                    name=sw.data.get('name'),
                                    value=str(sw.data.get('value')),
                                    cls='radio',
                                    checked = sw.data.get('selected', False),
                                    form='form'
                                )
            with div(cls='bg-base-100 p-5 mb-5'):
                with label(cls=SimpleFormMixin.form_control_classes):
                    with div(cls=SimpleFormMixin.label_classes):
                        span(source_name_field.label, cls=SimpleFormMixin.label_text_classes)
                    raw(str(source_name_field))
                with tags.div(cls=SimpleFormMixin.palette_classes + ' items-center'):
                    tags.div(cls='flex-1')
                    with tags.label(cls=SimpleFormMixin.toggle_label_classes):
                        tags.span(_(source_name_assumed_field.label.lower()), cls=SimpleFormMixin.label_text_classes)
                        raw(str(source_name_assumed_field))
                    tags.div(cls='flex-1')
                    for sw in source_name_inferred_field.subwidgets:
                        with tags.div(cls=SimpleFormMixin.form_control_classes):
                            with tags.label(cls='label cursor-pointer gap-5'):
                                tags.span(_(sw.choice_label), cls=SimpleFormMixin.label_text_classes)
                                tags.input_(
                                        type='radio',
                                        name=sw.data.get('name'),
                                        value=str(sw.data.get('value')),
                                        cls='radio',
                                        checked = sw.data.get('selected', False),
                                        form='form',
                                        disabled = True
                                    )

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
