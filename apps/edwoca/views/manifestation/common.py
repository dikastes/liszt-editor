import re

from haystack.query import SearchQuerySet
from dmad_on_django.models import Corporation, Period
from dmrism import models as dmrism_models
from edwoca import forms as edwoca_forms
from haystack.query import SQ
from ...forms.manifestation import *
from calendar import monthrange
from ...forms.item import SignatureForm, ItemDigitizedCopyForm, PersonProvenanceStationForm, CorporationProvenanceStationForm, ItemProvenanceCommentForm, NewItemSignatureFormSet, ItemManuscriptForm, ItemHandwritingForm, PersonProvenanceStationBibForm, CorporationProvenanceStationBibForm, PersonProvenanceFormSet, PersonProvenanceBibFormSet, CorporationProvenanceFormSet, CorporationProvenanceBibFormSet, PersonProvenanceStationWebReference, CorporationProvenanceStationWebReference, PersonProvenanceStationWebReferenceForm, CorporationProvenanceStationWebReferenceForm
from ...forms.modification import ItemModificationForm, ModificationHandwritingForm
from ...forms.dedication import ManifestationPersonDedicationForm, ManifestationCorporationDedicationForm
from ...models import Manifestation as EdwocaManifestation, Letter, Expression, Work, ItemModification, ModificationHandwriting
from ..base import *
from ...models import ManifestationTitle, ManifestationTitleHandwriting, ItemDigitalCopy
from bib.models import ZotItem
from django.db.models import Q, Model
from django.forms import inlineformset_factory
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy, reverse
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST
from django.views.generic import DeleteView, FormView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.detail import DetailView
from django.apps import apps
from liszt_util.forms import SearchForm
from dmrism.models.item import ItemSignature, PersonProvenanceStation, CorporationProvenanceStation, Item, Library, ItemHandwriting
from liszt_util.tools import swap_order
from dmrism.models.item import ItemSignature, PersonProvenanceStation, CorporationProvenanceStation, Item, Library, ItemHandwriting, CorporationProvenanceStationBib, PersonProvenanceStationBib
from dmrism.models.manifestation import Manifestation as DmrismManifestation, Publication, ManifestationPersonDedication, ManifestationCorporationDedication, PublicationPlace
from dmrism.models.manifestation import ManifestationBib, Publication


class ManifestationDetailView(EntityMixin, DetailView):
    model = EdwocaManifestation


class ManifestationListView(EdwocaListView):
    model = EdwocaManifestation

    def get_queryset(self):
        return super().get_queryset().filter(is_singleton = False)


class ManifestationSearchView(EdwocaSearchView):
    model = EdwocaManifestation
    form_class = ManifestationSearchForm

    def get_queryset(self):
        return super().get_queryset().filter(is_singleton = False)


class SingletonListView(EdwocaListView):
    model = EdwocaManifestation

    def get_queryset(self):
        return super().get_queryset().filter(is_singleton = True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['list_entity_type'] = 'singleton'
        return context


class SingletonSearchView(EdwocaSearchView):
    model = EdwocaManifestation
    form_class = ManifestationSearchForm

    def get_queryset(self):
        return super().get_queryset().filter(is_singleton = True)

    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', '')

        # redirect to list view if empty query
        if not query or query == '':
            return redirect(f'edwoca:singleton_list')

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['list_entity_type'] = 'singleton'
        return context


def singleton_collection_create(request):
    if request.method == 'POST':
        form = SingletonCreateForm(request.POST)

        forms_valid = True
        if form.is_valid():
            manifestation = EdwocaManifestation.objects.create(
                is_singleton=True,
                is_collection=True,
                source_title = form.cleaned_data['source_title']
            )

            item = Item.objects.create(manifestation=manifestation)

            library = form.cleaned_data['library']
            signature = ItemSignature.objects.create(
                library=library,
                signature=form.cleaned_data['signature']
            )
            item.signatures.add(signature)

            return redirect('edwoca:manifestation_update', pk=manifestation.pk)
    else:
        form = SingletonCreateForm(is_collection = True)

    return render(request, 'edwoca/create_singleton.html', {
        'form': form,
    })


def singleton_create(request):
    if request.method == 'POST':
        form = SingletonCreateForm(request.POST)
        if form.is_valid():
            manifestation = EdwocaManifestation.objects.create(
                is_singleton=True,
                source_type=form.cleaned_data.get('source_type'),
                working_title = form.cleaned_data['working_title']
            )

            item = Item.objects.create(manifestation=manifestation)

            library = form.cleaned_data['library']
            signature = ItemSignature.objects.create(
                library=library,
                signature=form.cleaned_data['signature']
            )
            item.signatures.add(signature)

            return redirect('edwoca:manifestation_update', pk=manifestation.pk)
    else:
        form = SingletonCreateForm()

    return render(request, 'edwoca/create_singleton.html', {
        'form': form,
    })


def manifestation_collection_create(request, publisher_pk=None):
    publisher = get_object_or_404(Corporation, pk=publisher_pk) if publisher_pk else None

    if request.method == 'POST':
        if not publisher:
            # handle error, maybe redirect to search page
            return redirect('edwoca:manifestation_collection_create')

        data = request.POST.copy()
        data['publisher'] = publisher
        form = ManifestationCreateForm(data)
        if form.is_valid():
            manifestation = EdwocaManifestation.objects.create(
                    plate_number = form.cleaned_data.get('plate_number'),
                    source_title = form.cleaned_data['source_title'],
                    is_collection = True
                )
            manifestation.save()
            Publication.objects.create(
                    publisher = form.cleaned_data.get('publisher'),
                    manifestation = manifestation
                )

            return redirect('edwoca:manifestation_update', pk=manifestation.pk)
    else:
        if publisher:
            form = ManifestationCreateForm(is_collection = True, initial = {'publisher': publisher})
            context = {
                    'form': form,
                    'referrer': 'manifestation_collection_create'
                }
        else:
            form = ManifestationCreateForm(is_collection = True, )
            context = {
                    'referrer': 'manifestation_collection_create'
                }

    if not publisher:
        if request.GET.get('q'):
            search_form = SearchForm(request.GET)
            context['search_form'] = search_form
            context['publisher_list'] = search_form.search().models(Corporation)
        else:
            context['search_form'] = SearchForm()

    return render(request, 'edwoca/create_manifestation.html', context)


def manifestation_create(request, publisher_pk=None):
    publisher = get_object_or_404(Corporation, pk=publisher_pk) if publisher_pk else None

    if request.method == 'POST':

        data = request.POST.copy()
        if publisher:
            data['publisher'] = publisher.pk

        form = ManifestationCreateForm(data)
        if form.is_valid():

            display = form.cleaned_data.get('display')
            period = Period.objects.create(
                display=display,
            )

            try:
                period.parse_display()
                period.save()
            except Exception as e:
                print(e)

            manifestation = EdwocaManifestation.objects.create(
                    source_type = form.cleaned_data.get('source_type'),
                    plate_number = form.cleaned_data.get('plate_number'),
                    working_title = form.cleaned_data['temporary_title'],
                    period = period
            )

            chosen_publisher = form.cleaned_data.get('publisher')
            if chosen_publisher:
                chosen_publisher = Corporation.objects.get(pk=chosen_publisher)
                Publication.objects.create(
                        publisher = chosen_publisher,
                        manifestation = manifestation
                )

            return redirect('edwoca:manifestation_update', pk=manifestation.pk)
    else:

        context = {
            'form': ManifestationCreateForm(),
            'referrer': 'manifestation_create'
        }

        return render(request, 'edwoca/create_manifestation.html', context)

def publisher_search_view(request):
    search_text = request.GET.get('publisher_search', '')

    if len(search_text) < 2:
        return HttpResponse('')

    publisher = SearchQuerySet().models(Corporation).filter(content=search_text)
    return render(request, 'edwoca/partials/manifestation/publisher_results.html', {'publisher_list': publisher})

def manifestation_update(request, pk):
    manifestation = Manifestation.objects.get(id=pk)
    context = {
        'object': manifestation,
        'entity_type': 'manifestation'
    }

    if request.method == 'POST':
        manifestation_form = ManifestationForm(request.POST, instance=manifestation)

        signature_forms = []
        if manifestation.is_singleton:
            item = manifestation.get_single_item()
            signature_forms_valid = True

            for signature in manifestation.get_single_item().signatures.all():
                signature_form = SignatureForm(
                        request.POST,
                        instance = signature,
                        prefix = f"signature-{signature.id}"
                    )
                signature_forms.append(signature_form)

        if manifestation_form.is_valid() and all(s.is_valid() for s in signature_forms):
            manifestation_form.save()
            for signature in manifestation.get_single_item().signatures.all():
                signature.status = ItemSignature.Status.FORMER
                signature.save()
            for signature_form in signature_forms:
                signature_form.save()
        else:
            context['manifestation_form'] = manifestation_form
            context['signature_forms'] = signature_forms

            return render(request, 'edwoca/manifestation_update.html', context)

        if 'add_signature' in request.POST:
            status = ItemSignature.Status.CURRENT
            if item.signatures.count():
                status = ItemSignature.Status.FORMER
            signature = ItemSignature.objects.create(
                    item = item,
                    status = status
                )
            signature_forms += [ SignatureForm(instance = signature, prefix = f"signature-{signature.id}") ]

        context['signature_forms'] = signature_forms
        context['library_search_form'] = SearchForm()

        return redirect('edwoca:manifestation_update', pk = pk)
    else:
        expression_search_form = FramedSearchForm(request.GET or None, prefix='expression', placeholder = _('search expressions'))
        context['expression_search_form'] = expression_search_form
        if 'expression_link' in request.GET:
            expression_link = get_object_or_404(Expression, pk = request.GET['expression_link'])
            context['expression_link'] = expression_link
        if expression_search_form.is_valid() and expression_search_form.cleaned_data.get('q'):
            context['expression_query'] = expression_search_form.cleaned_data.get('q')
            context['found_expressions'] = expression_search_form.search().models(Expression)

        manifestation_form = ManifestationForm(instance=manifestation)

        signature_forms = []
        if manifestation.is_singleton:
            for signature in manifestation.get_single_item().signatures.all():
                signature_form = SignatureForm(
                        instance = signature,
                        prefix = f"signature-{signature.id}"
                    )
                signature_forms.append(signature_form)
            context['signature_forms'] = signature_forms

        context['library_search_form'] = SearchForm()
        context['manifestation_form'] = manifestation_form

    return render(request, 'edwoca/manifestation_update.html', context)


def manifestation_item_create(request, pk):
    manifestation = get_object_or_404(Manifestation, pk = pk)
    Item.objects.create(manifestation = manifestation)
    return redirect('edwoca:manifestation_relations', pk = pk)


def manifestation_item_delete(request, item_id):
    item = get_object_or_404(Item, pk = item_id)
    item.delete()
    return redirect('edwoca:manifestation_relations', pk = item.manifestation.id)


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
    model = EdwocaManifestation
    success_url = reverse_lazy('edwoca:manifestation_list')
    template_name = 'edwoca/delete.html'


class ManifestationHandwritingDeleteView(DeleteView):
    model = ItemHandwriting

    def get_success_url(self):
        return reverse_lazy('edwoca:manifestation_manuscript', kwargs={'pk': self.object.item.manifestation.id})


class RelatedManifestationAddView(RelatedEntityAddView):
    template_name = 'edwoca/manifestation_relations.html'
    model = RelatedManifestation


class RelatedManifestationRemoveView(DeleteView):
    model = RelatedManifestation

    def get_success_url(self):
        return reverse_lazy('edwoca:manifestation_relations', kwargs={'pk': self.kwargs.get('referrer_pk')})


class ManifestationRelationsUpdateView(EntityMixin, UpdateView):
    template_name = 'edwoca/manifestation_relations.html'
    model = EdwocaManifestation
    form_class = RelatedManifestationForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        manuscript_search_form = ManifestationSearchForm(self.request.GET or None, prefix='manuscript', placeholder=_('search manuscripts'))
        collection_search_form = ManifestationSearchForm(self.request.GET or None, prefix='collection', placeholder = _('search manifestations'))
        print_search_form = ManifestationSearchForm(self.request.GET or None, prefix='print', placeholder=_('search prints'))
        context['relations_comment_form'] = ManifestationRelationsCommentForm(instance=self.object)
        context['manuscript_search_form'] = manuscript_search_form
        context['collection_search_form'] = collection_search_form
        context['print_search_form'] = print_search_form

        if 'manuscript_link' in self.request.GET:
            manuscript_link = get_object_or_404(Manifestation, pk = self.request.GET['manuscript_link'])
            context['manuscript_link'] = manuscript_link
        if 'print_link' in self.request.GET:
            print_link = get_object_or_404(Manifestation, pk = self.request.GET['print_link'])
            context['print_link'] = print_link

        if manuscript_search_form.is_valid() and manuscript_search_form.cleaned_data.get('q'):
            context['manuscript_query'] = manuscript_search_form.cleaned_data.get('q')
            context['found_manuscripts'] = manuscript_search_form.search().models(Manifestation).filter(is_singleton = True)

        if collection_search_form.is_valid() and collection_search_form.cleaned_data.get('q'):
            context['collection_query'] = collection_search_form.cleaned_data.get('q')
            found_collections = (collection_search_form
                    .search()
                    .models(Manifestation)
                    .filter(may_have_component = True)
                )
            if self.object.is_collection:
                found_collections = found_collections.filter(is_collection = True)
            context['found_collections'] = found_collections

        if print_search_form.is_valid() and print_search_form.cleaned_data.get('q'):
            context['print_query'] = print_search_form.cleaned_data.get('q')
            context['found_prints'] = print_search_form.search().models(Manifestation).filter(is_singleton = False)

        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        form = ManifestationRelationsCommentForm(request.POST, instance=self.object)
        if not form.is_valid():
            context = self.get_context_data(**kwargs)
            context['relations_comment_form'] = form
            return self.render_to_response(context)
        else:
            form.save()

        if 'collection-link-type' in request.POST:
            manifestation_link = get_object_or_404(
                Manifestation,
                pk=request.POST.get('collection-link')
            )
            link_type = request.POST.get('collection-link-type')

            if link_type == 'component':
                self.object.component_of = manifestation_link
                self.object.part_of = None
                self.object.part_label = None
            else:
                label = getattr(Manifestation.PartLabel, link_type.upper())
                self.object.part_label = label
                self.object.part_of = manifestation_link
                self.object.component_of = None

            self.object.save()

        if 'manifestation-link-type' in request.POST:
            manifestation_link = get_object_or_404(
                Manifestation,
                pk=request.POST.get('manifestation-link')
            )
            link_type = getattr(
                RelatedManifestation.Label,
                request.POST.get('manifestation-link-type').upper()
            )

            if self.object.is_singleton:
                source = self.object
                target = manifestation_link
            else:
                source = manifestation_link
                target = self.object

            RelatedManifestation.objects.create(
                source_manifestation=source,
                target_manifestation=target,
                label=link_type
            )

        return redirect('edwoca:manifestation_relations', pk=self.object.id)

def collection_remove(request, pk):
    manifestation = get_object_or_404(Manifestation, pk = pk)
    manifestation.part_of = None
    manifestation.component_of = None
    manifestation.save()
    return redirect('edwoca:manifestation_relations', pk = pk)


def manifestation_expression_add(request, pk, expression_pk):
    manifestation = get_object_or_404(Manifestation, pk=pk)
    expression = get_object_or_404(Expression, pk=expression_pk)
    manifestation.expressions.add(expression)
    return redirect('edwoca:manifestation_update', pk=pk)


def manifestation_expression_remove(request, pk, expression_pk):
    manifestation = get_object_or_404(Manifestation, pk=pk)
    expression = get_object_or_404(Expression, pk=expression_pk)
    manifestation.expressions.remove(expression)
    return redirect('edwoca:manifestation_update', pk=pk)


class ManifestationHistoryUpdateView(SimpleFormView):
    model = Manifestation
    property = 'history'
    template_name = 'edwoca/manifestation_history.html'
    form_class = ManifestationHistoryForm

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()

        if not form.is_valid():
            return self.form_invalid(form)

        place_forms = []
        for manifestation_place in self.object.manifestationplace_set.all():
            place_form = ManifestationPlaceForm(request.POST, instance = manifestation_place, prefix=f'manifestation-place-{manifestation_place.id}')
            if not place_form.is_valid():
                return self.form_invalid(form)
            place_forms.append(place_form)

        for place_form in place_forms:
            place_form.save()

        self.object = form.save()
        period = self.object.period

        if 'calculate-machine-readable-date' in request.POST:
            period.parse_display()
            period.save()
        elif 'clear-machine-readable-date' in request.POST:
            period.not_before = None
            period.not_after = None
            period.assumed = False
            period.inferred = False
            period.save()

        return redirect('edwoca:manifestation_history', pk = self.object.id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_form = SearchForm(self.request.GET or None)
        context['searchform'] = search_form
        context['show_search_form'] = True

        context['place_forms'] = []
        for manifestation_place in self.object.manifestationplace_set.all():
            place_form = ManifestationPlaceForm(instance = manifestation_place, prefix=f'manifestation-place-{manifestation_place.id}')
            context['place_forms'].append(place_form)

        if search_form.is_valid() and search_form.cleaned_data.get('q'):
            context['query'] = search_form.cleaned_data.get('q')
            context[f"found_places"] = search_form.search().models(Place)

        return context

    def get_model(self):
        return self.model.__name__


def manifestation_add_place_view(request, pk, place_id):
    manifestation = get_object_or_404(Manifestation, pk=pk)
    place = get_object_or_404(Place, pk=place_id)

    manifestation.places.add(place)

    return redirect('edwoca:manifestation_history', pk=pk)


def manifestation_remove_place_view(request, pk, place_id):
    manifestation = get_object_or_404(Manifestation, pk=pk)
    manifestation_place = get_object_or_404(ManifestationPlace, pk=place_id)

    manifestation_place.delete()

    return redirect('edwoca:manifestation_history', pk=pk)


def manifestation_add_publisher(request, pk, publisher_id):
    manifestation = get_object_or_404(Manifestation, pk=pk)
    publisher = get_object_or_404(Corporation, pk=publisher_id)

    manifestation.publisher = publisher
    manifestation.save()

    return redirect('edwoca:manifestation_print', pk=pk)


def manifestation_remove_publisher(request, pk):
    manifestation = get_object_or_404(Manifestation, pk=pk)
    manifestation.publisher = None
    manifestation.save()
    return redirect('edwoca:manifestation_print', pk=pk)


def manifestation_add_stitcher(request, pk, stitcher_id):
    manifestation = get_object_or_404(Manifestation, pk=pk)
    stitcher = get_object_or_404(Corporation, pk=stitcher_id)
    manifestation.stitcher = stitcher
    manifestation.save()
    return redirect('edwoca:manifestation_print', pk=pk)


def manifestation_remove_stitcher(request, pk):
    manifestation = get_object_or_404(Manifestation, pk=pk)
    manifestation.stitcher = None
    manifestation.save()
    return redirect('edwoca:manifestation_print', pk=pk)


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


def manifestation_letter_add(request, pk, letter_pk):
    manifestation = get_object_or_404(Manifestation, pk=pk)
    letter = get_object_or_404(Letter, pk=letter_pk)
    letter.manifestation.add(manifestation)
    return redirect('edwoca:manifestation_bibliography', pk=pk)


def manifestation_letter_remove(request, pk, letter_pk):
    manifestation = get_object_or_404(Manifestation, pk=pk)
    letter = get_object_or_404(Letter, pk=letter_pk)
    letter.manifestation.remove(manifestation)
    return redirect('edwoca:manifestation_bibliography', pk=pk)


class ManifestationBibliographyUpdateView(BaseBibliographyUpdateView):
    model = Manifestation
    form = ManifestationBibForm


class ManifestationCommentUpdateView(SimpleFormView):
    model = Manifestation
    property = 'comment'
    view_title = _('comment')


def manifestation_print_update(request, pk):
    manifestation = get_object_or_404(EdwocaManifestation, pk=pk)
    context = {
        'object': manifestation,
        'entity_type': 'manifestation'
    }

    if request.method == 'POST':
        if 'add-publication' in request.POST:
            Publication.objects.create(manifestation=manifestation)
            return redirect('edwoca:manifestation_print', pk=pk)

        add_place_string = 'add-publication-place'
        if add_place_string in request.POST:
            publication_id = request.POST.get(add_place_string)
            publication = Publication.objects.get(pk=publication_id)
            PublicationPlace.objects.create(publication = publication)

        form = ManifestationPrintForm(request.POST, instance=manifestation)
        text_type_form = ManifestationTextTypeForm(request.POST, instance=manifestation)

        all_forms = [ form, text_type_form ]
        publications = []
        for publication in manifestation.publications.all():
            prefix = f'publication_{publication.id}'
            #publication_form = PublicationForm(request.POST, instance = publication, prefix = prefix)
            publication_place_forms = []
            for publication_place in publication.place_relations.all():
                prefix = f'publication_place_relation_{publication_place.id}'
                publication_place_form = PublicationPlaceForm(request.POST, instance = publication_place, prefix = prefix)
                publication_place_forms.append(publication_place_form)
                all_forms.append(publication_place_form)
            publications.append({
                    'publication': publication,
                    'publication_place_forms': publication_place_forms
                })

        if all(f.is_valid() for f in all_forms):
            for f in all_forms:
                f.save()
        else:
            context['form'] = form
            context['text_type_form'] = text_type_form
            context['publications'] = publications
            return render(request, 'edwoca/manifestation_print.html', context)

        if 'calculate-machine-readable-date' in request.POST:
            manifestation.period.parse_display()
            manifestation.period.save()
        if 'clear-machine-readable-date' in request.POST:
            manifestation.period.not_before = None
            manifestation.period.not_after = None
            manifestation.period.assumed = False
            manifestation.period.inferred = False
            manifestation.period.save()

        remove_place_string = 'remove-place'
        if remove_place_string in request.POST:
            publication_place_id = request.POST.get(remove_place_string)
            publication_place = PublicationPlace.objects.get(pk = publication_place_id)
            publication_place.place = None
            publication_place.save()

        remove_stitcher_string = 'remove-stitcher'
        if remove_stitcher_string in request.POST:
            manifestation.stitcher = None
            manifestation.save()

        remove_publisher_string = 'remove-publisher'
        if remove_publisher_string in request.POST:
            publication_id = request.POST.get(remove_publisher_string)
            publication = Publication.objects.get(pk = publication_id)
            publication.publisher = None
            publication.save()

        remove_place_string = 'remove-publication-place'
        if remove_place_string in request.POST:
            publication_place_id = request.POST.get(remove_place_string)
            PublicationPlace.objects.get(pk=publication_place_id).delete()

        remove_publication_string = 'remove-publication'
        if remove_publication_string in request.POST:
            publication_id = request.POST.get(remove_publication_string)
            Publication.objects.get(pk=publication_id).delete()

        return redirect('edwoca:manifestation_print', pk=pk)

    context['form'] = ManifestationPrintForm(instance = manifestation)
    context['text_type_form'] = ManifestationTextTypeForm(instance=manifestation)

    publications = []
    for publication in manifestation.publications.all():
        prefix = f'publication_{publication.id}'

        publication_place_forms = []
        for publication_place in publication.place_relations.all():
            prefix = f'publication_place_relation_{publication_place.id}'
            publication_place_form = PublicationPlaceForm(instance = publication_place, prefix = prefix)
            publication_place_forms.append(publication_place_form)
        publications.append({
                'publication': publication,
                'publication_place_forms': publication_place_forms
            })

        #publisher_search_form = SearchForm(request.GET or None, prefix='publisher')
        #found_publishers = []
        #if publisher_search_form.is_valid() and publisher_search_form.cleaned_data.get('q'):
            #found_publishers = publisher_search_form.search().models(Corporation)

        #place_search_form = SearchForm(request.GET or None, prefix='place')
        #found_places = []
        #if place_search_form.is_valid() and place_search_form.cleaned_data.get('q'):
            #found_places = place_search_form.search().models(Place)

        #publication_forms.append({
                #'publication_form': PublicationForm(instance = publication, prefix = prefix),
                #'publication': publication,
                #'publisher_search_form': publisher_search_form,
                #'found_publishers': found_publishers,
                #'place_search_form': place_search_form,
                #'found_places':found_places
            #})

    context['publications'] = publications

    if manifestation.stitcher:
        context['linked_stitcher'] = manifestation.stitcher
        #search_form = SearchForm(request.GET or None, prefix='stitcher')
        #context['stitcher_searchform'] = search_form
        #context['show_stitcher_search_form'] = True

        #if search_form.is_valid() and search_form.cleaned_data.get('q'):
            #context['stitcher_query'] = search_form.cleaned_data.get('q')
            #context[f'found_stitchers'] = search_form.search().models(Corporation)

    return render(request, 'edwoca/manifestation_print.html', context)


def manifestation_add_publication_place(request, pk, publication_id, place_id):
    publication = get_object_or_404(Publication, pk=publication_id)
    place = get_object_or_404(Place, pk=place_id)
    publication.place.add(place)
    publication.save()
    return redirect('edwoca:manifestation_print', pk=pk)


def manifestation_remove_publication_place(request, pk, publication_id, place_id):
    publication = get_object_or_404(Publication, pk=publication_id)
    place = get_object_or_404(Place, pk=place_id)
    publication.place.remove(place)
    publication.save()
    return redirect('edwoca:manifestation_print', pk=pk)


def manifestation_add_publication_publisher(request, pk, publication_id, publisher_id):
    publication = get_object_or_404(Publication, pk=publication_id)
    publisher = get_object_or_404(Corporation, pk=publisher_id)
    publication.publisher = publisher
    publication.save()
    return redirect('edwoca:manifestation_print', pk=pk)


def manifestation_remove_publication_publisher(request, pk, publication_id):
    publication = get_object_or_404(Publication, pk=publication_id)
    publication.publisher = None
    publication.save()
    return redirect('edwoca:manifestation_print', pk=pk)


class ManifestationPublicationDeleteView(DeleteView):
    model = Publication

    def get_success_url(self):
        return reverse_lazy('edwoca:manifestation_print', kwargs={'pk': self.object.manifestation.id})


class ManifestationClassificationUpdateView(SimpleFormView):
    model = Manifestation
    property = 'classification'
    view_title = _('source category')


def manifestation_provenance(request, pk):
    manifestation = get_object_or_404(EdwocaManifestation, pk=pk)
    item = manifestation.get_single_item()
    context = {
        'object': manifestation,
        'entity_type': 'manifestation',
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

        return redirect('edwoca:manifestation_provenance', pk=pk)
    else:
        pp_stations = construct_ps_set('person')
        cp_stations = construct_ps_set('corporation')
        provenance_comment_form = ItemProvenanceCommentForm(instance=item)

        context['pp_stations'] = pp_stations
        context['cp_stations'] = cp_stations
        context['form'] = provenance_comment_form
        return render(request, 'edwoca/provenance.html', context)


def manifestation_add_handwriting_writer(request, pk, handwriting_pk, person_pk):
    handwriting = get_object_or_404(ItemHandwriting, pk=handwriting_pk)
    person = get_object_or_404(Person, pk=person_pk)
    handwriting.writer = person
    handwriting.save()
    return redirect('edwoca:manifestation_manuscript', pk=pk)


def manifestation_remove_handwriting_writer(request, pk, handwriting_pk):
    handwriting = get_object_or_404(ItemHandwriting, pk=handwriting_pk)
    handwriting.writer = None
    handwriting.save()
    return redirect('edwoca:manifestation_manuscript', pk=pk)


class ModificationHandwritingDeleteView(DeleteView):
    model = ModificationHandwriting

    def get_success_url(self):
        if self.object.modification.item.manifestation.is_singleton:
            return reverse_lazy('edwoca:manifestation_manuscript', kwargs={'pk': self.object.modification.item.manifestation.id})
        else:
            return reverse_lazy('edwoca:item_manuscript', kwargs={'pk': self.object.modification.item.item.id})


def modification_add_related_work(request, modification_pk, work_pk):
    modification = get_object_or_404(ItemModification, pk=modification_pk)
    work = get_object_or_404(Work, pk=work_pk)
    modification.related_work = work
    modification.save()
    if modification.item.manifestation.is_singleton:
        return redirect('edwoca:manifestation_manuscript', pk=modification.item.manifestation.id)
    else:
        return redirect('edwoca:item_manuscript', pk=modification.item.id)


def modification_remove_related_work(request, modification_pk):
    modification = get_object_or_404(ItemModification, pk=modification_pk)
    modification.related_work = None
    modification.save()
    if modification.item.manifestation.is_singleton:
        return redirect('edwoca:manifestation_manuscript', pk=modification.item.manifestation.id)
    else:
        return redirect('edwoca:item_manuscript', pk=modification.item.id)


def modification_add_related_expression(request, modification_pk, expression_pk):
    modification = get_object_or_404(ItemModification, pk=modification_pk)
    expression = get_object_or_404(Expression, pk=expression_pk)
    modification.related_expression = expression
    modification.save()
    if modification.item.manifestation.is_singleton:
        return redirect('edwoca:manifestation_manuscript', pk=modification.item.manifestation.id)
    else:
        return redirect('edwoca:item_manuscript', pk=modification.item.id)


def modification_remove_related_expression(request, modification_pk):
    modification = get_object_or_404(ItemModification, pk=modification_pk)
    modification.related_expression = None
    modification.save()
    if modification.item.manifestation.is_singleton:
        return redirect('edwoca:manifestation_manuscript', pk=modification.item.manifestation.id)
    else:
        return redirect('edwoca:item_manuscript', pk=modification.item.id)


def manifestation_digital_copy(request, pk):
    manifestation = get_object_or_404(Manifestation, pk=pk)
    item = manifestation.items.first()
    context = {
        'object': manifestation,
        'item': item,
        'entity_type': 'manifestation',
    }

    if request.method == 'POST':
        if 'add-digital-copy' in request.POST:
            ItemDigitalCopy.objects.create(item = item)

        forms = []
        for digital_copy in item.digital_copies.all():
            prefix = f'digital_copy_{digital_copy.id}'
            form = ItemDigitizedCopyForm(request.POST, instance=digital_copy, prefix=prefix)
            if form.is_valid():
                form.save()
            forms.append(form)

        if all(f.is_valid() for f in forms):
            for form in forms:
                form.save()
        else:
            context['forms'] = forms
            return render(request, 'edwoca/manifestation_digital_copy.html', context)

        if 'remove-digital-copy' in request.POST:
            pk = request.POST.get('remove-digital-copy')
            get_object_or_404(ItemDigitalCopy, pk=pk).delete()

        return redirect('edwoca:manifestation_digital_copy', pk=manifestation.pk)
    else:
        forms = []
        for digital_copy in item.digital_copies.all():
            prefix = f'digital_copy_{digital_copy.id}'
            forms.append(ItemDigitizedCopyForm(instance=digital_copy, prefix=prefix))
        context['forms'] = forms

    return render(request, 'edwoca/manifestation_digital_copy.html', context)


def manifestation_person_dedication_remove_dedicatee(request, pk, dedication_id):
    dedication = get_object_or_404(ManifestationPersonDedication, pk=dedication_id)
    dedication.dedicatee = None
    dedication.save()
    return redirect('edwoca:manifestation_title', pk=pk)


def manifestation_corporation_dedication_remove_dedicatee(request, pk, dedication_id):
    dedication = get_object_or_404(ManifestationCorporationDedication, pk=dedication_id)
    dedication.dedicatee = None
    dedication.save()
    return redirect('edwoca:manifestation_title', pk=pk)


def manifestation_person_dedication_remove_place(request, pk, dedication_id):
    dedication = ManifestationPersonDedication.objects.get(pk=dedication_id)
    dedication.place = None
    dedication.save()
    return redirect('edwoca:manifestation_title', pk=pk)


def manifestation_corporation_dedication_remove_place(request, pk, dedication_id):
    dedication = get_object_or_404(ManifestationCorporationDedication, pk=dedication_id)
    dedication.place = None
    dedication.save()
    return redirect('edwoca:manifestation_title', pk=pk)


def manifestation_copy(request, pk):
    manifestation = get_object_or_404(Manifestation, pk = pk)
    manifestation_copy = manifestation.get_copy()
    return redirect('edwoca:manifestation_detail', pk = manifestation_copy.id)


def part_create(request, pk, publisher_pk = None):
    existing_manifestation = get_object_or_404(Manifestation, pk = pk)
    publisher = get_object_or_404(Corporation, pk=publisher_pk) if publisher_pk else None

    if request.method == 'POST':
        if not publisher:
            # handle error, maybe redirect to search page
            return redirect('edwoca:manifestation_create')

        form = ManifestationCreateForm(request.POST)
        if form.is_valid():
            period = Period.objects.create(
                    not_before = form.cleaned_data.get('not_before'),
                    not_after = form.cleaned_data.get('not_after'),
                    display = form.cleaned_data.get('display')
                )
            manifestation = Manifestation.objects.create(
                    working_title = form.cleaned_data.get('temporary_title'),
                    plate_number = form.cleaned_data.get('plate_number'),
                    source_type = form.cleaned_data.get('source_type'),
                    part_of = existing_manifestation,
                    period = period
                )
            Publication.objects.create(
                    publisher = form.cleaned_data.get('publisher'),
                    manifestation = manifestation
                )
            return redirect('edwoca:manifestation_update', pk = manifestation.id)
    else:
        form = ManifestationCreateForm(initial = {'publisher':publisher}) if publisher else None

    context = {
            'form': form,
            'referrer': 'part_create',
            'existing_manifestation': existing_manifestation
        }
    if not publisher:
        if request.GET.get('q'):
            search_form = SearchForm(request.GET)
            context['search_form'] = search_form
            context['publisher_list'] = search_form.search().models(Corporation)
        else:
            context['search_form'] = SearchForm()

    return render(request, 'edwoca/create_manifestation.html', context)


def component_create(request, pk, publisher_pk = None):
    existing_manifestation = get_object_or_404(Manifestation, pk = pk)
    publisher = get_object_or_404(Corporation, pk=publisher_pk) if publisher_pk else None

    if request.method == 'POST':
        if not publisher:
            # handle error, maybe redirect to search page
            return redirect('edwoca:manifestation_create')

        form = ManifestationCreateForm(request.POST)
        if form.is_valid():
            period = Period.objects.create(
                    not_before = form.cleaned_data.get('not_before'),
                    not_after = form.cleaned_data.get('not_after'),
                    display = form.cleaned_data.get('display')
                )
            manifestation = Manifestation.objects.create(
                    working_title = form.cleaned_data.get('temporary_title'),
                    plate_number = form.cleaned_data.get('plate_number'),
                    source_type = form.cleaned_data.get('source_type'),
                    component_of = existing_manifestation,
                    period = period
                )
            Publication.objects.create(
                    publisher = form.cleaned_data.get('publisher'),
                    manifestation = manifestation
                )
            return redirect('edwoca:manifestation_update', pk = manifestation.id)
    else:
        form = ManifestationCreateForm(initial = {'publisher':publisher}) if publisher else None

    context = {
            'form': form,
            'referrer': 'component_create',
            'existing_manifestation': existing_manifestation
        }
    if not publisher:
        if request.GET.get('q'):
            search_form = SearchForm(request.GET)
            context['search_form'] = search_form
            context['publisher_list'] = search_form.search().models(Corporation)
        else:
            context['search_form'] = SearchForm()

    return render(request, 'edwoca/create_manifestation.html', context)


def singleton_part_create(request, pk, part_label):
    existing_manifestation = get_object_or_404(Manifestation, pk = pk)

    if request.method == 'POST':
        form = SingletonCreateForm(request.POST)
        if form.is_valid():
            manifestation = EdwocaManifestation.objects.create(
                is_singleton=True,
                source_type = form.cleaned_data.get('source_type'),
                working_title = form.cleaned_data.get('working_title'),
                part_of = existing_manifestation,
                part_label = getattr(EdwocaManifestation.PartLabel, part_label.upper())
            )

            item = Item.objects.create(manifestation=manifestation)

            library = form.cleaned_data['library']
            signature = ItemSignature.objects.create(
                library=library,
                signature=form.cleaned_data['signature']
            )
            item.signatures.add(signature)
            return redirect('edwoca:manifestation_update', pk = manifestation.id)
    else:
        form = SingletonCreateForm()

    return render(request, 'edwoca/create_singleton.html', {'form': form})


def singleton_component_create(request, pk):
    existing_manifestation = get_object_or_404(Manifestation, pk = pk)

    if request.method == 'POST':
        form = SingletonCreateForm(request.POST)
        if form.is_valid():
            manifestation = EdwocaManifestation.objects.create(
                is_singleton=True,
                source_type=form.cleaned_data.get('source_type'),
                working_title = form.cleaned_data['working_title'],
                component_of = existing_manifestation
            )

            item = Item.objects.create(manifestation=manifestation)

            library = form.cleaned_data['library']
            signature = ItemSignature.objects.create(
                library=library,
                signature=form.cleaned_data['signature']
            )
            item.signatures.add(signature)
            return redirect('edwoca:manifestation_update', pk = manifestation.id)
    else:
        form = SingletonCreateForm()

    return render(request, 'edwoca/create_singleton.html', {'form': form})


def manifestation_set_collection(request, pk):
    manifestation = get_object_or_404(Manifestation, pk = pk)
    manifestation.set_collection(is_collection = True)
    manifestation.save()

    return redirect('edwoca:manifestation_relations', pk = pk)


def manifestation_unset_collection(request, pk):
    manifestation = get_object_or_404(Manifestation, pk = pk)
    manifestation.set_collection(is_collection = False)
    manifestation.save()

    return redirect('edwoca:manifestation_relations', pk = pk)


@require_POST
def collection_part_swap_view(request, pk, parent_pk, direction):
    def initialize_order_indices(qs):
        for i, child in enumerate(qs.all()):
            if child.order_index == 0:
                child.order_index = i
                child.save()

    manifestation = get_object_or_404(EdwocaManifestation, pk=pk)
    parent_manifestation = get_object_or_404(EdwocaManifestation, pk=parent_pk)

    if parent_manifestation.collection_parts.count():
        initialize_order_indices(parent_manifestation.collection_parts)
    if parent_manifestation.collection_components.count():
        initialize_order_indices(parent_manifestation.collection_components)

    success = swap_order(manifestation, direction)

    context = {'object': parent_manifestation}

    return render(
        request,
        'edwoca/partials/manifestation/collection_part_list.html',
        context
    )


