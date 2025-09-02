from dmrism.models import ManifestationTitle
from django.forms import ModelForm, Textarea, TextInput, Select, HiddenInput
from dominate.tags import div, label
from dominate.util import raw
from django.utils.safestring import mark_safe


class ManifestationTitleForm(ModelForm):
    class Meta:
        model = ManifestationTitle
        fields = ['title', 'title_type', 'status', 'manifestation']
        widgets = {
            'title': Textarea(attrs={'class': 'textarea textarea-bordered h-64'}),
            'title_type': Select(attrs={'class': 'select select-bordered w-full'}),
            'status': Select(attrs={'class': 'select select-bordered w-full'}),
            'manifestation': HiddenInput(),
        }

    def as_daisy(self):
        form = div(cls='flex flex-col gap-5')

        # Title field (textarea)
        title_label = label(self['title'].label, _for=self['title'].id_for_label, cls='form-control w-full')
        title_label.add(raw(str(self['title'])))
        form.add(title_label)

        # Remaining properties on a palette with flex-1
        palette = div(cls='flex flex-wrap gap-5')
        for field_name in ['title_type', 'status']:
            field = self[field_name]
            field_label = label(field.label, _for=field.id_for_label, cls='form-control flex-1 min-w-[200px]')
            field_label.add(raw(str(field)))
            palette.add(field_label)
        form.add(palette)

        return mark_safe(str(form))
