from django.urls import reverse_lazy
from django.shortcuts import render
from haystack.generic_views import SearchView
from dmad_on_django.models import Work
from .base import *


def work_list(request):
    context = {
        'objects': [{'id': work.id, 'designator': work.designator()} for work in Work.objects.all()],
        'active': 'work'
    }
    return render(request, 'dmad_on_django/work_list.html', context)


class WorkSearchView(DmadSearchView):
    model=Work


class WorkListView(DmadListView):
    model=Work


class WorkCreateView(DmadCreateView):
    model = Work

    def get_success_url(self):
        return reverse_lazy('dmad_on_django:work_update', kwargs={'pk': self.object.id})


class WorkUpdateView(DmadUpdateView):
    model = Work


class WorkDeleteView(DeleteView):
    model = Work
    success_url = reverse_lazy('dmad_on_django:work_list')


class WorkLinkView(LinkView):
    model = Work

    def get_success_url(self):
        return reverse_lazy('dmad_on_django:work_update', kwargs={'pk': self.object.id})


class WorkUnlinkView(UnlinkView):
    model = Work


class WorkPullView(PullView):
    model = Work
