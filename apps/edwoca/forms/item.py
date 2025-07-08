from .base import *
from ..models.item import *
from dominate.tags import div, label, span
from dominate.util import raw
from django.forms import ModelForm, TextInput, Select, HiddenInput, CheckboxInput, Textarea
from django.forms.models import inlineformset_factory
from django.utils.safestring import mark_safe


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
        form = div()
        for field in self.visible_fields():
            field_label = label(field.label, _for=field.id_for_label, cls='input input-bordered flex items-center gap-2 my-5')
            field_label.add(raw(str(field)))
            form.add(field_label)

        return mark_safe(str(form))


class ItemTitleForm(TitleForm):
    class Meta(TitleForm.Meta):
        model = ItemTitle
        fields = TitleForm.Meta.fields + ['item']
        widgets = dict(TitleForm.Meta.widgets, **{ 'item': HiddenInput() })


class ItemLocationForm(ModelForm, SimpleFormMixin):
    class Meta:
        model = Item
        fields = ['location']
        widgets = {
                'location': Textarea( attrs = {
                        'class': SimpleFormMixin.text_area_classes
                    })
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


ItemTitleFormSet = inlineformset_factory(
        Item,
        ItemTitle,
        form = ItemTitleForm,
        formset = SkipEmptyTitleFormSet,
        extra = 1,
        max_num = 100,
        can_delete = True
    )





class ProvenanceForm(ModelForm):
    class Meta:
        fields = ['owner', 'item', 'comment']
        widgets = {
                'title': TextInput( attrs = {
                        'class': 'grow w-full'
                    }),
                'language': Select( attrs = {
                        'class': 'autocomplete-select select select-bordered w-full'
                    }),
                'status': Select( attrs = {
                        'class': 'select w-full select-bordered'
                    }),
                'id': HiddenInput()
            }
