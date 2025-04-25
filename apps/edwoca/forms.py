from dominate.tags import div, label
from dominate.util import raw
from django.forms.renderers import TemplatesSetting
from django.forms.models import inlineformset_factory, ModelForm, BaseInlineFormSet
from django.forms import ModelForm, TextInput, Select, HiddenInput, CheckboxInput
from .models import Work, WorkTitle
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


class WorkTitleForm(ModelForm):
    class Meta:
        model = WorkTitle
        fields = ['title', 'language', 'id', 'work']
        widgets = {
                'title': TextInput( attrs = {
                        'class': 'grow'
                    }),
                'language': Select( attrs = {
                        'class': 'autocomplete-select select select-bordered flex-1'
                    }),
                'id': HiddenInput(),
                'work': HiddenInput(),
                'DELETE': CheckboxInput( attrs = {
                        'class': 'flex-0'
                    })
            }
        labels = {
                'id': '',
                'work': ''
            }

    def as_daisy(self):
        form = div()

        if self.instance.pk:
           form.add(raw(str(self['id'])))
        form.add(raw(str(self['work'])))

        title_field = self['title']
        lang_field = self['language']

        title_field_label = label(title_field.label, cls='input input-bordered flex items-center gap-2 my-5')
        title_field_label.add(raw(str(title_field)))

        lang_container = div(cls='flex-1')
        lang_container.add(raw(str(lang_field)))

        palette = div(cls='flex flex-rows w-full gap-10 my-5')
        palette.add(lang_container)

        if 'DELETE' in self.fields:
            del_field = self['DELETE']
            del_field_label = label(del_field.label, cls='input input-bordered flex items-center gap-2')
            del_field_label.add(raw(str(del_field)))
            palette.add(del_field_label)

        form.add(title_field_label)
        form.add(palette)

        return mark_safe(str(form))


class SkipEmptyWorkTitleFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        for form in self.forms:
            raw_title = form.cleaned_data['title']
            if not raw_title:
                form.cleaned_data['DELETE'] = True


WorkTitleFormSet = inlineformset_factory(
        Work,
        WorkTitle,
        form = WorkTitleForm,
        formset = SkipEmptyWorkTitleFormSet,
        extra = 1,
        max_num = 100,
        can_delete = True
    )

