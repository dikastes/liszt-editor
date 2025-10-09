from .base import *
from bib.models import ZotItem
from django import forms
from django.conf import settings
from django.forms import ModelForm, TextInput, Select, HiddenInput, CheckboxInput, Textarea, DateTimeField, SelectDateWidget, CharField
from django.forms.models import inlineformset_factory
from django.utils.safestring import mark_safe
from dmad_on_django.models import Period
from dmrism.models.item import Item, PersonProvenanceStation, CorporationProvenanceStation, Library
from dmrism.models.manifestation import Manifestation, ManifestationTitle, ManifestationBib, RelatedManifestation, ManifestationTitleHandwriting
from dominate.tags import div, label, span
from dominate.util import raw


class ManifestationForm(ModelForm):
    class Meta:
        model = Manifestation
        fields = ['rism_id', 'private_head_comment']
        widgets = {
                'rism_id': TextInput( attrs = {
                        'class': 'grow h-full'
                    }),
                'private_head_comment': Textarea( attrs = {
                        'class': 'textarea textarea-bordered w-full'
                    })
            }

    def as_daisy(self):
        form = div()
        rism_id_label = label(self['rism_id'].label, _for=self['rism_id'].id_for_label, cls='input input-bordered flex items-center gap-2 my-5')
        rism_id_label.add(raw(str(self['rism_id'])))
        form.add(rism_id_label)

        private_head_comment_label = label(cls='form-control', _for=self['private_head_comment'].id_for_label)
        private_head_comment_label.add(span(self['private_head_comment'].label, cls='label-text'))
        private_head_comment_label.add(raw(str(self['private_head_comment'])))
        form.add(private_head_comment_label)

        return mark_safe(str(form))


class ManifestationDedicationForm(ModelForm, SimpleFormMixin):
    class Meta:
        model = Manifestation
        fields = ['dedication', 'private_title_comment']
        widgets = {
                'dedication': Textarea( attrs = {
                        'class': SimpleFormMixin.text_area_classes
                    }),
                'private_title_comment': Textarea( attrs = {
                        'class': SimpleFormMixin.text_area_classes
                    })
            }
        labels = {
            'private_title_comment': 'Interner Widmungskommentar',
        }


class ManifestationTitleForm(ModelForm):
    class Meta:
        model = ManifestationTitle
        fields = ['title', 'title_type', 'status', 'manifestation']
        widgets = {
            'title': Textarea(attrs={'class': 'textarea textarea-bordered h-64'}),
            'title_type': Select(attrs={'class': 'select select-bordered w-full'}),
            'status': Select(attrs={'class': 'select select-bordered w-full'}),
            'manifestation': HiddenInput(),
        }

    def as_daisy(self):
        form = div(cls='flex flex-col gap-5')

        # Title field (textarea)
        title_label = label(self['title'].label, _for=self['title'].id_for_label, cls='form-control w-full')
        title_label.add(raw(str(self['title'])))
        form.add(title_label)

        # Remaining properties on a palette with flex-1
        palette = div(cls='flex flex-wrap gap-5')
        for field_name in ['title_type', 'status']:
            field = self[field_name]
            field_label = label(field.label, _for=field.id_for_label, cls='form-control flex-1 min-w-[200px]')
            field_label.add(raw(str(field)))
            palette.add(field_label)
        form.add(palette)
        form.add(raw(str(self['manifestation'])))

        return mark_safe(str(form))


class ManifestationCommentForm(CommentForm):
    class Meta:
        model = Manifestation
        fields = CommentForm.Meta.fields + ['taken_information']
        widgets = dict(CommentForm.Meta.widgets, **{
                'taken_information': Textarea( attrs = {
                        'class': SimpleFormMixin.text_area_classes
                    })
            })


class ManifestationBibForm(BaseBibForm):
    class Meta(BaseBibForm.Meta):
        model = ManifestationBib
        fields = BaseBibForm.Meta.fields + [ 'manifestation' ]
        widgets = dict(BaseBibForm.Meta.widgets, **{ 'manifestation': HiddenInput() })


class ManifestationHistoryForm(ModelForm, SimpleFormMixin):
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
        model = Manifestation
        fields = ['history', 'id', 'date_diplomatic', 'private_history_comment']
        widgets = {
                'history': Textarea( attrs = {
                        'class': SimpleFormMixin.text_area_classes
                    }),
                'date_diplomatic': Textarea( attrs = {
                        'class': SimpleFormMixin.text_area_classes
                    }),
                'private_history_comment': Textarea( attrs = {
                        'class': SimpleFormMixin.text_area_classes
                    })
            }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.period:
            self.fields['not_before'].initial = self.instance.period.not_before
            self.fields['not_after'].initial = self.instance.period.not_after
            self.fields['display'].initial = self.instance.period.display

    def save(self, commit=True):
        manifestation_instance = super().save(commit=False)

        # Ensure period exists or create it
        if not manifestation_instance.period:
            manifestation_instance.period = Period()

        period_instance = manifestation_instance.period
        period_instance.not_before = self.cleaned_data['not_before']
        period_instance.not_after = self.cleaned_data['not_after']
        period_instance.display = self.cleaned_data['display']

        if commit:
            period_instance.save()
            manifestation_instance.save()
        else:
            self._pending_save_period = period_instance
            self._pending_save_manifestation = manifestation_instance

        return manifestation_instance

    def as_daisy(self):
        form = div(cls='mb-10')

        not_before_field = self['not_before']
        not_after_field = self['not_after']
        display_field = self['display']
        #history_field = self['history']

        not_before_container = label(cls='form-control')
        not_before_label = div(not_before_field.label, cls='label-text')
        not_before_selects = div(cls='flex')
        not_before_selects.add(raw(str(not_before_field)))
        not_before_container.add(not_before_label)
        not_before_container.add(not_before_selects)
        if not_before_field.errors:
            not_before_container.add(div(span(not_before_field.errors, cls='text-primary text-sm'), cls='label'))

        not_after_container = label(cls='form-control')
        not_after_label = div(not_after_field.label, cls='label-text')
        not_after_selects = div(cls='flex')
        not_after_selects.add(raw(str(not_after_field)))
        not_after_container.add(not_after_label)
        not_after_container.add(not_after_selects)
        if not_after_field.errors:
            not_after_container.add(div(span(not_after_field.errors, cls='text-primary text-sm'), cls='label'))

        display_container = label(display_field.label, _for = display_field.id_for_label, cls='input input-bordered flex items-center gap-2 my-5')
        display_container.add(raw(str(display_field)))
        if display_field.errors:
            display_container.add(div(span(display_field.errors, cls='text-primary text-sm'), cls='label'))

        date_diplomatic_field = self['date_diplomatic']
        date_diplomatic_wrap = label(cls='form-control')
        date_diplomatic_label = div(cls='label')
        date_diplomatic_span = span(date_diplomatic_field.label, cls='label-text')
        date_diplomatic_label.add(date_diplomatic_span)
        date_diplomatic_wrap.add(date_diplomatic_label)
        date_diplomatic_wrap.add(raw(str(date_diplomatic_field)))

        #history_wrap = label(cls='form-control')
        #history_label = div(cls='label')
        #history_span = span(history_field.label, cls='label-text')
        #history_label.add(history_span)
        #history_wrap.add(history_label)
        #history_wrap.add(raw(str(history_field)))

        period_palette = div(cls='flex flex-rows w-full gap-10 my-5')
        period_palette.add(not_before_container)
        period_palette.add(not_after_container)
        #period_palette.add(display_container)

        form.add(period_palette)
        form.add(display_container)
        form.add(date_diplomatic_wrap)

        private_history_comment_field = self['private_history_comment']
        private_history_comment_wrap = label(cls='form-control')
        private_history_comment_label = div(cls='label')
        private_history_comment_span = span(private_history_comment_field.label, cls='label-text')
        private_history_comment_label.add(private_history_comment_span)
        private_history_comment_wrap.add(private_history_comment_label)
        private_history_comment_wrap.add(raw(str(private_history_comment_field)))
        form.add(private_history_comment_wrap)

        return mark_safe(str(form))


class RelatedManifestationForm(ModelForm):
    class Meta:
        model = RelatedManifestation
        fields = [ 'source_manifestation', 'target_manifestation', 'label' ]
        widgets = {
                'source_manifestation': HiddenInput(),
                'target_manifestation': HiddenInput(),
                'label': Select( attrs = {
                        'class': 'select w-full select-bordered'
                    })
            }

    def as_daisy(self):
        form = div(cls='mb-10')

        label_container = div(cls='flex-1')
        label_container.add(raw(str(self['label'])))

        form.add(label_container)

        return mark_safe(str(form))


class ManifestationClassificationForm(ModelForm):
    class Meta:
        model = Manifestation
        fields = [
                'manifestation_form',
                'edition_type',
                'function',
                'source_type'
            ]
        widgets = {
                'manifestation_form': Select( attrs = {
                        'class': 'select w-full select-bordered'
                    }),
                'edition_type': Select( attrs = {
                        'class': 'select w-full select-bordered'
                    }),
                'function': Select( attrs = {
                        'class': 'select w-full select-bordered'
                    }),
                'source_type': Select( attrs = {
                        'class': 'select w-full select-bordered'
                    }),
            }

    def as_daisy(self):
        form = div(cls='mb-10')

        manifestation_form_field = self['manifestation_form']
        edition_type_field = self['edition_type']
        function_field = self['function']
        source_type_field = self['source_type']

        manifestation_form_label = label(manifestation_form_field.label, cls='flex-1')
        manifestation_form_label.add(raw(str(manifestation_form_field)))

        edition_type_label = label(edition_type_field.label, cls='flex-1')
        edition_type_label.add(raw(str(edition_type_field)))

        function_label = label(function_field.label, cls='flex-1')
        function_label.add(raw(str(function_field)))

        source_type_label = label(source_type_field.label, cls='flex-1')
        source_type_label.add(raw(str(source_type_field)))

        palette1 = div(cls='flex flex-rows w-full gap-10 my-5')
        palette1.add(manifestation_form_label)
        palette1.add(edition_type_label)

        palette2 = div(cls='flex flex-rows w-full gap-10 my-5')
        palette2.add(function_label)
        palette2.add(source_type_label)

        form.add(palette1)
        form.add(palette2)

        return mark_safe(str(form))


ManifestationTitleFormSet = inlineformset_factory(
        Manifestation,
        ManifestationTitle,
        form = ManifestationTitleForm,
        formset = SkipEmptyTitleFormSet,
        extra = 1,
        max_num = 100,
        can_delete = True
    )





class ManifestationRelationsCommentForm(ModelForm, SimpleFormMixin):
    class Meta:
        model = Manifestation
        fields = ['private_relations_comment']
        widgets = {
                'private_relations_comment': Textarea( attrs = {
                        'class': SimpleFormMixin.text_area_classes
                    })
            }


class ManifestationCreateForm(forms.Form):
    temporary_title = forms.CharField(label='Temporärer Titel', max_length=255, required=False)
    signature = forms.CharField(label='Signatur', max_length=255)
    library = forms.ModelChoiceField(queryset=Library.objects.all(), label='Bibliothek', empty_label="Bibliothek auswählen", widget=forms.Select(attrs={'class': 'select select-bordered w-full'}))


class ManifestationTitleHandwritingForm(ModelForm):
    class Meta:
        model = ManifestationTitleHandwriting
        fields = ['medium', 'manifestation_title', 'dubious_writer']
        widgets = {
            'medium': TextInput(attrs={'class': 'w-full'}),
            'manifestation_title': HiddenInput(),
            'dubious_writer': CheckboxInput(attrs={'class': 'toggle'}),
        }

    def as_daisy(self):
        form = div(cls='flex flex-col gap-5')

        # Fields for the palette
        palette = div(cls='flex flex-wrap gap-5')

        medium_field = self['medium']
        medium_label = label(medium_field.label, _for=medium_field.id_for_label, cls='input input-bordered flex items-center gap-2 flex-1')
        medium_label.add(raw(str(medium_field)))
        palette.add(medium_label)

        dubious_writer_field = self['dubious_writer']
        dubious_writer_label = label(_for=dubious_writer_field.id_for_label, cls='label cursor-pointer flex items-center gap-5')
        dubious_writer_label.add(span(dubious_writer_field.label, cls='label-text'))
        dubious_writer_label.add(raw(str(dubious_writer_field)))
        palette.add(dubious_writer_label)

        form.add(palette)
        form.add(raw(str(self['manifestation_title'])))

        return mark_safe(str(form))
