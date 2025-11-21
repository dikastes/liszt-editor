from .base import *
from django.conf import settings
from dmad_on_django.models import Period
from dmrism.models.item import *
from dominate.tags import div, label, span
from dominate.util import raw
from django import forms
from django.forms import ModelForm, TextInput, Select, HiddenInput, CheckboxInput, Textarea, SelectDateWidget, CharField
from django.forms.models import inlineformset_factory
from django.utils.safestring import mark_safe


class ItemForm(ModelForm):
    class Meta:
        model = Item
        fields = ['rism_id']
        widgets = {
                'rism_id': TextInput( attrs = {
                        'class': 'grow w-full'
                    })
            }

    def as_daisy(self):
        form = div(cls='mb-10')

        rism_id_field = self['rism_id']
        rism_id_field_label = label(rism_id_field.label, cls='input input-bordered flex flex-1 items-center gap-2')
        rism_id_field_label.add(raw(str(rism_id_field)))

        form.add(rism_id_field_label)

        return mark_safe(str(form))

class SignatureForm(ModelForm):
    class Meta:
        model = ItemSignature
        fields = ['library', 'signature', 'status', 'id']
        widgets = {
                'library': Select( attrs = {
                        'class': 'autocomplete-select select select-bordered w-full'
                    }),
                'signature': TextInput( attrs = {
                        'class': 'grow w-full'
                    }),
                'status': Select( attrs = {
                        'class': 'select select-bordered w-full'
                    }),
                'id': HiddenInput()
            }

    def as_daisy(self):
        form = div(cls='mb-10')

        if self.instance.pk:
           form.add(raw(str(self['id'])))

        library_field = self['library']
        signature_field = self['signature']
        status_field = self['status']

        library_container = div(cls='flex-1')
        library_container.add(raw(str(library_field)))

        signature_field_label = label(signature_field.label, cls='input input-bordered flex flex-1 items-center gap-2')
        signature_field_label.add(raw(str(signature_field)))

        status_container = div(cls='flex-0')
        status_container.add(raw(str(status_field)))

        upper_palette = div(cls='flex flex-rows w-full gap-10 my-5')
        lower_palette = div(cls='flex flex-rows w-full gap-10 my-5')

        upper_palette.add(library_container)
        upper_palette.add(status_container)
        lower_palette.add(signature_field_label)

        form.add(upper_palette)
        form.add(lower_palette)

        if 'DELETE' in self.fields:
            del_field = self['DELETE']
            del_field_label = label(del_field.label, cls='input input-bordered flex-0 flex items-center gap-2')
            del_field_label.add(raw(str(del_field)))
            lower_palette.add(del_field_label)

        return mark_safe(str(form))


SignatureFormSet = inlineformset_factory(
        Item,
        ItemSignature,
        form = SignatureForm,
        extra = 0,
        max_num = 100,
        can_delete = True
    )

NewItemSignatureFormSet = inlineformset_factory(
        Item,
        ItemSignature,
        form = SignatureForm,
        extra = 1,
        max_num = 1,
        can_delete = False
    )


#class ItemDedicationForm(ModelForm, SimpleFormMixin):
    #class Meta:
        #model = Item
        #fields = ['dedication', 'private_dedication_comment']
        #widgets = {
                #'dedication': Textarea( attrs = {
                        #'class': SimpleFormMixin.text_area_classes
                    #}),
                #'private_dedication_comment': Textarea( attrs = {
                        #'class': SimpleFormMixin.text_area_classes
                    #})
            #}
        #labels = {
            #'private_dedication_comment': 'Interner Widmungskommentar',
        #}


class ItemCommentForm(CommentForm):
    class Meta:
        model = Item
        fields = CommentForm.Meta.fields + ['taken_information']
        widgets = dict(CommentForm.Meta.widgets, **{
                'taken_information': Textarea( attrs = {
                        'class': SimpleFormMixin.text_area_classes
                    })
            })


class ItemContributorForm(ContributorForm):
    class Meta(ContributorForm.Meta):
        model = ItemContributor
        fields = ContributorForm.Meta.fields + [ 'item' ]
        widgets = dict(ContributorForm.Meta.widgets, **{ 'item': HiddenInput() })


class RelatedItemForm(ModelForm):
    class Meta:
        model = RelatedItem
        fields = [ 'source_item', 'target_item', 'label' ]
        widgets = {
                'source_item': HiddenInput(),
                'target_item': HiddenInput(),
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


class PersonProvenanceStationForm(ModelForm):
    kwargs = {
        'years': range(settings.EDWOCA_FIXED_DATES['birth']['year'], 2051),
        'attrs': {
            'class': 'select select-bordered'
        }
    }
    not_before = forms.DateField(widget=SelectDateWidget(**kwargs), required=False)
    not_after = forms.DateField(widget=SelectDateWidget(**kwargs), required=False)
    display = forms.CharField(required=False, widget=TextInput(attrs={'class': 'grow'}))

    class Meta:
        model = PersonProvenanceStation
        fields = ['not_before', 'not_after', 'display']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.period:
            self.fields['not_before'].initial = self.instance.period.not_before
            self.fields['not_after'].initial = self.instance.period.not_after
            self.fields['display'].initial = self.instance.period.display

    def save(self, commit=True):
        instance = super().save(commit=False)
        not_before = self.cleaned_data.get('not_before')
        not_after = self.cleaned_data.get('not_after')
        display = self.cleaned_data.get('display')

        if not_before or not_after or display:
            period, created = Period.objects.get_or_create(
                not_before=not_before,
                not_after=not_after,
                display=display
            )
            instance.period = period
        if commit:
            instance.save()
        return instance

    def as_daisy(self):
        form = div(cls='mb-10')

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

        display_container = label(display_field.label, _for=display_field.id_for_label, cls='input input-bordered flex items-center gap-2 my-5')
        display_container.add(raw(str(display_field)))
        if display_field.errors:
            display_container.add(div(span(display_field.errors, cls='text-primary text-sm'), cls='label'))

        period_palette = div(cls='flex flex-rows w-full gap-10 my-5')
        period_palette.add(not_before_container)
        period_palette.add(not_after_container)

        form.add(period_palette)
        form.add(display_container)

        return mark_safe(str(form))


class CorporationProvenanceStationForm(ModelForm):
    kwargs = {
        'years': range(settings.EDWOCA_FIXED_DATES['birth']['year'], 2051),
        'attrs': {
            'class': 'select select-bordered'
        }
    }
    not_before = forms.DateField(widget=SelectDateWidget(**kwargs), required=False)
    not_after = forms.DateField(widget=SelectDateWidget(**kwargs), required=False)
    display = forms.CharField(required=False, widget=TextInput(attrs={'class': 'grow'}))

    class Meta:
        model = CorporationProvenanceStation
        fields = ['not_before', 'not_after', 'display']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.period:
            self.fields['not_before'].initial = self.instance.period.not_before
            self.fields['not_after'].initial = self.instance.period.not_after
            self.fields['display'].initial = self.instance.period.display

    def save(self, commit=True):
        instance = super().save(commit=False)
        not_before = self.cleaned_data.get('not_before')
        not_after = self.cleaned_data.get('not_after')
        display = self.cleaned_data.get('display')

        if not_before or not_after or display:
            period, created = Period.objects.get_or_create(
                not_before=not_before,
                not_after=not_after,
                display=display
            )
            instance.period = period
        if commit:
            instance.save()
        return instance

    def as_daisy(self):
        form = div(cls='mb-10')

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

        display_container = label(display_field.label, _for=display_field.id_for_label, cls='input input-bordered flex items-center gap-2 my-5')
        display_container.add(raw(str(display_field)))
        if display_field.errors:
            display_container.add(div(span(display_field.errors, cls='text-primary text-sm'), cls='label'))

        period_palette = div(cls='flex flex-rows w-full gap-10 my-5')
        period_palette.add(not_before_container)
        period_palette.add(not_after_container)

        form.add(period_palette)
        form.add(display_container)

        return mark_safe(str(form))


class LibraryForm(ModelForm):
    class Meta:
        model = Library
        fields = [ 'name', 'siglum' ]
        widgets = {
                'name': TextInput( attrs = {
                        'class': 'grow w-full'
                    }),
                'siglum': TextInput( attrs = {
                        'class': 'grow w-full'
                    }),
            }

    def as_daisy(self):
        form = div()
        for field in self.visible_fields():
            field_label = label(field.label, _for=field.id_for_label, cls='input input-bordered flex items-center gap-2 my-5')
            field_label.add(raw(str(field)))
            form.add(field_label)

        return mark_safe(str(form))


class ItemDigitizedCopyForm(ModelForm, SimpleFormMixin):
    class Meta:
        model = ItemDigitalCopy
        fields = ['url', 'link_type', 'item']
        widgets = {
            'url': TextInput(attrs={'class': SimpleFormMixin.text_input_classes}),
            'link_type': Select(attrs={'class': 'select select-bordered w-full'}),
            'item': HiddenInput(),
        }

    def as_daisy(self):
        form = div()
        for field_name in self.Meta.fields:
            if field_name == 'item':
                form.add(raw(str(self[field_name]))) # Render hidden input directly
            else:
                field = self[field_name]
                wrap = label(cls='form-control')
                label_div = div(cls='label')
                field_label = span(field.label, cls='label-text')
                label_div.add(field_label)
                wrap.add(label_div)
                wrap.add(raw(str(field)))
                form.add(wrap)
        return mark_safe(str(form))


class ItemProvenanceCommentForm(ModelForm, SimpleFormMixin):
    class Meta:
        model = Item
        fields = ['public_provenance_comment', 'private_provenance_comment']
        widgets = {
            'public_provenance_comment': Textarea(attrs={
                'class': SimpleFormMixin.text_area_classes
            }),
            'private_provenance_comment': Textarea(attrs={
                'class': SimpleFormMixin.text_area_classes
            })
        }


class ItemManuscriptForm(ModelForm, SimpleFormMixin):
    class Meta:
        model = Item
        fields = ['extent', 'measure', 'private_manuscript_comment']
        widgets = {
                'extent': Textarea( attrs = {
                        'class': SimpleFormMixin.text_area_classes
                    }),
                'measure': Textarea( attrs = {
                        'class': SimpleFormMixin.text_area_classes
                    }),
                'private_manuscript_comment': Textarea( attrs = {
                        'class': SimpleFormMixin.text_area_classes
                    })
            }


class ItemHandwritingForm(HandwritingForm):
    class Meta(HandwritingForm.Meta):
        model = ItemHandwriting


ItemHandwritingFormSet = inlineformset_factory(
        Item,
        ItemHandwriting,
        form = ItemHandwritingForm,
        extra = 0,
        can_delete = True
    )
