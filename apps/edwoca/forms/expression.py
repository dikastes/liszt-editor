from .base import *
from ..models.expression import *
from ..models.work import Work
from dominate.tags import div, label, span
from dominate.util import raw
from django.forms import ModelForm, TextInput, Select, HiddenInput, CheckboxInput, Textarea
from django.forms.models import inlineformset_factory
from django.utils.safestring import mark_safe


class ExpressionForm(ModelForm):
    class Meta:
        model = Expression
        fields = [ 'work', 'work_catalog_number' ]
        widgets = {
                'work': HiddenInput(),
                'work_catalog_number': TextInput( attrs = {
                        'class': 'grow'
                    }),
            }

    def as_daisy(self):
        form = div()
        for field in self.visible_fields():
            field_label = label(field.label, _for=field.id_for_label, cls='input input-bordered flex items-center gap-2 my-5')
            field_label.add(raw(str(field)))
            form.add(field_label)

        return mark_safe(str(form))


class ExpressionTitleForm(TitleForm):
    class Meta(TitleForm.Meta):
        model = ExpressionTitle
        fields = TitleForm.Meta.fields + ['expression']
        widgets = dict(TitleForm.Meta.widgets, **{ 'expression': HiddenInput() })


class ExpressionHistoryForm(ModelForm, SimpleFormMixin):
    class Meta:
        model = Work
        fields = ['history']
        widgets = {
                'history': Textarea( attrs = {
                        'class': SimpleFormMixin.text_area_classes
                    })
            }


class ExpressionCommentForm(CommentForm):
    class Meta:
        model = Expression
        fields = CommentForm.Meta.fields
        widgets = CommentForm.Meta.widgets


class ExpressionContributorForm(ContributorForm):
    class Meta:
        model = ExpressionContributor
        fields = ContributorForm.Meta.fields + [ 'expression' ]
        widgets = dict(ContributorForm.Meta.widgets, **{ 'expression': HiddenInput() })


class RelatedExpressionForm(ModelForm):
    class Meta:
        model = RelatedExpression
        fields = [ 'source_expression', 'target_expression', 'label' ]
        widgets = {
                'source_expression': HiddenInput(),
                'target_expression': HiddenInput(),
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


class MovementForm(ModelForm):
    class Meta:
        model = Movement
        fields = '__all__'
        widgets = {
                'title': TextInput( attrs = {
                        'class': 'grow w-full'
                    }),
                'tempo': TextInput( attrs = {
                        'class': 'grow w-full'
                    }),
                'meter': TextInput( attrs = {
                        'class': 'grow w-full'
                    }),
                'id': HiddenInput(),
                'DELETE': CheckboxInput( attrs = {
                        'class': 'flex-0'
                    })
            }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.key_instance = getattr(self.instance, 'key', None) or Key()
        self.key_form = KeyForm(instance=self.key_instance, prefix=f'key-{self.prefix}', **self._get_key_form_data())

        for name, field in self.key_form.fields.items():
            self.fields[name] = field
            if name in self.key_form.initial:
                self.initial[name] = self.key_form.initial[name]

    def _get_key_form_data(self):
        if hasattr(self, 'data'):
            return {'data': self.data}
        return {}

    def is_valid(self):
        return super().is_valid() and self.key_form.is_valid()

    def save(self, commit=True):
        movement_instance = super().save(commit=commit)
        self.key_instance.movement = movement_instance
        self.key_form.instance = self.movement_instance

        if commit:
            self.movement_form.save()
        else:
            self._pending_save = self.movement_form.save(commit=False)

        return b_instance

    def as_daisy(self):
        form = div()

        title_container = label(self['title'].label, cls='input input-bordered flex items-center gap-2 my-5')
        title_container.add(raw(str(self['title'])))
        tempo_container = label(self['tempo'].label, cls='input input-bordered flex items-center gap-2 my-5')
        tempo_container.add(raw(str(self['tempo'])))

        title_palette = div(cls='flex flex-rows w-full gap-10 my-5')
        title_palette.add(title_container)
        title_palette.add(tempo_container)

        meter_container = label(self['meter'].label, cls='input input-bordered flex items-center gap-2 my-5')
        meter_container.add(raw(str(self['meter'])))
        note_container = div(cls='flex-1')
        note_container.add(raw(str(self['note'])))
        acc_container = div(cls='flex-1')
        acc_container.add(raw(str(self['accidental'])))
        mode_container = div(cls='flex-1')
        mode_container.add(raw(str(self['mode'])))

        meta_palette = div(cls='flex flex-rows w-full gap-10 my-5')
        meta_palette.add(meter_container)
        meta_palette.add(note_container)
        meta_palette.add(acc_container)
        meta_palette.add(mode_container)

        if 'DELETE' in self.fields:
            del_field = self['DELETE']
            del_field_label = label(del_field.label, cls='input input-bordered flex items-center gap-2')
            del_field_label.add(raw(str(del_field)))
            meta_palette.add(del_field_label)

        form.add(title_palette)
        form.add(meta_palette)

        return mark_safe(str(form))


class KeyForm(ModelForm):
    class Meta:
        model = Key
        fields = [ 'note', 'accidental', 'mode' ]
        widgets = {
                'note': Select( attrs = {
                        'class': 'select w-full select-bordered'
                    }),
                'accidental': Select( attrs = {
                        'class': 'select w-full select-bordered'
                    }),
                'mode': Select( attrs = {
                        'class': 'select w-full select-bordered'
                    })
            }


ExpressionTitleFormSet = inlineformset_factory(
        Expression,
        ExpressionTitle,
        form = ExpressionTitleForm,
        formset = SkipEmptyTitleFormSet,
        extra = 1,
        max_num = 100,
        can_delete = True
    )


ExpressionContributorFormSet = inlineformset_factory(
        Expression,
        ExpressionContributor,
        form = ExpressionContributorForm,
        extra = 1,
        max_num = 100,
        can_delete = True
    )


MovementFormSet = inlineformset_factory(
        Expression,
        Movement,
        form = MovementForm,
        extra = 1,
        max_num = 100,
        can_delete = True
    )
