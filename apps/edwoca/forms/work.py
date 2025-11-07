from .base import *
from ..models.work import *
from dominate.tags import div, label, span
from dominate.util import raw
from django.forms import ModelForm, TextInput, Select, HiddenInput, CheckboxInput, Textarea
from django.forms.models import inlineformset_factory, formset_factory
from django.utils.safestring import mark_safe


class WorkForm(ModelForm):
    class Meta:
        model = Work
        fields = []

class WorkIdentificationForm(ModelForm):
    class Meta:
        model = Work
        fields = ['work_catalog_number', 'gnd_id']
        widgets = {
                'work_catalog_number': TextInput( attrs = {
                        'class': 'grow'
                    }),
                'gnd_id': TextInput( attrs = {
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


class WorkTitleForm(TitleForm):
    class Meta(TitleForm.Meta):
        model = WorkTitle
        fields = TitleForm.Meta.fields + ['work']
        widgets = dict(TitleForm.Meta.widgets, **{ 'work': HiddenInput() })


class WorkHistoryForm(ModelForm, SimpleFormMixin):
    class Meta:
        model = Work
        fields = ['history']
        widgets = {
                'history': Textarea( attrs = {
                        'class': SimpleFormMixin.text_area_classes
                    })
            }


class WorkCommentForm(CommentForm):
    class Meta:
        model = Work
        fields = CommentForm.Meta.fields
        widgets = CommentForm.Meta.widgets


class WorkContributorForm(ContributorForm):
    class Meta(ContributorForm.Meta):
        model = WorkContributor
        fields = ContributorForm.Meta.fields + ['work']
        widgets = dict(ContributorForm.Meta.widgets, **{ 'work': HiddenInput() })


class WorkBibForm(BaseBibForm):
    class Meta(BaseBibForm.Meta):
        model = WorkBib
        fields = BaseBibForm.Meta.fields + [ 'work' ]
        widgets = dict(BaseBibForm.Meta.widgets, **{ 'work': HiddenInput() })


class RelatedWorkForm(ModelForm):
    class Meta:
        model = RelatedWork
        fields = [ 'source_work', 'target_work', 'label' ]
        widgets = {
                'source_work': HiddenInput(),
                'target_work': HiddenInput(),
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


WorkTitleFormSet = inlineformset_factory(
        Work,
        WorkTitle,
        form = WorkTitleForm,
        formset = SkipEmptyTitleFormSet,
        extra = 1,
        max_num = 100,
        can_delete = True
    )