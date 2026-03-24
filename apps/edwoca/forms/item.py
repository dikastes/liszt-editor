from .base import *
from secrets import token_urlsafe
from django.urls import reverse_lazy, reverse
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from dmad_on_django.models import Period
from dmrism.models.item import *
from dominate.tags import div, label, span, form, input_
from dominate.util import raw
from django import forms
from django.forms import ModelForm, TextInput, Select, HiddenInput, CheckboxInput, Textarea, SelectDateWidget, CharField, BooleanField
from django.forms.models import inlineformset_factory
from django.utils.safestring import mark_safe
from liszt_util.forms.forms import GenericAsDaisyMixin
from liszt_util.forms.layouts import Layouts


class ItemForm(ModelForm):
    class Meta:
        model = Item
        fields = ['rism_id']
        widgets = {
                'rism_id': TextInput( attrs = {
                        'class': 'grow'
                    })
            }

    def as_daisy(self):
        form = div(cls='mb-10')

        rism_id_field = self['rism_id']
        rism_id_field_label = label(rism_id_field.label, cls='input input-bordered flex flex-1 items-center gap-2 my-5')
        rism_id_field_label.add(raw(str(rism_id_field)))

        form.add(rism_id_field_label)

        return mark_safe(str(form))

class SignatureForm(GenericAsDaisyMixin, ModelForm):
    layout = Layouts.LABEL_OUTSIDE

    class Meta:
        model = ItemSignature
        fields = ['library', 'signature', 'status', 'id']
        widgets = {
                'library': Select( attrs = {
                        'class': SimpleFormMixin.autocomplete_classes,
                        'form': 'form'
                    }),
                'signature': TextInput( attrs = {
                        'class': SimpleFormMixin.text_input_classes,
                        'form': 'form'
                    }),
                'status': Select( attrs = {
                        'class': SimpleFormMixin.select_classes,
                        'form': 'form'
                    }),
                'id': HiddenInput()
            }

    def as_daisy(self):
        form_wrapper = div(cls='mb-10')

        library_field = self['library']
        signature_field = self['signature']
        status_field = self['status']

        library_container = label(cls='form-control w-full flex-1')
        library_span = span(library_field.label, cls='label-text')
        library_div = div(cls='label')
        library_div.add(library_span)
        library_container.add(library_div)
        library_container.add(raw(str(library_field)))

        signature_container = label(cls='form-control w-full flex-1')
        signature_span = span(signature_field.label, cls='label-text')
        signature_div = div(cls='label')
        signature_div.add(signature_span)
        signature_container.add(signature_div)
        signature_container.add(raw(str(signature_field)))

        status_container = label(cls='form-control w-full max-w-xs flex-0')
        status_span = span(status_field.label, cls='label-text')
        status_div = div(cls='label')
        status_div.add(status_span)
        status_container.add(status_div)
        status_container.add(raw(str(status_field)))

        upper_palette = div(cls='flex flex-rows w-full gap-10 my-5')
        lower_palette = div(cls='flex flex-rows w-full gap-10 my-5')

        upper_palette.add(library_container)
        upper_palette.add(status_container)
        lower_palette.add(signature_container)

        form_wrapper.add(upper_palette)
        form_wrapper.add(lower_palette)

        return mark_safe(str(form_wrapper))


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


class PersonProvenanceStationForm(DateFormMixin, ModelForm):
    kwargs = {
        'years': range(settings.EDWOCA_FIXED_DATES['birth']['year'], 2051),
        'attrs': {
            'class': 'select select-bordered border-black bg-white',
            'form': 'form'
        }
    }
    not_before = forms.DateField(widget=SelectDateWidget(**kwargs), required=False)
    not_after = forms.DateField(widget=SelectDateWidget(**kwargs), required=False)
    display = forms.CharField(required=False, widget=TextInput(attrs={'class': SimpleFormMixin.text_input_classes, 'form': 'form'}))
    inferred = BooleanField(widget = CheckboxInput(attrs = { 'class': 'toggle', 'form': 'form'}), required = False)
    assumed = BooleanField(widget = CheckboxInput(attrs = { 'class': 'toggle', 'form': 'form'}), required = False)

    class Meta:
        model = PersonProvenanceStation
        fields = [
            'not_before',
            'not_after',
            'display',
            'inferred',
            'assumed'
        ]

    def as_daisy(self):
        form = div(cls='mb-10')
        date_div = self.get_date_div()

        for hidden in self.hidden_fields():
            hidden.field.widget.attrs['form'] = 'form'
            form.add(raw(str(hidden)))

        form.add(date_div)

        return mark_safe(str(form))


class CorporationProvenanceStationForm(DateFormMixin, ModelForm):
    kwargs = {
        'years': range(settings.EDWOCA_FIXED_DATES['birth']['year'], 2051),
        'attrs': {
            'class': 'select select-bordered border-black bg-white',
            'form': 'form'
        }
    }
    not_before = forms.DateField(widget=SelectDateWidget(**kwargs), required=False)
    not_after = forms.DateField(widget=SelectDateWidget(**kwargs), required=False)
    display = forms.CharField(required=False, widget=TextInput(attrs={'class': SimpleFormMixin.text_input_classes, 'form': 'form'}))
    inferred = BooleanField(widget = CheckboxInput(attrs = { 'class': 'toggle', 'form': 'form'}), required = False)
    assumed = BooleanField(widget = CheckboxInput(attrs = { 'class': 'toggle', 'form': 'form'}), required = False)

    class Meta:
        model = CorporationProvenanceStation
        fields = [
            'not_before',
            'not_after',
            'display',
            'inferred',
            'assumed'
        ]

    def as_daisy(self):
        form = div(cls='mb-10')
        date_div = self.get_date_div()

        for hidden in self.hidden_fields():
            hidden.field.widget.attrs['form'] = 'form'
            form.add(raw(str(hidden)))

        form.add(date_div)

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


class ItemDigitizedCopyForm(GenericAsDaisyMixin, ModelForm, SimpleFormMixin):
    layout = Layouts.LABEL_OUTSIDE
    class Meta:
        model = ItemDigitalCopy
        fields = ['url', 'link_type']
        widgets = {
                'url': TextInput(attrs={'class': SimpleFormMixin.text_input_classes, 'form': 'form'}),
                'link_type': Select(attrs={'class': SimpleFormMixin.select_classes, 'form': 'form'})
        }

    def as_daisy(self):
        form = div()

        url_field = self['url']
        link_type_field = self['link_type']

        with form:
            with label(cls=SimpleFormMixin.form_control_classes):
                with div(cls=SimpleFormMixin.label_classes):
                    span(_(url_field.label), cls=SimpleFormMixin.label_text_classes)
                raw(str(url_field))
            with label(cls=SimpleFormMixin.form_control_classes):
                with div(cls=SimpleFormMixin.label_classes):
                    span(_(link_type_field.label), cls=SimpleFormMixin.label_text_classes)
                raw(str(link_type_field))

        return mark_safe(str(form))


class ItemProvenanceCommentForm(ModelForm, SimpleFormMixin):
    class Meta:
        model = Item
        fields = ['public_provenance_comment', 'private_provenance_comment']
        widgets = {
            'public_provenance_comment': Textarea(attrs={
                'class': SimpleFormMixin.text_area_classes,
                'form': 'form'
            }),
            'private_provenance_comment': Textarea(attrs={
                'class': SimpleFormMixin.text_area_classes,
                'form': 'form'
            })
        }


class ItemManuscriptForm(ModelForm, SimpleFormMixin):
    class Meta:
        model = Item
        fields = ['extent', 'measure', 'private_manuscript_comment']
        widgets = {
                'extent': Textarea( attrs = {
                        'class': SimpleFormMixin.text_area_classes,
                        'form': 'form'
                    }),
                'measure': Textarea( attrs = {
                        'class': SimpleFormMixin.text_area_classes,
                        'form': 'form'
                    }),
                'private_manuscript_comment': Textarea( attrs = {
                        'class': SimpleFormMixin.text_area_classes,
                        'form': 'form'
                    })
            }

    def as_daisy(self):
        extent_field = self['extent']
        measure_field = self['measure']
        form = div()

        with form:
            with label():
                with div(cls=SimpleFormMixin.label_classes):
                    span(_(extent_field.label), cls=SimpleFormMixin.label_text_classes)
                raw(str(extent_field))
            with label():
                with div(cls=SimpleFormMixin.label_classes):
                    span(_(measure_field.label), cls=SimpleFormMixin.label_text_classes)
                raw(str(measure_field))

        return mark_safe(str(form))

    def comment_as_daisy(self):
        private_manuscript_comment_field = self['private_manuscript_comment']
        form = div()

        with form:
            with div(cls=SimpleFormMixin.label_classes):
                span(_(private_manuscript_comment_field.label), cls=SimpleFormMixin.label_text_classes)
            raw(str(private_manuscript_comment_field))

        return mark_safe(str(form))


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


class BaseProvenanceStationWebReferenceForm(ModelForm):
    class Meta:
        fields = [ 'url', 'comment' ]
        widgets = {
                'url': TextInput(attrs={'class': SimpleFormMixin.text_input_classes, 'form': 'form'}),
                'comment': Textarea(attrs={'class': SimpleFormMixin.text_area_classes, 'form': 'form'})
            }

    def as_daisy(self):
        form = div()

        url_field = self['url']
        comment_field = self['comment']

        with form:
            with label(cls=SimpleFormMixin.form_control_classes):
                with div(cls=SimpleFormMixin.label_classes):
                    span(url_field.label, cls=SimpleFormMixin.label_text_classes)
                raw(str(url_field))
            with label(cls=SimpleFormMixin.form_control_classes):
                with div(cls=SimpleFormMixin.label_classes):
                    span(comment_field.label, cls=SimpleFormMixin.label_text_classes)
                raw(str(comment_field))

        return mark_safe(str(form))


class PersonProvenanceStationWebReferenceForm(BaseProvenanceStationWebReferenceForm):
    class Meta:
        model = PersonProvenanceStationWebReference
        fields = BaseProvenanceStationWebReferenceForm.Meta.fields
        widgets = BaseProvenanceStationWebReferenceForm.Meta.widgets


class CorporationProvenanceStationWebReferenceForm(BaseProvenanceStationWebReferenceForm):
    class Meta:
        model = CorporationProvenanceStationWebReference
        fields = BaseProvenanceStationWebReferenceForm.Meta.fields
        widgets = BaseProvenanceStationWebReferenceForm.Meta.widgets


class PersonProvenanceStationBibForm(BaseBibForm):
    class Meta:
        model = PersonProvenanceStationBib
        fields = BaseBibForm.Meta.fields
        widgets = BaseBibForm.Meta.widgets


class CorporationProvenanceStationBibForm(BaseBibForm):
    class Meta:
        model = CorporationProvenanceStationBib
        fields = BaseBibForm.Meta.fields
        widgets = BaseBibForm.Meta.widgets


PersonProvenanceFormSet = inlineformset_factory(
    parent_model=Item,
    model=PersonProvenanceStation,
    form=PersonProvenanceStationForm,
    extra=0,
    can_delete=False
)

PersonProvenanceBibFormSet = inlineformset_factory(
    parent_model=PersonProvenanceStation,
    model=PersonProvenanceStationBib,
    form=PersonProvenanceStationBibForm,
    extra=0,
    can_delete=False
)

CorporationProvenanceFormSet = inlineformset_factory(
    parent_model=Item,
    model=CorporationProvenanceStation,
    form=CorporationProvenanceStationForm,
    extra=0,
    can_delete=False
)

CorporationProvenanceBibFormSet = inlineformset_factory(
    parent_model=CorporationProvenanceStation,
    model=CorporationProvenanceStationBib,
    form=CorporationProvenanceStationBibForm,
    extra=0,
    can_delete=False
)
