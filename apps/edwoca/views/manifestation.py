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
        if self.request.POST:
            context['title_formset'] = ManifestationTitleFormSet(self.request.POST)
        else:
            ManifestationTitleFormSet.can_delete = False
            context['title_form_set'] = ManifestationTitleFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        title_formset = context['title_formset']

        if title_formset.is_valid():
            response = super().form_valid(form)
            self.object = form.save()
            title_formset.instance = self.object
            title_formset.save()
            self.object.save()
            return response
        else:
            return self.form_invalid(form)


class ManifestationUpdateView(UpdateView):
    model = Manifestation
    form_class = ManifestationForm
    template_name = 'edwoca/simple_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['view_title'] = f"Manifestation { self.object } bearbeiten"
        context['button_label'] = "speichern"
        context['return_target'] = 'edwoca:manifestation_detail'
        context['return_pk'] = self.object.id
        return context


class ManifestationDeleteView(DeleteView):
    model = Manifestation
    success_url = reverse_lazy('edwoca:manifestation_list')
    template_name = 'edwoca/simple_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class ManifestationTitleUpdateView(FormsetUpdateView):
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
