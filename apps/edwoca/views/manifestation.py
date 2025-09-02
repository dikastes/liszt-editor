from .base import *
from ..models import Manifestation as EdwocaManifestation
from ..forms.manifestation import *
from ..forms import ManifestationForm, SignatureFormSet, ItemForm, ManifestationTitleForm, ManifestationDedicationForm, ManifestationTitleHandwritingForm
from dmad_on_django.forms import SearchForm
from ..models import ManifestationTitle, ManifestationTitleHandwriting
from dmad_on_django.models.person import Person
from django.forms import inlineformset_factory
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy, reverse
from django.views.generic import DeleteView, FormView
from django.views.generic.edit import CreateView, UpdateView
from dmad_on_django.models import Place, Corporation
from dmrism.models.manifestation import ManifestationBib, ManifestationContributor
from dmrism.models.manifestation import Manifestation as DmrismManifestation
from dmrism.models.item import Signature
from bib.models import ZotItem


class ManifestationListView(EdwocaListView):
    model = EdwocaManifestation

class ManifestationSearchView(EdwocaSearchView):
    model = EdwocaManifestation


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

            new_item_form = ItemForm(request.POST, prefix='new_item')
            new_signature_formset = SignatureFormSet(request.POST, prefix='new_signatures') # No instance here yet

            # Check if a new item should be created based on signature formset data
            if new_signature_formset.is_valid() and new_signature_formset.has_changed():
                # Create new_item instance
                new_item = new_item_form.save(commit=False) # Save new_item_form if it has data, otherwise it will be an empty item
                new_item.manifestation = manifestation
                new_item.save()

                # Associate the signature formset with the newly created item
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


def manifestation_title_update(request, pk):
    manifestation = get_object_or_404(Manifestation, pk=pk)
    context = {
        'object': manifestation,
        'entity_type': 'manifestation'
    }

    if request.method == 'POST':
        # Handle existing title forms
        for title_obj in manifestation.titles.all():
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

        dedication_form = ManifestationDedicationForm(request.POST, instance=manifestation)
        if dedication_form.is_valid():
            dedication_form.save()

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

        context['dedication_form'] = ManifestationDedicationForm(instance=manifestation)

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
    return redirect(reverse('edwoca:manifestation_title', kwargs={'pk': pk}) + f'#title-modal-{title_handwriting.manifestation_title.id}')


def manifestation_title_remove_handwriting_writer(request, pk, title_handwriting_pk):
    title_handwriting = get_object_or_404(ManifestationTitleHandwriting, pk=title_handwriting_pk)
    title_handwriting.writer = None
    title_handwriting.save()
    return redirect(reverse('edwoca:manifestation_title', kwargs={'pk': pk}) + f'#title-modal-{title_handwriting.manifestation_title.id}')


def manifestation_add_dedicatee(request, pk, person_id):
    manifestation = get_object_or_404(Manifestation, pk=pk)
    person = get_object_or_404(Person, pk=person_id)
    ManifestationContributor.objects.create(manifestation=manifestation, person=person, role='DD')
    return redirect('edwoca:manifestation_title', pk=pk)

def manifestation_remove_dedicatee(request, pk, contributor_id):
    contributor = get_object_or_404(ManifestationContributor, pk=contributor_id)
    contributor.delete()
    return redirect('edwoca:manifestation_title', pk=pk)


class ManifestationDeleteView(EntityMixin, DeleteView):
    model = EdwocaManifestation
    success_url = reverse_lazy('edwoca:manifestation_list')
    template_name = 'edwoca/simple_form.html'





class ManifestationTitleDeleteView(DeleteView):
    model = ManifestationTitle

    def get_success_url(self):
        return reverse_lazy('edwoca:manifestation_title', kwargs = {'pk': self.object.manifestation.id})


class ManifestationHandwritingDeleteView(DeleteView):
    model = ManifestationHandwriting

    def get_success_url(self):
        return reverse_lazy('edwoca:manifestation_manuscript', kwargs={'pk': self.object.manifestation.id})


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
    form_class = ManifestationHistoryForm

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


class ManifestationBibAddView(FormView):
    def post(self, request, *args, **kwargs):
        manifestation_.id = self.kwargs['pk']
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


#class ManifestationPrintUpdateView(EntityMixin, UpdateView):
    #pass
    #model = Manifestation
    #property = 'print'

class ManifestationPrintUpdateView(SimpleFormView):
    model = Manifestation
    property = 'print'
    template_name = 'edwoca/manifestation_print.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        manifestation = self.get_object()

        if manifestation.publisher:
            context['linked_publisher'] = manifestation.publisher
        else:
            search_form = SearchForm(self.request.GET or None)
            context['searchform'] = search_form
            context['show_search_form'] = True

            if search_form.is_valid() and search_form.cleaned_data.get('q'):
                context['query'] = search_form.cleaned_data.get('q')
                context[f"found_publishers"] = search_form.search().models(Corporation)

        return context

class ManifestationClassificationUpdateView(SimpleFormView):
    model = Manifestation
    property = 'classification'


def manifestation_manuscript_update(request, pk):
    manifestation = get_object_or_404(Manifestation, pk=pk)
    context = {
        'object': manifestation,
        'entity_type': 'manifestation'
    }

    if request.method == 'POST':
        if 'save_changes' in request.POST:
            form = ManifestationManuscriptForm(request.POST, instance=manifestation)
            if form.is_valid():
                form.save()

            for handwriting in manifestation.manifestationhandwriting_set.all():
                prefix = f'handwriting_{handwriting.id}'
                handwriting_form = ManifestationHandwritingForm(request.POST, instance=handwriting, prefix=prefix)
                if handwriting_form.is_valid():
                    handwriting_form.save()

        if 'add_handwriting' in request.POST:
            ManifestationHandwriting.objects.create(manifestation=manifestation)

        return redirect('edwoca:manifestation_manuscript', pk=pk)

    else:
        form = ManifestationManuscriptForm(instance=manifestation)
        handwriting_forms = []
        for handwriting in manifestation.handwritings.all():
            prefix = f'handwriting_{handwriting.id}'
            handwriting_forms.append(ManifestationHandwritingForm(instance=handwriting, prefix=prefix))
        context['handwriting_forms'] = handwriting_forms

    context['form'] = form
    search_form = SearchForm(request.GET or None)
    context['search_form'] = search_form

    if search_form.is_valid() and search_form.cleaned_data.get('q'):
        context['query'] = search_form.cleaned_data.get('q')
        context[f"found_persons"] = search_form.search().models(Person)

    if request.GET.get('handwriting_id'):
        context['handwriting_id'] = int(request.GET.get('handwriting_id'))

    return render(request, 'edwoca/manifestation_manuscript.html', context)


def manifestation_add_handwriting_writer(request, pk, handwriting_pk, person_pk):
    handwriting = get_object_or_404(ManifestationHandwriting, pk=handwriting_pk)
    person = get_object_or_404(Person, pk=person_pk)
    handwriting.writer = person
    handwriting.save()
    return redirect('edwoca:manifestation_manuscript', pk=pk)


def manifestation_remove_handwriting_writer(request, pk, handwriting_pk):
    handwriting = get_object_or_404(ManifestationHandwriting, pk=handwriting_pk)
    handwriting.writer = None
    handwriting.save()
    return redirect('edwoca:manifestation_manuscript', pk=pk)
