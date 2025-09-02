from .base import *
from dmrism.models.manifestation import *
from dominate.tags import div, label, span
from dominate.util import raw
from django.forms import ModelForm, TextInput, Select, HiddenInput, CheckboxInput, Textarea, DateTimeField, SelectDateWidget, CharField
from django.forms.models import inlineformset_factory
from django.utils.safestring import mark_safe
from dmad_on_django.models import Period


class ManifestationForm(ModelForm):
    class Meta:
        model = Manifestation
        fields = ['rism_id']
        widgets = {
                'rism_id': TextInput( attrs = {
                        'class': 'grow h-full'
                    })
            }

    def as_daisy(self):
        form = div()
        rism_id_label = label(self['rism_id'].label, _for=self['rism_id'].id_for_label, cls='input input-bordered flex items-center gap-2 my-5')
        rism_id_label.add(raw(str(self['rism_id'])))
        form.add(rism_id_label)

        return mark_safe(str(form))


class ManifestationDedicationForm(ModelForm, SimpleFormMixin):
    class Meta:
        model = Manifestation
        fields = ['dedication']
        widgets = {
                'dedication': Textarea( attrs = {
                        'class': SimpleFormMixin.text_area_classes
                    })
            }


class ManifestationTitleForm(ModelForm):
    class Meta(TitleForm.Meta):
        model = ManifestationTitle
        fields = ['title', 'title_type', 'status', 'manifestation']
        widgets = {
                'title': TextInput( attrs = {
                        'class': 'grow w-full'
                    }),
                'title_type': Select( attrs = {
                        'class': 'autocomplete-select select select-bordered w-full'
                    }),
                'status': Select( attrs = {
                        'class': 'autocomplete-select select select-bordered w-full'
                    }),
                'manifestation': HiddenInput()
                }

    def as_daisy(self):
        class_name = self.Meta.model.__name__.lower().replace('title', '')
        form = div(cls='mb-10')

        #if self.instance.pk:
           #form.add(raw(str(self['id'])))
        #form.add(raw(str(self[class_name])))

        title_field = self['title']
        type_field = self['title_type']
        status_field = self['status']
        medium_field = self['medium']

        title_field_label = label(title_field.label, cls='input input-bordered flex-1 flex items-center gap-2')
        title_field_label.add(raw(str(title_field)))

        type_container = div(cls='flex-1')
        type_container.add(raw(str(type_field)))

        status_container = div(cls='flex-1')
        status_container.add(raw(str(status_field)))

        medium_field_label = label(medium_field.label, cls='input input-bordered flex-1 flex items-center gap-2')
        medium_field_label.add(raw(str(medium_field)))

        palette1 = div(cls='flex flex-rows w-full gap-10 my-5')
        palette1.add(title_field_label)
        palette1.add(type_container)

        palette2 = div(cls='flex flex-rows w-full gap-10 my-5')
        palette2.add(medium_field_label)
        palette2.add(status_container)

        form.add(palette1)
        form.add(palette2)
        form.add(raw(str(self['manifestation'])))

        return mark_safe(str(form))


class ManifestationCommentForm(CommentForm):
    class Meta:
        model = Manifestation
        fields = CommentForm.Meta.fields
        widgets = CommentForm.Meta.widgets


class ManifestationBibForm(BaseBibForm):
    class Meta(BaseBibForm.Meta):
        model = ManifestationBib
        fields = BaseBibForm.Meta.fields + [ 'manifestation' ]
        widgets = dict(BaseBibForm.Meta.widgets, **{ 'manifestation': HiddenInput() })


class ManifestationContributorForm(ContributorForm):
    class Meta(ContributorForm.Meta):
        model = ManifestationContributor
        fields = ContributorForm.Meta.fields + [ 'manifestation' ]
        widgets = dict(ContributorForm.Meta.widgets, **{ 'manifestation': HiddenInput() })


class ManifestationHistoryForm(ModelForm, SimpleFormMixin):
    not_before = DateTimeField(widget = SelectDateWidget( attrs = {'class':'select select-bordered'}))
    not_after = DateTimeField(widget = SelectDateWidget( attrs = {'class':'select select-bordered'}))
    display = CharField(required=False, widget = TextInput( attrs = { 'class': 'grow'}))

    class Meta:
        model = Manifestation
        fields = ['history', 'id', 'date_diplomatic']
        widgets = {
                'history': Textarea( attrs = {
                        'class': SimpleFormMixin.text_area_classes
                    }),
                'date_diplomatic': Textarea( attrs = {
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
        #form.add(history_wrap)

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
                'function'
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
            }

    def as_daisy(self):
        form = div(cls='mb-10')

        manifestation_form_field = self['manifestation_form']
        edition_type_field = self['edition_type']
        function_field = self['function']

        manifestation_form_label = label(manifestation_form_field.label, cls='flex-1')
        manifestation_form_label.add(raw(str(manifestation_form_field)))

        edition_type_label = label(edition_type_field.label, cls='flex-1')
        edition_type_label.add(raw(str(edition_type_field)))

        function_type_label = label(function_field.label, cls='flex-1')
        function_type_label.add(raw(str(function_field)))

        palette = div(cls='flex flex-rows w-full gap-10 my-5')
        palette.add(manifestation_form_label)
        palette.add(edition_type_label)
        palette.add(function_type_label)

        form.add(palette)

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


class ManifestationPrintForm(ModelForm, SimpleFormMixin):
    class Meta:
        model = Manifestation
        fields = ['plate_number']
        widgets = {
                'plate_number': TextInput( attrs = {
                        'class': 'grow'
                    })
            }

    def as_daisy(self):
        form = div(cls='mb-10')

        plate_number_field = self['plate_number']

        plate_number_label = label(plate_number_field.label, cls='input input-bordered flex items-center gap-2')
        plate_number_label.add(raw(str(plate_number_field)))

        form.add(plate_number_label)

        return mark_safe(str(form))


class ManifestationManuscriptForm(ModelForm, SimpleFormMixin):
    class Meta:
        model = Manifestation
        fields = ['paper', 'extent', 'measure']
        widgets = {
                'paper': Textarea( attrs = {
                        'class': SimpleFormMixin.text_area_classes
                    }),
                'extent': Textarea( attrs = {
                        'class': SimpleFormMixin.text_area_classes
                    }),
                'measure': Textarea( attrs = {
                        'class': SimpleFormMixin.text_area_classes
                    })
            }


class ManifestationHandwritingForm(ModelForm, SimpleFormMixin):
    class Meta:
        model = ManifestationHandwriting
        fields = ['medium']
        widgets = {
                'medium': TextInput( attrs = {
                        'class': 'grow'
                    }),
            }

    def as_daisy(self):
        form = div()
        medium_field = self['medium']

        medium_label = label(medium_field.label, _for=medium_field.id_for_label, cls='input input-bordered flex items-center gap-2')
        medium_label.add(raw(str(medium_field)))
        form.add(medium_label)

        return mark_safe(str(form))


ManifestationHandwritingFormSet = inlineformset_factory(
        Manifestation,
        ManifestationHandwriting,
        form = ManifestationHandwritingForm,
        extra = 0,
        can_delete = True
    )
