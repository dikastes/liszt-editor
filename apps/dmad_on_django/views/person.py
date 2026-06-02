from django.urls import reverse_lazy
from django.shortcuts import render
from json import dumps
from dmad_on_django.models import Person, Work, Place
from .base import *

class PersonSearchView(DmadSearchView):
    model = Person


class PersonListView(DmadListView):
    model = Person


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
