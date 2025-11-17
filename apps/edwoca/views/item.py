from .base import *
from ..forms.item import *
from ..forms.dedication import ItemPersonDedicationForm, ItemCorporationDedicationForm
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse_lazy, reverse
from django.views.generic import DeleteView, ListView
from django.views.generic.edit import CreateView, UpdateView
from django.views.decorators.http import require_POST
from ..models import Item as EdwocaItem
from dmrism.models.item import Item, PersonProvenanceStation, CorporationProvenanceStation, ItemDigitalCopy, ItemPersonDedication, ItemCorporationDedication
from dmad_on_django.forms import SearchForm
from dmad_on_django.models import Person, Corporation, Place
from bib.models import ZotItem
from liszt_util.tools import swap_order
from django.contrib import messages
from django.http import HttpResponse
from django.template.loader import render_to_string





def item_set_template(request, pk):
    item = get_object_or_404(Item, pk=pk)
    manifestation = item.manifestation
    manifestation.items.update(is_template=False)
    item.is_template = True
    item.save()
    return redirect('edwoca:manifestation_relations', pk=manifestation.pk)


class ItemListView(EdwocaListView):
    model = EdwocaItem


class ItemSearchView(EdwocaSearchView):
    model = EdwocaItem


def item_update(request, pk):
    item = get_object_or_404(Item, pk=pk)
    item_form = ItemForm(request.POST or None, instance=item)

    if request.POST and 'add_signature' in request.POST:
        data = request.POST.copy()
        total_forms = int(data.get('signatures-TOTAL_FORMS', 0))
        data['signatures-TOTAL_FORMS'] = str(total_forms + 1)
        signature_formset = SignatureFormSet(data, instance=item)
    else:
        signature_formset = SignatureFormSet(request.POST or None, instance=item)

    if request.method == 'POST' and 'add_signature' not in request.POST:
        if item_form.is_valid():
            item_form.save()
        if signature_formset.is_valid():
            signature_formset.save()
            return redirect('edwoca:item_update', pk=pk)

    context = {
        'object': item,
        'signature_formset': signature_formset,
        'entity_type': 'item',
        'item_form': item_form
    }
    return render(request, 'edwoca/item_update.html', context)

@require_POST
def item_swap_view(request, pk, direction):

    item = get_object_or_404(EdwocaItem, pk=pk)
    success = swap_order(item, 'manifestation', direction)
    manifestation = item.manifestation

    context = {'object': manifestation}
    
    return render(
        request,
        'edwoca/partials/manifestation/item_list.html',
        context
    )
"""
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
"""


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

    q_letter = request.GET.get('letter-q')
    if q_letter:
        letter_search_form = SearchForm(request.GET, prefix='letter')
        if letter_search_form.is_valid():
            context['query_letter'] = letter_search_form.cleaned_data.get('q')
            context['found_letters'] = letter_search_form.search().models(Letter)
    else:
        letter_search_form = SearchForm(prefix='letter')
    context['letter_search_form'] = letter_search_form

    return render(request, 'edwoca/item_provenance.html', context)


def item_digital_copy(request, pk):
    item = get_object_or_404(Item, pk=pk)
    context = {
        'object': item,
        'entity_type': 'item',
    }

    if request.method == 'POST':
        for digital_copy in item.digital_copies.all():
            prefix = f'digital_copy_{digital_copy.id}'
            form = ItemDigitizedCopyForm(request.POST, instance=digital_copy, prefix=prefix)
            if form.is_valid():
                form.save()
        return redirect('edwoca:item_digital_copy', pk=pk)
    else:
        forms = []
        for digital_copy in item.digital_copies.all():
            prefix = f'digital_copy_{digital_copy.id}'
            forms.append(ItemDigitizedCopyForm(instance=digital_copy, prefix=prefix))
        context['forms'] = forms

    return render(request, 'edwoca/item_digcopy.html', context)


def item_digital_copy_add(request, item_id):
    item = get_object_or_404(Item, pk=item_id)
    ItemDigitalCopy.objects.create(item=item)
    if item.manifestation.is_singleton:
        return redirect('edwoca:manifestation_digital_copy', pk=item.manifestation.id)
    return redirect('edwoca:item_digital_copy', pk=item_id)


class ItemDigitalCopyDeleteView(DeleteView):
    model = ItemDigitalCopy

    def get_success_url(self):
        item = self.object.item
        if item.manifestation.is_singleton:
            return reverse('edwoca:manifestation_digital_copy', kwargs={'pk': manifestation.id})
        return reverse('edwoca:item_digital_copy', kwargs={'pk': manifestation.id})


class ItemCommentUpdateView(SimpleFormView):
    model = Item
    property = 'comment'
    form_class = ItemCommentForm
    template_name = 'edwoca/item_comment.html'


def item_dedication(request, pk):
    item = get_object_or_404(Item, pk=pk)
    context = {
        'object': item,
        'entity_type': 'item',
    }

    if request.method == 'POST':
        # Handle existing PersonDedication forms
        for person_dedication in item.itempersondedication_set.all():
            prefix = f'person_dedication_{person_dedication.id}'
            form = ItemPersonDedicationForm(request.POST, instance=person_dedication, prefix=prefix)
            if form.is_valid():
                form.save()

        # Handle existing CorporationDedication forms
        for corporation_dedication in item.itemcorporationdedication_set.all():
            prefix = f'corporation_dedication_{corporation_dedication.id}'
            form = ItemCorporationDedicationForm(request.POST, instance=corporation_dedication, prefix=prefix)
            if form.is_valid():
                form.save()

        return redirect('edwoca:item_dedication', pk=pk)
    else:
        # Initialize forms for existing PersonDedication
        person_dedication_forms = []
        for person_dedication in item.itempersondedication_set.all():
            prefix = f'person_dedication_{person_dedication.id}'
            person_dedication_forms.append(ItemPersonDedicationForm(instance=person_dedication, prefix=prefix))
        context['person_dedication_forms'] = person_dedication_forms

        # Initialize forms for existing CorporationDedication
        corporation_dedication_forms = []
        for corporation_dedication in item.itemcorporationdedication_set.all():
            prefix = f'corporation_dedication_{corporation_dedication.id}'
            corporation_dedication_forms.append(ItemCorporationDedicationForm(instance=corporation_dedication, prefix=prefix))
        context['corporation_dedication_forms'] = corporation_dedication_forms

    q_dedicatee = request.GET.get('dedicatee-q')
    q_place = request.GET.get('place-q')

    if q_dedicatee:
        dedicatee_search_form = SearchForm(request.GET, prefix='dedicatee')
        if dedicatee_search_form.is_valid():
            context['query_dedicatee'] = dedicatee_search_form.cleaned_data.get('q')
            context['found_persons'] = dedicatee_search_form.search().models(Person)
            context['found_corporations'] = dedicatee_search_form.search().models(Corporation)
    else:
        dedicatee_search_form = SearchForm(prefix='dedicatee')

    if q_place:
        place_search_form = SearchForm(request.GET, prefix='place')
        if place_search_form.is_valid():
            context['query_place'] = place_search_form.cleaned_data.get('q')
            context['found_places'] = place_search_form.search().models(Place)
    else:
        place_search_form = SearchForm(prefix='place')

    context['dedicatee_search_form'] = dedicatee_search_form
    context['place_search_form'] = place_search_form

    if request.GET.get('person_dedication_id'):
        context['person_dedication_id'] = int(request.GET.get('person_dedication_id'))
    if request.GET.get('corporation_dedication_id'):
        context['corporation_dedication_id'] = int(request.GET.get('corporation_dedication_id'))

    return render(request, 'edwoca/item_dedication.html', context)


def item_person_dedication_add(request, pk):
    item = get_object_or_404(Item, pk=pk)
    ItemPersonDedication.objects.create(item=item)
    return redirect('edwoca:item_dedication', pk=pk)

def item_corporation_dedication_add(request, pk):
    item = get_object_or_404(Item, pk=pk)
    ItemCorporationDedication.objects.create(item=item)
    return redirect('edwoca:item_dedication', pk=pk)


def item_person_dedication_delete(request, pk):
    dedication = get_object_or_404(ItemPersonDedication, pk=pk)
    item_pk = dedication.item.pk
    dedication.delete()
    return redirect('edwoca:item_dedication', pk=item_pk)

def item_corporation_dedication_delete(request, pk):
    dedication = get_object_or_404(ItemCorporationDedication, pk=pk)
    item_pk = dedication.item.pk
    dedication.delete()
    return redirect('edwoca:item_dedication', pk=item_pk)

def item_person_dedication_add_dedicatee(request, pk, dedication_id, person_id):
    dedication = get_object_or_404(ItemPersonDedication, pk=dedication_id)
    person = get_object_or_404(Person, pk=person_id)
    dedication.dedicatee = person
    dedication.save()
    return redirect('edwoca:item_dedication', pk=pk)

def item_person_dedication_remove_dedicatee(request, pk, dedication_id):
    dedication = get_object_or_404(ItemPersonDedication, pk=dedication_id)
    dedication.dedicatee = None
    dedication.save()
    return redirect('edwoca:item_dedication', pk=pk)

def item_corporation_dedication_add_dedicatee(request, pk, dedication_id, corporation_id):
    dedication = get_object_or_404(ItemCorporationDedication, pk=dedication_id)
    corporation = get_object_or_404(Corporation, pk=corporation_id)
    dedication.dedicatee = corporation
    dedication.save()
    return redirect('edwoca:item_dedication', pk=pk)

def item_corporation_dedication_remove_dedicatee(request, pk, dedication_id):
    dedication = get_object_or_404(ItemCorporationDedication, pk=dedication_id)
    dedication.dedicatee = None
    dedication.save()
    return redirect('edwoca:item_dedication', pk=pk)

def item_dedication_add_place(request, pk, dedication_id, place_id):
    # This is a bit tricky, as we don't know if it's a person or corporation dedication.
    # We will try to get the person dedication first, and if it fails, we get the corporation dedication.
    try:
        dedication = ItemPersonDedication.objects.get(pk=dedication_id)
    except ItemPersonDedication.DoesNotExist:
        dedication = get_object_or_404(ItemCorporationDedication, pk=dedication_id)
    place = get_object_or_404(Place, pk=place_id)
    dedication.place = place
    dedication.save()
    return redirect('edwoca:item_dedication', pk=pk)

def item_dedication_remove_place(request, pk, dedication_id):
    # This is a bit tricky, as we don't know if it's a person or corporation dedication.
    # We will try to get the person dedication first, and if it fails, we get the corporation dedication.
    try:
        dedication = ItemPersonDedication.objects.get(pk=dedication_id)
    except ItemPersonDedication.DoesNotExist:
        dedication = get_object_or_404(ItemCorporationDedication, pk=dedication_id)
    dedication.place = None
    dedication.save()
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


def item_manuscript_update(request, pk):
    item = get_object_or_404(Item, pk=pk)
    context = {
        'object': item,
        'entity_type': 'item'
    }

    if request.method == 'POST':
        if 'save_changes' in request.POST:
            form = ItemManuscriptForm(request.POST, instance=item)
            if form.is_valid():
                form.save()

            for handwriting in item.handwritings.all():
                prefix = f'handwriting_{handwriting.id}'
                handwriting_form = ItemHandwritingForm(request.POST, instance=handwriting, prefix=prefix)
                if handwriting_form.is_valid():
                    handwriting_form.save()

        if 'add_handwriting' in request.POST:
            ItemHandwriting.objects.create(item=item)

        return redirect('edwoca:item_manuscript', pk=pk)

    else:
        form = ItemManuscriptForm(instance=item)
        handwriting_forms = []
        for handwriting in item.handwritings.all():
            prefix = f'handwriting_{handwriting.id}'
            handwriting_forms.append(ItemHandwritingForm(instance=handwriting, prefix=prefix))
        context['handwriting_forms'] = handwriting_forms

    context['form'] = form
    search_form = SearchForm(request.GET or None)
    context['search_form'] = search_form

    if search_form.is_valid() and search_form.cleaned_data.get('q'):
        context['query'] = search_form.cleaned_data.get('q')
        context[f"found_persons"] = search_form.search().models(Person)

    if request.GET.get('handwriting_id'):
        context['handwriting_id'] = int(request.GET.get('handwriting_id'))

    return render(request, 'edwoca/item_manuscript.html', context)


def item_add_handwriting_writer(request, pk, handwriting_pk, person_pk):
    handwriting = get_object_or_404(ItemHandwriting, pk=handwriting_pk)
    person = get_object_or_404(Person, pk=person_pk)
    handwriting.writer = person
    handwriting.save()
    return redirect('edwoca:item_manuscript', pk=pk)


def item_remove_handwriting_writer(request, pk, handwriting_pk):
    handwriting = get_object_or_404(ItemHandwriting, pk=handwriting_pk)
    handwriting.writer = None
    handwriting.save()
    return redirect('edwoca:item_manuscript', pk=pk)


class ItemHandwritingDeleteView(DeleteView):
    model = ItemHandwriting

    def get_success_url(self):
        return reverse_lazy('edwoca:item_manuscript', kwargs={'pk': self.object.item.id})
