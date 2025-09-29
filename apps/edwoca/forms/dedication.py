from .base import SimpleFormMixin
from django import forms
from django.conf import settings
from django.forms import ModelForm, TextInput, Select, HiddenInput, CheckboxInput, Textarea, DateTimeField, SelectDateWidget, CharField
from dmrism.models.manifestation import ManifestationPersonDedication, ManifestationCorporationDedication
from dmrism.models.item import ItemPersonDedication, ItemCorporationDedication
from dmad_on_django.models import Period


class ManifestationPersonDedicationForm(forms.ModelForm):
    kwargs = {
            'years': range(settings.EDWOCA_FIXED_DATES['birth']['year'], 1900),
            'attrs': {
                'class': 'select select-bordered'
            }
        }
    not_before = DateTimeField(widget = SelectDateWidget(**kwargs), required = False)
    not_after = DateTimeField(widget = SelectDateWidget(**kwargs), required = False)
    display = CharField(required=False, widget = TextInput( attrs = { 'class': 'grow'}))

    class Meta:
        model = ManifestationPersonDedication
        fields = ['diplomatic_dedication']
        widgets = {
            'diplomatic_dedication': Textarea(attrs={
                'class': SimpleFormMixin.text_area_classes
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.period:
            self.fields['not_before'].initial = self.instance.period.not_before
            self.fields['not_after'].initial = self.instance.period.not_after
            self.fields['display'].initial = self.instance.period.display

    def save(self, commit=True):
        dedication_instance = super().save(commit=False)

        # Ensure period exists or create it
        if not dedication_instance.period:
            dedication_instance.period = Period()

        period_instance = dedication_instance.period
        period_instance.not_before = self.cleaned_data['not_before']
        period_instance.not_after = self.cleaned_data['not_after']
        period_instance.display = self.cleaned_data['display']

        if commit:
            period_instance.save()
            dedication_instance.period = period_instance
            dedication_instance.save()

        return dedication_instance

class ManifestationCorporationDedicationForm(forms.ModelForm):
    kwargs = {
            'years': range(settings.EDWOCA_FIXED_DATES['birth']['year'], 1900),
            'attrs': {
                'class': 'select select-bordered'
            }
        }
    not_before = DateTimeField(widget = SelectDateWidget(**kwargs), required = False)
    not_after = DateTimeField(widget = SelectDateWidget(**kwargs), required = False)
    display = CharField(required=False, widget = TextInput( attrs = { 'class': 'grow'}))

    class Meta:
        model = ManifestationCorporationDedication
        fields = ['diplomatic_dedication']
        widgets = {
            'diplomatic_dedication': Textarea(attrs={
                'class': SimpleFormMixin.text_area_classes
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.period:
            self.fields['not_before'].initial = self.instance.period.not_before
            self.fields['not_after'].initial = self.instance.period.not_after
            self.fields['display'].initial = self.instance.period.display

    def save(self, commit=True):
        dedication_instance = super().save(commit=False)

        # Ensure period exists or create it
        if not dedication_instance.period:
            dedication_instance.period = Period()

        period_instance = dedication_instance.period
        period_instance.not_before = self.cleaned_data['not_before']
        period_instance.not_after = self.cleaned_data['not_after']
        period_instance.display = self.cleaned_data['display']

        if commit:
            period_instance.save()
            dedication_instance.period = period_instance
            dedication_instance.save()

        return dedication_instance


class ItemPersonDedicationForm(forms.ModelForm):
    kwargs = {
            'years': range(settings.EDWOCA_FIXED_DATES['birth']['year'], 1900),
            'attrs': {
                'class': 'select select-bordered'
            }
        }
    not_before = DateTimeField(widget = SelectDateWidget(**kwargs), required = False)
    not_after = DateTimeField(widget = SelectDateWidget(**kwargs), required = False)
    display = CharField(required=False, widget = TextInput( attrs = { 'class': 'grow'}))

    class Meta:
        model = ItemPersonDedication
        fields = ['diplomatic_dedication']
        widgets = {
            'diplomatic_dedication': Textarea(attrs={
                'class': SimpleFormMixin.text_area_classes
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.period:
            self.fields['not_before'].initial = self.instance.period.not_before
            self.fields['not_after'].initial = self.instance.period.not_after
            self.fields['display'].initial = self.instance.period.display

    def save(self, commit=True):
        dedication_instance = super().save(commit=False)

        # Ensure period exists or create it
        if not dedication_instance.period:
            dedication_instance.period = Period()

        period_instance = dedication_instance.period
        period_instance.not_before = self.cleaned_data['not_before']
        period_instance.not_after = self.cleaned_data['not_after']
        period_instance.display = self.cleaned_data['display']

        if commit:
            period_instance.save()
            dedication_instance.period = period_instance
            dedication_instance.save()

        return dedication_instance


class ItemCorporationDedicationForm(forms.ModelForm):
    kwargs = {
            'years': range(settings.EDWOCA_FIXED_DATES['birth']['year'], 1900),
            'attrs': {
                'class': 'select select-bordered'
            }
        }
    not_before = DateTimeField(widget = SelectDateWidget(**kwargs), required = False)
    not_after = DateTimeField(widget = SelectDateWidget(**kwargs), required = False)
    display = CharField(required=False, widget = TextInput( attrs = { 'class': 'grow'}))

    class Meta:
        model = ItemCorporationDedication
        fields = ['diplomatic_dedication']
        widgets = {
            'diplomatic_dedication': Textarea(attrs={
                'class': SimpleFormMixin.text_area_classes
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.period:
            self.fields['not_before'].initial = self.instance.period.not_before
            self.fields['not_after'].initial = self.instance.period.not_after
            self.fields['display'].initial = self.instance.period.display

    def save(self, commit=True):
        dedication_instance = super().save(commit=False)

        # Ensure period exists or create it
        if not dedication_instance.period:
            dedication_instance.period = Period()

        period_instance = dedication_instance.period
        period_instance.not_before = self.cleaned_data['not_before']
        period_instance.not_after = self.cleaned_data['not_after']
        period_instance.display = self.cleaned_data['display']

        if commit:
            period_instance.save()
            dedication_instance.period = period_instance
            dedication_instance.save()

        return dedication_instance
