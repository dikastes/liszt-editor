from django.urls import reverse_lazy
from django.shortcuts import render
from json import dumps
from dmad_on_django.models import Corporation, Work, Place
from .base import *

class CorporationSearchView(DmadSearchView):
    model = Corporation


class CorporationListView(DmadListView):
    model = Corporation


def corporation_list(request):
    context = {
        'objects': dumps([
            {
                'id': corporation.id,
                'designator': corporation.get_designator(),
                'rendered_link': get_link(corporation, 'corporation'),
                'rework_in_gnd': corporation.rework_in_gnd,
                'gnd_id': corporation.gnd_id
            }
            for corporation in Corporation.objects.all()
        ]),
        'active': 'corporation',
        'corporation_count': Corporation.objects.count(),
        'work_count': Work.objects.count()
    }
    return render(request, 'dmad_on_django/corporation_list.html', context)


class CorporationCreateView(DmadCreateView):
    model = Corporation


class CorporationUpdateView(DmadUpdateView):
    model = Corporation


class CorporationDeleteView(DeleteView):
    model = Corporation
    success_url = reverse_lazy('dmad_on_django:corporation_list')


class CorporationLinkView(LinkView):
    model = Corporation

    def get_success_url(self):
        return reverse_lazy('dmad_on_django:corporation_update', kwargs={'pk': self.object.id})


class CorporationUnlinkView(UnlinkView):
    model = Corporation


class CorporationPullView(PullView):
    model = Corporation
