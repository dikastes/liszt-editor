from .base import *
from django import forms
from django.conf import settings
from django.forms import ModelForm, TextInput, Select, HiddenInput, CheckboxInput, Textarea, DateTimeField, CharField
from dmad_on_django.models import Period
from ..models.base import ItemModification
from ..models.base import ModificationHandwriting
from liszt_util.forms.base import SelectDateWidget
from dominate.tags import div, label, span
from dominate.util import raw
from django.utils.safestring import mark_safe

class ItemModificationForm(ModelForm):
    kwargs = {
        'years': range(settings.EDWOCA_FIXED_DATES['birth']['year'], 1900),
        'attrs': {
            'form': 'form'
        }
        #'attrs': {
            #'class': 'select select-bordered border-black bg-white'
        #}
    }
    not_before = DateTimeField(widget=SelectDateWidget(**kwargs), required=False)
    not_after = DateTimeField(widget=SelectDateWidget(**kwargs), required=False)
    display = CharField(required=False, widget=TextInput(attrs={'class': 'grow flex-1', 'form': 'form'}))

    class Meta:
        model = ItemModification
        fields = ['note']
        widgets = {
            'note': Textarea(attrs={'class': 'border-black bg-white textarea textarea-bordered w-full', 'form': 'form'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.period:
            self.fields['not_before'].initial = self.instance.period.not_before
            self.fields['not_after'].initial = self.instance.period.not_after
            self.fields['display'].initial = self.instance.period.display

    def save(self, commit=True):
        modification_instance = super().save(commit=False)

        if not modification_instance.period:
            modification_instance.period = Period.objects.create()

        period_instance = modification_instance.period
        period_instance.not_before = self.cleaned_data['not_before']
        period_instance.not_after = self.cleaned_data['not_after']
        period_instance.display = self.cleaned_data['display']

        if commit:
            period_instance.save()
            modification_instance.period = period_instance
            modification_instance.save()

        return modification_instance

    def as_daisy(self):
        form_container = div()

        # Display Field
        display_field = self['display']
        display_wrapper = div(cls='input input-bordered border-black bg-white w-full mb-5')
        display_label = label(cls='label flex gap-2 items-center')
        display_label.add(span(display_field.label, cls='flex-0 label-text'))
        display_label.add(raw(str(display_field)))
        display_wrapper.add(display_label)
        form_container.add(display_wrapper)

        # Period Fields (side-by-side)
        period_palette = div(cls='flex gap-5 mb-5')
        
        not_before_field = self['not_before']
        not_before_container = div(cls='form-control flex-1')
        not_before_label = label(cls='label')
        not_before_label.add(span(not_before_field.label, cls='label-text'))
        not_before_container.add(not_before_label)
        not_before_widget_wrapper = div(cls='flex')
        not_before_widget_wrapper.add(raw(str(not_before_field)))
        not_before_container.add(not_before_widget_wrapper)
        period_palette.add(not_before_container)

        not_after_field = self['not_after']
        not_after_container = div(cls='form-control flex-1')
        not_after_label = label(cls='label')
        not_after_label.add(span(not_after_field.label, cls='label-text'))
        not_after_container.add(not_after_label)
        not_after_widget_wrapper = div(cls='flex')
        not_after_widget_wrapper.add(raw(str(not_after_field)))
        not_after_container.add(not_after_widget_wrapper)
        period_palette.add(not_after_container)

        form_container.add(period_palette)

        # Note Field
        note_field = self['note']
        note_container = div(cls='form-control')
        note_label = label(cls='label')
        note_label.add(span(note_field.label, cls='label-text'))
        note_container.add(note_label)
        note_container.add(raw(str(note_field)))
        form_container.add(note_container)

        return mark_safe(str(form_container))

class ModificationHandwritingForm(HandwritingForm):
    class Meta(HandwritingForm.Meta):
        model = ModificationHandwriting
