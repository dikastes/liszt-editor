from dominate.tags import div, label, span
from dominate.util import raw
from django.forms.renderers import TemplatesSetting
from django.forms.models import modelformset_factory, inlineformset_factory, ModelForm, BaseInlineFormSet
from django.forms import ModelForm, TextInput, Select, HiddenInput, CheckboxInput, Textarea
from .models import Work, WorkTitle, WorkContributor, WorkBib, Expression, ExpressionTitle, RelatedWork
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


class WorkHistoryForm(ModelForm):
    class Meta:
        model = Work
        fields = ['history']
        widgets = {
                'history': Textarea( attrs = {
                        'class': 'textarea textarea-bordered w-full'
                    })
            }

    def as_daisy(self):
        form = div()
        wrap = label(cls='form-control')
        label_div = div(cls='label')
        hist_label = span(self['history'].label, cls='label-text')
        label_div.add(hist_label)
        wrap.add(label_div)
        wrap.add(raw(str(self['history'])))
        form.add(wrap)

        return mark_safe(str(form))


class WorkCommentForm(ModelForm):
    class Meta:
        model = Work
        fields = ['comment']
        widgets = {
                'comment': Textarea( attrs = {
                        'class': 'textarea textarea-bordered w-full'
                    })
            }

    def as_daisy(self):
        form = div()
        wrap = label(cls='form-control')
        label_div = div(cls='label')
        hist_label = span(self['comment'].label, cls='label-text')
        label_div.add(hist_label)
        wrap.add(label_div)
        wrap.add(raw(str(self['comment'])))
        form.add(wrap)

        return mark_safe(str(form))


class TitleForm(ModelForm):
    class Meta:
        fields = ['title', 'language', 'status', 'id']
        widgets = {
                'title': TextInput( attrs = {
                        'class': 'grow w-full'
                    }),
                'language': Select( attrs = {
                        'class': 'autocomplete-select select select-bordered'
                    }),
                'status': Select( attrs = {
                        'class': 'select w-full select-bordered'
                    }),
                'id': HiddenInput(),
                'DELETE': CheckboxInput( attrs = {
                        'class': 'flex-0'
                    })
            }

    def as_daisy(self):
        form = div(cls='mb-10')

        if self.instance.pk:
           form.add(raw(str(self['id'])))
        form.add(raw(str(self['work'])))

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
            del_field_label = label(del_field.label, cls='input input-bordered flex items-center gap-2')
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


class WorkBibForm(ModelForm):
    class Meta:
        model = WorkBib
        fields = [ 'bib', 'id', 'work' ]
        widgets = {
                'bib': Select( attrs = {
                        'class': 'autocomplete-select select select-bordered'
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


class WorkContributorForm(ModelForm):
    class Meta:
        model = WorkContributor
        fields = [ 'person', 'role', 'id', 'work' ]
        widgets = {
                'person': Select( attrs = {
                        'class': 'autocomplete-select select select-bordered'
                    }),
                'role': Select( attrs = {
                        'class': 'select w-full select-bordered'
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


WorkContributorFormSet = inlineformset_factory(
        Work,
        WorkContributor,
        form = WorkContributorForm,
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

class RelatedWorkForm(ModelForm):
    class Meta:
        model = RelatedWork
        fields = [ 'source_work', 'target_work', 'label' ]
        widgets = {
                'source_work': HiddenInput(),
                'target_work': HiddenInput(),
                'label': Select( attrs = {
                        'class': 'select w-full select-bordered'
                    }),
                'DELETE': CheckboxInput( attrs = {
                        'class': 'flex-0'
                    })
            }

    def as_daisy(self):
        form = div(cls='mb-10')

        if self.instance.pk:
           form.add(raw(str(self['id'])))
        form.add(raw(str(self['work'])))

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
