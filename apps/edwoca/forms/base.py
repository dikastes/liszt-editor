from django.forms import ModelForm, TextInput, Select, HiddenInput, CheckboxInput, Textarea, CharField
from django.forms.models import inlineformset_factory, BaseInlineFormSet
from django.utils.safestring import mark_safe
from dominate.tags import div, label, span
from dominate.util import raw
from dmad_on_django.forms import SearchForm


class SimpleFormMixin:
    text_area_classes = 'textarea textarea-bordered w-full'
    text_input_classes = 'input input-bordered w-full'

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

        # checken ob das form initialisiert ist, sonst kein delete-button
        if 'DELETE' in self.fields and self.instance.pk:
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
                'person': HiddenInput(),
                'role': Select( attrs = {
                        'class': 'select w-full select-bordered'
                    }),
                'id': HiddenInput(),
                'DELETE': CheckboxInput( attrs = {
                        'class': 'flex-0'
                    })
            }

    def as_daisy(self):
        form = div(cls='mb-10')

        role_container = div(cls='flex-1')
        role_container.add(raw(str(self['role'])))

        form.add(role_container)

        return mark_safe(str(form))


class CommentForm(ModelForm, SimpleFormMixin):
    class Meta:
        fields = ['private_comment', 'public_comment']
        widgets = {
                'private_comment': Textarea( attrs = {
                        'class': SimpleFormMixin.text_area_classes
                    }),
                'public_comment': Textarea( attrs = {
                        'class': SimpleFormMixin.text_area_classes
                    })
            }


class BaseBibForm(ModelForm):
    class Meta:
        fields = [ 'bib', 'id' ]
        widgets = {
                'bib': Select( attrs = {
                        'class': 'autocomplete-select select select-bordered w-full'
                    }),
                'id': HiddenInput()
            }

    def as_daisy(self):
        form = div(cls='mb-10')

        if self.instance.pk:
           form.add(raw(str(self['id'])))

        bib_field = self['bib']

        bib_container = div(cls='flex-1')
        bib_container.add(raw(str(bib_field)))

        form.add(bib_container)

        return mark_safe(str(form))


class EdwocaSearchForm(SearchForm):
    q = CharField(required=False, widget=TextInput())


class HandwritingForm(ModelForm):
    class Meta:
        fields = ['medium', 'dubious_writer']
        widgets = {
                'medium': TextInput( attrs = {
                        'class': 'grow'
                    }),
                'dubious_writer': CheckboxInput( attrs = {
                        'class': 'toggle'
                    })
            }

    def as_daisy(self):
        form = div(cls='flex gap-5') # Add flex and gap classes to the main form div
        medium_field = self['medium']
        dubious_writer_field = self['dubious_writer']

        medium_label = label(medium_field.label, _for=medium_field.id_for_label, cls='input input-bordered flex items-center gap-2 flex-1') # Add flex-1 to medium label
        medium_label.add(raw(str(medium_field)))

        dubious_writer_label = label(_for=dubious_writer_field.id_for_label, cls='label cursor-pointer flex items-center gap-5')
        dubious_writer_label.add(span(dubious_writer_field.label, cls='label-text'))
        dubious_writer_label.add(raw(str(dubious_writer_field)))

        form.add(medium_label)
        form.add(dubious_writer_label)

        return mark_safe(str(form))
