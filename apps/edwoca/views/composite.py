from ..forms.composite import *
from ..forms.item import SignatureFormSet, ItemDigitizedCopyForm, PersonProvenanceStationForm, CorporationProvenanceStationForm, ItemProvenanceCommentForm, NewItemSignatureFormSet, ItemManuscriptForm, ItemHandwritingForm
from ..forms.modification import ItemModificationForm, ModificationHandwritingForm
from ..forms.publication import PublicationForm
from ..forms.dedication import ManifestationPersonDedicationForm, ManifestationCorporationDedicationForm
from ..models import Manifestation as EdwocaManifestation, Letter, Expression, Work, ItemModification, ModificationHandwriting
from .base import *
from ..models import ManifestationTitle, ManifestationTitleHandwriting, ItemDigitalCopy
from ..models.composite import *
from .base import *
from bib.models import ZotItem
from django.forms import inlineformset_factory
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy, reverse
from django.views.generic import DeleteView, FormView
from django.views.generic.edit import CreateView, UpdateView
from dmad_on_django.forms import SearchForm
from dmad_on_django.models import Place, Corporation, Status, Person
from dmrism.models.item import ItemSignature, PersonProvenanceStation, CorporationProvenanceStation, Item, Library, ItemHandwriting
from dmrism.models.manifestation import Manifestation as DmrismManifestation, Publication, ManifestationPersonDedication, ManifestationCorporationDedication
from dmrism.models.manifestation import ManifestationBib


class CompositeListView(EdwocaListView):
    model = Composite

    def get_queryset(self):
        return super().get_queryset().filter(is_singleton = False)


class CompositeSearchView(EdwocaSearchView):
    model = Composite

    def get_queryset(self):
        return super().get_queryset().filter(is_singleton = False)



def composite_create(request):
    if request.method == 'POST':
        form = CompositeCreateForm(request.POST)
        if form.is_valid():
            composte = Composite.objects.create()
            if form.cleaned_data['temporary_title']:
                CompositeTitle.objects.create(
                    composte=composte,
                    title=form.cleaned_data['temporary_title'],
                    status=Status.TEMPORARY
                )

            item = Item.objects.create(composte=composte)

            library = form.cleaned_data['library']
            signature = ItemSignature.objects.create(
                library=library,
                signature=form.cleaned_data['signature']
            )
            item.signatures.add(signature)

            return redirect('edwoca:composte_update', pk=composte.pk)
    else:
        form = CompositeCreateForm()

    return render(request, 'edwoca/create_composte.html', {
        'form': form,
    })


def composte_update(request, pk):
    composte = Composite.objects.get(id=pk)
    context = {
        'object': composte,
        'entity_type': 'composte'
    }

    composte_form = CompositeForm(request.POST or None, instance=composte)
    if 'add_signature' in request.POST:
        data = request.POST.copy()
        total_forms = int(data.get(f'signatures-TOTAL_FORMS', 0))
        data[f'signatures-TOTAL_FORMS'] = str(total_forms + 1)
        signature_formset = SignatureFormSet(data, instance=item)
    else:
        signature_formset = SignatureFormSet(request.POST or None, instance=item)

    if request.method == 'POST' and 'save_changes' in request.POST:
        if item and composite_form.is_valid():
            composite_form.save()
        if signature_formset.is_valid():
            signature_formset.save()
        return redirect('edwoca:composite_update', pk=pk)

    context['signature_formset'] = signature_formset
    context['library_search_form'] = SearchForm()
    context['composite_form'] = composite_form

    return render(request, 'edwoca/composite_update.html', context)


class CompositeDeleteView(EntityMixin, DeleteView):
    model = Composite
    success_url = reverse_lazy('edwoca:composite_list')
    template_name = 'edwoca/simple_form.html'


class CompositeTitleDeleteView(DeleteView):
    model = CompositeTitle

    def get_success_url(self):
        return reverse_lazy('edwoca:composite_title', kwargs = {'pk': self.object.composite.id})


class CompositeManifestationRelationDeleteView(DeleteView):
    model = CompositeManifestationRelation

    def get_success_url(self):
        return reverse_lazy('edwoca:composite_relations', kwargs={'pk': self.object.composite.id})


class CompositeRelationsUpdateView(EntityMixin, RelationsUpdateView):
    template_name = 'edwoca/composite_relations.html'
    model = Composite
    form_class = RelatedManifestationForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['relations_comment_form'] = CompositeRelationsCommentForm(instance=self.object)
        expression_search_form = SearchForm(self.request.GET or None, prefix='expression')
        context['expression_search_form'] = expression_search_form
        if expression_search_form.is_valid() and expression_search_form.cleaned_data.get('q'):
            context['query_expression'] = expression_search_form.cleaned_data.get('q')
            context['found_expressions'] = expression_search_form.search().models(Expression)

        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        relations_comment_form = CompositeRelationsCommentForm(request.POST, instance=self.object)
        if relations_comment_form.is_valid():
            relations_comment_form.save()
            return redirect(self.object.get_absolute_url())
        else:
            context = self.get_context_data(**kwargs)
            context['relations_comment_form'] = relations_comment_form
            return self.render_to_response(context)


class CompositeHistoryUpdateView(SimpleFormView):
    model = Composite
    property = 'history'
    template_name = 'edwoca/composite_history.html'
    form_class = CompositeHistoryForm

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


def composite_add_place_view(request, pk, place_id):
    composite = get_object_or_404(Composite, pk=pk)
    place = get_object_or_404(Place, pk=place_id)

    composite.places.add(place)

    return redirect('edwoca:composite_history', pk=pk)


def composite_remove_place_view(request, pk, place_id):
    composite = get_object_or_404(Composite, pk=pk)
    place = get_object_or_404(Place, pk=place_id)

    composite.places.remove(place)

    return redirect('edwoca:composite_history', pk=pk)


def composite_add_publisher(request, pk, publisher_id):
    composite = get_object_or_404(Composite, pk=pk)
    publisher = get_object_or_404(Corporation, pk=publisher_id)

    composite.publisher = publisher
    composite.save()

    return redirect('edwoca:manifestation_print', pk=pk)


def composite_remove_publisher(request, pk):
    composite = get_object_or_404(Composite, pk=pk)
    composite.publisher = None
    composite.save()
    return redirect('edwoca:composite_print', pk=pk)


def composite_add_stitcher(request, pk, stitcher_id):
    composite = get_object_or_404(Composite, pk=pk)
    stitcher = get_object_or_404(Corporation, pk=stitcher_id)
    composite.stitcher = stitcher
    composite.save()
    return redirect('edwoca:composite_print', pk=pk)


def composite_remove_stitcher(request, pk):
    composite = get_object_or_404(Composite, pk=pk)
    composite.stitcher = None
    composite.save()
    return redirect('edwoca:composite_print', pk=pk)


class CompositeBibAddView(FormView):
    def post(self, request, *args, **kwargs):
        composite_id = self.kwargs['pk']
        zotitem_key = self.kwargs['zotitem_key']
        composite = Composite.objects.get(pk=composite_id)
        zotitem = ZotItem.objects.get(zot_key=zotitem_key)
        CompositeBib.objects.get_or_create(composite=composite, bib=zotitem)
        return redirect(reverse_lazy('edwoca:composite_bibliography', kwargs={'pk': composite_id}))


class CompositeBibDeleteView(DeleteView):
    model = CompositeBib

    def get_success_url(self):
        return reverse_lazy('edwoca:composite_bibliography', kwargs={'pk': self.object.composite.id})


def composite_letter_add(request, pk, letter_pk):
    composite = get_object_or_404(Composite, pk=pk)
    letter = get_object_or_404(Letter, pk=letter_pk)
    letter.composite.add(composite)
    return redirect('edwoca:composite_bibliography', pk=pk)


def composite_letter_remove(request, pk, letter_pk):
    composite = get_object_or_404(Composite, pk=pk)
    letter = get_object_or_404(Letter, pk=letter_pk)
    letter.composite.remove(composite)
    return redirect('edwoca:composite_bibliography', pk=pk)


class CompositeBibliographyUpdateView(EntityMixin, UpdateView):
    model = Composite
    fields = []
    property = 'bib'
    template_name = 'edwoca/bib_update.html'

    def get_success_url(self):
        return reverse_lazy('edwoca:composite_bibliography', kwargs = {'pk': self.object.id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        zotitem_search_form = SearchForm(self.request.GET or None, prefix='zotitem')
        context['zotitem_searchform'] = zotitem_search_form
        context['show_zotitem_search_form'] = True

        if zotitem_search_form.is_valid() and zotitem_search_form.cleaned_data.get('q'):
            context['zotitem_query'] = zotitem_search_form.cleaned_data.get('q')
            context[f"found_bibs"] = zotitem_search_form.search().models(ZotItem)

        letter_search_form = SearchForm(self.request.GET or None, prefix='letter')
        context['letter_searchform'] = letter_search_form
        context['show_letter_search_form'] = True

        if letter_search_form.is_valid() and letter_search_form.cleaned_data.get('q'):
            context['letter_query'] = letter_search_form.cleaned_data.get('q')
            context[f"found_letters"] = letter_search_form.search().models(Letter)

        return context


class CompositeCommentUpdateView(SimpleFormView):
    model = Composite
    property = 'comment'


def composite_print_update(request, pk):
    composite = get_object_or_404(DmrismManifestation, pk=pk)
    context = {
        'object': composite,
        'entity_type': 'composite'
    }

    if request.method == 'POST':
        if 'add_publication' in request.POST:
            Publication.objects.create(composite=composite)
            return redirect('edwoca:composite_print', pk=pk)

        for publication in composite.publications.all():
            prefix = f'publication_{publication.id}'
            form = PublicationForm(request.POST, instance=publication, prefix=prefix)
            if form.is_valid():
                form.save()
        


        return redirect('edwoca:composite_print', pk=pk)

    publication_forms = []
    for publication in composite.publications.all():
        prefix = f'publication_{publication.id}'
        publication_forms.append(PublicationForm(instance=publication, prefix=prefix))
    
    context['publication_forms'] = publication_forms

    if composite.stitcher:
        context['linked_stitcher'] = composite.stitcher
    else:
        search_form = SearchForm(request.GET or None, prefix='stitcher')
        context['stitcher_searchform'] = search_form
        context['show_stitcher_search_form'] = True

        if search_form.is_valid() and search_form.cleaned_data.get('q'):
            context['stitcher_query'] = search_form.cleaned_data.get('q')
            context[f"found_stitchers"] = search_form.search().models(Corporation)
    
    search_form = SearchForm(request.GET or None)
    if search_form.is_valid() and search_form.cleaned_data.get('q'):
        context['query'] = search_form.cleaned_data.get('q')
        context[f"found_publishers"] = search_form.search().models(Corporation)


    context['search_form'] = search_form

    return render(request, 'edwoca/composite_print.html', context)


def composite_add_publication_publisher(request, pk, publication_id, publisher_id):
    publication = get_object_or_404(Publication, pk=publication_id)
    publisher = get_object_or_404(Corporation, pk=publisher_id)
    publication.publisher = publisher
    publication.save()
    return redirect('edwoca:composite_print', pk=pk)


def composite_remove_publication_publisher(request, pk, publication_id):
    publication = get_object_or_404(Publication, pk=publication_id)
    publication.publisher = None
    publication.save()
    return redirect('edwoca:composite_print', pk=pk)


class CompositePublicationDeleteView(DeleteView):
    model = Publication

    def get_success_url(self):
        return reverse_lazy('edwoca:composite_print', kwargs={'pk': self.object.composite.id})


class CompositeClassificationUpdateView(SimpleFormView):
    model = Composite
    property = 'classification'


def composite_provenance(request, pk):
    composite = get_object_or_404(Composite, pk=pk)
    item = composite.items.all()[0]

    context = {
        'object': composite,
        'entity_type': 'composite',
        'item': item, # Pass item to context
    }

    if request.method == 'POST':
        # Handle existing PersonProvenanceStation forms
        for pps_obj in item.person_provenance_stations.all():
            prefix = f'person_provenance_{pps_obj.id}'
            pps_form = PersonProvenanceStationForm(request.POST, instance=pps_obj, prefix=prefix)
            if pps_form.is_valid():
                pps_form.save()

        # Handle existing CorporationProvenanceStation forms
        for cps_obj in item.corporation_provenance_stations.all():
            prefix = f'corporation_provenance_{cps_obj.id}'
            cps_form = CorporationProvenanceStationForm(request.POST, instance=cps_obj, prefix=prefix)
            if cps_form.is_valid():
                cps_form.save()

        # Handle private_provenance_comment form
        provenance_comment_form = ItemProvenanceCommentForm(request.POST, instance=item)
        if provenance_comment_form.is_valid():
            provenance_comment_form.save()

        return redirect('edwoca:composite_provenance', pk=pk)
    else:
        # Initialize forms for existing PersonProvenanceStation
        person_provenance_forms = []
        for pps_obj in item.person_provenance_stations.all():
            prefix = f'person_provenance_{pps_obj.id}'
            person_provenance_forms.append(PersonProvenanceStationForm(instance=pps_obj, prefix=prefix))
        context['person_provenance_forms'] = person_provenance_forms

        # Initialize forms for existing CorporationProvenanceStation
        corporation_provenance_forms = []
        for cps_obj in item.corporation_provenance_stations.all():
            prefix = f'corporation_provenance_{cps_obj.id}'
            corporation_provenance_forms.append(CorporationProvenanceStationForm(instance=cps_obj, prefix=prefix))
        context['corporation_provenance_forms'] = corporation_provenance_forms

        # Initialize private_provenance_comment form
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

    return render(request, 'edwoca/composite_provenance.html', context)


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


def composite_manuscript_update(request, pk):
    composite = get_object_or_404(Composite, pk=pk)
    item = composite.items.first()
    context = {
        'object': composite,
        'entity_type': 'composite'
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

        if 'add_handwriting' in request.POST:
            ItemHandwriting.objects.create(item=item)

        if 'add_modification' in request.POST:
            ItemModification.objects.create(item=item)

        if 'add_modification_handwriting' in request.POST:
            modification_id = request.POST.get('add_modification_handwriting')
            modification = get_object_or_404(ItemModification, pk=modification_id)
            ModificationHandwriting.objects.create(modification=modification)
            return redirect('edwoca:composite_manuscript', pk=pk)

        return redirect('edwoca:composite_manuscript', pk=pk)

    else:
        form = ItemManuscriptForm(instance=item)
        handwriting_forms = []
        for handwriting in item.handwritings.all():
            prefix = f'handwriting_{handwriting.id}'
            handwriting_forms.append(ItemHandwritingForm(instance=handwriting, prefix=prefix))
        context['handwriting_forms'] = handwriting_forms

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
    q_composite = request.GET.get('composite-q')

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

    if q_composite:
        composite_search_form = SearchForm(request.GET, prefix='composite')
        if composite_search_form.is_valid():
            context['query_composite'] = composite_search_form.cleaned_data.get('q')
            context['found_composites'] = composite_search_form.search().models(Composite)
    else:
        composite_search_form = SearchForm(prefix='composite')

    context['work_search_form'] = work_search_form
    context['expression_search_form'] = expression_search_form
    context['composite_search_form'] = composite_search_form

    if request.GET.get('modification_id'):
        context['modification_id'] = int(request.GET.get('modification_id'))

    return render(request, 'edwoca/manifestation_manuscript.html', context)


#def person_provenance_add_owner(request, pk, pps_id, person_id):
    #pps = get_object_or_404(PersonProvenanceStation, pk=pps_id)
    #person = get_object_or_404(Person, pk=person_id)
    #pps.owner = person
    #pps.save()
    #return redirect('edwoca:composite_provenance', pk=pk)



#def person_provenance_add_bib(request, pk, pps_id, bib_id):
    #pps = get_object_or_404(PersonProvenanceStation, pk=pps_id)
    #bib = get_object_or_404(ZotItem, pk=bib_id)
    #pps.bib = bib
    #pps.save()
    #return redirect('edwoca:composite_provenance', pk=pk)


#def corporation_provenance_add_owner(request, pk, cps_id, corporation_id):
    #cps = get_object_or_404(CorporationProvenanceStation, pk=cps_id)
    #corporation = get_object_or_404(Corporation, pk=corporation_id)
    #cps.owner = corporation
    #cps.save()
    #return redirect('edwoca:composite_provenance', pk=pk)


#def corporation_provenance_add_bib(request, pk, cps_id, bib_id):
    #cps = get_object_or_404(CorporationProvenanceStation, pk=cps_id)
    #bib = get_object_or_404(ZotItem, pk=bib_id)
    #cps.bib = bib
    #cps.save()
    #return redirect('edwoca:composite_provenance', pk=pk)


#def person_provenance_remove_owner(request, pk, pps_id):
    #pps = get_object_or_404(PersonProvenanceStation, pk=pps_id)
    #pps.owner = None
    #pps.save()
    #return redirect('edwoca:composite_provenance', pk=pk)


#def person_provenance_remove_bib(request, pk, pps_id):
    #pps = get_object_or_404(PersonProvenanceStation, pk=pps_id)
    #pps.bib = None
    #pps.save()
    #return redirect('edwoca:composite_provenance', pk=pk)


#def person_provenance_add_letter(request, pk, pps_id, letter_pk):
    #pps = get_object_or_404(PersonProvenanceStation, pk=pps_id)
    #letter = get_object_or_404(Letter, pk=letter_pk)
    #letter.person_provenance.add(pps)
    #return redirect('edwoca:composite_provenance', pk=pk)


#def person_provenance_remove_letter(request, pk, pps_id, letter_pk):
    #pps = get_object_or_404(PersonProvenanceStation, pk=pps_id)
    #letter = get_object_or_404(Letter, pk=letter_pk)
    #letter.person_provenance.remove(pps)
    #return redirect('edwoca:composite_provenance', pk=pk)


#def corporation_provenance_remove_owner(request, pk, cps_id):
    #cps = get_object_or_404(CorporationProvenanceStation, pk=cps_id)
    #cps.owner = None
    #cps.save()
    #return redirect('edwoca:composite_provenance', pk=pk)


#def corporation_provenance_remove_bib(request, pk, cps_id):
    #cps = get_object_or_404(CorporationProvenanceStation, pk=cps_id)
    #cps.bib = None
    #cps.save()
    #return redirect('edwoca:composite_provenance', pk=pk)


#def corporation_provenance_add_letter(request, pk, cps_id, letter_pk):
    #cps = get_object_or_404(CorporationProvenanceStation, pk=cps_id)
    #letter = get_object_or_404(Letter, pk=letter_pk)
    #letter.corporation_provenance.add(cps)
    #return redirect('edwoca:composite_provenance', pk=pk)


#def corporation_provenance_remove_letter(request, pk, cps_id, letter_pk):
    #cps = get_object_or_404(CorporationProvenanceStation, pk=cps_id)
    #letter = get_object_or_404(Letter, pk=letter_pk)
    #letter.corporation_provenance.remove(cps)
    #return redirect('edwoca:composite_provenance', pk=pk)


def composite_digital_copy(request, pk):
    composite = get_object_or_404(Composite, pk=pk)
    item = composite.items.first()
    context = {
        'object': composite,
        'item': item,
        'entity_type': 'composite',
    }

    if request.method == 'POST':
        for digital_copy in item.digital_copies.all():
            prefix = f'digital_copy_{digital_copy.id}'
            form = ItemDigitizedCopyForm(request.POST, instance=digital_copy, prefix=prefix)
            if form.is_valid():
                form.save()
        return redirect('edwoca:composite_digital_copy', pk=pk)
    else:
        forms = []
        for digital_copy in item.digital_copies.all():
            prefix = f'digital_copy_{digital_copy.id}'
            forms.append(ItemDigitizedCopyForm(instance=digital_copy, prefix=prefix))
        context['forms'] = forms

    return render(request, 'edwoca/composite_digital_copy.html', context)


def composite_digital_copy_add(request, pk):
    composite = get_object_or_404(Composite, pk=pk)
    item = composite.items.first()
    ItemDigitalCopy.objects.create(item=item)
    return redirect('edwoca:composite_digital_copy', pk=pk)


class CompositeDigitalCopyDeleteView(DeleteView):
    model = ItemDigitalCopy

    def get_success_url(self):
        composite = self.object.item.composite
        return reverse('edwoca:composite_digital_copy',kwargs={'pk': composite.id})


#def person_dedication_add(request, pk):
    #composite = get_object_or_404(Composite, pk=pk)
    #CompositePersonDedication.objects.create(composite=composite)
    #return redirect('edwoca:composite_title', pk=pk)


#def corporation_dedication_add(request, pk):
    #composite = get_object_or_404(Composite, pk=pk)
    #CompositeCorporationDedication.objects.create(composite=composite)
    #return redirect('edwoca:composite_title', pk=pk)


def composite_title_update(request, pk):
    composite = get_object_or_404(Manifestation, pk=pk)
    context = {
        'object': composite,
        'entity_type': 'composite'
    }

    if request.method == 'POST':
        # Handle existing title forms
        for title_obj in composite.titles.all():
            prefix = f'title_{title_obj.id}'
            title_form = ManifestationTitleForm(request.POST, instance=title_obj, prefix=prefix)
            if title_form.is_valid():
                title_form.save()

            # Handle existing ManifestationTitleHandwriting forms for this title
            for handwriting_obj in title_obj.handwritings.all():
                handwriting_prefix = f'title_handwriting_{handwriting_obj.id}'
                handwriting_form = ManifestationTitleHandwritingForm(request.POST, instance=handwriting_obj, prefix=handwriting_prefix)
                if handwriting_form.is_valid():
                    handwriting_form.save()

        # Handle new title form
        new_title_form = ManifestationTitleForm(request.POST, prefix='new_title')
        if new_title_form.is_valid() and new_title_form.has_changed():
            new_title = new_title_form.save(commit=False)
            new_title.manifestation = manifestation
            new_title.save()

        # Handle adding new ManifestationTitleHandwriting
        if 'add_title_handwriting' in request.POST:
            title_id_to_add_handwriting = request.POST.get('add_title_handwriting_to_title_id')
            if title_id_to_add_handwriting:
                title_obj = get_object_or_404(ManifestationTitle, pk=title_id_to_add_handwriting)
                ManifestationTitleHandwriting.objects.create(manifestation_title=title_obj)

        return redirect('edwoca:manifestation_title', pk=pk)
    else:
        # Initialize forms for existing titles
        title_forms = []
        for title_obj in manifestation.titles.all():
            prefix = f'title_{title_obj.id}'
            title_form = CompositeTitleForm(instance=title_obj, prefix=prefix) # Get the form instance

            # Initialize forms for existing ManifestationTitleHandwriting for this title
            handwriting_forms = []
            for handwriting_obj in composite_obj.handwritings.all():
                handwriting_prefix = f'composite_handwriting_{handwriting_obj.id}'
                handwriting_forms.append(CompositeTitleHandwritingForm(instance=handwriting_obj, prefix=handwriting_prefix))
            title_form.handwriting_forms = handwriting_forms # Attach to the form instance

            title_forms.append(title_form) # Append the form instance to the list

        context['title_forms'] = title_forms

        # Initialize form for new title
        new_title_form = ManifestationTitleForm(prefix='new_title', initial = {'manifestation': manifestation})
        context['new_title_form'] = new_title_form

    q_place = request.GET.get('place-q')

    if q_place:
        place_search_form = SearchForm(request.GET, prefix='place')
        if place_search_form.is_valid():
            context['query_place'] = place_search_form.cleaned_data.get('q')
            context['found_places'] = place_search_form.search().models(Place)
    else:
        place_search_form = SearchForm(prefix='place')

    context['place_search_form'] = place_search_form

    if request.GET.get('person_dedication_id'):
        context['person_dedication_id'] = int(request.GET.get('person_dedication_id'))
    if request.GET.get('corporation_dedication_id'):
        context['corporation_dedication_id'] = int(request.GET.get('corporation_dedication_id'))

    search_form = SearchForm(request.GET or None)
    context['search_form'] = search_form

    if search_form.is_valid() and search_form.cleaned_data.get('q'):
        context['query'] = search_form.cleaned_data.get('q')
        context[f"found_persons"] = search_form.search().models(Person)

    return render(request, 'edwoca/manifestation_title.html', context)


def composite_title_create(request, pk):
    composite = get_object_or_404(Composite, pk=pk)
    CompositeTitle.objects.create(composite=composite,title='(neu)')
    return redirect('edwoca:composite_title', pk = pk)
