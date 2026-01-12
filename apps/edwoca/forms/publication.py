from .base import *
from django.forms import HiddenInput, TextInput, ModelForm, Select
from dmrism.models.manifestation import Publication
from liszt_util.forms.forms import GenericAsDaisyMixin

class PublicationForm(GenericAsDaisyMixin, ModelForm):
    class Meta:
        model = Publication
        fields = ['publisher', 'place_status']
        widgets = {
            'publisher': HiddenInput(),
            'place_status': Select(attrs={'form': 'form', 'class': SimpleFormMixin.select_classes })
        }
