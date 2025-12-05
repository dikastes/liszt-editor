from .base import *
from ..models.work import *
from ..forms.work import WorkForm, WorkTitleForm, WorkTitleFormSet, WorkCreateForm, WorkIdentificationForm, RelatedWorkForm, WorkContributorForm, WorkBibForm, WorkHeadCommentForm
from ..forms.dedication import WorkPersonDedicationForm, WorkCorporationDedicationForm
from dmad_on_django.models import Work as DmadWork, Person, Place, Corporation, SubjectTerm, Status
from edwoca.forms import EdwocaSearchForm
from bib.models import ZotItem
from ..models.base import Letter
from django.forms.models import formset_factory
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import DeleteView
from django.views.generic.edit import CreateView, ModelFormMixin
from django.views.generic.detail import DetailView


class WorkDetailView(EntityMixin, DetailView):
    model = Work


class WorkListView(EdwocaListView):
    model = Work


def work_create(request):
    if request.method == 'POST':
        form = WorkCreateForm(request.POST)
        if form.is_valid():
            work = Work.objects.create()
            if form.cleaned_data.get('temporary_title'):
                WorkTitle.objects.create(
                    work=work,
                    title=form.cleaned_data['temporary_title'],
                    status=Status.TEMPORARY
                )
            return redirect('edwoca:work_update', pk=work.pk)
    else:
        form = WorkCreateForm()

    return render(request, 'edwoca/create_work.html', {
        'form': form,
    })


class WorkUpdateView(EntityMixin, UpdateView):
    model = Work
    form_class = WorkForm
    template_name = 'edwoca/work_update.html'
    context_object_name = 'work'


class WorkDeleteView(EntityMixin, DeleteView):
    model = Work
    success_url = reverse_lazy('edwoca:index')
    template_name = 'edwoca/delete.html'
    context_object_name = 'work'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class WorkTitleUpdateView(EntityMixin, TitleUpdateView):
    model = Work
    form_class = WorkTitleFormSet
    formset_property = 'titles'
    template_name = 'edwoca/work_title.html'

    def get_success_url(self):
        return reverse_lazy('edwoca:work_title', kwargs = {'pk': self.get_object().id})

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        formset = self.get_form_class()(request.POST, request.FILES, instance=self.object)
        identification_form = WorkIdentificationForm(request.POST, instance=self.object)
        head_comment_form = WorkHeadCommentForm(request.POST, instance=self.object)

        if formset.is_valid() and identification_form.is_valid() and head_comment_form.is_valid():
            formset.save()
            identification_form.save()
            head_comment_form.save()

            # Handle existing PersonDedication forms
            for person_dedication in self.object.workpersondedication_set.all():
                prefix = f'person_dedication_{person_dedication.id}'
                form = WorkPersonDedicationForm(request.POST, instance=person_dedication, prefix=prefix)
                if form.is_valid():
                    form.save()

            # Handle existing CorporationDedication forms
            for corporation_dedication in self.object.workcorporationdedication_set.all():
                prefix = f'corporation_dedication_{corporation_dedication.id}'
                form = WorkCorporationDedicationForm(request.POST, instance=corporation_dedication, prefix=prefix)
                if form.is_valid():
                    form.save()

            return self.form_valid(formset)
        else:
            return self.form_invalid(formset, identification_form=identification_form, head_comment_form=head_comment_form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'identification_form' not in kwargs:
            context['identification_form'] = WorkIdentificationForm(instance=self.object)
        if 'head_comment_form' not in kwargs:
            context['head_comment_form'] = WorkHeadCommentForm(instance=self.object)

        # Initialize forms for existing PersonDedication
        person_dedication_forms = []
        for person_dedication in self.object.workpersondedication_set.all():
            prefix = f'person_dedication_{person_dedication.id}'
            person_dedication_forms.append(WorkPersonDedicationForm(instance=person_dedication, prefix=prefix))
        context['person_dedication_forms'] = person_dedication_forms

        # Initialize forms for existing CorporationDedication
        corporation_dedication_forms = []
        for corporation_dedication in self.object.workcorporationdedication_set.all():
            prefix = f'corporation_dedication_{corporation_dedication.id}'
            corporation_dedication_forms.append(WorkCorporationDedicationForm(instance=corporation_dedication, prefix=prefix))
        context['corporation_dedication_forms'] = corporation_dedication_forms

        q_dedicatee = self.request.GET.get('dedicatee-q')
        q_place = self.request.GET.get('place-q')

        if q_dedicatee:
            dedicatee_search_form = EdwocaSearchForm(self.request.GET, prefix='dedicatee')
            if dedicatee_search_form.is_valid():
                context['query_dedicatee'] = dedicatee_search_form.cleaned_data.get('q')
                context['found_persons'] = dedicatee_search_form.search().models(Person)
                context['found_corporations'] = dedicatee_search_form.search().models(Corporation)
        else:
            dedicatee_search_form = EdwocaSearchForm(prefix='dedicatee')

        if q_place:
            place_search_form = EdwocaSearchForm(self.request.GET, prefix='place')
            if place_search_form.is_valid():
                context['query_place'] = place_search_form.cleaned_data.get('q')
                context['found_places'] = place_search_form.search().models(Place)
        else:
            place_search_form = EdwocaSearchForm(prefix='place')

        context['dedicatee_search_form'] = dedicatee_search_form
        context['place_search_form'] = place_search_form

        if self.request.GET.get('person_dedication_id'):
            context['person_dedication_id'] = int(self.request.GET.get('person_dedication_id'))
        if self.request.GET.get('corporation_dedication_id'):
            context['corporation_dedication_id'] = int(self.request.GET.get('corporation_dedication_id'))

        return context


class WorkRelationsUpdateView(EntityMixin, RelationsUpdateView):
    template_name = 'edwoca/work_relations.html'
    model = Work
    form_class = RelatedWorkForm


class RelatedWorkAddView(RelatedEntityAddView):
    template_name = 'edwoca/work_relations.html'
    model = RelatedWork


class RelatedWorkRemoveView(DeleteView):
    model = RelatedWork

    def get_success_url(self):
        return reverse_lazy('edwoca:work_relations', kwargs={'pk': self.object.source_work.id})


class ReferenceWorkRemoveView(DeleteView):
    model = WorkWorkReference

    def get_success_url(self):
        return reverse_lazy('edwoca:work_references', kwargs={'pk': self.object.work.id})


class ReferencePersonRemoveView(DeleteView):
    model = PersonWorkReference

    def get_success_url(self):
        return reverse_lazy('edwoca:work_references', kwargs={'pk': self.object.work.id})


class ReferenceCorporationRemoveView(DeleteView):
    model = CorporationWorkReference

    def get_success_url(self):
        return reverse_lazy('edwoca:work_references', kwargs={'pk': self.object.work.id})


class ReferencePlaceRemoveView(DeleteView):
    model = PlaceWorkReference

    def get_success_url(self):
        return reverse_lazy('edwoca:work_references', kwargs={'pk': self.object.work.id})


class ReferenceSubjectTermRemoveView(DeleteView):
    model = SubjectTermWorkReference

    def get_success_url(self):
        return reverse_lazy('edwoca:work_references', kwargs={'pk': self.object.work.id})


class WorkSearchView(EdwocaSearchView):
    model = Work


class WorkContributorsUpdateView(EntityMixin, ContributorsUpdateView):
    model = Work
    form_class = WorkContributorForm


class WorkContributorAddView(ContributorAddView):
    model = WorkContributor


class WorkContributorRemoveView(DeleteView):
    model = WorkContributor

    def get_success_url(self):
        return reverse_lazy('edwoca:work_contributors', kwargs={'pk': self.object.work.id})


class WorkHistoryUpdateView(SimpleFormView):
    model = Work
    property = 'history'


class WorkBibliographyUpdateView(EntityMixin, UpdateView):
    model = Work
    form_class = WorkBibForm
    property = 'bib'
    template_name = 'edwoca/bib_update.html'

    def get_success_url(self):
        return reverse_lazy('edwoca:work_bibliography', kwargs = {'pk': self.object.id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        zotitem_search_form = EdwocaSearchForm(self.request.GET or None, prefix='zotitem')
        context['zotitem_searchform'] = zotitem_search_form
        context['show_zotitem_search_form'] = True

        if zotitem_search_form.is_valid() and zotitem_search_form.cleaned_data.get('q'):
            context['zotitem_query'] = zotitem_search_form.cleaned_data.get('q')
            context[f"found_bibs"] = zotitem_search_form.search().models(ZotItem)

        letter_search_form = EdwocaSearchForm(self.request.GET or None, prefix='letter')
        context['letter_searchform'] = letter_search_form
        context['show_letter_search_form'] = True

        if letter_search_form.is_valid() and letter_search_form.cleaned_data.get('q'):
            context['letter_query'] = letter_search_form.cleaned_data.get('q')
            context[f"found_letters"] = letter_search_form.search().models(Letter)

        context['entity_type'] = 'work'
        return context


class WorkCommentUpdateView(SimpleFormView):
    model = Work
    property = 'comment'


class WorkHeadCommentUpdateView(SimpleFormView):
    model = Work
    property = 'private_head_comment'




class WorkBibAddView(FormView):
    def post(self, request, *args, **kwargs):
        work_id = self.kwargs['pk']
        zotitem_key = self.kwargs['zotitem_key']
        work = Work.objects.get(pk=work_id)
        zotitem = ZotItem.objects.get(zot_key=zotitem_key)
        WorkBib.objects.get_or_create(work=work, bib=zotitem)
        return redirect(reverse_lazy('edwoca:work_bibliography', kwargs={'pk': work_id}))


class WorkBibDeleteView(DeleteView):
    model = WorkBib

    def get_success_url(self):
        return reverse_lazy('edwoca:work_bibliography', kwargs={'pk': self.object.work.id})


def work_expression_create(request, pk):
    work = get_object_or_404(Work, pk = pk)
    Expression.objects.create(work = work)
    return redirect('edwoca:work_relations', pk = pk)


class WorkReferencesUpdateView(EntityMixin, UpdateView):
    model = Work
    fields = []
    template_name = 'edwoca/work_references.html'
    reference_models = { 
            'work': DmadWork,
            'person': Person,
            'corporation': Corporation,
            'place': Place,
            'subject_term': SubjectTerm,
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['show_search_forms'] = True
        for reference_model in self.reference_models:
            search_form = EdwocaSearchForm(self.request.GET or None, prefix = f'{reference_model}_search')
            context[f'{reference_model}_searchform'] = search_form

            if search_form.is_valid() and search_form.cleaned_data.get('q'):
                context[f'{reference_model}_query'] = search_form.cleaned_data.get('q')
                context[f'found_{reference_model}s'] = search_form.search().models(self.reference_models[reference_model])

        return context


def reference_work_add(request, pk, target_reference_work):
    work = get_object_or_404(Work, pk = pk)
    reference_work = get_object_or_404(DmadWork, pk = target_reference_work)
    WorkWorkReference.objects.create(work = work, reference_work = reference_work)
    return redirect('edwoca:work_references', pk = pk)


def reference_person_add(request, pk, target_reference_person):
    work = get_object_or_404(Work, pk = pk)
    person = get_object_or_404(Person, pk = target_reference_person)
    PersonWorkReference.objects.create(work = work, person = person)
    return redirect('edwoca:work_references', pk = pk)


def reference_corporation_add(request, pk, target_reference_corporation):
    work = get_object_or_404(Work, pk = pk)
    corporation = get_object_or_404(Corporation, pk = target_reference_corporation)
    CorporationWorkReference.objects.create(work = work, corporation = corporation)
    return redirect('edwoca:work_references', pk = pk)


def reference_place_add(request, pk, target_reference_place):
    work = get_object_or_404(Work, pk = pk)
    place = get_object_or_404(Place, pk = target_reference_place)
    PlaceWorkReference.objects.create(work = work, place = place)
    return redirect('edwoca:work_references', pk = pk)


def reference_subjectterm_add(request, pk, target_reference_subjectterm):
    work = get_object_or_404(Work, pk = pk)
    subject_term = get_object_or_404(SubjectTerm, pk = target_reference_subjectterm)
    SubjectTermWorkReference.objects.create(work = work, subject_term = subject_term)
    return redirect('edwoca:work_references', pk = pk)

def work_person_dedication_add(request, pk):
    work = get_object_or_404(Work, pk=pk)
    WorkPersonDedication.objects.create(work=work)
    return redirect('edwoca:work_title', pk=pk)

def work_corporation_dedication_add(request, pk):
    work = get_object_or_404(Work, pk=pk)
    WorkCorporationDedication.objects.create(work=work)
    return redirect('edwoca:work_title', pk=pk)


def work_person_dedication_delete(request, pk):
    dedication = get_object_or_404(WorkPersonDedication, pk=pk)
    work_pk = dedication.work.pk
    dedication.delete()
    return redirect('edwoca:work_title', pk=work_pk)

def work_corporation_dedication_delete(request, pk):
    dedication = get_object_or_404(WorkCorporationDedication, pk=pk)
    work_pk = dedication.work.pk
    dedication.delete()
    return redirect('edwoca:work_title', pk=work_pk)

def work_person_dedication_add_dedicatee(request, pk, dedication_id, person_id):
    dedication = get_object_or_404(WorkPersonDedication, pk=dedication_id)
    person = get_object_or_404(Person, pk=person_id)
    dedication.dedicatee = person
    dedication.save()
    return redirect('edwoca:work_title', pk=pk)

def work_person_dedication_remove_dedicatee(request, pk, dedication_id):
    dedication = get_object_or_404(WorkPersonDedication, pk=dedication_id)
    dedication.dedicatee = None
    dedication.save()
    return redirect('edwoca:work_title', pk=pk)

def work_corporation_dedication_add_dedicatee(request, pk, dedication_id, corporation_id):
    dedication = get_object_or_404(WorkCorporationDedication, pk=dedication_id)
    corporation = get_object_or_404(Corporation, pk=corporation_id)
    dedication.dedicatee = corporation
    dedication.save()
    return redirect('edwoca:work_title', pk=pk)

def work_corporation_dedication_remove_dedicatee(request, pk, dedication_id):
    dedication = get_object_or_404(WorkCorporationDedication, pk=dedication_id)
    dedication.dedicatee = None
    dedication.save()
    return redirect('edwoca:work_title', pk=pk)

def work_dedication_add_place(request, pk, dedication_id, place_id):
    # This is a bit tricky, as we don't know if it's a person or corporation dedication.
    # We will try to get the person dedication first, and if it fails, we get the corporation dedication.
    try:
        dedication = WorkPersonDedication.objects.get(pk=dedication_id)
    except WorkPersonDedication.DoesNotExist:
        dedication = get_object_or_404(WorkCorporationDedication, pk=dedication_id)
    place = get_object_or_404(Place, pk=place_id)
    dedication.place = place
    dedication.save()
    return redirect('edwoca:work_title', pk=pk)


def work_dedication_remove_place(request, pk, dedication_id):
    # This is a bit tricky, as we don't know if it's a person or corporation dedication.
    # We will try to get the person dedication first, and if it fails, we get the corporation dedication.
    try:
        dedication = WorkPersonDedication.objects.get(pk=dedication_id)
    except WorkPersonDedication.DoesNotExist:
        dedication = get_object_or_404(WorkCorporationDedication, pk=dedication_id)
    dedication.place = None
    dedication.save()
    return redirect('edwoca:work_title', pk=pk)

def work_letter_add(request, pk, letter_pk):
    work = get_object_or_404(Work, pk=pk)
    letter = get_object_or_404(Letter, pk=letter_pk)
    letter.work.add(work)
    return redirect('edwoca:work_bibliography', pk=pk)

def work_letter_remove(request, pk, letter_pk):
    work = get_object_or_404(Work, pk=pk)
    letter = get_object_or_404(Letter, pk=letter_pk)
    work.letters.remove(letter)
    return redirect('edwoca:work_bibliography', pk=pk)
