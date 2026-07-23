from .base import *
from edwoca import forms as edwoca_forms
from dmrism import models as dmrism_models
from ..forms.item import *
from ..forms.dedication import ItemPersonDedicationForm, ItemCorporationDedicationForm
from ..forms.modification import ItemModificationForm, ModificationHandwritingForm
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse_lazy, reverse
from django.views.generic import DeleteView, ListView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.detail import DetailView
from django.views.decorators.http import require_POST
from ..models import Item as EdwocaItem, ItemModification, ModificationHandwriting, Work, Expression, Manifestation
from dmrism.models.item import Item, PersonProvenanceStation, CorporationProvenanceStation, ItemDigitalCopy, ItemPersonDedication, ItemCorporationDedication, ItemHandwriting
from dmad_on_django.forms import SearchForm
from dmad_on_django.models import Person, Corporation, Place
from bib.models import ZotItem
from liszt_util.tools import swap_order
from django.contrib import messages
from django.contrib.messages import get_messages
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.db import transaction
from django.utils.html import mark_safe
from haystack.query import SearchQuerySet


def item_set_template(request, pk):
    item = get_object_or_404(Item, pk=pk)
    manifestation = item.manifestation
    manifestation.items.update(is_template=False)
    item.is_template = True
    item.save()
    return redirect('edwoca:manifestation_relations', pk=manifestation.pk)


class ItemDetailView(EntityMixin, DetailView):
    model = EdwocaItem


class ItemListView(EdwocaListView):
    model = EdwocaItem

    def get_queryset(self):
        return super().get_queryset().filter(manifestation__is_singleton = False)


class ItemSearchView(EdwocaSearchView):
    model = EdwocaItem

    def get_queryset(self):
        return super().get_queryset().filter(manifestation_is_singleton = False)


def item_history(request, pk):
    pass


def item_letter_add(request, pk, letter_pk):
    item = get_object_or_404(EdwocaItem, pk=pk)
    letter = get_object_or_404(Letter, pk=letter_pk)
    letter.item.add(item)
    return redirect('edwoca:item_bibliography', pk=pk)


def item_letter_remove(request, pk, letter_pk):
    item = get_object_or_404(EdwocaItem, pk=pk)
    letter = get_object_or_404(Letter, pk=letter_pk)
    letter.item.remove(item)
    return redirect('edwoca:item_bibliography', pk=pk)


class ItemBibliographyUpdateView(BaseBibliographyUpdateView):
    model = EdwocaItem
    form = ItemBibForm

    def get_success_url(self):
        return reverse_lazy('edwoca:item_bibliography', kwargs = {'pk': self.object.id})


def item_update(request, pk):
    item = get_object_or_404(EdwocaItem, pk=pk)

    context = {
            'object': item,
            'entity_type': 'item'
        }

    if request.method == 'POST':
        item_form = ItemForm(request.POST, instance=item)

        signature_forms = []
        for signature in item.signatures.all():
            signature_form = SignatureForm(
                    request.POST,
                    instance = signature,
                    prefix = f"signature-{signature.id}"
                )
            signature_forms.append(signature_form)

        all_forms = signature_forms + [ item_form ]
        if all(f.is_valid() for f in all_forms):
            for f in all_forms:
                f.save()
        else:
            context.update({
                    'form': item_form,
                    'signature_forms': signature_forms
                })
            return render(request, 'edwoca/item_update.html', context)

        if 'add-signature' in request.POST:
            status = ItemSignature.Status.CURRENT
            if item.signatures.count():
                status = ItemSignature.Status.FORMER
            signature = ItemSignature.objects.create(
                    item = item,
                    status = status
                )

        if 'remove-signature' in request.POST:
            signature_pk = request.POST.get('remove-signature')
            item_signature = get_object_or_404(ItemSignature, pk=request.POST.get('remove-signature'))
            item_signature.delete()

        return redirect('edwoca:item_update', pk = pk)
    else:
        item_form = ItemForm(instance=item)

        signature_forms = []

        for signature in item.signatures.all():
            signature_form = SignatureForm(
                    instance = signature,
                    prefix = f"signature-{signature.id}"
                )
            signature_forms.append(signature_form)

        context.update({
                'form': item_form,
                'signature_forms': signature_forms
            })
        return render(request, 'edwoca/item_update.html', context)


@require_POST
def item_swap_view(request, pk, direction):

    item = get_object_or_404(EdwocaItem, pk=pk)
    success = swap_order(item, direction)
    if not success:
        messages.error(request, "Element steht am Anfang oder Ende der Liste")

    manifestation = item.manifestation

    context = {'object': manifestation}

    return render(
        request,
        'edwoca/partials/manifestation/item_list.html',
        context
    )


@require_POST
def item_move_view(request, item_pk):
    item = get_object_or_404(Item, pk=item_pk)
    target_manifestation_pk = request.POST.get('target_manifestation_pk')

    if not target_manifestation_pk:
        return HttpResponse("Keine Ziel Manifestation ausgewählt", status=400)

    target_manifestation = get_object_or_404(Manifestation, pk=target_manifestation_pk)

    # Verschieben ausführen
    old_manifestation = item.move_to_manifestation(target_manifestation)

    # Erfolgsmeldung für den Verschiebevorgang
    messages.success(request, f'Exemplar wurde erfolgreich nach "{target_manifestation}" verschoben.')

    # Sonderfall: Alte Manifestation ist jetzt leer
    if not old_manifestation.items.exists():
        msg = mark_safe(
            f'Manifestation hat keine Exemplare mehr. '
            f'<a href="{reverse("edwoca:manifestation_delete", kwargs={"pk":old_manifestation.id})}" '
            f'style="text-decoration: underline; font-weight: bold; color: inherit;">Löschen?</a>'
        )
        messages.warning(request, msg, extra_tags='safe')

    response = render(
        request, 'edwoca/partials/manifestation/item_list.html',
        {'object': old_manifestation}
    )

    response.content += b'<div id="modal-container" hx-swap-oob="true"></div>'

    return response

def item_move_modal(request, pk):
    item = get_object_or_404(Item, pk=pk)
    return render (
        request,
        'edwoca/partials/manifestation/item_move_modal.html',
        {'item': item}
    )

def manifestation_autocomplete(request):
    q = request.GET.get('q','')
    results = (
        SearchQuerySet().models(Manifestation)
        .filter(is_singleton=False)
        .autocomplete(text=q)[:10]
        if len(q) >= 3 else []
    )

    return render (
        request,
        'edwoca/partials/manifestation/item_move_search_results.html',
        {'results':results}
    )


class ItemRelationsUpdateView(EntityMixin, RelationsUpdateView):
    template_name = 'edwoca/item_relations.html'
    model = EdwocaItem
    form_class = RelatedItemForm


class RelatedItemAddView(RelatedEntityAddView):
    template_name = 'edwoca/item_relations.html'
    model = RelatedItem


class RelatedItemRemoveView(DeleteView):
    model = RelatedItem

    def get_success_url(self):
        return reverse_lazy('edwoca:item_relations', kwargs={'pk': self.object.source_item.id})


class ItemContributorsUpdateView(EntityMixin, ContributorsUpdateView):
    model = EdwocaItem
    form_class = ItemContributorForm


class ItemContributorAddView(ContributorAddView):
    model = ItemContributor


class ItemContributorRemoveView(DeleteView):
    model = ItemContributor

    def get_success_url(self):
        return reverse_lazy('edwoca:item_contributors', kwargs={'pk': self.object.item.id})


def item_provenance(request, pk):
    item = get_object_or_404(EdwocaItem, pk=pk)
    context = {
        'object': item,
        'entity_type': 'item',
    }

    def construct_ps_set(ps_class, post = None):
        stations = []

        for obj in getattr(item, f'{ps_class}_provenance_stations').all():
            prefix = f'{ps_class}_provenance_{obj.id}'
            form = getattr(edwoca_forms, f'{ps_class.capitalize()}ProvenanceStationForm')(post, instance=obj, prefix=prefix)
            bib_forms = []
            for bib in obj.bib_set.all():
                prefix = f'{ps_class}_ps_bib_{bib.bib.zot_key}'
                bib_form = getattr(edwoca_forms, f'{ps_class.capitalize()}ProvenanceStationBibForm')(post, instance=bib, prefix=prefix)
                bib_forms += [ bib_form ]
            webref_forms = []
            for pp_webref in obj.web_references.all():
                prefix = f'{ps_class}_ps_webref_{pp_webref.id}'
                webref_form = getattr(edwoca_forms, f'{ps_class.capitalize()}ProvenanceStationWebReferenceForm')(post, instance=pp_webref, prefix=prefix)
                webref_forms += [ webref_form ]
            stations.append({
                'instance': obj,
                'form': form,
                'bib_forms': bib_forms,
                'webref_forms': webref_forms
                })

        return stations

    if request.method == 'POST':

        # create provenance station
        pp_stations = construct_ps_set('person', request.POST)
        cp_stations = construct_ps_set('corporation', request.POST)

        for ps_class in ['person', 'corporation']:
            ps_key = f'add-{ps_class}-provenance-station'
            if ps_key in request.POST:
                period = Period.objects.create()
                getattr(dmrism_models, f'{ps_class.capitalize()}ProvenanceStation').objects.create(item = item, period = period)
            webref_key = f'add-{ps_class}-provenance-webref'
            if webref_key in request.POST:
                station_id = request.POST.get(webref_key)
                station = getattr(dmrism_models, f'{ps_class.capitalize()}ProvenanceStation').objects.get(pk = station_id)
                creation_kwargs = { f'{ps_class}_provenance_station': station }
                getattr(dmrism_models, f'{ps_class.capitalize()}ProvenanceStationWebReference').objects.create(**creation_kwargs)

        pps_forms = []
        pps_bib_forms = []
        pps_webref_forms = []

        # take care of saving webref forms, bib forms
        pps_forms = []
        for pps_obj in pp_stations:
            prefix = f'person_provenance_{pps_obj['instance'].id}'
            pps_form = PersonProvenanceStationForm(request.POST, instance=pps_obj['instance'], prefix=prefix)
            pps_forms += [ pps_form ]
            for bib_form in pps_obj['bib_forms']:
                pps_bib_forms += [ bib_form ]
            for webref_form in pps_obj['webref_forms']:
                pps_webref_forms += [ webref_form ]

        cps_forms = []
        cps_bib_forms = []
        cps_webref_forms = []

        for cps_obj in cp_stations:
            prefix = f'corporation_provenance_{cps_obj['instance'].id}'
            cps_form = PersonProvenanceStationForm(request.POST, instance=cps_obj['instance'], prefix=prefix)
            cps_forms += [ cps_form ]
            for bib_form in cps_obj['bib_forms']:
                cps_bib_forms += [ bib_form ]
            for webref_form in cps_obj['webref_forms']:
                cps_webref_forms += [ webref_form ]

        provenance_comment_form = ItemProvenanceCommentForm(request.POST, instance=item)

        all_forms = (pps_forms +
            pps_bib_forms +
            pps_webref_forms +
            cps_forms +
            cps_bib_forms +
            cps_webref_forms +
            [ provenance_comment_form ]
        )

        if all(form.is_valid() for form in all_forms):
            for form in all_forms:
                form.save()
        else:
            context['pp_stations'] = pp_stations
            context['cp_stations'] = cp_stations
            context['form'] = provenance_comment_form
            return render(request, 'edwoca/provenance.html', context)

        powner_key = 'remove-provenance-owner-person'
        if powner_key in request.POST:
            ps_station_id, person_id = request.POST.get(powner_key).split('/')
            ps_station = PersonProvenanceStation.objects.get(pk=ps_station_id)
            person = Person.objects.get(pk=person_id)
            ps_station.owner.remove(person)
        cowner_key = 'remove-provenance-owner-corporation'
        if cowner_key in request.POST:
            ps_station_id = request.POST.get(cowner_key)
            ps_station = CorporationProvenanceStation.objects.get(pk=ps_station_id)
            ps_station.owner = None
            ps_station.save()

        for ps_class in ['person', 'corporation']:
            # remove bib from provenance station
            bib_key = f'remove-{ps_class}-provenance-bib'
            if bib_key in request.POST:
                bib_id = request.POST.get(bib_key)
                getattr(dmrism_models, f'{ps_class.capitalize()}ProvenanceStationBib').objects.get(bib__zot_key=bib_id).delete()
            # remove letter from provenance station
            letter_key = f'remove-{ps_class}-provenance-letter'
            if letter_key in request.POST:
                ps_station_id, letter_id = request.POST.get(letter_key).split('/')
                ps_station = getattr(dmrism_models, f'{ps_class.capitalize()}ProvenanceStation').objects.get(pk=ps_station_id)
                letter = Letter.objects.get(pk=letter_id)
                getattr(letter, f'{ps_class}_provenance').remove(ps_station)
            # remove webref from provenance station
            webref_key = f'remove-{ps_class}-provenance-webref'
            if webref_key in request.POST:
                webref_id = request.POST.get(webref_key)
                getattr(dmrism_models, f'{ps_class.capitalize()}ProvenanceStationWebReference').objects.get(pk=webref_id).delete()
            # remove provenance station
            ps_key = f'remove-{ps_class}-provenance-station'
            if ps_key in request.POST:
                ps_id = request.POST.get(ps_key)
                ps = getattr(dmrism_models, f'{ps_class.capitalize()}ProvenanceStation').objects.get(pk = ps_id)
                ps.delete()

        calculate_date_string = '-calculate-machine-readable-date'
        clear_date_string = '-clear-machine-readable-date'
        separator = '_provenance_'
        for key in request.POST.keys():
            if calculate_date_string in key:
                ps_class, id = key.replace(calculate_date_string, '').split(separator)
                ps = getattr(dmrism_models, f'{ps_class.capitalize()}ProvenanceStation').objects.get(pk = id)
                ps.period.parse_display()
                ps.period.save()
            if clear_date_string in key:
                ps_class, id = key.replace(clear_date_string, '').split(separator)
                ps = getattr(dmrism_models, f'{ps_class.capitalize()}ProvenanceStation').objects.get(pk = id)
                ps.period.not_before = None
                ps.period.not_after = None
                ps.period.save()

        return redirect('edwoca:item_provenance', pk=pk)
    else:
        pp_stations = construct_ps_set('person')
        cp_stations = construct_ps_set('corporation')
        provenance_comment_form = ItemProvenanceCommentForm(instance=item)

        context['pp_stations'] = pp_stations
        context['cp_stations'] = cp_stations
        context['form'] = provenance_comment_form
        return render(request, 'edwoca/provenance.html', context)

    return render(request, 'edwoca/manifestation_provenance.html', context)


def item_digital_copy(request, pk):
    item = get_object_or_404(EdwocaItem, pk=pk)
    context = {
        'object': item,
        'entity_type': 'item',
    }

    if request.method == 'POST':
        add_copy_string = 'add-digital-copy'
        if add_copy_string in request.POST:
            ItemDigitalCopy.objects.create(item=item)

        for digital_copy in item.digital_copies.all():
            prefix = f'digital_copy_{digital_copy.id}'
            form = ItemDigitizedCopyForm(request.POST, instance=digital_copy, prefix=prefix)
            if form.is_valid():
                form.save()

        remove_copy_string = 'remove-digital-copy'
        if remove_copy_string in request.POST:
            copy_id = request.POST.get(remove_copy_string)
            copy = get_object_or_404(ItemDigitalCopy, pk=copy_id)
            copy.delete()

        return redirect('edwoca:item_digital_copy', pk=pk)
    else:
        forms = []
        for digital_copy in item.digital_copies.all():
            prefix = f'digital_copy_{digital_copy.id}'
            forms.append(ItemDigitizedCopyForm(instance=digital_copy, prefix=prefix))
        context['forms'] = forms

    return render(request, 'edwoca/manifestation_digital_copy.html', context)


class ItemCommentUpdateView(SimpleFormView):
    model = EdwocaItem
    property = 'comment'
    form_class = ItemCommentForm
    template_name = 'edwoca/item_comment.html'


def item_dedication(request, pk):
    item = get_object_or_404(EdwocaItem, pk=pk)
    context = {
        'object': item,
        'entity_type': 'item',
    }

    if request.method == 'POST':
        if 'create-person-dedication' in request.POST:
            ItemPersonDedication.objects.create(
                    item = item
                )
        if 'create-corporation-dedication' in request.POST:
            ItemCorporationDedication.objects.create(
                    item = item
                )

        person_dedication_forms = []
        for person_dedication in item.itempersondedication_set.all():
            prefix = f'person_dedication_{person_dedication.id}'
            form = ItemPersonDedicationForm(request.POST, instance=person_dedication, prefix=prefix)
            person_dedication_forms += [ form ]

        corporation_dedication_forms = []
        for corporation_dedication in item.itemcorporationdedication_set.all():
            prefix = f'corporation_dedication_{corporation_dedication.id}'
            form = ItemCorporationDedicationForm(request.POST, instance=corporation_dedication, prefix=prefix)
            corporation_dedication_forms += [ form ]

        all_forms = person_dedication_forms + corporation_dedication_forms
        if all(f.is_valid for f in all_forms):
            for f in all_forms:
                f.save()
        else:
            context['person_dedication_forms'] = person_dedication_forms
            context['person_dedication_forms'] = person_dedication_forms

            return render(request, 'edwoca/item_dedication.html', context)

        if 'remove-person-dedication' in request.POST:
            person_dedication = get_object_or_404(ItemPersonDedication, pk = request.POST.get('remove-person-dedication'))
            person_dedication.delete()
        if 'remove-corporation-dedication' in request.POST:
            corporation_dedication = get_object_or_404(ItemCorporationDedication, pk = request.POST.get('remove-corporation-dedication'))
            corporation_dedication.delete()

        return redirect('edwoca:item_dedication', pk=pk)
    else:
        person_dedication_forms = []
        for person_dedication in item.itempersondedication_set.all():
            prefix = f'person_dedication_{person_dedication.id}'
            form = ItemPersonDedicationForm(instance=person_dedication, prefix=prefix)
            person_dedication_forms += [ form ]

        corporation_dedication_forms = []
        for corporation_dedication in item.itemcorporationdedication_set.all():
            prefix = f'corporation_dedication_{corporation_dedication.id}'
            form = ItemCorporationDedicationForm(instance=corporation_dedication, prefix=prefix)
            corporation_dedication_forms += [ form ]

        context['person_dedication_forms'] = person_dedication_forms
        context['corporation_dedication_forms'] = corporation_dedication_forms

    #q_dedicatee = request.GET.get('dedicatee-q')
    #q_place = request.GET.get('place-q')

    #if q_dedicatee:
        #dedicatee_search_form = SearchForm(request.GET, prefix='dedicatee')
        #if dedicatee_search_form.is_valid():
            #context['query_dedicatee'] = dedicatee_search_form.cleaned_data.get('q')
            #context['found_persons'] = dedicatee_search_form.search().models(Person)
            #context['found_corporations'] = dedicatee_search_form.search().models(Corporation)
    #else:
        #dedicatee_search_form = SearchForm(prefix='dedicatee')

    #if q_place:
        #place_search_form = SearchForm(request.GET, prefix='place')
        #if place_search_form.is_valid():
            #context['query_place'] = place_search_form.cleaned_data.get('q')
            #context['found_places'] = place_search_form.search().models(Place)
    #else:
        #place_search_form = SearchForm(prefix='place')

    #context['dedicatee_search_form'] = dedicatee_search_form
    #context['place_search_form'] = place_search_form

    #if request.GET.get('person_dedication_id'):
        #context['person_dedication_id'] = int(request.GET.get('person_dedication_id'))
    #if request.GET.get('corporation_dedication_id'):
        #context['corporation_dedication_id'] = int(request.GET.get('corporation_dedication_id'))

        return render(request, 'edwoca/item_dedication.html', context)


def item_person_dedication_add(request, pk):
    item = get_object_or_404(EdwocaItem, pk=pk)
    ItemPersonDedication.objects.create(item=item)
    return redirect('edwoca:item_dedication', pk=pk)


def item_corporation_dedication_add(request, pk):
    item = get_object_or_404(EdwocaItem, pk=pk)
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


def item_person_dedication_remove_dedicatee(request, pk, dedication_id, person_id):
    dedication = get_object_or_404(ItemPersonDedication, pk=dedication_id)
    person = get_object_or_404(Person, pk=person_id)
    dedication.dedicatee.remove(person)
    dedication.save()
    return redirect('edwoca:item_dedication', pk=pk)


def item_corporation_dedication_add_dedicatee(request, pk, dedication_id, corporation_id):
    dedication = get_object_or_404(ItemCorporationDedication, pk=dedication_id)
    corporation = get_object_or_404(Corporation, pk=corporation_id)
    dedication.dedicatee = corporation
    dedication.save()
    return redirect('edwoca:item_dedication', pk=pk)


def item_corporation_dedication_remove_dedicatee(request, pk, dedication_id, corporation_id):
    dedication = get_object_or_404(ItemCorporationDedication, pk=dedication_id)
    corporation = get_object_or_404(Corporation, pk=corporation_id)
    dedication.dedicatee.remove(corporation)
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


def item_person_dedication_remove_place(request, pk, dedication_id):
    dedication = ItemPersonDedication.objects.get(pk=dedication_id)
    dedication.place = None
    dedication.save()
    return redirect('edwoca:item_dedication', pk=pk)


def item_corporation_dedication_remove_place(request, pk, dedication_id):
    dedication = get_object_or_404(ItemCorporationDedication, pk=dedication_id)
    dedication.place = None
    dedication.save()
    return redirect('edwoca:item_dedication', pk=pk)


class ItemDeleteView(EntityMixin, DeleteView):
    model = EdwocaItem
    template_name = 'edwoca/delete.html'

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


class LibraryUpdateView(EntityMixin, UpdateView):
    model = Library
    #template_name = 'edwoca/simple_form.html'
    template_name = 'edwoca/library_update.html'
    form_class = LibraryForm

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if 'delete-corporation' in request.POST:
            self.object.corporation = None
            self.object.save()

        return response


class LibraryDeleteView(DeleteView):
    model = Library
    template_name = 'edwoca/delete.html'
    success_url = reverse_lazy('edwoca:library_list')


def item_manuscript_update(request, pk):
    item = get_object_or_404(EdwocaItem, pk=pk)
    context = {
        'object': item,
        'entity_type': 'item'
    }

    if request.method == 'POST':
        remove_modification_string = 'remove-modification'
        if remove_modification_string in request.POST:
            modification_id = request.POST.get(remove_modification_string)
            modification = ItemModification.objects.get(pk = modification_id)
            modification.delete()

        remove_handwriting_string = 'remove-modificationhandwriting'
        if remove_handwriting_string in request.POST:
            handwriting_id = request.POST.get(remove_handwriting_string)
            handwriting = ModificationHandwriting.objects.get(pk = handwriting_id)
            handwriting.delete()

        form = ItemManuscriptForm(request.POST, instance=item)
        function_form = FunctionForm(request.POST, instance=item)
        completeness_form = ItemCompletenessForm(request.POST, instance=item)
        text_type_form = ItemTextTypeForm(request.POST, instance=item)

        all_forms = [
                form,
                function_form,
                completeness_form,
                text_type_form
            ]

        if all(f.is_valid for f in all_forms):
            for f in all_forms:
                f.save()
        else:
            context['form'] = form
            context['function_form'] = function_form
            context['text_type_form'] = text_type_form
            context['completeness_form'] = completeness_form
            return render(request, 'edwoca:item_manuscript.html', context)

        for modification in item.modifications.all():
            prefix = f'modification_{modification.id}'
            modification_form = ItemModificationForm(request.POST, instance=modification, prefix=prefix)
            if modification_form.is_valid():
                modification_form.save()

            for handwriting in modification.handwritings.all():
                prefix = f'modification_handwriting_{handwriting.id}'
                handwriting_form = ModificationHandwritingForm(request.POST, instance=handwriting, prefix=prefix)
                if handwriting_form.is_valid():
                    handwriting_form.save()

        if 'add-modification' in request.POST:
            ItemModification.objects.create(item=item)

        add_handwriting_string = 'add-modification-handwriting'
        if add_handwriting_string in request.POST:
            modification_id = request.POST.get(add_handwriting_string)
            modification = get_object_or_404(ItemModification, pk=modification_id)
            ModificationHandwriting.objects.create(modification=modification)
            return redirect('edwoca:item_manuscript', pk=pk)

        return redirect('edwoca:item_manuscript', pk=pk)

    else:
        form = ItemManuscriptForm(instance=item)
        function_form = FunctionForm(instance=item)
        text_type_form = ItemTextTypeForm(instance=item)
        completeness_form = ItemCompletenessForm(instance=item)
        modifications = []
        for modification in item.modifications.all():
            prefix = f'modification_{modification.id}'
            modification_form = ItemModificationForm(instance=modification, prefix=prefix)

            handwriting_forms = []
            for handwriting in modification.handwritings.all():
                prefix = f'modification_handwriting_{handwriting.id}'
                handwriting_forms.append(ModificationHandwritingForm(instance=handwriting, prefix=prefix))

            modifications.append({
                'form': modification_form,
                'handwriting_forms': handwriting_forms
            })

        context['modifications'] = modifications

    context['form'] = form
    context['function_form'] = function_form
    context['text_type_form'] = text_type_form
    context['completeness_form'] = completeness_form
    search_form = SearchForm(request.GET or None)
    context['search_form'] = search_form

    if search_form.is_valid() and search_form.cleaned_data.get('q'):
        context['query'] = search_form.cleaned_data.get('q')
        context[f"found_persons"] = search_form.search().models(Person)

    if request.GET.get('handwriting_id'):
        context['handwriting_id'] = int(request.GET.get('handwriting_id'))

    if request.GET.get('add_handwriting_for_modification'):
        context['add_handwriting_for_modification'] = True
        context['modification_id'] = int(request.GET.get('modification_id'))
        if search_form.is_valid() and search_form.cleaned_data.get('q'):
            context['query'] = search_form.cleaned_data.get('q')
            context[f"found_persons"] = search_form.search().models(Person)

    if request.GET.get('modification_handwriting_id'):
        context['modification_handwriting_id'] = int(request.GET.get('modification_handwriting_id'))

    # Search forms for modifications
    q_work = request.GET.get('work-q')
    q_expression = request.GET.get('expression-q')
    q_manifestation = request.GET.get('manifestation-q')

    if q_work:
        work_search_form = SearchForm(request.GET, prefix='work')
        if work_search_form.is_valid():
            context['query_work'] = work_search_form.cleaned_data.get('q')
            context['found_works'] = work_search_form.search().models(Work)
    else:
        work_search_form = SearchForm(prefix='work')

    if q_expression:
        expression_search_form = SearchForm(request.GET, prefix='expression')
        if expression_search_form.is_valid():
            context['query_expression'] = expression_search_form.cleaned_data.get('q')
            context['found_expressions'] = expression_search_form.search().models(Expression)
    else:
        expression_search_form = SearchForm(prefix='expression')

    if q_manifestation:
        manifestation_search_form = SearchForm(request.GET, prefix='manifestation')
        if manifestation_search_form.is_valid():
            context['query_manifestation'] = manifestation_search_form.cleaned_data.get('q')
            context['found_manifestations'] = manifestation_search_form.search().models(Manifestation)
    else:
        manifestation_search_form = SearchForm(prefix='manifestation')

    context['work_search_form'] = work_search_form
    context['expression_search_form'] = expression_search_form
    context['manifestation_search_form'] = manifestation_search_form

    if request.GET.get('modification_id'):
        context['modification_id'] = int(request.GET.get('modification_id'))

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


class ModificationDeleteView(DeleteView):
    model = ItemModification

    def get_success_url(self):
        if self.object.item.manifestation.is_singleton:
            return reverse_lazy('edwoca:manifestation_manuscript', kwargs={'pk': self.object.item.manifestation.id})
        else:
            return reverse_lazy('edwoca:item_manuscript', kwargs={'pk': self.object.item.id})


def modification_add_handwriting_writer(request, handwriting_pk, person_pk):
    handwriting = get_object_or_404(ModificationHandwriting, pk=handwriting_pk)
    person = get_object_or_404(Person, pk=person_pk)
    handwriting.writer = person
    handwriting.save()
    if handwriting.modification.item.manifestation.is_singleton:
        return redirect('edwoca:manifestation_manuscript', pk=handwriting.modification.item.manifestation.id)
    else:
        return redirect('edwoca:item_manuscript', pk=handwriting.modification.item.id)


def modification_remove_handwriting_writer(request, handwriting_pk):
    handwriting = get_object_or_404(ModificationHandwriting, pk=handwriting_pk)
    handwriting.writer = None
    handwriting.save()
    if handwriting.modification.item.manifestation.is_singleton:
        return redirect('edwoca:manifestation_manuscript', pk=handwriting.modification.item.manifestation.id)
    else:
        return redirect('edwoca:manifestation_manuscript', pk=handwriting.modification.item.id)


class ItemBibAddView(FormView):
    def post(self, request, *args, **kwargs):
        item_id = self.kwargs['pk']
        zotitem_key = self.kwargs['zotitem_key']
        item = Item.objects.get(pk=item_id)
        zotitem = ZotItem.objects.get(zot_key=zotitem_key)
        ItemBib.objects.get_or_create(item=item, bib=zotitem)
        return redirect(reverse_lazy('edwoca:item_bibliography', kwargs={'pk': item_id}))


class ItemBibDeleteView(DeleteView):
    model = ItemBib

    def get_success_url(self):
        return reverse_lazy('edwoca:item_bibliography', kwargs={'pk': self.object.item.id})


