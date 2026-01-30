from .base import *
from django.forms import HiddenInput, TextInput, ModelForm, Select
from dmrism.models.manifestation import Publication
from liszt_util.forms.forms import GenericAsDaisyMixin

class PublicationForm(GenericAsDaisyMixin, ModelForm):
    class Meta:
        model = Publication
        fields = ['assumed', 'inferred']
        widgets = {
            'assumed': CheckboxInput(attrs={'form': 'form', 'class': 'toggle' }),
            'inferred': CheckboxInput(attrs={'form': 'form', 'class': 'toggle' })
        }
