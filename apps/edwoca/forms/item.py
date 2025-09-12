from .base import *
from dmrism.models.item import *
from dominate.tags import div, label, span
from dominate.util import raw
from django.forms import ModelForm, TextInput, Select, HiddenInput, CheckboxInput, Textarea
from django.forms.models import inlineformset_factory
from django.utils.safestring import mark_safe


class ItemForm(ModelForm):
    class Meta:
        model = Item
        fields = ['cover', 'handwriting']
        widgets = {
                'cover': Textarea( attrs = {
                        'class': SimpleFormMixin.text_area_classes
                    }),
                'handwriting': TextInput( attrs = {
                        'class': 'grow w-full'
                    })
            }


class SignatureForm(ModelForm):
    class Meta:
        model = Signature
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

        del_field = self['DELETE']
        del_field_label = label(del_field.label, cls='input input-bordered flex-0 flex items-center gap-2')
        del_field_label.add(raw(str(del_field)))

        upper_palette = div(cls='flex flex-rows w-full gap-10 my-5')
        lower_palette = div(cls='flex flex-rows w-full gap-10 my-5')

        upper_palette.add(library_container)
        upper_palette.add(status_container)
        lower_palette.add(signature_field_label)
        lower_palette.add(del_field_label)

        form.add(upper_palette)
        form.add(lower_palette)

        return mark_safe(str(form))


SignatureFormSet = inlineformset_factory(
        Item,
        Signature,
        form = SignatureForm,
        extra = 0,
        max_num = 100,
        can_delete = True
    )


class ItemDedicationForm(ModelForm, SimpleFormMixin):
    class Meta:
        model = Item
        fields = ['dedication', 'private_dedication_comment']
        widgets = {
                'dedication': Textarea( attrs = {
                        'class': SimpleFormMixin.text_area_classes
                    }),
                'private_dedication_comment': Textarea( attrs = {
                        'class': SimpleFormMixin.text_area_classes
                    })
            }
        labels = {
            'private_dedication_comment': 'Interner Widmungskommentar',
        }


class ItemCommentForm(CommentForm):
    class Meta:
        model = Item
        fields = CommentForm.Meta.fields
        widgets = CommentForm.Meta.widgets


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
    class Meta:
        model = PersonProvenanceStation
        fields = ['period']
        widgets = {
                'period': Select( attrs = {
                        'class': 'autocomplete-select select select-bordered w-full'
                    })
            }


class CorporationProvenanceStationForm(ModelForm):
    class Meta:
        model = CorporationProvenanceStation
        fields = ['period']
        widgets = {
                'period': Select( attrs = {
                        'class': 'autocomplete-select select select-bordered w-full'
                    })
            }


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
        model = DigitalCopy
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
