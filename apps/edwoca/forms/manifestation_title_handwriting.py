from dmrism.models import ManifestationTitleHandwriting
from django.forms import ModelForm, TextInput, Select, HiddenInput, CheckboxInput
from dominate.tags import div, label, span
from dominate.util import raw
from django.utils.safestring import mark_safe


class ManifestationTitleHandwritingForm(ModelForm):
    class Meta:
        model = ManifestationTitleHandwriting
        fields = ['medium', 'manifestation_title', 'dubious_writer']
        widgets = {
            'medium': TextInput(attrs={'class': 'w-full'}),
            'manifestation_title': HiddenInput(),
            'dubious_writer': CheckboxInput(attrs={'class': 'toggle'}),
        }

    def as_daisy(self):
        form = div(cls='flex flex-col gap-5')

        # Fields for the palette
        palette = div(cls='flex flex-wrap gap-5')

        medium_field = self['medium']
        medium_label = label(medium_field.label, _for=medium_field.id_for_label, cls='input input-bordered flex items-center gap-2 flex-1')
        medium_label.add(raw(str(medium_field)))
        palette.add(medium_label)

        dubious_writer_field = self['dubious_writer']
        dubious_writer_label = label(_for=dubious_writer_field.id_for_label, cls='label cursor-pointer flex items-center gap-5')
        dubious_writer_label.add(span(dubious_writer_field.label, cls='label-text'))
        dubious_writer_label.add(raw(str(dubious_writer_field)))
        palette.add(dubious_writer_label)

        form.add(palette)
        form.add(raw(str(self['manifestation_title'])))

        return mark_safe(str(form))