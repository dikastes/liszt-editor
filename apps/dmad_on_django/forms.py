from haystack.forms import SearchForm
from django.forms import TextInput, Textarea, ModelForm
from .models import Person
from liszt_util.forms.forms import GenericAsDaisyMixin
from liszt_util.forms.layouts import Layouts

formWidgets = {
        "interim_designator": TextInput(attrs={
                'class': 'input input-bordered'
            }),
        'gnd_id': TextInput(attrs={
                'class': 'input input-bordered'
            }),
        'comment': Textarea(attrs={
                'class': 'input input-bordered h-64'
            })
    }

class SearchForm(GenericAsDaisyMixin, SearchForm):
    layout = Layouts.LABEL_INSIDE

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['q'].widget.attrs.update({
                'class': 'w-full',
                'placeholder': 'Suche'
            })
        self.fields['q'].label = ''



class DmadUpdateForm(GenericAsDaisyMixin, ModelForm):
    layout = Layouts.LABEL_OUTSIDE


class DmadCreateForm(GenericAsDaisyMixin, ModelForm):
    layout = Layouts.LABEL_OUTSIDE

class DmadLinkForm(GenericAsDaisyMixin, ModelForm):
    layout = Layouts.LABEL_OUTSIDE
