from .base import *
from django import forms
from ..models import Letter, LetterMentioning
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
    display = CharField(required=False, widget = TextInput( attrs = { 'class': SimpleFormMixin.text_input_classes}))
    inferred = TypedChoiceField(
            choices = ((False, _('based on source')), (True, _('inferred'))),
            coerce = lambda x: x == 'True',
            widget = RadioSelect(
                    attrs = { 'class': 'radio', 'form': 'form'}
                ),
            required = False
        )
    assumed = BooleanField(widget = CheckboxInput(attrs = { 'class': 'toggle', 'form': 'form'}), required = False)

    def __init__(self, *args, **kwargs):
        #kwargs.update({'period_property', 'edition_period'})
        #super().__init__(*args, **kwargs)
        super().__init__(period_property = 'source_period', *args, **kwargs)

    def as_daisy(self):
        form = div()

        with form:
            self.get_date_div()

        return form


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
    not_before = DateField(widget = SelectDateWidget(**kwargs), required = False)
    not_after = DateField(widget = SelectDateWidget(**kwargs), required = False)
    display = CharField(required=False, widget = TextInput( attrs = { 'class': SimpleFormMixin.text_input_classes}))
    inferred = TypedChoiceField(
            choices = ((False, _('based on source')), (True, _('inferred'))),
            coerce = lambda x: x == 'True',
            widget = RadioSelect(
                    attrs = { 'class': 'radio', 'form': 'form'}
                ),
            required = False
        )
    assumed = BooleanField(widget = CheckboxInput(attrs = { 'class': 'toggle', 'form': 'form'}), required = False)

    def __init__(self, *args, **kwargs):
        #kwargs.update({'period_property', 'source_period'})
        super().__init__(period_property = 'source_period', *args, **kwargs)

    def as_daisy(self):
        form = div()

        with form:
            self.get_date_div()

        return form


class LetterForm(ModelForm, SimpleFormMixin):
    kwargs = {
            'years': range(settings.EDWOCA_FIXED_DATES['birth']['year'], 1900),
            #'attrs': {
                #'class': 'select select-bordered bg-white border-black'
            #}
        }
    #not_before_source = DateTimeField(widget = SelectDateWidget(**kwargs), required = False)
    #not_after_source = DateTimeField(widget = SelectDateWidget(**kwargs), required = False)
    #display_source = CharField(required=False, widget = TextInput( attrs = { 'class': 'grow'}))
    #not_before_edition = DateTimeField(widget = SelectDateWidget(**kwargs), required = False)
    #not_after_edition = DateTimeField(widget = SelectDateWidget(**kwargs), required = False)
    #display_edition = CharField(required=False, widget = TextInput( attrs = { 'class': 'grow'}))

    class Meta:
        model = Letter
        fields = ['comment', 'diplomatic_date']
        widgets = {
            'comment': Textarea(attrs={
                'class': SimpleFormMixin.text_area_classes + ' bg-white border-black'
            }),
        }

    #def __init__(self, *args, **kwargs):
        #super().__init__(*args, **kwargs)
        #if self.instance and self.instance.source_period:
            #self.fields['not_before_source'].initial = self.instance.source_period.not_before
            #self.fields['not_after_source'].initial = self.instance.source_period.not_after
            #self.fields['display_source'].initial = self.instance.source_period.display
        #if self.instance and self.instance.edition_period:
            #self.fields['not_before_edition'].initial = self.instance.edition_period.not_before
            #self.fields['not_after_edition'].initial = self.instance.edition_period.not_after
            #self.fields['display_edition'].initial = self.instance.edition_period.display

    #def save(self, commit=True):
        #letter_instance = super().save(commit=False)

        # Ensure period exists or create it
        #if not letter_instance.period:
            #letter_instance.period = Period()

        #source_period_instance = letter_instance.source_period
        #source_period_instance.not_before = self.cleaned_data['not_before_source']
        #source_period_instance.not_after = self.cleaned_data['not_after_source']
        #source_period_instance.display = self.cleaned_data['display_source']

        #edition_period_instance = letter_instance.period
        #edition_period_instance.not_before = self.cleaned_data['not_before_edition']
        #edition_period_instance.not_after = self.cleaned_data['not_after_edition']
        #edition_period_instance.display = self.cleaned_data['display_edition']

        #if commit:
            #source_period_instance.save()
            #edition_period_instance.save()
            #letter_instance.save()

        #return letter_instance

    def diplomatic_date_as_daisy(self):
        form = div()

        diplomatic_date_field = self['diplomatic_date']
        with form:
            with label(cls=SimpleFormMixin.form_control_classes):
                with div(cls=SimpleFormMixin.label_classes):
                    span(diplomatic_date_field.label, cls=SimpleFormMixin.label_text_classes)
                raw(str(diplomatic_date_field))

        return form

    def comment_as_daisy(self):
        form = div(cls='mb-10')

        #source_not_before_field = self['not_before_source']
        #source_not_after_field = self['not_after_source']
        #source_display_field = self['display_source']
        #edition_not_before_field = self['not_before_edition']
        #edition_not_after_field = self['not_after_edition']
        #edition_display_field = self['display_edition']
        comment_field = self['comment']

        #not_before_container = label(cls='form-control')
        #not_before_label = div(_('not before'), cls='label-text')
        #not_before_selects = div(cls='flex')
        #not_before_selects.add(raw(str(not_before_field)))
        #not_before_container.add(not_before_label)
        #not_before_container.add(not_before_selects)
        #if not_before_field.errors:
            #not_before_container.add(div(span(not_before_field.errors, cls='text-primary text-sm'), cls='label'))

        #not_after_container = label(cls='form-control')
        #not_after_label = div(_('not after'), cls='label-text')
        #not_after_selects = div(cls='flex')
        #not_after_selects.add(raw(str(not_after_field)))
        #not_after_container.add(not_after_label)
        #not_after_container.add(not_after_selects)
        #if not_after_field.errors:
            #not_after_container.add(div(span(not_after_field.errors, cls='text-primary text-sm'), cls='label'))

        #display_container = label(_('standardized date'), _for = display_field.id_for_label, cls='input input-bordered bg-white border-black flex items-center gap-2 my-5')
        #display_container.add(raw(str(display_field)))
        #if display_field.errors:
            #display_container.add(div(span(display_field.errors, cls='text-primary text-sm'), cls='label'))

        comment_container = label(cls='form-control')
        comment_label = div(comment_field.label, cls='label-text')
        comment_container.add(comment_label)
        comment_container.add(raw(str(comment_field)))
        if comment_field.errors:
            comment_container.add(div(span(comment_field.errors, cls='text-primary text-sm'), cls='label'))

        #period_palette = div(cls='flex flex-rows w-full gap-10 my-5')
        #period_palette.add(not_before_container)
        #period_palette.add(not_after_container)

        #form.add(display_container)
        #form.add(period_palette)
        form.add(comment_container)

        return mark_safe(str(form))

class LetterMentioningForm(ModelForm):
    class Meta:
        model = LetterMentioning
        fields = ['pages']
        widgets = {
                'pages': TextInput(attrs={'form': 'form', 'class': 'flex-1 min-w-0'})
        }
