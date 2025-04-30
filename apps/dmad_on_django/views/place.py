from django.urls import reverse_lazy
from django.shortcuts import render
from haystack.generic_views import SearchView
from json import dumps

from dmad_on_django.models import Place, Person, Work
from dmad_on_django.forms import SearchForm
from .base import DmadCreateView, DmadUpdateView, LinkView, UnlinkView, PullView
from .base import get_link

class PlaceSearchView(SearchView):
    template_name = 'dmad_on_django/place_list.html'
    form_class = SearchForm

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        if self.kwargs.get('type') == 'rework':
            context['object_list'] = Place.objects.filter(rework_in_gnd=True)
        elif self.kwargs.get('type') == 'stub':
            context['object_list'] = Place.objects.filter(gnd_id__isnull=True)
        else:
            context['object_list'] = [result.object for result in context['object_list']]
        context.update({
            'active': 'place',
            'type': self.kwargs.get('type'),
            'person_count': Person.objects.count(),
            'work_count': Work.objects.count(),
            'rework_count': Person.objects.filter(rework_in_gnd=True).count(),
            'stub_count': Person.objects.filter(gnd_id__isnull=True).count(),
            'place_count': Place.objects.count()
        })
        return context
    
    def form_invalid(self, form):
        if self.request.htmx:
            context = self.get_context_data(**{
                    self.form_name: form,
                    'object_list': self.get_queryset()
                })
            return render(self.request, 'dmad_on_django/partials/search_results.html', context)
        return super().form_invalid(form)

    def form_valid(self, form):
        if self.request.htmx:
            self.queryset = form.search()
            context = self.get_context_data(**{
                    self.form_name: form,
                    'query': form.cleaned_data.get(self.search_field),
                    'object_list': self.queryset
                })
            return render(self.request, 'dmad_on_django/partials/search_results.html', context)
        return super().form_valid(form)


def place_list(request):
    context = {
        'objects': dumps([
            {
                'id': place.id,
                'designator': place.get_designator(),
                'rendered_link': get_link(place, 'place'),
                'rework_in_gnd': place.rework_in_gnd,
                'gnd_id': place.gnd_id
            }
            for place in Place.objects.all()
        ]),
        'active': 'place',
        'person_count': Person.objects.count(),
        'work_count': Work.objects.count(),
        'place_count': Place.objects.count()
    }
    return render(request, 'dmad_on_django/place_list.html', context)


class PlaceCreateView(DmadCreateView):
    model = Place


class PlaceUpdateView(DmadUpdateView):
    model = Place


class PlaceLinkView(LinkView):
    model = Place


class PlaceUnlinkView(UnlinkView):
    model = Place


class PlacePullView(PullView):
    model = Place