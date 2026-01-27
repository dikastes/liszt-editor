import dominate.tags as tags
from dominate.util import raw
from .base import SimpleFormMixin, DateFormMixin
from django import forms
from django.conf import settings
from django.forms import ModelForm, TextInput, Select, HiddenInput, CheckboxInput, Textarea, DateTimeField, CharField, BooleanField
from django.utils.safestring import mark_safe
from liszt_util.forms import SelectDateWidget
from dmrism.models.manifestation import ManifestationPersonDedication, ManifestationCorporationDedication
from dmrism.models.item import ItemPersonDedication, ItemCorporationDedication
from edwoca.models.work import WorkPersonDedication, WorkCorporationDedication
from dmad_on_django.models import Period


class WorkPersonDedicationForm(DateFormMixin, forms.ModelForm):
    kwargs = {
            'years': range(settings.EDWOCA_FIXED_DATES['birth']['year'], 1900),
            'attrs': {
                'form': 'form',
                'class': 'select select-bordered'
            }
        }
    display = CharField(required=False, widget = TextInput( attrs = { 'class': 'grow'}))
    not_before = DateTimeField(widget = SelectDateWidget(**kwargs), required = False)
    not_after = DateTimeField(widget = SelectDateWidget(**kwargs), required = False)
    inferred = BooleanField(widget = CheckboxInput(attrs = { 'class': 'toggle', 'form': 'form'}), required = False)
    assumed = BooleanField(widget = CheckboxInput(attrs = { 'class': 'toggle', 'form': 'form'}), required = False)

    class Meta:
        model = WorkPersonDedication
        fields = ['diplomatic_dedication']
        widgets = {
            'diplomatic_dedication': Textarea(attrs={
                'class': SimpleFormMixin.text_area_classes
            }),
        }


class WorkCorporationDedicationForm(forms.ModelForm):
    kwargs = {
            'years': range(settings.EDWOCA_FIXED_DATES['birth']['year'], 1900),
            'attrs': {
                'class': 'select select-bordered'
            }
        }
    display = CharField(required=False, widget = TextInput( attrs = { 'class': 'grow'}))
    not_before = DateTimeField(widget = SelectDateWidget(**kwargs), required = False)
    not_after = DateTimeField(widget = SelectDateWidget(**kwargs), required = False)
    inferred = BooleanField(widget = CheckboxInput(attrs = { 'class': 'toggle', 'form': 'form'}), required = False)
    assumed = BooleanField(widget = CheckboxInput(attrs = { 'class': 'toggle', 'form': 'form'}), required = False)


    class Meta:
        model = WorkCorporationDedication
        fields = ['diplomatic_dedication']
        widgets = {
            'diplomatic_dedication': Textarea(attrs={
                'class': SimpleFormMixin.text_area_classes
            }),
        }


class ManifestationBaseDedicationMixin:
    def as_daisy(self):
        date_div = self.get_date_div()
        form = tags.div()

        dedication_field = self['diplomatic_dedication']
        dedication_label = tags.label()
        dedication_label_text = tags.span(dedication_field.label, cls='label-text')
        dedication_label.add(dedication_label_text)
        dedication_label.add(raw(str(dedication_field)))

        form.add(date_div)
        form.add(dedication_label)

        return mark_safe(str(form))


class ManifestationPersonDedicationForm(DateFormMixin, ManifestationBaseDedicationMixin, forms.ModelForm):
    kwargs = {
            'years': range(settings.EDWOCA_FIXED_DATES['birth']['year'], 1900),
            'attrs': {
                'form': 'form',
                'class': 'select select-bordered'
            }
        }
    display = CharField(required=False, widget = TextInput( attrs = { 'form': 'form', 'class': 'grow'}))
    not_before = DateTimeField(widget = SelectDateWidget(**kwargs), required = False)
    not_after = DateTimeField(widget = SelectDateWidget(**kwargs), required = False)
    inferred = BooleanField(widget = CheckboxInput(attrs = { 'class': 'toggle', 'form': 'form'}), required = False)
    assumed = BooleanField(widget = CheckboxInput(attrs = { 'class': 'toggle', 'form': 'form'}), required = False)


    class Meta:
        model = ManifestationPersonDedication
        fields = ['diplomatic_dedication']
        widgets = {
            'diplomatic_dedication': Textarea(attrs={
                'form': 'form',
                'class': SimpleFormMixin.text_area_classes
            }),
        }


class ManifestationCorporationDedicationForm(DateFormMixin, ManifestationBaseDedicationMixin, forms.ModelForm):
    kwargs = {
            'years': range(settings.EDWOCA_FIXED_DATES['birth']['year'], 1900),
            'attrs': {
                'form': 'form',
                'class': 'select select-bordered'
            }
        }
    display = CharField(required=False, widget = TextInput( attrs = { 'form': 'form', 'class': 'grow'}))
    not_before = DateTimeField(widget = SelectDateWidget(**kwargs), required = False)
    not_after = DateTimeField(widget = SelectDateWidget(**kwargs), required = False)
    inferred = BooleanField(widget = CheckboxInput(attrs = { 'class': 'toggle', 'form': 'form'}), required = False)
    assumed = BooleanField(widget = CheckboxInput(attrs = { 'class': 'toggle', 'form': 'form'}), required = False)


    class Meta:
        model = ManifestationCorporationDedication
        fields = ['diplomatic_dedication']
        widgets = {
            'diplomatic_dedication': Textarea(attrs={
                'form': 'form',
                'class': SimpleFormMixin.text_area_classes
            }),
        }


class ItemPersonDedicationForm(forms.ModelForm):
    kwargs = {
            'years': range(settings.EDWOCA_FIXED_DATES['birth']['year'], 1900),
            'attrs': {
                'class': 'select select-bordered'
            }
        }
    display = CharField(required=False, widget = TextInput( attrs = { 'class': 'grow'}))
    not_before = DateTimeField(widget = SelectDateWidget(**kwargs), required = False)
    not_after = DateTimeField(widget = SelectDateWidget(**kwargs), required = False)

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
    display = CharField(required=False, widget = TextInput( attrs = { 'class': 'grow'}))
    not_before = DateTimeField(widget = SelectDateWidget(**kwargs), required = False)
    not_after = DateTimeField(widget = SelectDateWidget(**kwargs), required = False)

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
