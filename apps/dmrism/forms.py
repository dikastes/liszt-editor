from .models import Manifestation
from django.forms import ModelForm, TextInput, Textarea
from dominate.tags import div, label, span
from dominate.util import raw
from django.utils.safestring import mark_safe


class ManifestationEditForm(ModelForm):
    class Meta:
        model = Manifestation
        fields = ['rism_id']
        widgets = {
                'rism_id': TextInput( attrs = {
                        'class': 'grow h-full'
                    })
            }

    def as_daisy(self):
        form = div()
        rism_id_label = label(self['rism_id'].label, _for=self['rism_id'].id_for_label, cls='input input-bordered flex items-center gap-2 my-5')
        rism_id_label.add(raw(str(self['rism_id'])))
        form.add(rism_id_label)

        return mark_safe(str(form))
