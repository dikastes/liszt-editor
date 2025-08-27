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

class SearchForm(SearchForm):

    layout = Layouts.LABEL_INSIDE

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['q'].widget.attrs.update({
                'class': 'input input-bordered',
                'placeholder': 'Suche'
            })
        self.fields['q'].label = ''

class AsDaisyModelForm(GenericAsDaisyMixin, ModelForm):
    layout = Layouts.LABEL_INSIDE

