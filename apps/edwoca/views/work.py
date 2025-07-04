from .base import *
from ..forms.work import *
from django.forms.models import formset_factory
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import DeleteView
from django.views.generic.edit import CreateView, ModelFormMixin


class WorkListView(EdwocaListView):
    model = Work



class WorkCreateView(CreateView):
    model = Work
    form_class = WorkForm
    template_name = 'edwoca/create.html'

    def get_success_url(self):
        return reverse_lazy('edwoca:work_update', kwargs = {'pk': self.object.id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'title_formset' not in context:
            if self.request.POST:
                context['title_formset'] = WorkTitleFormSet(self.request.POST, self.request.FILES)
            else:
                WorkTitleFormSet.can_delete = False
                context['title_form_set'] = WorkTitleFormSet()
        context['view_title'] = f"Neues Werk anlegen"
        context['button_label'] = "speichern"
        context['return_target'] = 'edwoca:index'
        context['return_pk'] = None
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        title_formset = WorkTitleFormSet(self.request.POST, self.request.FILES, instance=self.object)

        if title_formset.is_valid():
            self.object.save()
            title_formset.save()
            return redirect(self.get_success_url())
        else:
            self.object = None # Reset object so get_context_data doesn't try to use it for instance
            return self.form_invalid(form, title_formset=title_formset)

    def form_invalid(self, form, title_formset=None):
        context = self.get_context_data(form=form, title_formset=title_formset)
        return self.render_to_response(context)


class WorkUpdateView(UpdateView):
    model = Work
    form_class = WorkForm
    template_name = 'edwoca/work_update.html'
    context_object_name = 'work'


class WorkDeleteView(DeleteView):
    model = Work
    success_url = reverse_lazy('edwoca:index')
    template_name = 'edwoca/simple_form.html'
    context_object_name = 'work'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class WorkTitleUpdateView(TitleUpdateView):
    model = Work
    form_class = WorkTitleFormSet
    formset_property = 'titles'

    def get_success_url(self):
        return reverse_lazy('edwoca:work_title', kwargs = {'pk': self.object.id})


class WorkRelationsUpdateView(RelationsUpdateView):
    template_name = 'edwoca/work_relations.html'
    model = Work
    form_class = RelatedWorkForm


class WorkRelatedWorksUpdateView(UpdateView):
    model = Work
    fields = []
    template_name = 'edwoca/work_related_works.html'


class RelatedWorkAddView(RelatedEntityAddView):
    template_name = 'edwoca/work_relations.html'
    model = RelatedWork


class RelatedWorkRemoveView(DeleteView):
    model = RelatedWork

    def get_success_url(self):
        return reverse_lazy('edwoca:work_relations', kwargs={'pk': self.object.source_work.id})


class WorkSearchView(EdwocaSearchView):
    model = Work


class WorkBibView(ModelFormMixin):
    model = WorkBib
    fields = [
            'bib',
            'work'
        ]


class WorkContributorsUpdateView(ContributorsUpdateView):
    model = Work


class WorkHistoryUpdateView(SimpleFormView):
    model = Work
    property = 'history'


class WorkBibliographyUpdateView(FormsetUpdateView):
    model = Work
    form_class = WorkBibFormSet
    property = 'bib'

    def get_success_url(self):
        return reverse_lazy('edwoca:work_bibliography', kwargs = {'pk': self.object.id})


class WorkCommentUpdateView(SimpleFormView):
    model = Work
    property = 'comment'
