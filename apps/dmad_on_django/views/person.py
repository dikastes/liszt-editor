from django.urls import reverse_lazy
from django.shortcuts import render
from json import dumps
from dmad_on_django.models import Person, Work, Place
from dmad_on_django.forms import SearchForm

from .base import (DmadCreateView,DmadUpdateView, DeleteView,
                     LinkView, UnlinkView, PullView, DmadSearchView)

from .base import get_link, search_gnd, json_search

class PersonSearchView(DmadSearchView):
    model = Person
    template_name = 'dmad_on_django/person_list.html'
    form_class = SearchForm

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        if self.kwargs.get('type') == 'rework':
            context['object_list'] = Person.objects.filter(rework_in_gnd=True)
        elif self.kwargs.get('type') == 'stub':
            context['object_list'] = Person.objects.filter(gnd_id__isnull=True)
        else:
            context['object_list'] = [result.object for result in context['object_list']]
        context.update({
            'active': 'person',
            'type': self.kwargs.get('type'),
            'rework_count': Person.objects.filter(rework_in_gnd=True).count(),
            'stub_count': Person.objects.filter(gnd_id__isnull=True).count()
        })
        return context


def person_list(request):
    context = {
        'objects': dumps([
            {
                'id': person.id,
                'designator': person.get_designator(),
                'rendered_link': get_link(person, 'person'),
                'rework_in_gnd': person.rework_in_gnd,
                'gnd_id': person.gnd_id
            }
            for person in Person.objects.all()
        ]),
        'active': 'person',
        'person_count': Person.objects.count(),
        'work_count': Work.objects.count()
    }
    return render(request, 'dmad_on_django/person_list.html', context)


class PersonCreateView(DmadCreateView):
    model = Person


class PersonUpdateView(DmadUpdateView):
    model = Person


class PersonDeleteView(DeleteView):
    model = Person
    success_url = reverse_lazy('dmad_on_django:person_list')


class PersonLinkView(LinkView):
    model = Person

    def get_success_url(self):
        return reverse_lazy('dmad_on_django:person_update', kwargs={'pk': self.object.id})


class PersonUnlinkView(UnlinkView):
    model = Person


class PersonPullView(PullView):
    model = Person