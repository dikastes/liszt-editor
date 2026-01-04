from ..forms.manifestation import *
from calendar import monthrange
from ..forms.item import SignatureForm, ItemDigitizedCopyForm, PersonProvenanceStationForm, CorporationProvenanceStationForm, ItemProvenanceCommentForm, NewItemSignatureFormSet, ItemManuscriptForm, ItemHandwritingForm
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
from django.views.generic import DeleteView, FormView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.detail import DetailView
from liszt_util.forms import SearchForm
from dmad_on_django.models import Place, Corporation, Status, Person
from dmrism.models.item import ItemSignature, PersonProvenanceStation, CorporationProvenanceStation, Item, Library, ItemHandwriting
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


def singleton_create(request):
    if request.method == 'POST':
        form = SingletonCreateForm(request.POST)
        if form.is_valid():
            manifestation = EdwocaManifestation.objects.create(
                is_singleton=True,
                source_type=form.cleaned_data.get('source_type')
            )
            if form.cleaned_data.get('temporary_title'):
                ManifestationTitle.objects.create(
                    manifestation=manifestation,
                    title=form.cleaned_data['temporary_title'],
                    status=Status.TEMPORARY
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
            manifestation = EdwocaManifestation.objects.create()
            #manifestation.publisher = form.cleaned_data.get('publisher')
            #manifestation.plate_number = form.cleaned_data.get('plate_number')
            manifestation.source_type = form.cleaned_data.get('source_type')
            manifestation.save()
            Publication.objects.create(
                    publisher = form.cleaned_data.get('publisher'),
                    plate_number = form.cleaned_data.get('plate_number'),
                    manifestation = manifestation
                )

            if form.cleaned_data.get('temporary_title'):
                ManifestationTitle.objects.create(
                    manifestation=manifestation,
                    title=form.cleaned_data['temporary_title'],
                    status=Status.TEMPORARY
                )
            return redirect('edwoca:manifestation_update', pk=manifestation.pk)
    else:
        form = ManifestationCreateForm(initial = {'publisher':publisher}) if publisher else None

    context = {'form': form}
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

    manifestation_form = ManifestationForm(request.POST or None, instance=manifestation)
    if manifestation.is_singleton:
        item = manifestation.items.first()

        if manifestation.is_singleton:
            context['signature_forms'] = []
            for signature in manifestation.get_single_item().signatures.all():
                signature_form = SignatureForm(
                        request.POST or None,
                        instance = signature,
                        prefix = f"signature-{signature.id}"
                    )
                context['signature_forms'] += [ signature_form ]
                if request.POST and signature_form.is_valid():
                    signature_form.save()
            if 'add_signature' in request.POST:
                item = manifestation.get_single_item()
                status = ItemSignature.Status.CURRENT
                if item.signatures.count():
                    status = ItemSignature.Status.FORMER
                signature = ItemSignature.objects.create(
                        item = item,
                        status = status
                    )
                context['signature_forms'] += [ SignatureForm(instance = signature, prefix = f"signature-{signature.id}") ]
        context['library_search_form'] = SearchForm()
    if request.POST and manifestation_form.is_valid():
            manifestation_form.save()
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
    ManifestationTitle.objects.create(manifestation=manifestation,title='(neu)')
    return redirect('edwoca:manifestation_title', pk = pk)

def manifestation_title_update(request, pk):
    manifestation = get_object_or_404(Manifestation, pk=pk)
    context = {
        'object': manifestation,
        'entity_type': 'manifestation'
    }

    if request.method == 'POST':
        print_form = ManifestationPrintForm(request.POST, instance=manifestation)
        if print_form.is_valid():
            print_form.save()
        # Handle existing title forms
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

        # Handle existing PersonDedication forms
        for person_dedication in manifestation.manifestation_person_dedications.all():
            prefix = f'person_dedication_{person_dedication.id}'
            form = ManifestationPersonDedicationForm(request.POST, instance=person_dedication, prefix=prefix)
            if form.is_valid():
                form.save()

        # Handle existing CorporationDedication forms
        for corporation_dedication in manifestation.manifestation_corporation_dedications.all():
            prefix = f'corporation_dedication_{corporation_dedication.id}'
            form = ManifestationCorporationDedicationForm(request.POST, instance=corporation_dedication, prefix=prefix)
            if form.is_valid():
                form.save()

        return redirect('edwoca:manifestation_title', pk=pk)
    else:
        # Initialize forms for existing titles
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

        # Initialize form for new title
        new_title_form = ManifestationTitleForm(prefix='new_title', initial = {'manifestation': manifestation})
        context['new_title_form'] = new_title_form

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

    search_form = SearchForm(request.GET or None)
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
        return reverse_lazy('edwoca:manifestation_relations', kwargs={'pk': self.object.source_manifestation.id})


class ManifestationRelationsUpdateView(EntityMixin, RelationsUpdateView):
    template_name = 'edwoca/manifestation_relations.html'
    model = Manifestation
    form_class = RelatedManifestationForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['relations_comment_form'] = ManifestationRelationsCommentForm(instance=self.object)
        expression_search_form = SearchForm(self.request.GET or None, prefix='expression')
        context['expression_search_form'] = expression_search_form
        if expression_search_form.is_valid() and expression_search_form.cleaned_data.get('q'):
            context['query_expression'] = expression_search_form.cleaned_data.get('q')
            context['found_expressions'] = expression_search_form.search().models(Expression)

        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        relations_comment_form = ManifestationRelationsCommentForm(request.POST, instance=self.object)
        if relations_comment_form.is_valid():
            relations_comment_form.save()
            return redirect(self.object.get_absolute_url())
        else:
            context = self.get_context_data(**kwargs)
            context['relations_comment_form'] = relations_comment_form
            return self.render_to_response(context)


def manifestation_expression_add(request, pk, expression_pk):
    manifestation = get_object_or_404(Manifestation, pk=pk)
    expression = get_object_or_404(Expression, pk=expression_pk)
    manifestation.expressions.add(expression)
    return redirect('edwoca:manifestation_relations', pk=pk)


def manifestation_expression_remove(request, pk, expression_pk):
    manifestation = get_object_or_404(Manifestation, pk=pk)
    expression = get_object_or_404(Expression, pk=expression_pk)
    manifestation.expressions.remove(expression)
    return redirect('edwoca:manifestation_relations', pk=pk)


class ManifestationHistoryUpdateView(SimpleFormView):
    model = Manifestation
    property = 'history'
    template_name = 'edwoca/manifestation_history.html'
    form_class = ManifestationHistoryForm

    def post(self, request, *args, **kwargs):
        response = super().post(self, request, *args, **kwargs)
        if 'calculate-machine-readable-date' in request.POST:
            period = self.object.period
            period.parse_display()
            period.save()

        return response


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

    manifestation.places.add(place)

    return redirect('edwoca:manifestation_history', pk=pk)


def manifestation_remove_place_view(request, pk, place_id):
    manifestation = get_object_or_404(Manifestation, pk=pk)
    place = get_object_or_404(Place, pk=place_id)

    manifestation.places.remove(place)

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


# this doesn't seem to need a manifestationbibform!
class ManifestationBibliographyUpdateView(EntityMixin, UpdateView):
    model = Manifestation
    form_class = ManifestationBibForm
    property = 'bib'
    template_name = 'edwoca/bib_update.html'

    def get_success_url(self):
        return reverse_lazy('edwoca:manifestation_bibliography', kwargs = {'pk': self.object.id})

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


class ManifestationCommentUpdateView(SimpleFormView):
    model = Manifestation
    property = 'comment'


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
            form = PublicationForm(request.POST, instance=publication, prefix=prefix)
            if form.is_valid():
                form.save()
        return redirect('edwoca:manifestation_print', pk=pk)

    publication_forms = []
    for publication in manifestation.publications.all():
        prefix = f'publication_{publication.id}'
        publication_forms.append(PublicationForm(instance=publication, prefix=prefix))

    context['publication_forms'] = publication_forms

    if manifestation.stitcher:
        context['linked_stitcher'] = manifestation.stitcher
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

    return render(request, 'edwoca/manifestation_print.html', context)


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


def manifestation_provenance(request, pk):
    manifestation = get_object_or_404(Manifestation, pk=pk)
    item = manifestation.items.all()[0]

    context = {
        'object': manifestation,
        'entity_type': 'manifestation',
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

        return redirect('edwoca:manifestation_provenance', pk=pk)
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

    return render(request, 'edwoca/manifestation_provenance.html', context)


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

        return redirect('edwoca:manifestation_manuscript', pk=pk)

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
    pps.owner = person
    pps.save()
    return redirect('edwoca:manifestation_provenance', pk=pk)



def person_provenance_add_bib(request, pk, pps_id, bib_id):
    pps = get_object_or_404(PersonProvenanceStation, pk=pps_id)
    bib = get_object_or_404(ZotItem, pk=bib_id)
    pps.bib = bib
    pps.save()
    return redirect('edwoca:manifestation_provenance', pk=pk)


def corporation_provenance_add_owner(request, pk, cps_id, corporation_id):
    cps = get_object_or_404(CorporationProvenanceStation, pk=cps_id)
    corporation = get_object_or_404(Corporation, pk=corporation_id)
    cps.owner = corporation
    cps.save()
    return redirect('edwoca:manifestation_provenance', pk=pk)


def corporation_provenance_add_bib(request, pk, cps_id, bib_id):
    cps = get_object_or_404(CorporationProvenanceStation, pk=cps_id)
    bib = get_object_or_404(ZotItem, pk=bib_id)
    cps.bib = bib
    cps.save()
    return redirect('edwoca:manifestation_provenance', pk=pk)


def person_provenance_remove_owner(request, pk, pps_id):
    pps = get_object_or_404(PersonProvenanceStation, pk=pps_id)
    pps.owner = None
    pps.save()
    return redirect('edwoca:manifestation_provenance', pk=pk)


def person_provenance_remove_bib(request, pk, pps_id):
    pps = get_object_or_404(PersonProvenanceStation, pk=pps_id)
    pps.bib = None
    pps.save()
    return redirect('edwoca:manifestation_provenance', pk=pk)

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


def corporation_provenance_remove_bib(request, pk, cps_id):


    cps = get_object_or_404(CorporationProvenanceStation, pk=cps_id)


    cps.bib = None


    cps.save()


    return redirect('edwoca:manifestation_provenance', pk=pk)





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
    ManifestationPersonDedication.objects.create(manifestation=manifestation)
    return redirect('edwoca:manifestation_title', pk=pk)


def corporation_dedication_add(request, pk):
    manifestation = get_object_or_404(Manifestation, pk=pk)
    ManifestationCorporationDedication.objects.create(manifestation=manifestation)
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
    dedication.dedicatee = person
    dedication.save()
    return redirect('edwoca:manifestation_title', pk=pk)


def manifestation_person_dedication_remove_dedicatee(request, pk, dedication_id):
    dedication = get_object_or_404(ManifestationPersonDedication, pk=dedication_id)
    dedication.dedicatee = None
    dedication.save()
    return redirect('edwoca:manifestation_title', pk=pk)


def manifestation_corporation_dedication_add_dedicatee(request, pk, dedication_id, corporation_id):
    dedication = get_object_or_404(ManifestationCorporationDedication, pk=dedication_id)
    corporation = get_object_or_404(Corporation, pk=corporation_id)
    dedication.dedicatee = corporation
    dedication.save()
    return redirect('edwoca:manifestation_title', pk=pk)


def manifestation_corporation_dedication_remove_dedicatee(request, pk, dedication_id):
    dedication = get_object_or_404(ManifestationCorporationDedication, pk=dedication_id)
    dedication.dedicatee = None
    dedication.save()
    return redirect('edwoca:manifestation_title', pk=pk)


def manifestation_dedication_add_place(request, pk, dedication_id, place_id):
    # This is a bit tricky, as we don't know if it's a person or corporation dedication.
    # We will try to get the person dedication first, and if it fails, we get the corporation dedication.
    try:
        dedication = ManifestationPersonDedication.objects.get(pk=dedication_id)
    except ManifestationPersonDedication.DoesNotExist:
        dedication = get_object_or_404(ManifestationCorporationDedication, pk=dedication_id)
    place = get_object_or_404(Place, pk=place_id)
    dedication.place = place
    dedication.save()
    return redirect('edwoca:manifestation_title', pk=pk)


def manifestation_dedication_remove_place(request, pk, dedication_id):
    # This is a bit tricky, as we don't know if it's a person or corporation dedication.
    # We will try to get the person dedication first, and if it fails, we get the corporation dedication.
    try:
        dedication = ManifestationPersonDedication.objects.get(pk=dedication_id)
    except ManifestationPersonDedication.DoesNotExist:
        dedication = get_object_or_404(ManifestationCorporationDedication, pk=dedication_id)
    dedication.place = None
    dedication.save()
    return redirect('edwoca:manifestation_title', pk=pk)


def manifestation_publication_remove_publisher(request, pk):
    # This is a bit tricky, as we don't know if it's a person or corporation dedication.
    # We will try to get the person dedication first, and if it fails, we get the corporation dedication.
    publication = get_object_or_404(Publication, pk=pk)
    publication.publisher = None
    publication.save()
    return redirect('edwoca:manifestation_print', pk=publication.manifestation.id)
