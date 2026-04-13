import re
from haystack.query import SQ
from ..forms.manifestation import *
from calendar import monthrange
from ..forms.item import SignatureForm, ItemDigitizedCopyForm, PersonProvenanceStationForm, CorporationProvenanceStationForm, ItemProvenanceCommentForm, NewItemSignatureFormSet, ItemManuscriptForm, ItemHandwritingForm, PersonProvenanceStationBibForm, CorporationProvenanceStationBibForm, PersonProvenanceFormSet, PersonProvenanceBibFormSet, CorporationProvenanceFormSet, CorporationProvenanceBibFormSet, PersonProvenanceStationWebReference, CorporationProvenanceStationWebReference, PersonProvenanceStationWebReferenceForm, CorporationProvenanceStationWebReferenceForm
from ..forms.modification import ItemModificationForm, ModificationHandwritingForm
from ..forms.publication import PublicationForm
from ..forms.dedication import ManifestationPersonDedicationForm, ManifestationCorporationDedicationForm
from ..models import Manifestation as EdwocaManifestation, Letter, Expression, Work, ItemModification, ModificationHandwriting
from .base import *
from ..models import ManifestationTitle, ManifestationTitleHandwriting, ItemDigitalCopy
from .base import *
from bib.models import ZotItem
from django.forms import inlineformset_factory
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy, reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import DeleteView, FormView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.detail import DetailView
from liszt_util.forms import SearchForm
from dmad_on_django.models import Place, Corporation, Status, Person
from dmrism.models.item import ItemSignature, PersonProvenanceStation, CorporationProvenanceStation, Item, Library, ItemHandwriting, CorporationProvenanceStationBib, PersonProvenanceStationBib
from dmrism.models.manifestation import Manifestation as DmrismManifestation, Publication, ManifestationPersonDedication, ManifestationCorporationDedication
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
        if not publisher:
            # handle error, maybe redirect to search page
            return redirect('edwoca:manifestation_create')

        data = request.POST.copy()
        data['publisher'] = publisher
        form = ManifestationCreateForm(data)
        if form.is_valid():
            manifestation = EdwocaManifestation.objects.create(
                    source_type = form.cleaned_data.get('source_type'),
                    plate_number = form.cleaned_data.get('plate_number'),
                    working_title = form.cleaned_data['temporary_title']
                    )
            Publication.objects.create(
                    publisher = form.cleaned_data.get('publisher'),
                    manifestation = manifestation
                )

            return redirect('edwoca:manifestation_update', pk=manifestation.pk)
    else:
        if publisher:
            form = ManifestationCreateForm(initial = {'publisher': publisher})
            context = {
                    'form': form,
                    'referrer': 'manifestation_create'
                }
        else:
            form = ManifestationCreateForm()
            context = {
                    'referrer': 'manifestation_create'
                }


    if not publisher:
        if request.GET.get('q'):
            search_form = SearchForm(request.GET)
            context['search_form'] = search_form
            context['publisher_list'] = search_form.search().models(Corporation)
        else:
            context['search_form'] = SearchForm()

    return render(request, 'edwoca/create_manifestation.html', context)


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

def manifestation_title_create(request, pk):
    manifestation = get_object_or_404(Manifestation, pk=pk)
    ManifestationTitle.objects.create(manifestation=manifestation)
    return redirect('edwoca:manifestation_title', pk = pk)

def manifestation_title_update(request, pk):
    manifestation = get_object_or_404(Manifestation, pk=pk)
    context = {
        'object': manifestation,
        'entity_type': 'manifestation'
    }

    if request.method == 'POST':
        # collect any invalid forms and create a global render method in case one is invalid
        form = ManifestationTitleDedicationForm(request.POST, instance=manifestation)
        if form.is_valid():
            form.save()
        context['form'] = form

        print_form = ManifestationPrintForm(request.POST, instance=manifestation)
        if print_form.is_valid():
            print_form.save()
        # Handle existing title forms
        title_forms = []
        for title_obj in manifestation.titles.all():
            prefix = f'title_{title_obj.id}'
            title_form = ManifestationTitleForm(request.POST, instance=title_obj, prefix=prefix)
            if title_form.is_valid():
                title_form.save()

            # Handle existing ManifestationTitleHandwriting forms for this title
            for handwriting_obj in title_obj.handwritings.all():
                handwriting_prefix = f'title_handwriting_{handwriting_obj.id}'
                data = request.POST.copy()
                if f'{handwriting_prefix}-medium' not in data:
                    data[f'{handwriting_prefix}-medium'] = handwriting_obj.medium
                handwriting_form = ManifestationTitleHandwritingForm(data, instance=handwriting_obj, prefix=handwriting_prefix)
                if handwriting_form.is_valid():
                    handwriting_form.save()
            title_forms.append(title_form)
        context['title_forms'] = title_forms

        # Handle new title form
        #new_title_form = ManifestationTitleForm(request.POST, prefix='new_title')
        #if new_title_form.is_valid() and new_title_form.has_changed():
            #new_title = new_title_form.save(commit=False)
            #new_title.manifestation = manifestation
            #new_title.save()

        # Handle adding new ManifestationTitleHandwriting
        if 'add_title_handwriting' in request.POST:
            title_id_to_add_handwriting = request.POST.get('add_title_handwriting_to_title_id')
            if title_id_to_add_handwriting:
                title_obj = get_object_or_404(ManifestationTitle, pk=title_id_to_add_handwriting)
                ManifestationTitleHandwriting.objects.create(manifestation_title=title_obj)

        # Handle existing PersonDedication forms
        person_dedication_forms = []
        for person_dedication in manifestation.manifestation_person_dedications.all():
            prefix = f'person_dedication_{person_dedication.id}'
            form = ManifestationPersonDedicationForm(request.POST, instance=person_dedication, prefix=prefix)
            if form.is_valid():
                form.save()
            if f'{prefix}-calculate-machine-readable-date' in request.POST:
                period = person_dedication.period
                period.parse_display()
                period.save()
                form = ManifestationPersonDedicationForm(instance=person_dedication, prefix=prefix)
            if f'{prefix}-clear-machine-readable-date' in request.POST:
                period = person_dedication.period
                period.not_before = None
                period.not_after = None
                period.inferred = False
                period.assumed = False
                period.save()
                form = ManifestationPersonDedicationForm(instance=person_dedication, prefix=prefix)
            person_dedication_forms.append(form)
        context['person_dedication_forms'] = person_dedication_forms

        # Handle existing CorporationDedication forms
        corporation_dedication_forms = []
        for corporation_dedication in manifestation.manifestation_corporation_dedications.all():
            prefix = f'corporation_dedication_{corporation_dedication.id}'
            form = ManifestationCorporationDedicationForm(request.POST, instance=corporation_dedication, prefix=prefix)
            if form.is_valid():
                form.save()
            if f'{prefix}-calculate-machine-readable-date' in request.POST:
                period = corporation_dedication.period
                period.parse_display()
                period.save()
                form = ManifestationCorporationDedicationForm(instance=corporation_dedication, prefix=prefix)
            if f'{prefix}-clear-machine-readable-date' in request.POST:
                period = corporation_dedication.period
                period.not_before = None
                period.not_after = None
                period.inferred = False
                period.assumed = False
                period.save()
                form = ManifestationCorporationDedicationForm(instance=corporation_dedication, prefix=prefix)
            corporation_dedication_forms.append(form)
        context['corporation_dedication_forms'] = corporation_dedication_forms

        return redirect('edwoca:manifestation_title', pk = manifestation.id)

    else:
        # Initialize forms for existing titles
        form = ManifestationTitleDedicationForm(instance=manifestation)
        context['form'] = form

        title_forms = []
        for title_obj in manifestation.titles.all():
            prefix = f'title_{title_obj.id}'
            title_form = ManifestationTitleForm(instance=title_obj, prefix=prefix) # Get the form instance

            # Initialize forms for existing ManifestationTitleHandwriting for this title
            handwriting_forms = []
            for handwriting_obj in title_obj.handwritings.all():
                handwriting_prefix = f'title_handwriting_{handwriting_obj.id}'
                handwriting_forms.append(ManifestationTitleHandwritingForm(instance=handwriting_obj, prefix=handwriting_prefix))
            title_form.handwriting_forms = handwriting_forms # Attach to the form instance

            title_forms.append(title_form) # Append the form instance to the list

        context['title_forms'] = title_forms

        # Initialize forms for existing PersonDedication
        person_dedication_forms = []
        for person_dedication in manifestation.manifestation_person_dedications.all():
            prefix = f'person_dedication_{person_dedication.id}'
            person_dedication_forms.append(ManifestationPersonDedicationForm(instance=person_dedication, prefix=prefix))
        context['person_dedication_forms'] = person_dedication_forms

        # Initialize forms for existing CorporationDedication
        corporation_dedication_forms = []
        for corporation_dedication in manifestation.manifestation_corporation_dedications.all():
            prefix = f'corporation_dedication_{corporation_dedication.id}'
            corporation_dedication_forms.append(ManifestationCorporationDedicationForm(instance=corporation_dedication, prefix=prefix))
        context['corporation_dedication_forms'] = corporation_dedication_forms

    context['print_form'] = ManifestationPrintForm(instance=manifestation)

    q_dedicatee = request.GET.get('dedicatee-q')
    q_place = request.GET.get('place-q')

    if q_dedicatee:
        dedicatee_search_form = FramedSearchForm(request.GET, prefix='dedicatee', placeholder=_('search persons'))
        if dedicatee_search_form.is_valid():
            context['query_dedicatee'] = dedicatee_search_form.cleaned_data.get('q')
            context['found_persons'] = dedicatee_search_form.search().models(Person)
            context['found_corporations'] = dedicatee_search_form.search().models(Corporation)
    else:
        dedicatee_search_form = FramedSearchForm(prefix='dedicatee', placeholder=_('search persons'))

    if q_place:
        place_search_form = FramedSearchForm(request.GET, prefix='place', placeholder=_('search place'))
        if place_search_form.is_valid():
            context['query_place'] = place_search_form.cleaned_data.get('q')
            context['found_places'] = place_search_form.search().models(Place)
    else:
        place_search_form = FramedSearchForm(prefix='place', placeholder=_('search place'))

    context['dedicatee_search_form'] = dedicatee_search_form
    context['place_search_form'] = place_search_form

    if request.GET.get('person_dedication_id'):
        context['person_dedication_id'] = int(request.GET.get('person_dedication_id'))
    if request.GET.get('corporation_dedication_id'):
        context['corporation_dedication_id'] = int(request.GET.get('corporation_dedication_id'))

    search_form = FramedSearchForm(request.GET or None, placeholder=_('search persons'))
    context['search_form'] = search_form

    if search_form.is_valid() and search_form.cleaned_data.get('q'):
        context['query'] = search_form.cleaned_data.get('q')
        context[f"found_persons"] = search_form.search().models(Person)

    return render(request, 'edwoca/manifestation_title.html', context)


def manifestation_writer_add(request, pk, title_id, writer_id):
    title = get_object_or_404(ManifestationTitle, pk=title_id)
    writer = get_object_or_404(Person, pk=writer_id)
    title.writer = writer
    title.save()
    return redirect(reverse('edwoca:manifestation_title', kwargs={'pk': pk}) + f'#title-modal-{title_id}')


def manifestation_writer_remove(request, pk, title_id):
    title = get_object_or_404(ManifestationTitle, pk=title_id)
    title.writer = None
    title.save()
    return redirect(reverse('edwoca:manifestation_title', kwargs={'pk': pk}) + f'#title-modal-{title_id}')


def manifestation_title_add_handwriting_writer(request, pk, title_handwriting_pk, person_pk):
    title_handwriting = get_object_or_404(ManifestationTitleHandwriting, pk=title_handwriting_pk)
    person = get_object_or_404(Person, pk=person_pk)
    title_handwriting.writer = person
    title_handwriting.save()
    return redirect(reverse('edwoca:manifestation_title', kwargs={'pk': pk}))


def manifestation_title_remove_handwriting_writer(request, pk, title_handwriting_pk):
    title_handwriting = get_object_or_404(ManifestationTitleHandwriting, pk=title_handwriting_pk)
    title_handwriting.writer = None
    title_handwriting.save()
    return redirect(reverse('edwoca:manifestation_title', kwargs={'pk': pk}))


def manifestation_add_dedicatee(request, pk, person_id):
    manifestation = get_object_or_404(Manifestation, pk=pk)
    person = get_object_or_404(Person, pk=person_id)
    manifestation.dedicatees.add(person)
    return redirect('edwoca:manifestation_title', pk=pk)


def manifestation_remove_dedicatee(request, pk, dedicatee_id):
    dedicatee = get_object_or_404(Person, pk=dedicatee_id)
    manifestation = get_object_or_404(Manifestation, pk=pk)
    manifestation.dedicatees.remove(dedicatee)
    return redirect('edwoca:manifestation_title', pk=pk)


class ManifestationDeleteView(EntityMixin, DeleteView):
    model = EdwocaManifestation
    success_url = reverse_lazy('edwoca:manifestation_list')
    template_name = 'edwoca/delete.html'


class ManifestationTitleDeleteView(DeleteView):
    model = ManifestationTitle

    def get_success_url(self):
        return reverse_lazy('edwoca:manifestation_title', kwargs = {'pk': self.object.manifestation.id})


class ManifestationHandwritingDeleteView(DeleteView):
    model = ItemHandwriting

    def get_success_url(self):
        return reverse_lazy('edwoca:manifestation_manuscript', kwargs={'pk': self.object.item.manifestation.id})


class ManifestationTitleHandwritingDeleteView(DeleteView):
    model = ManifestationTitleHandwriting

    def get_success_url(self):
        return reverse_lazy('edwoca:manifestation_title', kwargs={'pk': self.object.manifestation_title.manifestation.id})


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
            context['found_collections'] = collection_search_form.search().models(Manifestation)#.filter(is_collection = True)

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


class ManifestationBibliographyUpdateView(EntityMixin, UpdateView):
    model = Manifestation
    fields = []
    property = 'bib'
    template_name = 'edwoca/bib_update.html'

    def get_success_url(self):
        return reverse_lazy('edwoca:manifestation_bibliography', kwargs = {'pk': self.object.id})

    def form_valid(self, form):
        context = self.get_context_data()
        manifestation_bib_forms = context['manifestation_bib_forms']

        if not all(f.is_valid() for f in manifestation_bib_forms):
            return self.form_invalid(form)

        self.object = form.save()

        for f in manifestation_bib_forms:
            f.save()

        return redirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        manifestation_bib_forms = []
        for manifestation_bib in self.object.bib_set.all():
            manifestation_bib_form = ManifestationBibForm(
                    prefix = f'manifestation_bib_{manifestation_bib.pk}',
                    instance = manifestation_bib,
                    data = self.request.POST or None
                )
            manifestation_bib_forms.append(manifestation_bib_form)
        context['manifestation_bib_forms'] = manifestation_bib_forms

        zotitem_search_form = SearchForm(self.request.GET or None, prefix='zotitem')
        context['zotitem_searchform'] = zotitem_search_form
        context['show_zotitem_search_form'] = True

        if zotitem_search_form.is_valid() and zotitem_search_form.cleaned_data.get('q'):
            context['zotitem_query'] = zotitem_search_form.cleaned_data.get('q')
            context['found_bibs'] = zotitem_search_form.search().models(ZotItem)

        letter_search_form = SearchForm(self.request.GET or None, prefix='letter')
        context['letter_searchform'] = letter_search_form
        context['show_letter_search_form'] = True

        if letter_search_form.is_valid() and letter_search_form.cleaned_data.get('q'):
            context['letter_query'] = letter_search_form.cleaned_data.get('q')
            context[f"found_letters"] = letter_search_form.search().models(Letter)

        return context


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
        if 'add_publication' in request.POST:
            Publication.objects.create(manifestation=manifestation)
            return redirect('edwoca:manifestation_print', pk=pk)

        for publication in manifestation.publications.all():
            prefix = f'publication_{publication.id}'
            publication_form = PublicationForm(request.POST, instance=publication, prefix=prefix)
            if publication_form.is_valid():
                publication_form.save()

        form = ManifestationPrintForm(request.POST, instance=manifestation)
        if form.is_valid():
            form.save()

        if 'calculate-machine-readable-date' in request.POST:
            manifestation.period.parse_display()
            manifestation.period.save()
        if 'clear-machine-readable-date' in request.POST:
            manifestation.period.not_before = None
            manifestation.period.not_after = None
            manifestation.period.assumed = False
            manifestation.period.inferred = False
            manifestation.period.save()

        return redirect('edwoca:manifestation_print', pk=pk)

    context['form'] = ManifestationPrintForm(instance = manifestation)

    publication_forms = []
    for publication in manifestation.publications.all():
        prefix = f'publication_{publication.id}'

        publisher_search_form = SearchForm(request.GET or None, prefix='publisher')
        found_publishers = []
        if publisher_search_form.is_valid() and publisher_search_form.cleaned_data.get('q'):
            found_publishers = publisher_search_form.search().models(Corporation)

        place_search_form = SearchForm(request.GET or None, prefix='place')
        found_places = []
        if place_search_form.is_valid() and place_search_form.cleaned_data.get('q'):
            found_places = place_search_form.search().models(Place)

        publication_forms.append({
                'publication_form': PublicationForm(instance=publication, prefix=prefix),
                'publisher_search_form': publisher_search_form,
                'found_publishers': found_publishers,
                'place_search_form': place_search_form,
                'found_places':found_places
            })

    context['publication_forms'] = publication_forms

    if manifestation.stitcher:
        context['linked_stitcher'] = manifestation.stitcher
    else:
        search_form = SearchForm(request.GET or None, prefix='stitcher')
        context['stitcher_searchform'] = search_form
        context['show_stitcher_search_form'] = True

        if search_form.is_valid() and search_form.cleaned_data.get('q'):
            context['stitcher_query'] = search_form.cleaned_data.get('q')
            context[f'found_stitchers'] = search_form.search().models(Corporation)

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


class ManifestationProvenanceView(UpdateView):
    model = Manifestation
    form_class = ItemProvenanceCommentForm
    template_name = 'edwoca/manifestation_provenance.html'

    def build_nested_bib_formsets(self, parent_formset, formset_class, data=None):
        enriched = []
        request = self.request

        search_structure = {
                'bib': {
                        'model': ZotItem,
                        'placeholder': _('search zotero')
                    },
                'letter': {
                        'model': Letter,
                        'placeholder': _('search letters')
                    }
            }
        if parent_formset.__class__.__name__ == 'PersonProvenanceStationFormSet':
            search_structure['owner'] = {
                    'model': Person,
                    'placeholder': _('search persons')
                }
            webref_form_class = PersonProvenanceStationWebReferenceForm
        else:
            search_structure['owner'] = {
                    'model': Corporation,
                    'placeholder': _('search corporations')
                }
            webref_form_class = CorporationProvenanceStationWebReferenceForm

        for form in parent_formset.forms:
            instance = form.instance

            webref_forms = []
            for webref in form.instance.web_references.all():
                webref_forms.append(webref_form_class(instance = webref, data = data))

            entry = {
                    'form': form,
                    'web_reference_forms': webref_forms
                }

            for model in search_structure:
                prefix = f"{form.prefix}-{model}"

                formset = formset_class(
                    data=data,
                    instance=instance,
                    prefix=prefix
                )

                search_prefix = f"{form.prefix}-{model}"
                q = request.GET.get(f"{search_prefix}-q")

                if q:
                    search_form = FramedSearchForm(request.GET, prefix=search_prefix)
                    if search_form.is_valid():
                        results = search_form.search().models(search_structure[model]['model'])
                        query = search_form.cleaned_data.get('q')
                    else:
                        results = []
                        query = None
                else:
                    search_form = FramedSearchForm(
                        prefix=search_prefix,
                        placeholder=search_structure[model]['placeholder']
                    )
                    results = []
                    query = None
                entry[f'{model}_formset'] = formset
                entry[f'{model}_search_form'] = search_form
                entry[f'{model}_query'] = query
                entry[f'{model}_results'] = results

            enriched.append(entry)

        return enriched

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        item = self.object.get_single_item()

        if self.request.POST:
            person_formset = PersonProvenanceFormSet(
                self.request.POST,
                instance=item,
                prefix='person'
            )
            corporation_formset = CorporationProvenanceFormSet(
                self.request.POST,
                instance=item,
                prefix='corporation'
            )
        else:
            person_formset = PersonProvenanceFormSet(
                instance=item,
                prefix='person'
            )
            corporation_formset = CorporationProvenanceFormSet(
                instance=item,
                prefix='corporation'
            )

        enriched_person_formset = self.build_nested_bib_formsets(
            person_formset,
            PersonProvenanceBibFormSet,
            data=self.request.POST if self.request.POST else None
        )

        enriched_corporation_formset = self.build_nested_bib_formsets(
            corporation_formset,
            CorporationProvenanceBibFormSet,
            data=self.request.POST if self.request.POST else None
        )

        context.update({
            'item': item,
            'person_formset': person_formset,
            'corporation_formset': corporation_formset,
            'enriched_person_formset': enriched_person_formset,
            'enriched_corporation_formset': enriched_corporation_formset,
            'entity_type': 'manifestation'
        })

        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        item = self.object.get_single_item()

        self.person_formset = PersonProvenanceFormSet(
            request.POST,
            instance=item,
            prefix='person'
        )

        self.corporation_formset = CorporationProvenanceFormSet(
            request.POST,
            instance=item,
            prefix='corporation'
        )

        self.enriched_person = self.build_nested_bib_formsets(
            self.person_formset,
            PersonProvenanceBibFormSet,
            data=request.POST
        )

        self.enriched_corporation = self.build_nested_bib_formsets(
            self.corporation_formset,
            CorporationProvenanceBibFormSet,
            data=request.POST
        )

        form = self.get_form()

        self.person_formset = PersonProvenanceFormSet(
            request.POST,
            instance=item,
            prefix='person'
        )

        self.corporation_formset = CorporationProvenanceFormSet(
            request.POST,
            instance=item,
            prefix='corporation'
        )

        if (
            form.is_valid()
            and self.person_formset.is_valid()
            and self.corporation_formset.is_valid()
            and self._all_nested_valid()
        ):
            return self._forms_valid(form)

        return self._forms_invalid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.object.get_single_item()
        return kwargs

    def _all_nested_valid(self):
        person_bib = [e['bib_formset'] for e in self.enriched_person]
        corp_bib = [e['bib_formset'] for e in self.enriched_corporation]
        pwr_forms = [form for forms in self.enriched_person for form in forms['web_reference_forms']]
        cwr_forms = [form for forms in self.enriched_corporation for form in forms['web_reference_forms']]

        return (
            all(fs.is_valid() for fs in person_bib)
            and all(fs.is_valid() for fs in corp_bib)
            and all(fs.is_valid() for fs in pwr_forms)
            and all(fs.is_valid() for fs in cwr_forms)
        )

    def _forms_valid(self, form):
        single_item = form.save()

        self.person_formset.instance = single_item
        self.corporation_formset.instance = single_item

        self.person_formset.save()
        self.corporation_formset.save()

        for entry in self.enriched_person:
            entry['bib_formset'].instance = entry['form'].instance
            entry['bib_formset'].save()
            for form in entry['web_reference_forms']:
                form.save()

        for entry in self.enriched_corporation:
            entry['bib_formset'].instance = entry['form'].instance
            entry['bib_formset'].save()
            for form in entry['web_reference_forms']:
                form.save()

        self._handle_period_buttons(self.person_formset)
        self._handle_period_buttons(self.corporation_formset)

        return redirect('edwoca:manifestation_provenance', pk=self.object.pk)

    def _forms_invalid(self, form):
        return self.render_to_response(
            self.get_context_data(
                form=form,
                enriched_person_formset=self.enriched_person,
                enriched_corporation_formset=self.enriched_corporation,
            ))

    def _handle_period_buttons(self, formset):
        for form in formset.forms:
            instance = form.instance
            prefix = form.prefix

            if f'{prefix}-calculate-machine-readable-date' in self.request.POST:
                period = self._ensure_period(instance)
                period.parse_display()
                period.save()

            if f'{prefix}-clear-machine-readable-date' in self.request.POST:
                period = self._ensure_period(instance)
                period.not_before = None
                period.not_after = None
                period.assumed = False
                period.inferred = False
                period.save()

    def _ensure_period(self, instance):
        if instance.period is None:
            instance.period = Period.objects.create()
            instance.save(update_fields=['period'])
        return instance.period


"""
def manifestation_provenance(request, pk):
    manifestation = get_object_or_404(Manifestation, pk=pk)
    item = manifestation.items.all()[0]

    context = {
        'object': manifestation,
        'entity_type': 'manifestation',
        'item': item
    }

    if request.method == 'POST':
        person_provenance_forms = []
        for pps_obj in item.person_provenance_stations.all():
            prefix = f'person_provenance_{pps_obj.id}'
            pps_form = PersonProvenanceStationForm(request.POST, instance=pps_obj, prefix=prefix)
            pps_bib_forms = []
            for pps_bib in pps_obj.bib_set.all():
                prefix = f'person_provenance_bib_{pps_bib.id}'
                pps_bib_forms.append(PersonProvenanceStationBibForm(request.POST, instance=pps_bib, prefix=prefix))

            if f'{prefix}-calculate-machine-readable-date' in request.POST:
                period = pps_obj.period
                period.parse_display()
                period.save()
                pps_form = PersonProvenanceStationForm(instance=pps_obj, prefix=prefix)
            if f'{prefix}-clear-machine-readable-date' in request.POST:
                period = pps_obj.period
                period.not_before = None
                period.not_after = None
                period.assumed = False
                period.inferred = False
                period.save()
                pps_form = PersonProvenanceStationForm(instance=pps_obj, prefix=prefix)
            person_provenance_forms.append(pps_form)

        corporation_provenance_forms = []
        for cps_obj in item.corporation_provenance_stations.all():
            prefix = f'corporation_provenance_{cps_obj.id}'
            cps_form = CorporationProvenanceStationForm(request.POST, instance=cps_obj, prefix=prefix)

            if f'{prefix}-calculate-machine-readable-date' in request.POST:
                period = cps_obj.period
                period.parse_display()
                period.save()
                cps_form = PersonProvenanceStationForm(instance=cps_obj, prefix=prefix)
            if f'{prefix}-clear-machine-readable-date' in request.POST:
                period = cps_obj.period
                period.not_before = None
                period.not_after = None
                period.assumed = False
                period.inferred = False
                period.save()
                cps_form = PersonProvenanceStationForm(instance=cps_obj, prefix=prefix)
            corporation_provenance_forms.append(cps_form)

        # Handle private_provenance_comment form
        provenance_comment_form = ItemProvenanceCommentForm(request.POST, instance=item)
        if provenance_comment_form.is_valid():
            provenance_comment_form.save()

        context['provenance_comment_form'] = provenance_comment_form
        breakpoint()
        if pps_form.is_valid()\
            and all(f.is_valid() for f in pps_bib_forms)\
            and cps_form.is_valid()\
            and all(f.is_valid() for f in cps_bib_forms)\
            and provenance_comment_form.is_valid():
            cps_form.save()
            pps_form.save()
            provenance_comment_form.save()

            for form in pps_bib_forms + cps_bib_forms:
                form.save()

        else:
            context['person_provenance_forms'] = person_provenance_forms
            context['corporation_provenance_forms'] = corporation_provenance_forms
            # ab hier muss ergänzt werden
            context['']

        return redirect()

    else:
        # Initialize forms for existing PersonProvenanceStation
        person_provenance_forms = []
        for pps_obj in item.person_provenance_stations.all():
            prefix = f'person_provenance_{pps_obj.id}'
            person_provenance_station_bib_forms = []
            for bib_obj in pps_obj.bib_set.all():
                prefix = f'person_provenance_bib_{bib_obj.id}'
                person_provenance_station_bib_forms.append(PersonProvenanceStationBibForm(instance=bib_obj, prefix=prefix))
            person_provenance_forms.append({
                    'pps_form': PersonProvenanceStationForm(instance=pps_obj, prefix=prefix),
                    'pps_bib_forms': person_provenance_station_bib_forms
                })
        context['person_provenance_forms'] = person_provenance_forms

        # Initialize forms for existing CorporationProvenanceStation
        corporation_provenance_forms = []
        for cps_obj in item.corporation_provenance_stations.all():
            prefix = f'corporation_provenance_{cps_obj.id}'
            corporation_provenance_station_bib_forms = []
            for bib_obj in cps_obj.bib_set.all():
                prefix = f'corporation_provenance_bib_{bib_obj.id}'
                corporation_provenance_station_bib_forms.append(CorporationProvenanceStationBibForm(instance=bib_obj, prefix=prefix))
            corporation_provenance_forms.append({
                    'cps_form': CorporationProvenanceStationForm(instance=cps_obj, prefix=prefix),
                    'cps_bib_forms': corporation_provenance_station_bib_forms
                })
        context['corporation_provenance_forms'] = corporation_provenance_forms

        # Initialize private_provenance_comment form
        provenance_comment_form = ItemProvenanceCommentForm(instance=item)
        context['provenance_comment_form'] = provenance_comment_form

    q_bib = request.GET.get('bib-q')
    q_owner = request.GET.get('owner-q')

    if q_bib:
        bib_search_form = FramedSearchForm(request.GET, prefix='bib')
        if bib_search_form.is_valid():
            context['query_bib'] = bib_search_form.cleaned_data.get('q')
            context['found_bibs'] = bib_search_form.search().models(ZotItem)
    else:
        bib_search_form = FramedSearchForm(prefix='bib', placeholder=_('search zotero'))

    if q_owner:
        owner_search_form = FramedSearchForm(request.GET, prefix='owner')
        if owner_search_form.is_valid():
            context['query_owner'] = owner_search_form.cleaned_data.get('q')
            context['found_persons'] = owner_search_form.search().models(Person)
            context['found_corporations'] = owner_search_form.search().models(Corporation)
    else:
        owner_search_form = FramedSearchForm(prefix='owner', placeholder=_('search persons'))

    context['bib_search_form'] = bib_search_form
    context['owner_search_form'] = owner_search_form

    q_letter = request.GET.get('letter-q')
    if q_letter:
        letter_search_form = FramedSearchForm(request.GET, prefix='letter')
        if letter_search_form.is_valid():
            context['query_letter'] = letter_search_form.cleaned_data.get('q')
            context['found_letters'] = letter_search_form.search().models(Letter)
    else:
        letter_search_form = FramedSearchForm(prefix='letter', placeholder=_('search letters'))
    context['letter_search_form'] = letter_search_form

    return render(request, 'edwoca/manifestation_provenance.html', context)
"""

def person_provenance_add(request, item_id):
    item = get_object_or_404(Item, pk=item_id)
    PersonProvenanceStation.objects.create(item=item)
    if item.manifestation.is_singleton:
        return redirect('edwoca:manifestation_provenance', pk=item.manifestation.id)
    return redirect('edwoca:item_provenance', pk=item_id)


def corporation_provenance_add(request, item_id):
    item = get_object_or_404(Item, pk=item_id)
    CorporationProvenanceStation.objects.create(item=item)
    if item.manifestation.is_singleton:
        return redirect('edwoca:manifestation_provenance', pk=item.manifestation.id)
    return redirect('edwoca:item_provenance', pk=item_id)


class PersonProvenanceStationDeleteView(DeleteView):
    model = PersonProvenanceStation

    def get_success_url(self):
        item = self.object.item
        if item.manifestation.is_singleton:
            return reverse('edwoca:manifestation_provenance', kwargs={'pk': item.id})
        return reverse('edwoca:item_provenance', kwargs={'pk': item.id})


class CorporationProvenanceStationDeleteView(DeleteView):
    model = CorporationProvenanceStation

    def get_success_url(self):
        item = self.object.item
        if item.manifestation.is_singleton:
            return reverse('edwoca:manifestation_provenance', kwargs={'pk': item.id})
        return reverse('edwoca:item_provenance', kwargs={'pk': item.id})


def manifestation_manuscript_update(request, pk):
    manifestation = get_object_or_404(Manifestation, pk=pk)
    item = manifestation.items.first()
    context = {
        'object': manifestation,
        'entity_type': 'manifestation'
    }
    item_handwriting_ids = [
            handwriting.id
            for handwriting
            in manifestation.get_single_item().handwritings.all()
        ]
    modification_handwriting_ids = [
            handwriting.id
            for modification
            in manifestation.get_single_item().modifications.all()
            for handwriting
            in modification.handwritings.all()
        ]

    if request.method == 'POST':
        form = ItemManuscriptForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
        else:
            return render(request, 'edwoca/manifestation_manuscript.html', context)
        context['form'] = form

        handwriting_forms = []
        for handwriting in item.handwritings.all():
            prefix = f'handwriting_{handwriting.id}'
            handwriting_form = ItemHandwritingForm(request.POST, instance=handwriting, prefix=prefix)
            if handwriting_form.is_valid():
                handwriting_form.save()
            handwriting_forms.append(handwriting_form)
        context['handwriting_forms'] = handwriting_forms

        modifications = []

        for modification in item.modifications.all():
            for handwriting in modification.handwritings.all():
                prefix = f'modification_handwriting_{handwriting.id}'
                handwriting_form = ModificationHandwritingForm(request.POST, instance=handwriting, prefix=prefix)
                if handwriting_form.is_valid():
                    handwriting_form.save()

            prefix = f'modification_{modification.id}'
            modification_form = ItemModificationForm(request.POST, instance=modification, prefix=prefix)
            if modification_form.is_valid():
                modification_form.save()

            if f'{prefix}-calculate-machine-readable-date' in request.POST:
                period = modification.period
                period.parse_display()
                period.save()
                modification_form = ItemModificationForm(instance=modification, prefix=prefix)
            if f'{prefix}-clear-machine-readable-date' in request.POST:
                period = modification.period
                period.not_before = None
                period.not_after = None
                period.assumed = False
                period.inferred = False
                period.save()
                modification_form = ItemModificationForm(instance=modification, prefix=prefix)


            handwriting_forms = []
            for handwriting in modification.handwritings.all():
                prefix = f'modification_handwriting_{handwriting.id}'
                handwriting_form = ModificationHandwritingForm(instance=handwriting, prefix = prefix)
                if handwriting_form.is_valid():
                    handwriting_form.save()
                handwriting_forms.append(handwriting_form)

            modifications.append({
                'form': modification_form,
                'handwriting_forms': handwriting_forms
            })

        if 'add_handwriting' in request.POST:
            ItemHandwriting.objects.create(item=item)

        if 'add_modification' in request.POST:
            modification = ItemModification.objects.create(item=item)
            prefix = f'modification_{modification.id}'

            modifications.append({
                'form': ItemModificationForm(instance = modification, prefix = prefix),
                'handwriting_forms': []
            })

        context['modifications'] = modifications

        if 'add_modification_handwriting' in request.POST:
            modification_id = request.POST.get('add_modification_handwriting')
            modification = get_object_or_404(ItemModification, pk=modification_id)
            ModificationHandwriting.objects.create(modification=modification)

        if 'delete_modification' in request.POST:
            modification_id = request.POST.get('delete_modification')
            modification = get_object_or_404(ItemModification, pk=modification_id)
            modification.delete()

        open_modifications = []
        for key in request.POST:
            if key.startswith('collapse_modification_'):
                mod_id = int(key.split('_')[-1])
                open_modifications.append(mod_id)
        request.session['open_modifications'] = open_modifications

        return redirect('edwoca:manifestation_manuscript', pk = manifestation.id)

    else:
        open_modifications = request.session.get('open_modifications', [])
        if 'open_modifications' in request.session:
            del request.session['open_modifications']
        context['open_modifications'] = open_modifications

        for handwriting_id in item_handwriting_ids + modification_handwriting_ids:
            prefix = f'handwriting-{handwriting_id}'
            if f'{prefix}-q' in request.GET:
                search_form = SearchForm(request.GET or None, prefix = prefix)
                if search_form.is_valid() and search_form.cleaned_data.get('q'):
                    context['query'] = search_form.cleaned_data.get('q')
                    context['search_form'] = search_form
                    context['handwriting_found_persons'] = {
                            'handwriting_id': handwriting_id,
                            'results': search_form.search().models(Person)
                        }

        form = ItemManuscriptForm(instance=item)
        handwriting_forms = []
        for handwriting in item.handwritings.all():
            prefix = f'handwriting_{handwriting.id}'
            handwriting_forms.append(ItemHandwritingForm(instance=handwriting, prefix=prefix))
        context['handwriting_forms'] = handwriting_forms

        modifications = []
        for modification in item.modifications.all():
            #modification.ensure_period()
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
    #context['search_form'] = search_form

    if request.GET.get('handwriting_id'):
        context['handwriting_id'] = int(request.GET.get('handwriting_id'))

    if request.GET.get('modification_id'):
        context['add_handwriting_for_modification'] = True
        context['modification_id'] = int(request.GET.get('modification_id'))
        if search_form.is_valid() and search_form.cleaned_data.get('q'):
            context['query'] = search_form.cleaned_data.get('q')
            context[f"modification_found_persons"] = search_form.search().models(Person)

    if request.GET.get('modification_handwriting_id'):
        context['modification_handwriting_id'] = int(request.GET.get('modification_handwriting_id'))

    # Search forms for modifications
    for key in request.GET:
        if key.startswith('modification-') and key.endswith('-q'):
            parts = key.split('-')
            modification_id = int(parts[1])
            model_name = parts[2]

            context['modification_id'] = modification_id
            if modification_id not in open_modifications:
                open_modifications.append(modification_id)

            query = request.GET.get(key)

            search_form = SearchForm({'q': query})

            if model_name == 'work':
                context['query_work'] = query
                context['found_works'] = search_form.search().models(Work)
            elif model_name == 'expression':
                context['query_expression'] = query
                context['found_expressions'] = search_form.search().models(Expression)
            elif model_name == 'manifestation':
                context['query_manifestation'] = query
                context['found_manifestations'] = search_form.search().models(Manifestation)

    work_search_form = SearchForm(prefix='work')
    expression_search_form = SearchForm(prefix='expression')
    manifestation_search_form = SearchForm(prefix='manifestation')

    context['work_search_form'] = work_search_form
    context['expression_search_form'] = expression_search_form
    context['manifestation_search_form'] = manifestation_search_form

    if request.GET.get('modification_id'):
        context['modification_id'] = int(request.GET.get('modification_id'))

    return render(request, 'edwoca/manifestation_manuscript.html', context)


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


def person_provenance_add_owner(request, pk, pps_id, person_id):
    pps = get_object_or_404(PersonProvenanceStation, pk=pps_id)
    person = get_object_or_404(Person, pk=person_id)
    pps.owner.add(person)
    pps.save()
    return redirect('edwoca:manifestation_provenance', pk=pk)



def person_provenance_add_bib(request, pk, pps_id, bib_id):
    pps = get_object_or_404(PersonProvenanceStation, pk=pps_id)
    bib = get_object_or_404(ZotItem, pk=bib_id)
    pps.bib.add(bib)
    pps.save()
    return redirect('edwoca:manifestation_provenance', pk=pk)


def person_provenance_add_webref(request, pk, pps_id):
    pps = get_object_or_404(PersonProvenanceStation, pk=pps_id)
    PersonProvenanceStationWebReference.objects.create(person_provenance_station = pps)

    item = pps.item
    if item.manifestation.is_singleton:
        return redirect('edwoca:manifestation_provenance', pk=item.manifestation.id)
    return redirect('edwoca:item_provenance', pk=item.id)


def corporation_provenance_add_webref(request, pk, cps_id):
    cps = get_object_or_404(CorporationProvenanceStation, pk=cps_id)
    CorporationProvenanceStationWebReference.objects.create(corporation_provenance_station = cps)

    item = cps.item
    if item.manifestation.is_singleton:
        return redirect('edwoca:manifestation_provenance', pk=item.manifestation.id)
    return redirect('edwoca:item_provenance', pk=item.id)


def person_provenance_remove_webref(request, webref_id):
    webref = get_object_or_404(PersonProvenanceStationWebReference, pk=webref_id)
    webref.delete()

    item = webref.person_provenance_station.item
    if item.manifestation.is_singleton:
        return redirect('edwoca:manifestation_provenance', pk=item.manifestation.id)
    return redirect('edwoca:item_provenance', pk=item.id)


def corporation_provenance_remove_webref(request, webref_id):
    webref = get_object_or_404(CorporationProvenanceStationWebReference, pk=webref_id)
    webref.delete()

    item = webref.corporation_provenance_station.item
    if item.manifestation.is_singleton:
        return redirect('edwoca:manifestation_provenance', pk=item.manifestation.id)
    return redirect('edwoca:item_provenance', pk=item.id)


def corporation_provenance_add_owner(request, pk, cps_id, corporation_id):
    cps = get_object_or_404(CorporationProvenanceStation, pk=cps_id)
    corporation = get_object_or_404(Corporation, pk=corporation_id)
    cps.owner = corporation
    cps.save()
    return redirect('edwoca:manifestation_provenance', pk=pk)


def corporation_provenance_add_bib(request, pk, cps_id, bib_id):
    cps = get_object_or_404(CorporationProvenanceStation, pk=cps_id)
    bib = get_object_or_404(ZotItem, pk=bib_id)
    cps.bib.add(bib)
    cps.save()
    return redirect('edwoca:manifestation_provenance', pk=pk)


def person_provenance_remove_owner(request, pk, pps_id, owner_id):
    pps = get_object_or_404(PersonProvenanceStation, pk=pps_id)
    owner = get_object_or_404(Person, pk=owner_id)
    pps.owner.remove(owner)
    pps.save()
    return redirect('edwoca:manifestation_provenance', pk=pk)


def person_provenance_remove_bib(request, bib_id):
    provenance_station_bib = get_object_or_404(PersonProvenanceStationBib, pk=bib_id)
    provenance_station_bib.delete()

    item = provenance_station_bib.person_provenance_station.item
    if item.manifestation.is_singleton:
        return redirect('edwoca:manifestation_provenance', pk=item.manifestation.id)
    return redirect('edwoca:item_provenance', pk=item.id)

def person_provenance_add_letter(request, pk, pps_id, letter_pk):
    pps = get_object_or_404(PersonProvenanceStation, pk=pps_id)
    letter = get_object_or_404(Letter, pk=letter_pk)
    letter.person_provenance.add(pps)
    return redirect('edwoca:manifestation_provenance', pk=pk)

def person_provenance_remove_letter(request, pk, pps_id, letter_pk):
    pps = get_object_or_404(PersonProvenanceStation, pk=pps_id)
    letter = get_object_or_404(Letter, pk=letter_pk)
    letter.person_provenance.remove(pps)
    return redirect('edwoca:manifestation_provenance', pk=pk)


def corporation_provenance_remove_owner(request, pk, cps_id):
    cps = get_object_or_404(CorporationProvenanceStation, pk=cps_id)
    cps.owner = None
    cps.save()
    return redirect('edwoca:manifestation_provenance', pk=pk)


def corporation_provenance_remove_bib(request, bib_id):
    provenance_station_bib = get_object_or_404(CorporationProvenanceStationBib, pk=bib_id)
    provenance_station_bib.delete()

    item = provenance_station_bib.corporation_provenance_station.item
    if item.manifestation.is_singleton:
        return redirect('edwoca:manifestation_provenance', pk=item.manifestation.id)
    return redirect('edwoca:item_provenance', pk=item.id)


def corporation_provenance_add_letter(request, pk, cps_id, letter_pk):
    cps = get_object_or_404(CorporationProvenanceStation, pk=cps_id)
    letter = get_object_or_404(Letter, pk=letter_pk)
    letter.corporation_provenance.add(cps)
    return redirect('edwoca:manifestation_provenance', pk=pk)


def corporation_provenance_remove_letter(request, pk, cps_id, letter_pk):
    cps = get_object_or_404(CorporationProvenanceStation, pk=cps_id)
    letter = get_object_or_404(Letter, pk=letter_pk)
    letter.corporation_provenance.remove(cps)
    return redirect('edwoca:manifestation_provenance', pk=pk)


def manifestation_digital_copy(request, pk):
    manifestation = get_object_or_404(Manifestation, pk=pk)
    item = manifestation.items.first()
    context = {
        'object': manifestation,
        'item': item,
        'entity_type': 'manifestation',
    }

    if request.method == 'POST':
        forms = []
        for digital_copy in item.digital_copies.all():
            prefix = f'digital_copy_{digital_copy.id}'
            form = ItemDigitizedCopyForm(request.POST, instance=digital_copy, prefix=prefix)
            if form.is_valid():
                form.save()
            forms.append(form)
        context['forms'] = forms
        #return redirect('edwoca:manifestation_digital_copy', pk=pk)
    else:
        forms = []
        for digital_copy in item.digital_copies.all():
            prefix = f'digital_copy_{digital_copy.id}'
            forms.append(ItemDigitizedCopyForm(instance=digital_copy, prefix=prefix))
        context['forms'] = forms

    return render(request, 'edwoca/manifestation_digital_copy.html', context)


def manifestation_digital_copy_add(request, pk):
    manifestation = get_object_or_404(Manifestation, pk=pk)
    item = manifestation.items.first()
    ItemDigitalCopy.objects.create(item=item)
    return redirect('edwoca:manifestation_digital_copy', pk=pk)


class ManifestationDigitalCopyDeleteView(DeleteView):
    model = ItemDigitalCopy

    def get_success_url(self):
        manifestation = self.object.item.manifestation
        return reverse('edwoca:manifestation_digital_copy',kwargs={'pk': manifestation.id})



def person_dedication_add(request, pk):
    manifestation = get_object_or_404(Manifestation, pk=pk)
    period = Period.objects.create()
    ManifestationPersonDedication.objects.create(manifestation=manifestation, period=period)
    return redirect('edwoca:manifestation_title', pk=pk)


def corporation_dedication_add(request, pk):
    manifestation = get_object_or_404(Manifestation, pk=pk)
    period = Period.objects.create()
    ManifestationCorporationDedication.objects.create(manifestation=manifestation, period=period)
    return redirect('edwoca:manifestation_title', pk=pk)


def manifestation_person_dedication_delete(request, pk):
    dedication = get_object_or_404(ManifestationPersonDedication, pk=pk)
    manifestation_pk = dedication.manifestation.pk
    dedication.delete()
    return redirect('edwoca:manifestation_title', pk=manifestation_pk)


def manifestation_corporation_dedication_delete(request, pk):
    dedication = get_object_or_404(ManifestationCorporationDedication, pk=pk)
    manifestation_pk = dedication.manifestation.pk
    dedication.delete()
    return redirect('edwoca:manifestation_title', pk=manifestation_pk)


def manifestation_person_dedication_add_dedicatee(request, pk, dedication_id, person_id):
    dedication = get_object_or_404(ManifestationPersonDedication, pk=dedication_id)
    person = get_object_or_404(Person, pk=person_id)
    dedication.dedicatee.add(person)
    dedication.save()
    return redirect('edwoca:manifestation_title', pk=pk)


def manifestation_person_dedication_remove_dedicatee(request, pk, dedication_id, person_id):
    dedication = get_object_or_404(ManifestationPersonDedication, pk=dedication_id)
    person = get_object_or_404(Person, pk=person_id)
    dedication.dedicatee.remove(person)
    dedication.save()
    return redirect('edwoca:manifestation_title', pk=pk)


def manifestation_corporation_dedication_add_dedicatee(request, pk, dedication_id, corporation_id):
    dedication = get_object_or_404(ManifestationCorporationDedication, pk=dedication_id)
    corporation = get_object_or_404(Corporation, pk=corporation_id)
    dedication.dedicatee.add(corporation)
    dedication.save()
    return redirect('edwoca:manifestation_title', pk=pk)


def manifestation_corporation_dedication_remove_dedicatee(request, pk, dedication_id, corporation_id):
    dedication = get_object_or_404(ManifestationCorporationDedication, pk=dedication_id)
    corporation = get_object_or_404(Corporation, pk=corporation_id)
    dedication.dedicatee.remove(corporation)
    dedication.save()
    return redirect('edwoca:manifestation_title', pk=pk)


def manifestation_person_dedication_add_place(request, pk, dedication_id, place_id):
    dedication = ManifestationPersonDedication.objects.get(pk=dedication_id)
    place = get_object_or_404(Place, pk=place_id)
    dedication.place = place
    dedication.save()
    return redirect('edwoca:manifestation_title', pk=pk)


def manifestation_person_dedication_remove_place(request, pk, dedication_id):
    dedication = ManifestationPersonDedication.objects.get(pk=dedication_id)
    dedication.place = None
    dedication.save()
    return redirect('edwoca:manifestation_title', pk=pk)


def manifestation_corporation_dedication_add_place(request, pk, dedication_id, place_id):
    dedication = get_object_or_404(ManifestationCorporationDedication, pk=dedication_id)
    place = get_object_or_404(Place, pk=place_id)
    dedication.place = place
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
