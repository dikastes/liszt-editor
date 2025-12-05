from django.forms import HiddenInput, TextInput, ModelForm
from dmrism.models.manifestation import Publication
from liszt_util.forms.forms import GenericAsDaisyMixin

class PublicationForm(GenericAsDaisyMixin, ModelForm):
    class Meta:
        model = Publication
        fields = ['publisher', 'plate_number']
        widgets = {
            'publisher': HiddenInput(),
            'plate_number': TextInput(attrs={'form': 'form', 'class': 'w-16'})
        }
