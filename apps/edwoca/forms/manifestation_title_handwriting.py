from dmrism.models import ManifestationTitleHandwriting
from django.forms import ModelForm, TextInput, Select, HiddenInput
from dominate.tags import div, label
from dominate.util import raw
from django.utils.safestring import mark_safe


class ManifestationTitleHandwritingForm(ModelForm):
    class Meta:
        model = ManifestationTitleHandwriting
        fields = ['medium', 'manifestation_title']
        widgets = {
            'medium': TextInput(attrs={'class': 'w-full'}),
            'manifestation_title': HiddenInput(),
        }

    def as_daisy(self):
        form = div(cls='flex flex-col gap-4')

        # Fields for the palette
        palette = div(cls='flex flex-wrap gap-4')

        medium_field = self['medium']
        medium_label = label(medium_field.label, _for=medium_field.id_for_label, cls='input input-bordered flex items-center gap-2 flex-1')
        medium_label.add(raw(str(medium_field)))
        palette.add(medium_label)

        form.add(palette)
        form.add(raw(str(self['manifestation_title'])))

        return mark_safe(str(form))