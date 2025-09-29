from django import forms
from dmrism.models.manifestation import Publication
from liszt_util.forms.forms import GenericAsDaisyMixin

class PublicationForm(GenericAsDaisyMixin, forms.ModelForm):
    class Meta:
        model = Publication
        fields = ['publisher', 'plate_number']
        widgets = {
            'publisher': forms.HiddenInput(),
        }
