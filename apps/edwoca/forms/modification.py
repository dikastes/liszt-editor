from .base import *
from django import forms
from django.db.models import Q
from django.conf import settings
from django.forms import ModelForm, TextInput, Select, HiddenInput, CheckboxInput, Textarea, DateTimeField, CharField, BooleanField, DateField, ChoiceField
from django.utils.translation import gettext_lazy as _
from dmad_on_django.models import Period
from ..models.base import ItemModification, Manifestation, ModificationHandwriting
from dmrism.models.manifestation import RelatedExpression
from liszt_util.forms.base import SelectDateWidget
from dominate.tags import div, label, span
from dominate.util import raw
from django.utils.safestring import mark_safe

class ItemModificationForm(DateFormMixin, ModelForm):
    kwargs = {
            'years': range(settings.EDWOCA_FIXED_DATES['birth']['year'], 1900),
            'attrs': {
                'class': SimpleFormMixin.select_classes
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
            widget = Select(attrs = {'class': SimpleFormMixin.select_classes}),
            required = False
        )
    start_qualifier = ChoiceField(
            label = _('not before mode'),
            choices = Period.StartQualifier,
            widget = Select(attrs = {'class': SimpleFormMixin.select_classes}),
            required = False
        )
    end_qualifier = ChoiceField(
            label = _('not after mode'),
            choices = Period.EndQualifier,
            widget = Select(attrs = {'class': SimpleFormMixin.select_classes}),
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
            widget = TextInput( attrs = { 'class': SimpleFormMixin.text_input_classes })
        )
    inferred = TypedChoiceField(
            choices = ((False, _('based on source')), (True, _('inferred'))),
            coerce = lambda x: x == 'True',
            widget = RadioSelect(
                    attrs = { 'class': 'radio', 'form': 'form'}
                ),
            required = False
        )
    assumed = BooleanField(widget = CheckboxInput(attrs = { 'class': 'toggle', 'form': 'form'}), required = False)

    class Meta:
        model = ItemModification
        fields = [
                'note',
                'collection_component',
                'modification_description',
                'is_addition',
                'is_correction',
                'is_note',
                'is_title'
            ]
        widgets = {
            'note': Textarea(attrs={'class': SimpleFormMixin.text_area_classes, 'form': 'form'}),
            'modification_description': Textarea(attrs={'class': SimpleFormMixin.text_area_classes, 'form': 'form'}),
            'collection_component': Select(attrs={'class': SimpleFormMixin.select_classes, 'form': 'form'}),
            'is_addition': CheckboxInput(attrs = { 'class': 'toggle', 'form': 'form'}),
            'is_correction': CheckboxInput(attrs = { 'class': 'toggle', 'form': 'form'}),
            'is_title': CheckboxInput(attrs = { 'class': 'toggle', 'form': 'form'}),
            'is_note': CheckboxInput(attrs = { 'class': 'toggle', 'form': 'form'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


        component_manifestations = Manifestation.objects.filter(
                Q(component_of = self.instance.item.manifestation.id) |
                Q(pk = self.instance.item.manifestation.id)
            )

        self.fields['collection_component'].queryset = RelatedExpression.objects.filter(manifestation__in=component_manifestations)

    def collection_component_as_daisy(self):
        form = div()

        collection_component_field = self['collection_component']

        with form:
            with label(cls='form-control'):
                with div(cls='label'):
                    span(_('work relation (working title)'), cls='label-text')
                raw(str(collection_component_field))

        return mark_safe(str(form))

    def classification_as_daisy(self):
        form = div(cls='my-5')

        addition_field = self['is_addition']
        correction_field = self['is_correction']
        note_field = self['is_note']
        title_field = self['is_title']

        with form:
            with label(cls=SimpleFormMixin.toggle_inverted_classes):
                raw(str(addition_field))
                span(addition_field.label, cls=SimpleFormMixin.label_text_classes)
            with label(cls=SimpleFormMixin.toggle_inverted_classes):
                raw(str(correction_field))
                span(correction_field.label, cls=SimpleFormMixin.label_text_classes)
            with label(cls=SimpleFormMixin.toggle_inverted_classes):
                raw(str(note_field))
                span(note_field.label, cls=SimpleFormMixin.label_text_classes)
            with label(cls=SimpleFormMixin.toggle_inverted_classes):
                raw(str(title_field))
                span(title_field.label, cls=SimpleFormMixin.label_text_classes)

        return mark_safe(str(form))

    def description_as_daisy(self):
        form = div()

        description_field = self['modification_description']

        with form:
            with label(cls='form-control'):
                with div(cls='label'):
                    span(description_field.label, cls='label-text')
                raw(str(description_field))

        return mark_safe(str(form))

    def as_daisy(self):
        form = div()

        note_field = self['note']

        with form:
            self.get_date_div()
            with label(cls='form-control'):
                with div(cls='label'):
                    span(note_field.label, cls='label-text')
                raw(str(note_field))

        return mark_safe(str(form))


class ModificationHandwritingForm(HandwritingForm):
    class Meta(HandwritingForm.Meta):
        model = ModificationHandwriting
