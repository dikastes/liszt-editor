from .base import *
from django import forms
from django.conf import settings
from django.forms import ModelForm, TextInput, Select, HiddenInput, CheckboxInput, Textarea, DateTimeField, SelectDateWidget, CharField
from dmad_on_django.models import Period
from ..models.base import ItemModification
from ..models.base import ModificationHandwriting

class ItemModificationForm(ModelForm):
    kwargs = {
        'years': range(settings.EDWOCA_FIXED_DATES['birth']['year'], 1900),
        'attrs': {
            'class': 'select select-bordered'
        }
    }
    not_before = DateTimeField(widget=SelectDateWidget(**kwargs), required=False)
    not_after = DateTimeField(widget=SelectDateWidget(**kwargs), required=False)
    display = CharField(required=False, widget=TextInput(attrs={'class': 'grow input input-bordered'}))

    class Meta:
        model = ItemModification
        fields = ['note']
        widgets = {
            'note': Textarea(attrs={'class': 'textarea textarea-bordered w-full'}),
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

class ModificationHandwritingForm(HandwritingForm):
    class Meta(HandwritingForm.Meta):
        model = ModificationHandwriting
