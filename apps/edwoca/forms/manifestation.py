from .base import *
from bib.models import ZotItem
from django import forms
from django.conf import settings
from django.forms import ModelForm, TextInput, Select, HiddenInput, CheckboxInput, Textarea, DateTimeField, SelectDateWidget, CharField
from django.forms.models import inlineformset_factory
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from dmad_on_django.models import Period, Corporation
from dmrism.models.item import Item, PersonProvenanceStation, CorporationProvenanceStation, Library
from dmrism.models.manifestation import Manifestation, ManifestationTitle, ManifestationBib, RelatedManifestation, ManifestationTitleHandwriting
from dominate.tags import div, label, span, _input
from dominate.util import raw
from liszt_util.forms.forms import GenericAsDaisyMixin
from liszt_util.forms.layouts import Layouts


class ManifestationForm(GenericAsDaisyMixin, ModelForm):
    layout = Layouts.LABEL_OUTSIDE

    class Meta:
        model = Manifestation
        fields = ['rism_id', 'private_head_comment']
        widgets = {
                'rism_id': TextInput( attrs = {
                        'class': SimpleFormMixin.text_input_classes,
                        'form': 'form'
                    }),
                'private_head_comment': Textarea( attrs = {
                        'class': SimpleFormMixin.text_area_classes,
                        'form': 'form'
                    }),
            }


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
            'title': Textarea(attrs={'form': 'form', 'class': 'textarea border-black bg-white textarea-bordered h-64'}),
            'title_type': Select(attrs={'form': 'form', 'class': 'select select-bordered border-black bg-white w-full'}),
            'status': Select(attrs={'form': 'form', 'class': 'select select-bordered border-black bg-white w-full'}),
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
                'class': SimpleFormMixin.select_classes
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

        not_before_container = label(cls='form-control flex-0')
        not_before_label = div(_('not before'), cls='label-text')
        not_before_selects = div(cls='flex')
        not_before_selects.add(raw(str(not_before_field)))
        not_before_container.add(not_before_label)
        not_before_container.add(not_before_selects)
        if not_before_field.errors:
            not_before_container.add(div(span(not_before_field.errors, cls='text-primary text-sm'), cls='label'))

        not_after_container = label(cls='form-control flex-0')
        not_after_label = div(_('not after'), cls='label-text')
        not_after_selects = div(cls='flex')
        not_after_selects.add(raw(str(not_after_field)))
        not_after_container.add(not_after_label)
        not_after_container.add(not_after_selects)
        if not_after_field.errors:
            not_after_container.add(div(span(not_after_field.errors, cls='text-primary text-sm'), cls='label'))

        calculate_input = _input(type='submit', cls='btn btn-outline flex-0', value=_('calculate'), name='calculate-machine-readable-date')

        display_container = label(_('standardized date'), _for = display_field.id_for_label, cls=SimpleFormMixin.text_label_classes)
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

        period_palette = div(cls='flex flex-rows w-full gap-10 my-5 items-end')
        period_palette.add(not_before_container)
        period_palette.add(not_after_container)
        period_palette.add(div(cls='flex-1'))
        period_palette.add(calculate_input)

        form.add(display_container)
        form.add(period_palette)
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
                        'class': SimpleFormMixin.select_classes,
                    }),
                'edition_type': Select( attrs = {
                        'class': SimpleFormMixin.select_classes,
                    }),
                'function': Select( attrs = {
                        'class': SimpleFormMixin.select_classes,
                    }),
                'source_type': Select( attrs = {
                        'class': SimpleFormMixin.select_classes,
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
        if self.instance.is_singleton:
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
    kwargs = {
            'years': range(settings.EDWOCA_FIXED_DATES['birth']['year'], 1900),
            'attrs': {
                'class': 'select select-bordered'
            }
        }
    read_only_fields = ['publisher']
    temporary_title = forms.CharField(label=_('Temporary'), max_length=255, required=False, widget=TextInput(attrs={'class': 'input input-bordered w-full'}))
    plate_number = forms.CharField(label=_('plate number'), max_length=50, required=False, widget=TextInput(attrs={'class': 'input input-bordered w-full'}))
    source_type = forms.ChoiceField(label=_('source type'), choices=Manifestation.SourceType.choices, widget=forms.Select(attrs={'class': 'select select-bordered w-full'}))
    not_before = DateTimeField(widget = SelectDateWidget(**kwargs), required = False)
    not_after = DateTimeField(widget = SelectDateWidget(**kwargs), required = False)
    display = CharField(required=False, widget = TextInput( attrs = { 'class': 'grow'}))
    publisher = forms.ModelChoiceField(queryset=Corporation.objects.all(), label=_('publisher'), empty_label=_('choose publisher'), widget=forms.Select(attrs={'class': 'select select-bordered w-full'}))

    def __init__(self, *args, **kwargs):
        self.publisher_instance = kwargs.pop('publisher', None)
        super().__init__(*args, **kwargs)
        if 'initial' in kwargs and 'publisher' in kwargs['initial'] and \
            (publisher_instance := kwargs['initial']['publisher']):
            self.initial['publisher'] = publisher_instance
            self.fields['publisher'].queryset = Corporation.objects.filter(pk=publisher_instance.pk)
            self.fields['publisher'].widget.attrs['disabled'] = True

    def clean(self):
        cleaned_data = super().clean()
        if self.publisher_instance:
            cleaned_data['publisher'] = self.publisher_instance
        return cleaned_data

    def as_daisy(self):
        form = div(cls='mb-10')

        # Temporary Title
        temporary_title_field = self['temporary_title']
        temporary_title_container = label(cls='form-control w-full')
        temporary_title_label = div(cls='label')
        temporary_title_label.add(span(temporary_title_field.label, cls='label-text'))
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


class SingletonCreateForm(GenericAsDaisyMixin, forms.Form):
    layout = Layouts.LABEL_OUTSIDE
    temporary_title = forms.CharField(label=_('Temporary'), max_length=255, required=False)
    source_type = forms.ChoiceField(label=_('source type'), choices=Manifestation.SourceType.choices)
    library = forms.ModelChoiceField(queryset=Library.objects.all(), label=_('library'), empty_label=_('choose library'))
    signature = forms.CharField(label='Signatur', max_length=255)

    def as_daisy(self):
        root = div(cls="flex flex-col gap-5")

        palette1 = div(cls='flex flex-rows w-full gap-10 my-5')
        palette1.add(self._render_field('temporary_title'))
        palette1.add(self._render_field('source_type'))
        root.add(palette1)

        palette2 = div(cls='flex flex-rows w-full gap-10 my-5')
        palette2.add(self._render_field('library'))
        palette2.add(self._render_field('signature'))
        root.add(palette2)

        return mark_safe(root.render())

    def _render_field(self, field_name):
        field = self[field_name]
        widget = field.field.widget
        wrap = label(cls="form-control w-full")
        top = div(cls="label")
        top.add(span((field.label or field.name), cls="label-text"))
        if field.help_text:
            top.add(span(field.help_text, cls="label-text-alt"))
        wrap.add(top)

        cls = "input input-bordered w-full"
        if isinstance(widget, forms.Select):
            cls = "select select-bordered w-full"

        wrap.add(raw(field.as_widget(attrs={"class" : cls})))
        return wrap


class ManifestationPrintForm(ModelForm):
    class Meta:
        model = Manifestation
        fields = ['print_type']
        widgets = {
            'print_type': Select(attrs={'class': 'select select-bordered w-full'}),
        }


class ManifestationTitleHandwritingForm(HandwritingForm):
    class Meta(HandwritingForm.Meta):
        model = ManifestationTitleHandwriting
