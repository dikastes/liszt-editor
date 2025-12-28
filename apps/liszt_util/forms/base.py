from haystack.forms import SearchForm
from django.forms import SelectDateWidget as DjangoSelectDateWidget
from django.utils.translation import gettext_lazy as _
from .forms import GenericAsDaisyMixin


class SearchForm(GenericAsDaisyMixin, SearchForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'entity_type' in kwargs:
            placeholder = _(kwargs['entity_type'])
        else:
            placeholder = _('search')
        self.fields['q'].widget.attrs.update({
                'class': 'input input-bordered border-black bg-white flex-1 grow',
                'placeholder': placeholder
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
