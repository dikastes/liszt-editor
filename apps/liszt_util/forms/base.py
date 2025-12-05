from haystack.forms import SearchForm
from django.forms import SelectDateWidget as DjangoSelectDateWidget


class SearchForm(SearchForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['q'].widget.attrs.update({
                'class': 'input input-bordered border-black bg-white flex-0 grow',
                'placeholder': 'Suche'
            })
        self.fields['q'].label = ''


class SelectDateWidget(DjangoSelectDateWidget):
    DEFAULT_ATTRS = 'select select-bordered bg-white border-black'

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)

        for sub in context['widget']['subwidgets']:
            sub_name = sub.get('name', '')
            sub['attrs']['class'] = self.DEFAULT_ATTRS

            if sub_name.endswith('_day') or sub_name.endswith('_month'):
                sub['attrs']['class'] = self.DEFAULT_ATTRS + ' border-r-0'

        return context
