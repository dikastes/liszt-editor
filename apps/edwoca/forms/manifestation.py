from .base import *
from ..models.manifestation import *
from dominate.tags import div, label, span
from dominate.util import raw
from django.forms import ModelForm, TextInput, Select, HiddenInput, CheckboxInput, Textarea, DateTimeField, SelectDateWidget
from django.forms.models import inlineformset_factory
from django.utils.safestring import mark_safe
from dmad_on_django.models import Period


class ManifestationForm(ModelForm):
    class Meta:
        model = Manifestation
        fields = [
                'rism_id',
                'plate_number'
            ]
        widgets = {
                'rism_id': TextInput( attrs = {
                        'class': 'grow'
                    }),
                'plate_number': TextInput( attrs = {
                        'class': 'grow'
                    })
            }

    def as_daisy(self):
        form = div()
        for field in self.visible_fields():
            field_label = label(field.label, _for=field.id_for_label, cls='input input-bordered flex items-center gap-2 my-5')
            field_label.add(raw(str(field)))
            form.add(field_label)

        return mark_safe(str(form))


class ManifestationTitleForm(TitleForm):
    class Meta(TitleForm.Meta):
        model = ManifestationTitle
        fields = TitleForm.Meta.fields + ['manifestation']
        widgets = dict(TitleForm.Meta.widgets, **{ 'manifestation': HiddenInput() })


class ManifestationCommentForm(CommentForm):
    class Meta:
        model = Manifestation
        fields = CommentForm.Meta.fields
        widgets = CommentForm.Meta.widgets


class ManifestationBibForm(ModelForm):
    class Meta:
        model = ManifestationBib
        fields = [ 'bib', 'id', 'manifestation' ]
        widgets = {
                'bib': Select( attrs = {
                        'class': 'autocomplete-select select select-bordered w-full'
                    }),
                'id': HiddenInput(),
                'manifestation': HiddenInput(),
                'DELETE': CheckboxInput( attrs = {
                        'class': 'flex-0'
                    })
            }

    def as_daisy(self):
        form = div(cls='mb-10')

        if self.instance.pk:
           form.add(raw(str(self['id'])))
        form.add(raw(str(self['manifestation'])))

        bib_field = self['bib']

        bib_container = div(cls='flex-1')
        bib_container.add(raw(str(bib_field)))

        palette = div(cls='flex flex-rows w-full gap-10 my-5')
        palette.add(bib_container)

        if 'DELETE' in self.fields:
            del_field = self['DELETE']
            del_field_label = label(del_field.label, cls='input input-bordered flex flex-0 items-center gap-2')
            del_field_label.add(raw(str(del_field)))
            palette.add(del_field_label)

        form.add(palette)

        return mark_safe(str(form))


class ManifestationContributorForm(ContributorForm):
    class Meta:
        model = ManifestationContributor
        fields = ContributorForm.Meta.fields + [ 'manifestation' ]
        widgets = dict(ContributorForm.Meta.widgets, **{ 'manifestation': HiddenInput() })


class ManifestationHistoryForm(ModelForm, SimpleFormMixin):
    not_before = DateTimeField(widget = SelectDateWidget( attrs = {'class':'select select-bordered'}))
    not_after = DateTimeField(widget = SelectDateWidget( attrs = {'class':'select select-bordered'}))
    display = DateTimeField(widget = TextInput( attrs = { 'class': 'grow'}))

    class Meta:
        model = Manifestation
        fields = ['history', 'id']
        widgets = {
                'history': Textarea( attrs = {
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
        history_field = self['history']

        not_before_container = label(cls='form-control')
        not_before_label = div(not_before_field.label, cls='label-text')
        not_before_selects = div(cls='flex')
        not_before_selects.add(raw(str(not_before_field)))
        not_before_container.add(not_before_label)
        not_before_container.add(not_before_selects)

        not_after_container = label(cls='form-control')
        not_after_label = div(not_after_field.label, cls='label-text')
        not_after_selects = div(cls='flex')
        not_after_selects.add(raw(str(not_after_field)))
        not_after_container.add(not_after_label)
        not_after_container.add(not_after_selects)

        display_container = label(display_field.label, _for = display_field.id_for_label, cls='input input-bordered flex items-center gap-2 my-5')
        display_container.add(raw(str(display_field)))

        history_wrap = label(cls='form-control')
        history_label = div(cls='label')
        history_span = span(history_field.label, cls='label-text')
        history_label.add(history_span)
        history_wrap.add(history_label)
        history_wrap.add(raw(str(history_field)))

        period_palette = div(cls='flex flex-rows w-full gap-10 my-5')
        period_palette.add(not_before_container)
        period_palette.add(not_after_container)
        #period_palette.add(display_container)

        form.add(period_palette)
        form.add(display_container)
        form.add(history_wrap)

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
                'manifestation_type',
                'edition_type',
                'state'
            ]
        widgets = {
                'manifestation_type': Select( attrs = {
                        'class': 'select w-full select-bordered'
                    }),
                'edition_type': Select( attrs = {
                        'class': 'select w-full select-bordered'
                    }),
                'state': Select( attrs = {
                        'class': 'select w-full select-bordered'
                    }),
            }

    def as_daisy(self):
        form = div(cls='mb-10')

        manifestation_type_field = self['manifestation_type']
        edition_type_field = self['edition_type']
        state_field = self['state']

        manifestation_type_label = label(manifestation_type_field.label, cls='flex-1')
        manifestation_type_label.add(raw(str(manifestation_type_field)))

        edition_type_label = label(edition_type_field.label, cls='flex-1')
        edition_type_label.add(raw(str(edition_type_field)))

        state_type_label = label(state_field.label, cls='flex-1')
        state_type_label.add(raw(str(state_field)))

        palette = div(cls='flex flex-rows w-full gap-10 my-5')
        palette.add(manifestation_type_label)
        palette.add(edition_type_label)
        palette.add(state_type_label)

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


ManifestationBibFormSet = inlineformset_factory(
        Manifestation,
        ManifestationBib,
        form = ManifestationBibForm,
        extra = 1,
        max_num = 100,
        can_delete = True
    )


ManifestationContributorFormSet = inlineformset_factory(
        Manifestation,
        ManifestationContributor,
        form = ManifestationContributorForm,
        extra = 1,
        max_num = 100,
        can_delete = True
    )
