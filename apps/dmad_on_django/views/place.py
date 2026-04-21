from django.urls import reverse_lazy
from django.shortcuts import render
from .base import DmadSearchView
from json import dumps
from dmad_on_django.models import Place, Person, Work
from .base import *


class PlaceSearchView(DmadSearchView):
    model = Place


class PlaceListView(DmadListView):
    model = Place


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
