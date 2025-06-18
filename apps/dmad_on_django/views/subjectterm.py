from dmad_on_django.models import Place, Person, Work, Subjectterm
from dmad_on_django.forms import SearchForm
from django.shortcuts import render
from json import dumps
from .base import ( DmadCreateView, DmadUpdateView, LinkView,
UnlinkView, PullView, DmadSearchView, DeleteView )
from .base import get_link

class SubjecttermSearchView(DmadSearchView):
    model = Subjectterm
    template_name = 'dmad_on_django/subjectterm_list.html'
    form_class = SearchForm
    search_field = "q"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        if self.kwargs.get('type') == 'rework':
            context['object_list'] = Subjectterm.objects.filter(rework_in_gnd=True)
        elif self.kwargs.get('type') == 'stub':
            context['object_list'] = Subjectterm.objects.filter(gnd_id__isnull=True)
        else:
            context['object_list'] = [result.object for result in context['object_list']]
        context.update({
            'type': self.kwargs.get('type'),
            'rework_count': Subjectterm.objects.filter(rework_in_gnd=True).count(),
            'stub_count': Subjectterm.objects.filter(gnd_id__isnull=True).count()
        })
        return context
    
def subjectterm_list(request):
    context = {
        'objects': dumps([
            {
                'id': subjectterm.id,
                'rendered_link': get_link(subjectterm, 'subjectterm'),
                'rework_in_gnd': subjectterm.rework_in_gnd,
                'gnd_id': subjectterm.gnd_id
            }
            for subjectterm in Subjectterm.objects.all()
        ]),
    }
    return render(request, 'dmad_on_django/subjectterm_list.html', context)

class SubjecttermCreateView(DmadCreateView):
    model = Subjectterm

class SubjecttermUpdateView(DmadUpdateView):
    model = Subjectterm


class SubjecttermLinkView(LinkView):
    model = Subjectterm


class SubjecttermUnlinkView(UnlinkView):
    model = Subjectterm


class SubjecttermPullView(PullView):
    model = Subjectterm

class SubjecttermDeleteView(DeleteView):
    model = Subjectterm