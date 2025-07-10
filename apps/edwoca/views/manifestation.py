from .base import *
from ..forms.manifestation import *
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import DeleteView, FormView
from django.views.generic.edit import CreateView, UpdateView
from dmad_on_django.models import Place
from ..models.manifestation import ManifestationBib
from bib.models import ZotItem


class ManifestationMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entity_type'] = 'manifestation'
        return context


class ManifestationListView(EdwocaListView):
    model = Manifestation


class ManifestationSearchView(EdwocaSearchView):
    model = Manifestation


class ManifestationCreateView(ManifestationMixin, CreateView):
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


class ManifestationUpdateView(ManifestationMixin, UpdateView):
    model = Manifestation
    form_class = ManifestationForm
    template_name = 'edwoca/simple_form.html'


class ManifestationDeleteView(ManifestationMixin, DeleteView):
    model = Manifestation
    success_url = reverse_lazy('edwoca:manifestation_list')
    template_name = 'edwoca/simple_form.html'


class ManifestationTitleUpdateView(ManifestationMixin, TitleUpdateView):
    model = Manifestation
    form_class = ManifestationTitleFormSet
    formset_property = 'titles'

    def get_success_url(self):
        return reverse_lazy('edwoca:manifestation_title', kwargs = {'pk': self.object.id})


class RelatedManifestationAddView(ManifestationMixin, RelatedEntityAddView):
    template_name = 'edwoca/manifestation_relations.html'
    model = RelatedManifestation


class RelatedManifestationRemoveView(DeleteView):
    model = RelatedManifestation

    def get_success_url(self):
        return reverse_lazy('edwoca:manifestation_relations', kwargs={'pk': self.object.source_work.id})


class ManifestationContributorsUpdateView(ManifestationMixin, ContributorsUpdateView):
    model = Manifestation
    form_class = ManifestationContributorForm


class ManifestationContributorAddView(ManifestationMixin, ContributorAddView):
    model = ManifestationContributor


class ManifestationContributorRemoveView(DeleteView):
    model = ManifestationContributor

    def get_success_url(self):
        return reverse_lazy('edwoca:manifestation_contributors', kwargs={'pk': self.object.manifestation.id})


class ManifestationRelationsUpdateView(ManifestationMixin, RelationsUpdateView):
    template_name = 'edwoca/manifestation_relations.html'
    model = Manifestation
    form_class = RelatedManifestationForm


class ManifestationHistoryUpdateView(ManifestationMixin, SimpleFormView):
    model = Manifestation
    property = 'history'
    template_name = 'edwoca/manifestation_history.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_form = SearchForm(self.request.GET or None)
        context['searchform'] = search_form
        context['show_search_form'] = True

        if search_form.is_valid() and search_form.cleaned_data.get('q'):
            context['query'] = search_form.cleaned_data.get('q')
            context[f"found_places"] = search_form.search().models(Place)

        return context

    def get_model(self):
        return self.model.__name__


def manifestation_add_place_view(request, pk, place_id):
    manifestation = get_object_or_404(Manifestation, pk=pk)
    place = get_object_or_404(Place, pk=place_id)

    manifestation.place = place
    manifestation.save()

    return redirect('edwoca:manifestation_history', pk=pk)


def manifestation_remove_place_view(request, pk):
    manifestation = get_object_or_404(Manifestation, pk=pk)

    manifestation.place = None
    manifestation.save()

    return redirect('edwoca:manifestation_history', pk=pk)


class ManifestationBibAddView(FormView):
    def post(self, request, *args, **kwargs):
        manifestation_id = self.kwargs['pk']
        zotitem_key = self.kwargs['zotitem_key']
        manifestation = Manifestation.objects.get(pk=manifestation_id)
        zotitem = ZotItem.objects.get(zot_key=zotitem_key)
        ManifestationBib.objects.get_or_create(manifestation=manifestation, bib=zotitem)
        return redirect(reverse_lazy('edwoca:manifestation_bibliography', kwargs={'pk': manifestation_id}))

class ManifestationBibDeleteView(DeleteView):
    model = ManifestationBib

    def get_success_url(self):
        return reverse_lazy('edwoca:manifestation_bibliography', kwargs={'pk': self.object.manifestation.id})


class ManifestationBibliographyUpdateView(ManifestationMixin, UpdateView):
    model = Manifestation
    form_class = ManifestationBibForm
    property = 'bib'
    template_name = 'edwoca/bib_update.html'

    def get_success_url(self):
        return reverse_lazy('edwoca:manifestation_bibliography', kwargs = {'pk': self.object.id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_form = SearchForm(self.request.GET or None)
        context['searchform'] = search_form
        context['show_search_form'] = True

        if search_form.is_valid() and search_form.cleaned_data.get('q'):
            context['query'] = search_form.cleaned_data.get('q')
            context[f"found_bibs"] = search_form.search().models(ZotItem)
        return context


class ManifestationCommentUpdateView(ManifestationMixin, SimpleFormView):
    model = Manifestation
    property = 'comment'


class ManifestationPrintUpdateView(ManifestationMixin, UpdateView):
    pass
    #model = Manifestation
    #property = 'print'


class ManifestationClassificationUpdateView(ManifestationMixin, SimpleFormView):
    model = Manifestation
    property = 'classification'
