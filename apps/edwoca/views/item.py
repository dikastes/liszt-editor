from .base import *
from ..forms.item import *
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse_lazy, reverse
from django.views.generic import DeleteView, ListView
from django.views.generic.edit import CreateView, UpdateView
from ..models import Item as EdwocaItem
from dmrism.models.item import Item, PersonProvenanceStation, CorporationProvenanceStation, DigitalCopy
from dmad_on_django.forms import SearchForm
from dmad_on_django.models import Person, Corporation
from bib.models import ZotItem


class ItemListView(EdwocaListView):
    model = EdwocaItem


class ItemSearchView(EdwocaSearchView):
    model = EdwocaItem


def item_update(request, pk):
    item = get_object_or_404(Item, pk=pk)
    form = ItemForm(request.POST or None, instance=item)

    if request.POST and 'add_signature' in request.POST:
        data = request.POST.copy()
        total_forms = int(data.get('signatures-TOTAL_FORMS', 0))
        data['signatures-TOTAL_FORMS'] = str(total_forms + 1)
        signature_formset = SignatureFormSet(data, instance=item)
    else:
        signature_formset = SignatureFormSet(request.POST or None, instance=item)

    if request.method == 'POST' and 'add_signature' not in request.POST:
        if form.is_valid() and signature_formset.is_valid():
            form.save()
            signature_formset.save()
            return redirect('edwoca:item_update', pk=pk)

    context = {
        'object': item,
        'form': form,
        'signature_formset': signature_formset,
        'entity_type': 'item',
    }
    return render(request, 'edwoca/item_update.html', context)



class ItemCreateView(EntityMixin, CreateView):
    model = EdwocaItem
    form_class = ItemForm
    template_name = 'edwoca/create.html'

    def get_success_url(self):
        return reverse_lazy('edwoca:item_update', kwargs = {'pk': self.object.id})

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.manifestation = Manifestation.objects.get(id=self.kwargs['manifestation_id'])
        self.object.save()
        return redirect(self.get_success_url())


class ItemRelationsUpdateView(EntityMixin, RelationsUpdateView):
    template_name = 'edwoca/item_relations.html'
    model = Item
    form_class = RelatedItemForm


class RelatedItemAddView(RelatedEntityAddView):
    template_name = 'edwoca/item_relations.html'
    model = RelatedItem


class RelatedItemRemoveView(DeleteView):
    model = RelatedItem

    def get_success_url(self):
        return reverse_lazy('edwoca:item_relations', kwargs={'pk': self.object.source_item.id})


class ItemContributorsUpdateView(EntityMixin, ContributorsUpdateView):
    model = Item
    form_class = ItemContributorForm


class ItemContributorAddView(ContributorAddView):
    model = ItemContributor


class ItemContributorRemoveView(DeleteView):
    model = ItemContributor

    def get_success_url(self):
        return reverse_lazy('edwoca:item_contributors', kwargs={'pk': self.object.item.id})


def item_provenance(request, pk):
    item = get_object_or_404(Item, pk=pk)
    context = {
        'object': item,
        'entity_type': 'item',
    }

    if request.method == 'POST':
        for pps_obj in item.person_provenance_stations.all():
            prefix = f'person_provenance_{pps_obj.id}'
            pps_form = PersonProvenanceStationForm(request.POST, instance=pps_obj, prefix=prefix)
            if pps_form.is_valid():
                pps_form.save()

        for cps_obj in item.corporation_provenance_stations.all():
            prefix = f'corporation_provenance_{cps_obj.id}'
            cps_form = CorporationProvenanceStationForm(request.POST, instance=cps_obj, prefix=prefix)
            if cps_form.is_valid():
                cps_form.save()

        provenance_comment_form = ItemProvenanceCommentForm(request.POST, instance=item)
        if provenance_comment_form.is_valid():
            provenance_comment_form.save()

        return redirect('edwoca:item_provenance', pk=pk)
    else:
        person_provenance_forms = []
        for pps_obj in item.person_provenance_stations.all():
            prefix = f'person_provenance_{pps_obj.id}'
            person_provenance_forms.append(PersonProvenanceStationForm(instance=pps_obj, prefix=prefix))
        context['person_provenance_forms'] = person_provenance_forms

        corporation_provenance_forms = []
        for cps_obj in item.corporation_provenance_stations.all():
            prefix = f'corporation_provenance_{cps_obj.id}'
            corporation_provenance_forms.append(CorporationProvenanceStationForm(instance=cps_obj, prefix=prefix))
        context['corporation_provenance_forms'] = corporation_provenance_forms

        provenance_comment_form = ItemProvenanceCommentForm(instance=item)
        context['provenance_comment_form'] = provenance_comment_form

    q_bib = request.GET.get('bib-q')
    q_owner = request.GET.get('owner-q')

    if q_bib:
        bib_search_form = SearchForm(request.GET, prefix='bib')
        if bib_search_form.is_valid():
            context['query_bib'] = bib_search_form.cleaned_data.get('q')
            context['found_bibs'] = bib_search_form.search().models(ZotItem)
    else:
        bib_search_form = SearchForm(prefix='bib')

    if q_owner:
        owner_search_form = SearchForm(request.GET, prefix='owner')
        if owner_search_form.is_valid():
            context['query_owner'] = owner_search_form.cleaned_data.get('q')
            context['found_persons'] = owner_search_form.search().models(Person)
            context['found_corporations'] = owner_search_form.search().models(Corporation)
    else:
        owner_search_form = SearchForm(prefix='owner')

    context['bib_search_form'] = bib_search_form
    context['owner_search_form'] = owner_search_form

    return render(request, 'edwoca/item_provenance.html', context)


class ItemDigCopyView(SimpleFormView):
    model = Item
    property = 'digitized_copy'
    template_name = 'edwoca/item_digcopy.html'
    form_class = ItemDigitizedCopyForm

    def get_object(self):
        item = get_object_or_404(self.model, pk=self.kwargs['pk'])
        return item.digital_copies.first() or DigitalCopy(item=item)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        item = get_object_or_404(Item, pk=self.kwargs['pk'])
        context['object'] = item
        return context

    def get_success_url(self):
        return reverse_lazy('edwoca:item_digcopy', kwargs={'pk': self.kwargs['pk']})


class ItemCommentUpdateView(SimpleFormView):
    model = Item
    property = 'comment'
    form_class = ItemCommentForm
    template_name = 'edwoca/item_comment.html'


class ItemDedicationUpdateView(SimpleFormView):
    model = Item
    property = 'dedication'
    form_class = ItemDedicationForm
    template_name = 'edwoca/item_dedication.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_form = SearchForm(self.request.GET or None)
        context['searchform'] = search_form
        context['show_search_form'] = True

        if search_form.is_valid() and search_form.cleaned_data.get('q'):
            context['query'] = search_form.cleaned_data.get('q')
            context[f"found_persons"] = search_form.search().models(Person)
        return context


def item_add_dedicatee(request, pk, person_id):
    item = get_object_or_404(Item, pk=pk)
    person = get_object_or_404(Person, pk=person_id)
    item.dedicatees.add(person)
    return redirect('edwoca:item_dedication', pk=pk)


def item_remove_dedicatee(request, pk, dedicatee_id):
    dedicatee = get_object_or_404(Person, pk=dedicatee_id)
    item = get_object_or_404(Item, pk=pk)
    item.dedicatees.remove(dedicatee)
    return redirect('edwoca:item_dedication', pk=pk)


class ItemDeleteView(EntityMixin, DeleteView):
    model = EdwocaItem

    def get_success_url(self):
        return self.object.get_manifestation_url()


class LibraryListView(EdwocaListView):
    model = Library


class LibrarySearchView(EdwocaSearchView):
    model = Library


class LibraryCreateView(CreateView):
    model = Library
    template_name = 'edwoca/simple_form.html'
    form_class = LibraryForm


class LibraryUpdateView(UpdateView):
    model = Library
    template_name = 'edwoca/simple_form.html'
    form_class = LibraryForm


class LibraryDeleteView(DeleteView):
    model = Library
    template_name = 'edwoca/simple_form.html'
