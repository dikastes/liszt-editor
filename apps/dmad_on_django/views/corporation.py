from django.urls import reverse_lazy
from django.shortcuts import render
from json import dumps
from dmad_on_django.models import Corporation, Work, Place
from dmad_on_django.forms import SearchForm

from .base import (DmadCreateView,DmadUpdateView, DeleteView,
                     LinkView, UnlinkView, PullView, DmadSearchView)

from .base import get_link, search_gnd, json_search

class CorporationSearchView(DmadSearchView):
    model = Corporation
    template_name = 'dmad_on_django/corporation_list.html'
    form_class = SearchForm

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        if self.kwargs.get('type') == 'rework':
            context['object_list'] = Corporation.objects.filter(rework_in_gnd=True)
        elif self.kwargs.get('type') == 'stub':
            context['object_list'] = Corporation.objects.filter(gnd_id__isnull=True)
        else:
            context['object_list'] = [result.object for result in context['object_list']]
        context.update({
            'active': 'corporation',
            'type': self.kwargs.get('type'),
            'rework_count': Corporation.objects.filter(rework_in_gnd=True).count(),
            'stub_count': Corporation.objects.filter(gnd_id__isnull=True).count()
        })
        return context


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
