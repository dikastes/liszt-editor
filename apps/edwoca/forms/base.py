from ..models.expression import Expression
from django.forms import ModelForm, TextInput, Select, HiddenInput, CheckboxInput, Textarea
from django.forms.models import inlineformset_factory, BaseInlineFormSet
from django.utils.safestring import mark_safe
from dominate.tags import div, label, span
from dominate.util import raw


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
                'id': HiddenInput(),
                'DELETE': CheckboxInput( attrs = {
                        'class': 'flex-0'
                    })
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


class SkipEmptyTitleFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()

        for form in self.forms:
            if not hasattr(form, 'cleaned_data'):
                continue

            if not form.cleaned_data.get('title'):
                form.cleaned_data['DELETE'] = True

            raw_title = form.cleaned_data.get('title', '').strip()
            if not raw_title:
                form.cleaned_data['DELETE'] = True


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


class CommentForm(ModelForm, SimpleForm):
    class Meta:
        fields = ['private_comment', 'public_comment']
        widgets = {
                'private_comment': Textarea( attrs = {
                        'class': SimpleForm.text_area_classes
                    }),
                'public_comment': Textarea( attrs = {
                        'class': SimpleForm.text_area_classes
                    })
            }
