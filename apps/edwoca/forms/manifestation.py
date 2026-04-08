import re
from haystack.query import SQ
from .base import *
from liszt_util.forms import FramedSearchForm
from bib.models import ZotItem
from django import forms
from django.conf import settings
from django.forms import ModelForm, TextInput, Select, HiddenInput, CheckboxInput, Textarea, DateTimeField, SelectDateWidget, CharField, ChoiceField, BooleanField
from django.forms.models import inlineformset_factory
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from dmad_on_django.models import Period, Corporation
from dmad_on_django.models.base import DocumentationStatus
from dmrism.models.item import Item, Library
from dmrism.models.manifestation import Manifestation, ManifestationTitle, ManifestationBib, RelatedManifestation, ManifestationTitleHandwriting, ManifestationPlace
from dominate.tags import div, label, span, _input, h1, h2, h3
from dominate.util import raw
from liszt_util.forms.forms import GenericAsDaisyMixin
from liszt_util.forms.layouts import Layouts


class ManifestationForm(GenericAsDaisyMixin, ModelForm):
    layout = Layouts.LABEL_OUTSIDE

    class Meta:
        model = Manifestation
        fields = ['rism_id', 'private_head_comment', 'working_title']
        widgets = {
                'rism_id': TextInput( attrs = {
                        'class': SimpleFormMixin.text_input_classes,
                        'form': 'form'
                    }),
                'working_title': Textarea( attrs = {
                        'class': SimpleFormMixin.text_area_classes,
                        'form': 'form'
                    }),
                'private_head_comment': Textarea( attrs = {
                        'class': SimpleFormMixin.text_area_classes,
                        'form': 'form'
                    }),
            }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        wt_field = self.fields['working_title']
        wt_field.label = f'{wt_field.label}*'

class ManifestationTitleDedicationForm(GenericAsDaisyMixin, ModelForm):
    layout = Layouts.LABEL_OUTSIDE

    class Meta:
        model = Manifestation
        fields = [
                'source_title',
                'private_dedication_comment',
                'private_title_comment'
            ]
        widgets = {
                'source_title': Textarea( attrs = {
                        'class': SimpleFormMixin.text_area_classes,
                        'form': 'form'
                    }),
                'private_dedication_comment': Textarea( attrs = {
                        'class': SimpleFormMixin.text_area_classes,
                        'form': 'form'
                    }),
                'private_title_comment': Textarea( attrs = {
                        'class': SimpleFormMixin.text_area_classes,
                        'form': 'form'
                    })
            }

    def source_title_as_daisy(self):
        source_title_field = self['source_title']

        form_control = div(cls=SimpleFormMixin.form_control_classes)
        with form_control:
            with div(cls=SimpleFormMixin.label_classes):
                span(source_title_field.label + '*', cls=SimpleFormMixin.label_text_classes)
            raw(str(source_title_field))

        return mark_safe(str(form_control))

    def dedication_comment_as_daisy(self):
        dedication_comment_field = self['private_dedication_comment']

        form_control = div(cls=SimpleFormMixin.form_control_classes)
        with form_control:
            with div(cls=SimpleFormMixin.label_classes):
                span(dedication_comment_field.label, cls=SimpleFormMixin.label_text_classes)
            raw(str(dedication_comment_field))

        return mark_safe(str(form_control))

    def title_comment_as_daisy(self):
        title_comment_field = self['private_title_comment']

        form_control = div(cls=SimpleFormMixin.form_control_classes)
        with form_control:
            with div(cls=SimpleFormMixin.label_classes):
                span(title_comment_field.label, cls=SimpleFormMixin.label_text_classes)
            raw(str(title_comment_field))

        return mark_safe(str(form_control))


class ManifestationTitleForm(ModelForm):
    class Meta:
        model = ManifestationTitle
        fields = ['title', 'title_type', 'manifestation']
        widgets = {
            'title': Textarea(attrs={'form': 'form', 'class': 'textarea border-black bg-white textarea-bordered h-64'}),
            'title_type': Select(attrs={'form': 'form', 'class': 'select select-bordered border-black bg-white w-full'}),
            'manifestation': HiddenInput(attrs={'form': 'form'}),
        }

    def as_daisy(self):
        form = div(cls='flex flex-col gap-5')

        # Title field (textarea)
        title_label = label(self['title'].label, _for=self['title'].id_for_label, cls='form-control w-full')
        title_label.add(raw(str(self['title'])))
        form.add(title_label)

        # Remaining properties on a palette with flex-1
        palette = div(cls='flex flex-wrap gap-5')
        for field_name in ['title_type']:
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
        fields = CommentForm.Meta.fields + ['taken_information', 'first_editor', 'editing_history', 'needs_review']
        widgets = dict(CommentForm.Meta.widgets, **{
                'taken_information': Textarea( attrs = {
                        'class': SimpleFormMixin.text_area_classes
                    }),
                'first_editor': TextInput( attrs = {
                        'class': SimpleFormMixin.text_input_classes
                    }),
                'editing_history': Textarea( attrs = {
                        'class': SimpleFormMixin.text_area_classes
                    }),
                'needs_review': CheckboxInput( attrs = {
                        'class': 'toggle'
                    })
            })

    first_save = forms.DateTimeField(
            label=_('first save') + '*',
            required = False,
            disabled = True,
            widget = SelectDateWidget( attrs = { 'class': SimpleFormMixin.select_classes + ' disabled:!bg-white disabled:!border-black disabled:!text-black' })
        )
    last_save = forms.DateTimeField(
            label=_('last save'),
            required = False,
            disabled = True,
            widget = SelectDateWidget( attrs = { 'class': SimpleFormMixin.select_classes + ' disabled:!bg-white disabled:!border-black disabled:!text-black'})
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['first_save'].initial = self.instance.first_save
            self.fields['last_save'].initial = self.instance.last_save
        fe_field = self.fields['first_editor']
        fe_field.label = f'{fe_field.label}*'

    def as_daisy(self):
        form = div()

        private_comment_field = self['private_comment']
        public_comment_field = self['public_comment']
        first_editor_field = self['first_editor']
        taken_information_field = self['taken_information']
        first_save_field = self['first_save']
        last_save_field = self['last_save']
        editing_history_field = self['editing_history']
        needs_review_field = self['needs_review']

        with form:
            with label(cls=SimpleFormMixin.form_control_classes):
                with div(cls=SimpleFormMixin.label_classes):
                    span(private_comment_field.label, cls=SimpleFormMixin.label_text_classes)
                raw(str(private_comment_field))
            with label(cls=SimpleFormMixin.form_control_classes):
                with div(cls=SimpleFormMixin.label_classes):
                    span(public_comment_field.label, cls=SimpleFormMixin.label_text_classes)
                raw(str(public_comment_field))
            with label(cls=SimpleFormMixin.form_control_classes):
                with div(cls=SimpleFormMixin.label_classes):
                    span(taken_information_field.label, cls=SimpleFormMixin.label_text_classes)
                raw(str(taken_information_field))
            h2(_('editing history'), cls='my-5')
            h3(_('initial recording'), cls='my-5')
            with label(cls=SimpleFormMixin.form_control_classes):
                with div(cls=SimpleFormMixin.label_classes):
                    span(first_editor_field.label, cls=SimpleFormMixin.label_text_classes)
                raw(str(first_editor_field))
            with label(cls=SimpleFormMixin.form_control_classes):
                with div(cls=SimpleFormMixin.label_classes):
                    span(first_save_field.label, cls=SimpleFormMixin.label_text_classes)
                with div(cls='flex'):
                    with div(cls='flex'):
                        raw(str(first_save_field))
                    div(cls='flex-1')
            h3(_('further recording'), cls='my-5')
            with label(cls=SimpleFormMixin.form_control_classes):
                with div(cls=SimpleFormMixin.label_classes):
                    span(editing_history_field.label, cls=SimpleFormMixin.label_text_classes)
                raw(str(editing_history_field))
            with div(cls=SimpleFormMixin.palette_classes + ' items-end'):
                with label(cls=SimpleFormMixin.palette_form_control_classes):
                    with div(cls=SimpleFormMixin.label_classes):
                        span(last_save_field.label, cls=SimpleFormMixin.label_text_classes)
                    with div(cls='flex'):
                        with div(cls='flex'):
                            raw(str(last_save_field))
                        div(cls='flex-1')
                div(cls='flex-1')
                with label(cls=SimpleFormMixin.toggle_label_classes + ' flex-0'):
                    span(needs_review_field.label, cls=SimpleFormMixin.label_text_classes)
                    raw(str(needs_review_field))

        return mark_safe(str(form))


class ManifestationBibForm(BaseBibForm):
    class Meta:
        model = ManifestationBib
        fields = BaseBibForm.Meta.fields
        widgets = BaseBibForm.Meta.widgets


class ManifestationHistoryForm(DateFormMixin, ModelForm, SimpleFormMixin):
    kwargs = {
            'years': range(settings.EDWOCA_FIXED_DATES['birth']['year'], 1900),
            'attrs': {
                'class': SimpleFormMixin.select_classes
            }
        }
    not_before = DateTimeField(widget = SelectDateWidget(**kwargs), required = False)
    not_after = DateTimeField(widget = SelectDateWidget(**kwargs), required = False)
    display = CharField(required=False, widget = TextInput( attrs = { 'class': SimpleFormMixin.text_input_classes }))
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
        model = Manifestation
        fields = [
            'history',
            'id',
            'date_diplomatic',
            'private_history_comment',
            'not_before',
            'not_after',
            'display',
            'inferred',
            'assumed',
            #'place_inferred',
            #'place_assumed'
        ]
        widgets = {
                'history': Textarea( attrs = {

                        'class': SimpleFormMixin.text_area_classes
                    }),
                'date_diplomatic': Textarea( attrs = {
                        'class': SimpleFormMixin.text_area_classes
                    }),
                'private_history_comment': Textarea( attrs = {
                        'class': SimpleFormMixin.text_area_classes,
                        'form': 'form'
                    }),
                #'place_inferred': CheckboxInput( attrs = {
                        #'class': SimpleFormMixin.toggle_classes,
                        #'form': 'form'
                    #}),
                #'place_assumed': CheckboxInput( attrs = {
                        #'class': SimpleFormMixin.toggle_classes,
                        #'form': 'form'
                    #})
            }

    def as_daisy(self):
        form = div(cls='mb-10')
        date_div = self.get_date_div()

        date_diplomatic_field = self['date_diplomatic']
        date_diplomatic_wrap = label(cls='form-control')
        date_diplomatic_label = div(cls='label')
        date_diplomatic_span = span(date_diplomatic_field.label, cls='label-text')
        date_diplomatic_label.add(date_diplomatic_span)
        date_diplomatic_wrap.add(date_diplomatic_label)
        date_diplomatic_wrap.add(raw(str(date_diplomatic_field)))

        form.add(date_diplomatic_wrap)
        form.add(date_div)

        return mark_safe(str(form))

    def comment_as_daisy(self):
        form = div(cls='mb-10')

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
                'source_type',
                'album_page',
                'performance_material',
                'authorized_edition',
                'first_edition',
                'part',
                'further_edition',
                'correction_sheet',
                'proof',
                'stitch_template',
                'dedication_item',
                'choir_score',
                'piano_reduction',
                'particell',
                'score',
                'is_text'
            ]
        widgets = {
                'manifestation_form': Select( attrs = {
                        'class': SimpleFormMixin.select_classes,
                    }),
                'source_type': Select( attrs = {
                        'class': SimpleFormMixin.select_classes,
                    }),
                'album_page': CheckboxInput( attrs = {
                        'class': 'toggle'
                    }),
                'performance_material': CheckboxInput( attrs = {
                        'class': 'toggle'
                    }),
                'authorized_edition': CheckboxInput( attrs = {
                        'class': 'toggle'
                    }),
                'first_edition': CheckboxInput( attrs = {
                        'class': 'toggle'
                    }),
                'part': CheckboxInput( attrs = {
                        'class': 'toggle'
                    }),
                'further_edition': CheckboxInput( attrs = {
                        'class': 'toggle'
                    }),
                'proof': CheckboxInput( attrs = {
                        'class': 'toggle'
                    }),
                'correction_sheet': CheckboxInput( attrs = {
                        'class': 'toggle'
                    }),
                'stitch_template': CheckboxInput( attrs = {
                        'class': 'toggle'
                    }),
                'dedication_item': CheckboxInput( attrs = {
                        'class': 'toggle'
                    }),
                'choir_score': CheckboxInput( attrs = {
                        'class': 'toggle'
                    }),
                'piano_reduction': CheckboxInput( attrs = {
                        'class': 'toggle'
                    }),
                'particell': CheckboxInput( attrs = {
                        'class': 'toggle'
                    }),
                'score': CheckboxInput( attrs = {
                        'class': 'toggle'
                    }),
                'is_text': CheckboxInput( attrs = {
                        'class': 'toggle'
                    }),
            }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.is_singleton:
            self.fields['source_type'].choices = [
                    (Manifestation.SourceType.TRANSCRIPT.value, Manifestation.SourceType.TRANSCRIPT.label),
                    (Manifestation.SourceType.CORRECTED_TRANSCRIPT.value, Manifestation.SourceType.CORRECTED_TRANSCRIPT.label),
                    (Manifestation.SourceType.AUTOGRAPH.value, Manifestation.SourceType.AUTOGRAPH.label),
                    (Manifestation.SourceType.QUESTIONABLE_AUTOGRAPH.value, Manifestation.SourceType.QUESTIONABLE_AUTOGRAPH.label)
                ]
        else:
            self.fields['source_type'].choices = [
                    (Manifestation.SourceType.CORRECTED_PRINT.value, Manifestation.SourceType.CORRECTED_PRINT.label)
                ]

        st_field = self.fields['source_type']
        st_field.label = f'{st_field.label}*'

    def as_daisy(self):
        form = div(cls='mb-10')

        source_type_field = self['source_type']
        manifestation_form_field = self['manifestation_form']

        # common source functions
        album_page_field = self['album_page']
        performance_material_field = self['performance_material']

        # print source functions
        authorized_edition_field = self['authorized_edition']
        first_edition_field = self['first_edition']
        proof_field = self['proof']
        further_edition_field = self['further_edition']

        # manuscript source functions
        correction_sheet_field = self['correction_sheet']
        stitch_template_field = self['stitch_template']
        dedication_item_field = self['dedication_item']
        part_field = self['part']

        # editions types
        choir_score_field = self['choir_score']
        piano_reduction_field = self['piano_reduction']
        particell_field = self['particell']
        score_field = self['score']
        text_field = self['is_text']

        instance = self.instance

        with form:
            # upper palette with source type and manifestaion form
            with label(cls=SimpleFormMixin.form_control_classes):
                with div(cls=SimpleFormMixin.label_classes):
                    span(source_type_field.label, cls=SimpleFormMixin.label_text_classes)
                raw(str(source_type_field))
            with label(cls=SimpleFormMixin.form_control_classes):
                with div(cls=SimpleFormMixin.label_classes):
                    span(manifestation_form_field.label, cls=SimpleFormMixin.label_text_classes)
                raw(str(manifestation_form_field))
            # lower palette with toggles
            h1(_('function'), cls='text-lg my-5')
            with label(cls=SimpleFormMixin.toggle_inverted_classes):
                raw(str(album_page_field))
                span(album_page_field.label, cls=SimpleFormMixin.label_text_classes)
            with label(cls=SimpleFormMixin.toggle_inverted_classes):
                raw(str(performance_material_field))
                span(performance_material_field.label, cls=SimpleFormMixin.label_text_classes)
            if instance.is_singleton:
                with label(cls=SimpleFormMixin.toggle_inverted_classes):
                    raw(str(correction_sheet_field))
                    span(correction_sheet_field.label, cls=SimpleFormMixin.label_text_classes)
                with label(cls=SimpleFormMixin.toggle_inverted_classes):
                    raw(str(stitch_template_field))
                    span(stitch_template_field.label, cls=SimpleFormMixin.label_text_classes)
                with label(cls=SimpleFormMixin.toggle_inverted_classes):
                    raw(str(dedication_item_field))
                    span(dedication_item_field.label, cls=SimpleFormMixin.label_text_classes)
            else:
                with label(cls=SimpleFormMixin.toggle_inverted_classes):
                    raw(str(authorized_edition_field))
                    span(authorized_edition_field.label, cls=SimpleFormMixin.label_text_classes)
                with label(cls=SimpleFormMixin.toggle_inverted_classes):
                    raw(str(first_edition_field))
                    span(first_edition_field.label, cls=SimpleFormMixin.label_text_classes)
                with label(cls=SimpleFormMixin.toggle_inverted_classes):
                    raw(str(proof_field))
                    span(proof_field.label, cls=SimpleFormMixin.label_text_classes)
                with label(cls=SimpleFormMixin.toggle_inverted_classes):
                    raw(str(further_edition_field))
                    span(further_edition_field.label, cls=SimpleFormMixin.label_text_classes)

            h1(_('edition type') + '*', cls='text-lg my-5')
            if not instance.is_text:
                with label(cls=SimpleFormMixin.toggle_inverted_classes):
                    raw(str(choir_score_field))
                    span(choir_score_field.label, cls=SimpleFormMixin.label_text_classes)
                with label(cls=SimpleFormMixin.toggle_inverted_classes):
                    raw(str(piano_reduction_field))
                    span(piano_reduction_field.label, cls=SimpleFormMixin.label_text_classes)
                with label(cls=SimpleFormMixin.toggle_inverted_classes):
                    raw(str(particell_field))
                    span(particell_field.label, cls=SimpleFormMixin.label_text_classes)
                with label(cls=SimpleFormMixin.toggle_inverted_classes):
                    raw(str(score_field))
                    span(score_field.label, cls=SimpleFormMixin.label_text_classes)
                with label(cls=SimpleFormMixin.toggle_inverted_classes):
                    raw(str(part_field))
                    span(part_field.label, cls=SimpleFormMixin.label_text_classes)
            if not (instance.choir_score or instance.piano_reduction or instance.particell or instance.score or instance.part):
                with label(cls=SimpleFormMixin.toggle_inverted_classes):
                    raw(str(text_field))
                    span(text_field.label, cls=SimpleFormMixin.label_text_classes)

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
    kwargs = {
            'years': range(settings.EDWOCA_FIXED_DATES['birth']['year'], 1900),
            'attrs': {
                'class': 'select select-bordered'
            }
        }
    read_only_fields = ['publisher']
    temporary_title = forms.CharField(label=_('Temporary'), max_length=255, required=False, widget=TextInput(attrs={'class': SimpleFormMixin.text_input_classes}))
    source_title = forms.CharField(label=_('source title'), max_length=255, required=False, widget=TextInput(attrs={'class': SimpleFormMixin.text_input_classes}))
    plate_number = forms.CharField(label=_('plate number'), max_length=50, required=False, widget=TextInput(attrs={'class': SimpleFormMixin.text_input_classes}))
    source_type = forms.ChoiceField(label=_('source type'), choices=Manifestation.SourceType.choices, widget=forms.Select(attrs={'class': SimpleFormMixin.select_classes}), required = False)
    not_before = DateTimeField(widget = SelectDateWidget(**kwargs), required = False)
    not_after = DateTimeField(widget = SelectDateWidget(**kwargs), required = False)
    display = CharField(required=False, widget = TextInput( attrs = { 'class': 'grow'}))
    publisher = forms.ModelChoiceField(queryset=Corporation.objects.all(), label=_('publisher'), empty_label=_('choose publisher'), widget=forms.Select(attrs={'class': 'select select-bordered w-full'}))

    def __init__(self, *args, **kwargs):
        self.is_collection = kwargs.pop('is_collection', False)
        self.publisher_instance = kwargs.pop('publisher', None)
        #if self.publisher_instance:
            #self.initial['publisher'] = self.publisher_instance
            #self.fields['publisher'].queryset = Corporation.objects.filter(pk=self.publisher_instance.pk)
            #self.fields['publisher'].widget.attrs['disabled'] = True
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        if self.publisher_instance:
            cleaned_data['publisher'] = self.publisher_instance
        return cleaned_data

    def as_daisy(self):
        form = div(cls='mb-10')

        # Temporary Title
        if self.is_collection:
            source_title_field = self['source_title']
            source_title_container = label(cls='form-control w-full')
            source_title_label = div(cls='label')
            source_title_label.add(span(source_title_field.label + '*', cls='label-text'))
            source_title_container.add(source_title_label)
            source_title_container.add(raw(str(source_title_field)))
            if source_title_field.errors:
                source_title_container.add(div(span(source_title_field.errors, cls='text-primary text-sm'), cls='label'))
            form.add(source_title_container)
        else:
            temporary_title_field = self['temporary_title']
            temporary_title_container = label(cls='form-control w-full')
            temporary_title_label = div(cls='label')
            temporary_title_label.add(span(temporary_title_field.label + '*', cls='label-text'))
            temporary_title_container.add(temporary_title_label)
            temporary_title_container.add(raw(str(temporary_title_field)))
            if temporary_title_field.errors:
                temporary_title_container.add(div(span(temporary_title_field.errors, cls='text-primary text-sm'), cls='label'))
            form.add(temporary_title_container)

        # Publisher
        publisher_field = self['publisher']
        publisher_container = label(cls='form-control w-full')
        publisher_label = div(cls='label')
        publisher_label.add(span(publisher_field.label, cls='label-text'))
        publisher_container.add(publisher_label)
        publisher_container.add(raw(str(publisher_field)))
        if publisher_field.errors:
            publisher_container.add(div(span(publisher_field.errors, cls='text-primary text-sm'), cls='label'))
        form.add(publisher_container)

        # Plate Number
        plate_number_field = self['plate_number']
        plate_number_container = label(cls='form-control w-full')
        plate_number_label = div(cls='label')
        plate_number_label.add(span(plate_number_field.label, cls='label-text'))
        plate_number_container.add(plate_number_label)
        plate_number_container.add(raw(str(plate_number_field)))
        if plate_number_field.errors:
            plate_number_container.add(div(span(plate_number_field.errors, cls='text-primary text-sm'), cls='label'))
        form.add(plate_number_container)

        # Source Type
        if not self.is_collection:
            source_type_field = self['source_type']
            source_type_container = label(cls='form-control w-full')
            source_type_label = div(cls='label')
            source_type_label.add(span(source_type_field.label, cls='label-text'))
            source_type_container.add(source_type_label)
            source_type_container.add(raw(str(source_type_field)))
            if source_type_field.errors:
                source_type_container.add(div(span(source_type_field.errors, cls='text-primary text-sm'), cls='label'))
            form.add(source_type_container)

        # Date Fields
        not_before_field = self['not_before']
        not_after_field = self['not_after']
        display_field = self['display']

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

        period_palette = div(cls='flex flex-rows w-full gap-10 my-5')
        period_palette.add(not_before_container)
        period_palette.add(not_after_container)
        form.add(period_palette)
        form.add(display_container)

        return mark_safe(str(form))


class SingletonCreateForm(forms.ModelForm):
    class Meta:
        model = Manifestation
        fields = [
                'working_title',
                'source_title',
                'source_type',
                'library',
                'signature'
            ]

    working_title = forms.CharField(
            label = _('working title') + '*',
            max_length = 255,
            required = False,
            widget = TextInput(attrs={'class': SimpleFormMixin.text_input_classes})
        )
    source_title = forms.CharField(
            label = _('source title') + '*',
            max_length = 255,
            required = False,
            widget = TextInput(attrs={'class': SimpleFormMixin.text_input_classes})
        )
    source_type = forms.ChoiceField(
            label = _('source type') + '*',
            choices = Manifestation.SourceType.choices[:-1],
            widget = Select(attrs={'class': SimpleFormMixin.select_classes}),
            required = False
        )
    library = forms.ModelChoiceField(
            queryset = Library.objects.all(),
            label = _('holding institution') + '*',
            empty_label = _('choose library'),
            widget = Select(attrs={'class': SimpleFormMixin.select_classes})
        )
    signature = forms.CharField(
            label = _('Signature'),
            max_length = 255,
            widget = TextInput(attrs={'class': SimpleFormMixin.text_input_classes}),
            required = False
        )

    def __init__(self, *args, **kwargs):
        self.is_collection = kwargs.pop('is_collection', False)
        super().__init__(*args, **kwargs)

    def as_daisy(self):
        root = div(cls="flex flex-col gap-5")
        source_title_field = self['source_title']
        working_title_field = self['working_title']
        source_type_field = self['source_type']
        library_field = self['library']
        signature_field = self['signature']

        with root:
            with div(cls='flex w-full gap-10 my-5'):
                with label(cls=SimpleFormMixin.palette_form_control_classes):
                    if self.is_collection:
                        with div(cls=SimpleFormMixin.label_classes):
                            span(source_title_field.label, cls=SimpleFormMixin.label_text_classes)
                        raw(str(source_title_field))
                    else:
                        with div(cls=SimpleFormMixin.label_classes):
                            span(working_title_field.label, cls=SimpleFormMixin.label_text_classes)
                        raw(str(working_title_field))
                if not self.is_collection:
                    with label(cls=SimpleFormMixin.palette_form_control_classes):
                        with div(cls=SimpleFormMixin.label_classes):
                            span(source_type_field.label, cls=SimpleFormMixin.label_text_classes)
                        raw(str(source_type_field))
            with div(cls='flex w-full gap-10 my-5'):
                with label(cls=SimpleFormMixin.palette_form_control_classes):
                    with div(cls=SimpleFormMixin.label_classes):
                        span(library_field.label, cls=SimpleFormMixin.label_text_classes)
                    raw(str(library_field))
                with label(cls=SimpleFormMixin.palette_form_control_classes):
                    with div(cls=SimpleFormMixin.label_classes):
                        span(signature_field.label, cls=SimpleFormMixin.label_text_classes)
                    raw(str(signature_field))

        return mark_safe(root.render())


class ManifestationPrintForm(DateFormMixin, ModelForm):
    kwargs = {
            'years': range(settings.EDWOCA_FIXED_DATES['birth']['year'], 1900),
            'attrs': {
                'class': SimpleFormMixin.select_classes,
                'form': 'form'
            },
        }
    not_before = DateTimeField(widget = SelectDateWidget(**kwargs), required = False)
    not_after = DateTimeField(widget = SelectDateWidget(**kwargs), required = False)
    display = CharField(required=False, widget = TextInput( attrs = { 'class': 'grow', 'form': 'form'}))
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
        model = Manifestation
        fields = [
                'plate_number',
                'private_print_comment',
                'print_type',
                'extent',
                'edition'
            ]
        widgets = {
            'plate_number': TextInput(
                    attrs={
                            'class': SimpleFormMixin.text_input_classes,
                            'form': 'form'
                        }
                ),
            'private_print_comment': Textarea(
                    attrs={
                            'class': SimpleFormMixin.text_area_classes,
                            'form': 'form'
                        }
                ),
            'print_type': Select(
                    attrs={
                            'class': SimpleFormMixin.select_classes,
                            'form': 'form'
                        }
                ),
            'extent': Textarea(
                    attrs={
                            'class': SimpleFormMixin.text_area_classes,
                            'form': 'form'
                        }
                ),
            'edition': Select(
                    attrs={
                            'class': SimpleFormMixin.select_classes,
                            'form': 'form'
                        }
                ),
        }

    def platenumber_as_daisy(self):
        form = div()
        plate_number_field = self['plate_number']

        with form:
            with label(cls='form-control w-full'):
                with div(cls='label'):
                    span(plate_number_field.label, cls='label-text')
                raw(str(plate_number_field))

        return mark_safe(str(form))


    def publication_characteristics_as_daisy(self):
        form = div()
        comment_field = self['private_print_comment']

        with form:
            with div(cls='my-10'):
                self.get_date_div()
            with label(cls='form-control w-full'):
                with div(cls='label'):
                    span(comment_field.label, cls='label-text')
                raw(str(comment_field))

        return mark_safe(str(form))

    def print_characteristics_as_daisy(self):
        form = div()
        type_field = self['print_type']
        extent_field = self['extent']
        edition_field = self['edition']

        with form:
            with div(cls='flex gap-5'):
                with label(cls='flex-1 form-control w-full'):
                    with div(cls='label'):
                        span(type_field.label, cls='label-text')
                    raw(str(type_field))
                with label(cls='flex-1 form-control w-full'):
                    with div(cls='label'):
                        span(edition_field.label, cls='label-text')
                    raw(str(edition_field))
            with label(cls='form-control w-full'):
                with div(cls='label'):
                    span(extent_field.label, cls='label-text')
                raw(str(extent_field))

        return mark_safe(str(form))

class ManifestationTitleHandwritingForm(HandwritingForm):
    class Meta(HandwritingForm.Meta):
        model = ManifestationTitleHandwriting


class ManifestationSearchForm(FramedSearchForm):
    def search(self):
        if not self.is_valid():
            return self.no_query_found()

        query = self.cleaned_data.get('q')

        if not query:
            return self.searchqueryset

        query_norm = re.sub(r'[^A-Za-z0-9]', '', query).lower()

        if query.isnumeric() and (int_q := int(query)) > 99:
            return self.searchqueryset.filter(signature_numbers = int_q)

        sqs = self.searchqueryset.filter(
                SQ(content = query) |
                SQ(signature_normalized = query_norm)
            )

        return sqs


class ManifestationPlaceForm(ModelForm, SimpleFormMixin):
    inferred = BooleanField(widget = CheckboxInput(attrs = { 'class': 'toggle', 'form': 'form'}), required = False)
    assumed = BooleanField(widget = CheckboxInput(attrs = { 'class': 'toggle', 'form': 'form'}), required = False)

    class Meta:
        model = ManifestationPlace
        fields = [
            'inferred',
            'assumed'
        ]
        widgets = {
                'inferred': CheckboxInput( attrs = {
                        'class': SimpleFormMixin.toggle_classes,
                        'form': 'form'
                    }),
                'assumed': CheckboxInput( attrs = {
                        'class': SimpleFormMixin.toggle_classes,
                        'form': 'form'
                    })
            }

    def as_daisy(self):
        palette = div(cls='flex gap-10 items-center')

        place_assumed_field = self['assumed']
        place_inferred_field = self['inferred']

        place_documentation_label = _('place as documented')
        if self.instance.assumed:
            if self.instance.inferred:
                place_documentation_label = _('place inferred assumed')
            else:
                place_documentation_label = _('place assumed')
        else:
            if self.instance.inferred:
                place_documentation_label = _('place inferred')

        with palette:
            div(cls='flex-1')
            div(place_documentation_label, cls='flex-0 mr-10')
            with div(cls=SimpleFormMixin.palette_form_control_classes):
                with label(cls=SimpleFormMixin.toggle_label_classes):
                    span(_(place_inferred_field.label.lower()), cls=SimpleFormMixin.label_text_classes)
                    raw(str(place_inferred_field))
            with div(cls=SimpleFormMixin.palette_form_control_classes):
                with label(cls=SimpleFormMixin.toggle_label_classes):
                    span(_(place_assumed_field.label.lower()), cls=SimpleFormMixin.label_text_classes)
                    raw(str(place_assumed_field))

        return mark_safe(str(palette))


class ManifestationTextTypeForm(ModelForm, SimpleFormMixin):
    class Meta:
        model = Manifestation
        fields = ['is_lyrics', 'is_program', 'is_explanation']
        widgets = {
                'is_lyrics': CheckboxInput( attrs = {
                        'class': 'toggle',
                        'form': 'form'
                    }),
                'is_program': CheckboxInput( attrs = {
                        'class': 'toggle',
                        'form': 'form'
                    }),
                'is_explanation': CheckboxInput( attrs = {
                        'class': 'toggle',
                        'form': 'form'
                    })
            }

    def as_daisy(self):
        lyrics_field = self['is_lyrics']
        program_field = self['is_program']
        explanation_field = self['is_explanation']

        form = div()

        with form:
            h3(_('text type'), cls='text-lg my-5')
            with label(cls=SimpleFormMixin.toggle_inverted_classes):
                raw(str(lyrics_field))
                span(lyrics_field.label, cls=SimpleFormMixin.label_text_classes)
            with label(cls=SimpleFormMixin.toggle_inverted_classes):
                raw(str(program_field))
                span(program_field.label, cls=SimpleFormMixin.label_text_classes)
            with label(cls=SimpleFormMixin.toggle_inverted_classes):
                raw(str(explanation_field))
                span(explanation_field.label, cls=SimpleFormMixin.label_text_classes)

        return mark_safe(str(form))
