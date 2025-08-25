from haystack.forms import SearchForm


class SearchForm(SearchForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['q'].widget.attrs.update({
                'class': 'input input-bordered',
                'placeholder': 'Suche'
            })
        self.fields['q'].label = ''
