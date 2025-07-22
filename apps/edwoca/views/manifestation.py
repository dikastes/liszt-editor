from .base import *
from ..forms.manifestation import *
from ..forms import ManifestationForm, SignatureFormSet
from django.forms import inlineformset_factory
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy, reverse
from django.views.generic import DeleteView, FormView
from django.views.generic.edit import CreateView, UpdateView
from dmad_on_django.models import Place
from ..models.manifestation import ManifestationBib
from ..models.item import Signature
from bib.models import ZotItem


class ManifestationListView(EdwocaListView):
    model = Manifestation


class ManifestationSearchView(EdwocaSearchView):
    model = Manifestation


class ManifestationCreateView(CreateView):
    model = Manifestation
    form_class = ManifestationForm
    template_name = 'edwoca/create.html'

    def get_success_url(self):
        return self.object.get_absolute_url()

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


#class ManifestationUpdateView(EntityMixin, UpdateView):
    #model = Manifestation
    #form_class = ManifestationForm
    #template_name = 'edwoca/manifestation_update.html'

def manifestation_update(request, pk):
    manifestation = Manifestation.objects.get(id=pk)
    context = {
        'object': manifestation,
        'entity_type': 'manifestation'
    }

    if manifestation.is_singleton:
        item = manifestation.items.first()
        manifestation_form = ManifestationForm(request.POST or None, instance=manifestation)
        context['manifestation_form'] = manifestation_form

        if 'add_signature' in request.POST:
            data = request.POST.copy()
            total_forms = int(data.get(f'signatures-TOTAL_FORMS', 0))
            data[f'signatures-TOTAL_FORMS'] = str(total_forms + 1)
            signature_formset = SignatureFormSet(data, instance=item)
        else:
            signature_formset = SignatureFormSet(request.POST or None, instance=item)

        if request.method == 'POST' and 'save_changes' in request.POST:
            if item and manifestation_form.is_valid():
                manifestation_form.save()
            if signature_formset.is_valid():
                signature_formset.save()
            return redirect('edwoca:manifestation_update', pk=pk)

        context['signature_formset'] = signature_formset
        context['library_search_form'] = SearchForm()
    else:
        if request.method == 'POST' and 'save_changes' in request.POST:
            for item in manifestation.items.all():
                manifestation_form = ManifestationForm(request.POST, instance=item, prefix=f'item_{item.id}')
                if manifestation_form.is_valid():
                    manifestation_form.save()

                signature_formset = SignatureFormSet(request.POST, instance=item, prefix=f'signatures_{item.id}')
                if signature_formset.is_valid():
                    signature_formset.save()

            new_item_form = ManifestationForm(request.POST, prefix='new_item')
            if new_item_form.is_valid() and new_item_form.has_changed():
                new_item = new_item_form.save(commit=False)
                new_item.manifestation = manifestation
                new_item.save()
                new_signature_formset = SignatureFormSet(request.POST, instance=new_item, prefix='new_signatures')
                if new_signature_formset.is_valid():
                    new_signature_formset.save()

            return redirect('edwoca:manifestation_update', pk=pk)

        item_forms = []
        for item in manifestation.items.all():
            signature_prefix = f'signatures_{item.id}'

            signature_formset_data = request.POST or None

            if f'add_signature_{item.id}' in request.POST:
                data = request.POST.copy()
                total_forms = int(data.get(f'{signature_prefix}-TOTAL_FORMS', 0))
                data[f'{signature_prefix}-TOTAL_FORMS'] = str(total_forms + 1)
                signature_formset_data = data

            item_forms.append({
                'item': item,
                'signature_formset': SignatureFormSet(signature_formset_data, instance=item, prefix=signature_prefix)
            })

        new_signature_formset = SignatureFormSet(request.POST or None, prefix='new_signatures')

        context['item_forms'] = item_forms
        context['new_signature_formset'] = new_signature_formset

    return render(request, 'edwoca/manifestation_update.html', context)


def manifestation_set_singleton(request, pk):
    manifestation = Manifestation.objects.get(id = pk)
    manifestation.set_singleton()
    manifestation.save()
    return redirect('edwoca:manifestation_update', pk = pk)


def manifestation_unset_singleton(request, pk):
    manifestation = Manifestation.objects.get(id = pk)
    manifestation.unset_singleton()
    manifestation.save()
    return redirect('edwoca:manifestation_update', pk = pk)


def manifestation_set_missing(request, pk):
    manifestation = Manifestation.objects.get(id = pk)
    manifestation.set_missing()
    manifestation.save()
    return redirect('edwoca:manifestation_update', pk = pk)


def manifestation_unset_missing(request, pk):
    manifestation = Manifestation.objects.get(id = pk)
    manifestation.unset_missing()
    manifestation.save()
    return redirect('edwoca:manifestation_update', pk = pk)


class ManifestationDeleteView(EntityMixin, DeleteView):
    model = Manifestation
    success_url = reverse_lazy('edwoca:manifestation_list')
    template_name = 'edwoca/simple_form.html'


class ManifestationTitleUpdateView(EntityMixin, TitleUpdateView):
    model = Manifestation
    form_class = ManifestationTitleFormSet
    formset_property = 'titles'

    def get_success_url(self):
        return reverse_lazy('edwoca:manifestation_title', kwargs = {'pk': self.object.id})


class RelatedManifestationAddView(EntityMixin, RelatedEntityAddView):
    template_name = 'edwoca/manifestation_relations.html'
    model = RelatedManifestation


class RelatedManifestationRemoveView(DeleteView):
    model = RelatedManifestation

    def get_success_url(self):
        return reverse_lazy('edwoca:manifestation_relations', kwargs={'pk': self.object.source_work.id})


class ManifestationContributorsUpdateView(EntityMixin, ContributorsUpdateView):
    model = Manifestation
    form_class = ManifestationContributorForm


class ManifestationContributorAddView(ContributorAddView):
    model = ManifestationContributor


class ManifestationContributorRemoveView(DeleteView):
    model = ManifestationContributor

    def get_success_url(self):
        return reverse_lazy('edwoca:manifestation_contributors', kwargs={'pk': self.object.manifestation.id})


class ManifestationRelationsUpdateView(EntityMixin, RelationsUpdateView):
    template_name = 'edwoca/manifestation_relations.html'
    model = Manifestation
    form_class = RelatedManifestationForm


class ManifestationHistoryUpdateView(SimpleFormView):
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


class ManifestationBibliographyUpdateView(EntityMixin, UpdateView):
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


class ManifestationCommentUpdateView(SimpleFormView):
    model = Manifestation
    property = 'comment'


class ManifestationPrintUpdateView(EntityMixin, UpdateView):
    pass
    #model = Manifestation
    #property = 'print'


class ManifestationClassificationUpdateView(SimpleFormView):
    model = Manifestation
    property = 'classification'
