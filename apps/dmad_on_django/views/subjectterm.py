from dmad_on_django.models import Place, Person, Work, SubjectTerm
from dmad_on_django.forms import SearchForm
from django.shortcuts import render
from json import dumps
from .base import ( DmadCreateView, DmadUpdateView, LinkView,
UnlinkView, PullView, DmadSearchView, DeleteView )
from .base import get_link

class SubjectTermSearchView(DmadSearchView):
    model = SubjectTerm
    template_name = 'dmad_on_django/subjectterm_list.html'
    form_class = SearchForm
    search_field = "q"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        if self.kwargs.get('type') == 'rework':
            context['object_list'] = SubjectTerm.objects.filter(rework_in_gnd=True)
        elif self.kwargs.get('type') == 'stub':
            context['object_list'] = SubjectTerm.objects.filter(gnd_id__isnull=True)
        else:
            context['object_list'] = [result.object for result in context['object_list']]
        context.update({
            'type': self.kwargs.get('type'),
            'rework_count': SubjectTerm.objects.filter(rework_in_gnd=True).count(),
            'stub_count': SubjectTerm.objects.filter(gnd_id__isnull=True).count()
        })
        return context
    
def subject_term_list(request):
    context = {
        'objects': dumps([
            {
                'id': subject_term.id,
                'rendered_link': get_link(subject_term, 'subjectterm'),
                'rework_in_gnd': subject_term.rework_in_gnd,
                'gnd_id': subject_term.gnd_id
            }
            for subject_term in SubjectTerm.objects.all()
        ]),
    }
    return render(request, 'dmad_on_django/subjectterm_list.html', context)

class SubjectTermCreateView(DmadCreateView):
    model = SubjectTerm

class SubjectTermUpdateView(DmadUpdateView):
    model = SubjectTerm


class SubjectTermLinkView(LinkView):
    model = SubjectTerm


class SubjectTermUnlinkView(UnlinkView):
    model = SubjectTerm


class SubjectTermPullView(PullView):
    model = SubjectTerm

class SubjectTermDeleteView(DeleteView):
    model = SubjectTerm
