from .base import *
from django import forms
from django.conf import settings
from django.forms import ModelForm, TextInput, Select, HiddenInput, CheckboxInput, Textarea, DateTimeField, CharField, BooleanField
from dmad_on_django.models import Period
from ..models.base import ItemModification
from ..models.base import ModificationHandwriting
from liszt_util.forms.base import SelectDateWidget
from dominate.tags import div, label, span
from dominate.util import raw
from django.utils.safestring import mark_safe

class ItemModificationForm(DateFormMixin, ModelForm):
    kwargs = {
        'years': range(settings.EDWOCA_FIXED_DATES['birth']['year'], 1900),
        'attrs': {
            'form': 'form'
        }
    }
    not_before = DateTimeField(widget=SelectDateWidget(**kwargs), required=False)
    not_after = DateTimeField(widget=SelectDateWidget(**kwargs), required=False)
    display = CharField(required=False, widget=TextInput(attrs={'class': 'grow flex-1', 'form': 'form'}))
    inferred = BooleanField(widget = CheckboxInput(attrs = { 'class': 'toggle', 'form': 'form'}), required = False)
    assumed = BooleanField(widget = CheckboxInput(attrs = { 'class': 'toggle', 'form': 'form'}), required = False)

    class Meta:
        model = ItemModification
        fields = ['note']
        widgets = {
            'note': Textarea(attrs={'class': 'border-black bg-white textarea textarea-bordered w-full', 'form': 'form'}),
        }

    def as_daisy(self):
        form_container = div()
        date_div = self.get_date_div()

        # Note Field
        note_field = self['note']
        note_container = div(cls='form-control')
        note_label = label(cls='label')
        note_label.add(span(note_field.label, cls='label-text'))
        note_container.add(note_label)
        note_container.add(raw(str(note_field)))

        form_container.add(date_div)
        form_container.add(note_container)

        return mark_safe(str(form_container))


class ModificationHandwritingForm(HandwritingForm):
    class Meta(HandwritingForm.Meta):
        model = ModificationHandwriting
