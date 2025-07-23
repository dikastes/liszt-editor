from django.urls import reverse_lazy
from django.shortcuts import render
from haystack.generic_views import SearchView

from dmad_on_django.models import Work
from dmad_on_django.forms import SearchForm
from .base import DmadCreateView, DmadUpdateView, DeleteView, LinkView, UnlinkView, PullView, DmadSearchView

def work_list(request):
    context = {
        'objects': [{'id': work.id, 'designator': work.designator()} for work in Work.objects.all()],
        'active': 'work'
    }
    return render(request, 'dmad_on_django/work_list.html', context)


class WorkSearchView(DmadSearchView):
    model=Work
    template_name='dmad_on_django/work_list.html'
    form_class = SearchForm
    search_field = "q"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        if self.kwargs.get('type') == 'rework':
            context['object_list'] = Work.objects.filter(rework_in_gnd=True)
        elif self.kwargs.get('type') == 'stub':
            context['object_list'] = Work.objects.filter(gnd_id__isnull=True)
        else:
            context['object_list'] = [result.object for result in context['object_list']]
        context.update({
            'type': self.kwargs.get('type'),
            'rework_count': Work.objects.filter(rework_in_gnd=True).count(),
            'stub_count': Work.objects.filter(gnd_id__isnull=True).count()
        })
        return context


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