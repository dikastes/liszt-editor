from dominate.tags import div, label, span
from dominate.util import raw
from django.forms.renderers import TemplatesSetting
from django.forms.models import modelformset_factory, inlineformset_factory, ModelForm, BaseInlineFormSet
from django.forms import ModelForm, TextInput, Select, HiddenInput, CheckboxInput, Textarea, DateTimeField, SelectDateWidget
from .models import *
from edwoca import models
from django.utils.safestring import mark_safe

class EdwocaFormRenderer(TemplatesSetting):
    form_template_name = 'edwoca/form_snippet.html'


class WorkForm(ModelForm):
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


class SimpleForm:
    text_area_classes = 'textarea textarea-bordered w-full'

    def as_daisy(self):
        form = div()
        for field in self.Meta.fields:
            wrap = label(cls='form-control')
            label_div = div(cls='label')
            field_label = span(self[field].label, cls='label-text')
            label_div.add(field_label)
            wrap.add(label_div)
            wrap.add(raw(str(self[field])))
            form.add(wrap)

        return mark_safe(str(form))


class ItemLocationForm(ModelForm, SimpleForm):
    class Meta:
        model = Item
        fields = ['location']
        widgets = {
                'location': Textarea( attrs = {
                        'class': SimpleForm.text_area_classes
                    })
            }


class WorkHistoryForm(ModelForm, SimpleForm):
    class Meta:
        model = Work
        fields = ['history']
        widgets = {
                'history': Textarea( attrs = {
                        'class': SimpleForm.text_area_classes
                    })
            }


class ExpressionHistoryForm(ModelForm, SimpleForm):
    class Meta:
        model = Work
        fields = ['history']
        widgets = {
                'history': Textarea( attrs = {
                        'class': SimpleForm.text_area_classes
                    })
            }


class WorkCommentForm(ModelForm, SimpleForm):
    class Meta:
        model = Work
        fields = ['comment']
        widgets = {
                'comment': Textarea( attrs = {
                        'class': SimpleForm.text_area_classes
                    })
            }


class ItemCommentForm(ModelForm, SimpleForm):
    class Meta:
        model = Item
        fields = ['comment']
        widgets = {
                'comment': Textarea( attrs = {
                        'class': SimpleForm.text_area_classes
                    })
            }


class ManifestationCommentForm(ModelForm, SimpleForm):
    class Meta:
        model = Manifestation
        fields = ['comment']
        widgets = {
                'comment': Textarea( attrs = {
                        'class': SimpleForm.text_area_classes
                    })
            }


class ExpressionCommentForm(ModelForm, SimpleForm):
    class Meta:
        model = Expression
        fields = ['comment']
        widgets = {
                'comment': Textarea( attrs = {
                        'class': SimpleForm.text_area_classes
                    })
            }


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


class TitleForm(ModelForm):
    class Meta:
        fields = ['title', 'language', 'status', 'id']
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
                'id': HiddenInput()#,
                #'DELETE': CheckboxInput( attrs = {
                        #'class': 'flex-0'
                    #})
            }

    def as_daisy(self):
        class_name = self.Meta.model.__name__.lower().replace('title', '')
        form = div(cls='mb-10')

        if self.instance.pk:
           form.add(raw(str(self['id'])))
        form.add(raw(str(self[class_name])))

        title_field = self['title']
        lang_field = self['language']
        status_field = self['status']

        title_field_label = label(title_field.label, cls='input input-bordered flex items-center gap-2 my-5')
        title_field_label.add(raw(str(title_field)))

        status_container = div(cls='flex-1')
        status_container.add(raw(str(status_field)))

        lang_container = div(cls='flex-1')
        lang_container.add(raw(str(lang_field)))

        palette = div(cls='flex flex-rows w-full gap-10 my-5')
        palette.add(lang_container)
        palette.add(status_container)

        if 'DELETE' in self.fields:
            del_field = self['DELETE']
            del_field_label = label(del_field.label, cls='input input-bordered flex-0 flex items-center gap-2')
            del_field_label.add(raw(str(del_field)))
            palette.add(del_field_label)

        form.add(title_field_label)
        form.add(palette)

        return mark_safe(str(form))


class WorkTitleForm(TitleForm):
    class Meta(TitleForm.Meta):
        model = WorkTitle
        fields = TitleForm.Meta.fields + ['work']
        widgets = dict(TitleForm.Meta.widgets, **{ 'work': HiddenInput() })


class ItemTitleForm(TitleForm):
    class Meta(TitleForm.Meta):
        model = ItemTitle
        fields = TitleForm.Meta.fields + ['item']
        widgets = dict(TitleForm.Meta.widgets, **{ 'item': HiddenInput() })


class ExpressionTitleForm(TitleForm):
    class Meta(TitleForm.Meta):
        model = ExpressionTitle
        fields = TitleForm.Meta.fields + ['expression']
        widgets = dict(TitleForm.Meta.widgets, **{ 'expression': HiddenInput() })


class SkipEmptyTitleFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        for form in self.forms:
            raw_title = form.cleaned_data['title']
            if not raw_title:
                form.cleaned_data['DELETE'] = True


ExpressionTitleFormSet = inlineformset_factory(
        Expression,
        ExpressionTitle,
        form = ExpressionTitleForm,
        formset = SkipEmptyTitleFormSet,
        extra = 1,
        max_num = 100,
        can_delete = True
    )


WorkTitleFormSet = inlineformset_factory(
        Work,
        WorkTitle,
        form = WorkTitleForm,
        formset = SkipEmptyTitleFormSet,
        extra = 1,
        max_num = 100,
        can_delete = True
    )


ItemTitleFormSet = inlineformset_factory(
        Item,
        ItemTitle,
        form = ItemTitleForm,
        formset = SkipEmptyTitleFormSet,
        extra = 1,
        max_num = 100,
        can_delete = True
    )


class WorkBibForm(ModelForm):
    class Meta:
        model = WorkBib
        fields = [ 'bib', 'id', 'work' ]
        widgets = {
                'bib': Select( attrs = {
                        'class': 'autocomplete-select select select-bordered w-full'
                    }),
                'id': HiddenInput(),
                'work': HiddenInput(),
                'DELETE': CheckboxInput( attrs = {
                        'class': 'flex-0'
                    })
            }

    def as_daisy(self):
        form = div(cls='mb-10')

        if self.instance.pk:
           form.add(raw(str(self['id'])))
        form.add(raw(str(self['work'])))

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


class ContributorForm(ModelForm):
    class Meta:
        fields = [ 'person', 'role', 'id' ]
        widgets = {
                'person': Select( attrs = {
                        'class': 'autocomplete-select select select-bordered'
                    }),
                'role': Select( attrs = {
                        'class': 'select w-full select-bordered'
                    }),
                'id': HiddenInput(),
                'DELETE': CheckboxInput( attrs = {
                        'class': 'flex-0'
                    })
            }

    def as_daisy(self):
        class_name = self.Meta.model.__name__.lower().replace('contributor', '')
        form = div(cls='mb-10')

        if self.instance.pk:
           form.add(raw(str(self['id'])))
        form.add(raw(str(self[class_name])))

        person_field = self['person']
        role_field = self['role']

        person_container = div(cls='flex-1')
        person_container.add(raw(str(person_field)))

        role_container = div(cls='flex-1')
        role_container.add(raw(str(role_field)))

        palette = div(cls='flex flex-rows w-full gap-10 my-5')
        palette.add(person_container)
        palette.add(role_container)

        if 'DELETE' in self.fields:
            del_field = self['DELETE']
            del_field_label = label(del_field.label, cls='input input-bordered flex items-center gap-2')
            del_field_label.add(raw(str(del_field)))
            palette.add(del_field_label)

        form.add(palette)

        return mark_safe(str(form))


class ManifestationContributorForm(ContributorForm):
    class Meta:
        model = ManifestationContributor
        fields = ContributorForm.Meta.fields + [ 'manifestation' ]
        widgets = dict(ContributorForm.Meta.widgets, **{ 'manifestation': HiddenInput() })


class ManifestationHistoryForm(ContributorForm):
    not_before = DateTimeField(widget = SelectDateWidget( attrs = {'class':'select select-bordered'}))
    not_after = DateTimeField(widget = SelectDateWidget( attrs = {'class':'select select-bordered'}))
    display = DateTimeField(widget = TextInput( attrs = { 'class': 'grow'}))

    class Meta:
        model = Manifestation
        fields = ['history', 'id']
        widgets = {
                'history': Textarea( attrs = {
                        'class': SimpleForm.text_area_classes
                    })
            }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.period:
            self.fields['not_before'] = self.instance.period.not_before
            self.fields['not_after'] = self.instance.period.not_after
            self.fields['display'] = self.instance.period.display

    def save(self, commit=True):
        manifestation_instance = super().save(commit=False)
        period_instance = manifestation_instance.period
        period_instance.not_before = self.cleaned_data['not_before']
        period_instance.not_after = self.cleaned_data['not_after']
        period_instance.display = self.cleaned_data['display']

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


class WorkContributorForm(ContributorForm):
    class Meta:
        model = WorkContributor
        fields = ContributorForm.Meta.fields + [ 'work' ]
        widgets = dict(ContributorForm.Meta.widgets, **{ 'work': HiddenInput() })


class ItemContributorForm(ContributorForm):
    class Meta:
        model = ItemContributor
        fields = ContributorForm.Meta.fields + [ 'item' ]
        widgets = dict(ContributorForm.Meta.widgets, **{ 'item': HiddenInput() })


class ExpressionContributorForm(ContributorForm):
    class Meta:
        model = ExpressionContributor
        fields = ContributorForm.Meta.fields + [ 'expression' ]
        widgets = dict(ContributorForm.Meta.widgets, **{ 'expression': HiddenInput() })


ManifestationContributorFormSet = inlineformset_factory(
        Manifestation,
        ManifestationContributor,
        form = ManifestationContributorForm,
        extra = 1,
        max_num = 100,
        can_delete = True
    )


ItemContributorFormSet = inlineformset_factory(
        Item,
        ItemContributor,
        form = ItemContributorForm,
        extra = 1,
        max_num = 100,
        can_delete = True
    )


WorkContributorFormSet = inlineformset_factory(
        Work,
        WorkContributor,
        form = WorkContributorForm,
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


WorkBibFormSet = inlineformset_factory(
        Work,
        WorkBib,
        form = WorkBibForm,
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


ExpressionTitleFormSet = inlineformset_factory(
        Expression,
        ExpressionTitle,
        form = ExpressionTitleForm,
        formset = SkipEmptyTitleFormSet,
        extra = 1,
        max_num = 100,
        can_delete = True
    )

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


MovementFormSet = inlineformset_factory(
        Expression,
        Movement,
        form = MovementForm,
        extra = 1,
        max_num = 100,
        can_delete = True
    )


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

ManifestationTitleFormSet = inlineformset_factory(
        Manifestation,
        ManifestationTitle,
        form = ManifestationTitleForm,
        formset = SkipEmptyTitleFormSet,
        extra = 1,
        max_num = 100,
        can_delete = True
    )


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
