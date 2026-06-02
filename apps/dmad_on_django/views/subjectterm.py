from dmad_on_django.models import Place, Person, Work, SubjectTerm
from django.shortcuts import render
from json import dumps
from .base import *


class SubjectTermSearchView(DmadSearchView):
    model = SubjectTerm


class SubjectTermListView(DmadListView):
    model = SubjectTerm


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
