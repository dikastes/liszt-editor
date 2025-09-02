from haystack.forms import SearchForm
from django.forms import TextInput, Textarea
from .models import Person

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['q'].widget.attrs.update({
                'class': 'w-full',
                'placeholder': 'Suche'
            })
        self.fields['q'].label = ''

