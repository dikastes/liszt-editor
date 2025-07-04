from .base import *
from ..forms.manifestation import *
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import DeleteView
from django.views.generic.edit import CreateView, UpdateView


class ManifestationListView(EdwocaListView):
    model = Manifestation


class ManifestationSearchView(EdwocaSearchView):
    model = Manifestation


class ManifestationCreateView(CreateView):
    model = Manifestation
    form_class = ManifestationForm
    template_name = 'edwoca/create.html'

    def get_success_url(self):
        return reverse_lazy('edwoca:manifestation_update', kwargs = {'pk': self.object.id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'title_formset' not in context:
            if self.request.POST:
                context['title_formset'] = ManifestationTitleFormSet(self.request.POST, self.request.FILES)
            else:
                ManifestationTitleFormSet.can_delete = False
                context['title_form_set'] = ManifestationTitleFormSet()
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        title_formset = ManifestationTitleFormSet(self.request.POST, self.request.FILES, instance=self.object)

        if title_formset.is_valid():
            self.object.save()
            title_formset.save()
            return redirect(self.get_success_url())
        else:
            self.object = None
            return self.form_invalid(form, title_formset=title_formset)

    def form_invalid(self, form, title_formset=None):
        context = self.get_context_data(form=form, title_formset=title_formset)
        return self.render_to_response(context)


class ManifestationUpdateView(UpdateView):
    model = Manifestation
    form_class = ManifestationForm
    template_name = 'edwoca/simple_form.html'


class ManifestationDeleteView(DeleteView):
    model = Manifestation
    success_url = reverse_lazy('edwoca:manifestation_list')
    template_name = 'edwoca/simple_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class ManifestationTitleUpdateView(TitleUpdateView):
    model = Manifestation
    form_class = ManifestationTitleFormSet
    formset_property = 'titles'

    def get_success_url(self):
        return reverse_lazy('edwoca:manifestation_title', kwargs = {'pk': self.object.id})


class RelatedManifestationAddView(RelatedEntityAddView):
    template_name = 'edwoca/manifestation_relations.html'
    model = RelatedManifestation


class RelatedManifestationRemoveView(DeleteView):
    model = RelatedManifestation

    def get_success_url(self):
        return reverse_lazy('edwoca:manifestation_relations', kwargs={'pk': self.object.source_work.id})


class ManifestationContributorsUpdateView(ContributorsUpdateView):
    model = Manifestation


class ManifestationRelationsUpdateView(RelationsUpdateView):
    template_name = 'edwoca/manifestation_relations.html'
    model = Manifestation
    form_class = RelatedManifestationForm


class ManifestationHistoryUpdateView(SimpleFormView):
    model = Manifestation
    property = 'history'


class ManifestationBibliographyUpdateView(FormsetUpdateView):
    model = Manifestation
    form_class = ManifestationBibFormSet
    property = 'bib'

    def get_success_url(self):
        return reverse_lazy('edwoca:manifestation_bibliography', kwargs = {'pk': self.object.id})


class ManifestationCommentUpdateView(SimpleFormView):
    model = Manifestation
    property = 'comment'


class ManifestationPrintUpdateView(UpdateView):
    pass
    #model = Manifestation
    #property = 'print'


class ManifestationClassificationUpdateView(SimpleFormView):
    model = Manifestation
    property = 'classification'
