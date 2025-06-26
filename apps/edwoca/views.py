from django.urls import reverse_lazy
from django.shortcuts import render, get_object_or_404, redirect
from django.core import serializers
from django.http import JsonResponse
from django.views import generic
from django.views.generic import ListView
from django.forms import HiddenInput, formset_factory
from django.forms.models import inlineformset_factory
from .forms import *
from edwoca import forms as edwoca_forms
from edwoca import models as edwoca_models
from .models import *
from dmad_on_django.models import Status, Person, Period, Place
from dmad_on_django.forms import SearchForm
from bib.models import ZotItem
from json import dumps as json_dump
from haystack.generic_views import SearchView


def work_relation_view(request, work_id):
    try:
        work = Work.objects.get(pk=work_id)
    except Work.DoesNotExist:
        raise Http404(f"Unknown work with id {work_id}")


class RelationsUpdateView(generic.UpdateView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_form = SearchForm(self.request.GET or None)
        context['searchform'] = search_form
        context['show_search_form'] = True

        if search_form.is_valid() and search_form.cleaned_data.get('q'):
            context['query'] = search_form.cleaned_data.get('q')
            target_model = getattr(edwoca_models, self.request.GET['target_model'].capitalize())
            context[f"found_{target_model.__name__.lower()}s"] = search_form.search().models(target_model)

        return context


class WorkRelationsUpdateView(RelationsUpdateView):
    template_name = 'edwoca/work_relations.html'
    model = Work
    form_class = RelatedWorkForm


class ManifestationRelationsUpdateView(RelationsUpdateView):
    template_name = 'edwoca/manifestation_relations.html'
    model = Manifestation
    form_class = RelatedManifestationForm


class EdwocaSearchView(SearchView):
    template_name = 'edwoca/list.html'
    form_class = SearchForm

    # redirect to list view if empty query
    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', '')
        if not query or query == '':
            return redirect(f'edwoca:{self.model.__name__.lower()}_list')
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['work_count'] = Work.objects.all().count()
        context['manifestation_count'] = Manifestation.objects.all().count()
        context['object_list'] = [ result.object for result in context['object_list'] ]
        return context

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.models(getattr(edwoca_models, self.model.__name__))


class WorkSearchView(EdwocaSearchView):
    model = Work

class ManifestationSearchView(EdwocaSearchView):
    model = Manifestation

class EdwocaListView(ListView):
    template_name = 'edwoca/list.html'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = SearchForm()
        context['work_count'] = Work.objects.all().count()
        context['manifestation_count'] = Manifestation.objects.all().count()
        return context


class WorkListView(EdwocaListView):
    model = Work


class ManifestationListView(EdwocaListView):
    model = Manifestation



"""
class IndexView(generic.ListView):
    template_name = 'edwoca/index.html'
    context_object_name = 'entities'

    def get_queryset(self):
        return {
                'works': Work.objects.all().order_by('-id'),
                'sources': Manifestation.objects.all().order_by('-id')
            }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['work_count'] = Work.objects.count()
        context['expression_count'] = Expression.objects.count()
        context['manifestation_count'] = Manifestation.objects.count()
        context['item_count'] = Item.objects.count()
        context['person_count'] = Person.objects.count()
        context['place_count'] = Place.objects.count()
        context['corporation_count'] = 0
        return context
"""

def index(request):
    return redirect('edwoca:work_search')

class WorkCreateView(generic.edit.CreateView):
    model = Work
    form_class = WorkForm
    template_name = 'edwoca/create.html'

    def get_success_url(self):
        return reverse_lazy('edwoca:work_update', kwargs = {'pk': self.object.id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['title_formset'] = WorkTitleFormSet(self.request.POST)
        else:
            WorkTitleFormSet.can_delete = False
            context['title_form_set'] = WorkTitleFormSet()
        context['view_title'] = f"Neues Werk anlegen"
        context['button_label'] = "speichern"
        context['return_target'] = 'edwoca:index'
        context['return_pk'] = None
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        title_formset = context['title_formset']

        if title_formset.is_valid():
            response = super().form_valid(form)
            self.object = form.save()
            title_formset.instance = self.object
            title_formset.save()
            self.object.save()
            return response
        else:
            return self.form_invalid(form)


class WorkUpdateView(generic.edit.UpdateView):
    model = Work
    form_class = WorkForm
    template_name = 'edwoca/work_update.html'
    context_object_name = 'work'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title_form_set'] = formset_factory(WorkTitleForm)
        context['view_title'] = f"Werk { self.object } bearbeiten"
        context['button_label'] = "speichern"
        context['return_target'] = 'edwoca:work_detail'
        context['return_pk'] = self.object.id
        return context


class WorkDeleteView(generic.edit.DeleteView):
    model = Work
    success_url = reverse_lazy('edwoca:index')
    template_name = 'edwoca/simple_form.html'
    context_object_name = 'work'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class WorkBibView(generic.edit.ModelFormMixin):
    model = WorkBib
    fields = [
            'bib',
            'work'
        ]


class WorkTitleView(generic.edit.ModelFormMixin):
    model = WorkTitle
    fields = [
            'title',
            'status',
            'language',
            'work'
        ]


class WorkContributorView(generic.edit.ModelFormMixin):
    model = WorkContributor
    fields = [
            'work',
            'person',
            'role'
        ]


class ContributorsUpdateView(generic.edit.UpdateView):
    fields = []
    template_name = 'edwoca/contributor_update.html'

    def get_success_url(self):
        return reverse_lazy(f"edwoca:{self.model.__name__.lower()}_contributors", kwargs = {'pk': self.get_object().id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'form' not in kwargs:
            context['form'] = getattr(edwoca_forms, f"{self.model.__name__}ContributorFormSet")(instance = self.object)
        else:
            context['form'] = kwargs['form']
        return context

    def post(self, request, *args, **kwargs):
        model_name = self.model.__name__
        self.object = self.get_object()

        if 'add-form' in request.POST:
            data = request.POST.copy()
            total_forms = int(data.get('workcontributor_set-TOTAL_FORMS', 0))
            data['workcontributor_set-TOTAL_FORMS'] = str(total_forms + 1)
            form = getattr(edwoca_forms, f"{model_name}ContributorFormSet")(data, instance=self.object)
            return self.render_to_response(self.get_context_data(form=form))

        formset = getattr(edwoca_forms, f"{model_name}ContributorFormSet")(
                request.POST,
                instance = self.object,
                queryset = getattr(edwoca_models, f"{model_name}Contributor").objects.filter(**{model_name.lower(): self.object})
            )
        for form in formset:
            if not getattr(form.instance, model_name.lower()):
                setattr(form.instance, model_name.lower(), self.get_object())

        if formset.is_valid():
            for form in formset:
                formset.instance.save()
            return self.form_valid(formset)
        else:
            return self.form_invalid(formset)


class WorkContributorsUpdateView(ContributorsUpdateView):
    model = Work


class ExpressionContributorsUpdateView(ContributorsUpdateView):
    model = Expression


class ManifestationContributorsUpdateView(ContributorsUpdateView):
    model = Manifestation



class RelatedWorkView(generic.edit.ModelFormMixin):
    model = RelatedWork
    fields = [
            'source_work',
            'target_work',
            'comment',
            'label'
        ]








class ExpressionPeriodView(generic.edit.ModelFormMixin):
    model = Period
    fields = [
            'not_before',
            'not_after',
            'display'
        ]







class ExpressionTitleView(generic.edit.ModelFormMixin):
    model = ExpressionTitle
    fields = [
            'title',
            'language',
            'status',
            'expression'
        ]







class ExpressionContributorView(generic.edit.ModelFormMixin):
    model = ExpressionContributor
    fields = [
            'expression',
            'person',
            'role'
        ]







class ExpressionView(generic.edit.ModelFormMixin):
    model = Expression
    fields = [
            'incipit_music',
            'incipit_text',
            'period_comment',
            'history',
            'work'
        ]


class ExpressionCreateView(generic.CreateView):
    model = Expression
    form_class = ExpressionForm
    template_name = 'edwoca/create.html'

    def get_success_url(self):
        return reverse_lazy('edwoca:expression_update', kwargs = {'pk': self.object.id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = context['form']
        if self.request.POST:
            context['title_formset'] = ExpressionTitleFormSet(self.request.POST)
        else:
            WorkTitleFormSet.can_delete = False
            context['title_form_set'] = ExpressionTitleFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        title_formset = context['title_formset']

        instance = form.save(commit=False)
        instance.work = Work.objects.get(id=self.kwargs['work_id'])

        if title_formset.is_valid():
            instance.save()
            self.object = form.save()
            title_formset.instance = self.object
            title_formset.save()
            return redirect(self.get_success_url())
        else:
            return self.form_invalid(form)


class ExpressionUpdateView(generic.UpdateView):
    model = Expression
    form_class = ExpressionForm
    template_name = 'edwoca/expression_update.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title_form_set'] = formset_factory(WorkTitleForm)
        return context


class FormsetUpdateView(generic.UpdateView):
    template_name = 'edwoca/simple_formset.html'

    def get_context_dat(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'form' not in kwargs:
            context['form'] = self.form_class(instance = self.object)
        else:
            context['form'] = kwargs['form']
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        if 'add-form' in request.POST:
            data = request.POST.copy()
            total_forms = int(data.get(f'{self.formset_property}-TOTAL_FORMS', 0))
            data[f'{self.formset_property}-TOTAL_FORMS'] = str(total_forms + 1)
            data[f'{self.formset_property}-{total_forms}-language'] = 'de'
            form = self.form_class(data, instance=self.object)
            return self.render_to_response(self.get_context_data(form=form))

        form = self.form_class(request.POST, instance=self.object)
        for title_form in form.forms:
            raw_title = title_form.data.get(title_form.add_prefix('title'), '').strip()
            if not raw_title:
                form.empty_permitted = True
                title_form.fields['title'].required = False
                title_form.fields['language'].required = False

        if form.is_valid():
            form.save()
            return redirect(self.get_success_url())

        return self.render_to_response(self.get_context_data(form=form))


class ExpressionTitleUpdateView(FormsetUpdateView):
    model = Expression
    form_class = ExpressionTitleFormSet
    formset_property = 'titles'

    def get_success_url(self):
        return reverse_lazy('edwoca:expression_title_update', kwargs = {'pk': self.object.id})


class WorkTitleUpdateView(FormsetUpdateView):
    model = Work
    form_class = WorkTitleFormSet
    formset_property = 'titles'

    def get_success_url(self):
        return reverse_lazy('edwoca:work_title', kwargs = {'pk': self.object.id})


class ItemTitleUpdateView(FormsetUpdateView):
    model = Item
    form_class = ItemTitleFormSet
    formset_property = 'titles'

    def get_success_url(self):
        return reverse_lazy('edwoca:item_title', kwargs = {'pk': self.object.id})


class WorkDetailView(generic.detail.DetailView):
    model = Work

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['related_work_targets'] = RelatedWork.objects.filter(source_work=self.object)
        context['related_work_sources'] = RelatedWork.objects.filter(target_work=self.object)
        context['contributors'] = WorkContributor.objects.filter(work=self.object)
        return context


class ManifestationDetailView(generic.detail.DetailView):
    model = Manifestation

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['related_manifestation_targets'] = RelatedManifestation.objects.filter(source_manifestation=self.object)
        context['related_manifestation_sources'] = RelatedManifestation.objects.filter(target_manifestation=self.object)
        return context


class ManifestationCreateView(generic.edit.CreateView):
    model = Manifestation
    form_class = ManifestationForm
    template_name = 'edwoca/create.html'

    def get_success_url(self):
        return reverse_lazy('edwoca:manifestation_update', kwargs = {'pk': self.object.id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['title_formset'] = ManifestationTitleFormSet(self.request.POST)
        else:
            ManifestationTitleFormSet.can_delete = False
            context['title_form_set'] = ManifestationTitleFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        title_formset = context['title_formset']

        if title_formset.is_valid():
            response = super().form_valid(form)
            self.object = form.save()
            title_formset.instance = self.object
            title_formset.save()
            self.object.save()
            return response
        else:
            return self.form_invalid(form)


class ManifestationUpdateView(generic.edit.UpdateView):
    model = Manifestation
    form_class = ManifestationForm
    template_name = 'edwoca/simple_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['view_title'] = f"Manifestation { self.object } bearbeiten"
        context['button_label'] = "speichern"
        context['return_target'] = 'edwoca:manifestation_detail'
        context['return_pk'] = self.object.id
        return context


class ManifestationDeleteView(generic.edit.DeleteView):
    model = Manifestation
    success_url = reverse_lazy('edwoca:manifestation_list')
    template_name = 'edwoca/simple_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class ManifestationContributorView(generic.edit.ModelFormMixin):
    model = WorkContributor
    fields = [
            'manifestation',
            'person',
            'role'
        ]


class ItemContributorView(generic.edit.ModelFormMixin):
    model = WorkContributor
    fields = [
            'item',
            'person',
            'role'
        ]


class RelatedManifestationView(generic.edit.ModelFormMixin):
    model = RelatedManifestation
    fields = [
            'source_manifestation',
            'target_manifestation',
            'comment',
            'label'
        ]


class ItemView(generic.edit.ModelFormMixin):
    model = Item
    fields = [
            'cover',
            'handwriting',
            'history',
            'iiif_manifest',
            'manifestation'
        ]


class ProvenanceStateView(generic.edit.ModelFormMixin):
    model = ProvenanceState
    fields = [
            'item',
            'owner',
            'comment'
        ]


class ManifestationTitleUpdateView(FormsetUpdateView):
    model = Manifestation
    form_class = ManifestationTitleFormSet
    formset_property = 'titles'

    def get_success_url(self):
        return reverse_lazy('edwoca:manifestation_title', kwargs = {'pk': self.object.id})


def person_list(request):
    persons = [
            f"{person.names.get(status=Status.PRIMARY).last_name}_{person.names.get(status=Status.PRIMARY).first_name}-{person.gnd_id}"
            for person
            in Person.objects.all()
        ]
    serialized_persons = json_dump(persons)
    return JsonResponse(serialized_persons, safe=False)

def work_list(request):
    return render('edwoca:index')


class WorkRelatedWorksUpdateView(generic.edit.UpdateView):
    model = Work
    fields = []
    template_name = 'edwoca/work_related_works.html'

class SimpleFormView(generic.edit.UpdateView):
    template_name = 'edwoca/simple_form.html'

    def get_form_class(self):
        class_name = f"{self.model.__name__}{self.property.capitalize()}Form"
        return getattr(edwoca_forms, class_name)

    def get_success_url(self):
        return reverse_lazy(f"edwoca:{self.model.__name__.lower()}_{self.property}", kwargs={'pk': self.object.pk})


class WorkHistoryUpdateView(SimpleFormView):
    model = Work
    property = 'history'


class ManifestationHistoryUpdateView(SimpleFormView):
    model = Manifestation
    property = 'history'


class BibliographyUpdateView(generic.edit.UpdateView):
    template_name = 'edwoca/bibliography.html'
    instance = None  # wird im dispatch gesetzt

    def get_form_class():
        return getattr(edwoca_forms, f"{self.model.__name__}BibFormSet")

    def dispatch(self, request, *args, **kwargs):
        self.instance = get_object_or_404(self.model, pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy(f"edwoca:{self.model.__name__.lower()}_bibliography", kwargs={'pk': self.instance.pk})

    def get_form(self, form_class=None):
        formset_class = getattr(edwoca_forms, f"{self.model.__name__}BibFormSet")
        if self.request.method == 'POST':
            return formset_class(self.request.POST, instance=self.instance)
        return formset_class(instance=self.instance)

    def form_valid(self, formset):
        formset.save()
        return super().form_valid(formset)

    def form_invalid(self, formset):
        return self.render_to_response(self.get_context_data(form=formset))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object'] = self.instance
        context['form'] = kwargs.get('form', self.get_form())
        return context


class WorkBibliographyUpdateView(FormsetUpdateView):
    model = Work
    form_class = WorkBibFormSet
    property = 'bib'

    def get_success_url(self):
        return reverse_lazy('edwoca:work_bibliography_update', kwargs = {'pk': self.object.id})


class ManifestationBibliographyUpdateView(FormsetUpdateView):
    model = Manifestation
    form_class = ManifestationBibFormSet
    property = 'bib'

    def get_success_url(self):
        return reverse_lazy('edwoca:manifestation_bibliography_update', kwargs = {'pk': self.object.id})


class WorkCommentUpdateView(SimpleFormView):
    model = Work
    property = 'comment'


class ManifestationCommentUpdateView(SimpleFormView):
    model = Manifestation
    property = 'comment'


class RelatedEntityAddView(generic.edit.FormView):

    def get_form_name(self):
        return f"{self.model.__name__}Form"

    def get_model_name(self):
        return self.model.__name__.lower().replace('related', '')

    def get_form_class(self):
        return getattr(edwoca_forms, self.get_form_name())

    def get_success_url(self):
        return reverse_lazy(f"edwoca:{self.get_model_name()}_relations", kwargs={'pk': self.kwargs['pk']})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        kwargs['initial'] = {
            f"source_{self.get_model_name()}": self.kwargs['pk'],
            f"target_{self.get_model_name()}": self.kwargs[f"target_{self.get_model_name()}"],
        }
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model = getattr(edwoca_models, self.get_model_name().capitalize())
        context['show_search_form'] = False
        context[f"target_{self.get_model_name()}"] = model.objects.get(pk=self.kwargs[f"target_{self.get_model_name()}"])
        context['object'] = model.objects.get(pk=self.kwargs["pk"])
        return context

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class RelatedWorkAddView(RelatedEntityAddView):
    template_name = 'edwoca/work_relations.html'
    model = RelatedWork


class RelatedManifestationAddView(RelatedEntityAddView):
    template_name = 'edwoca/manifestation_relations.html'
    model = RelatedManifestation


class RelatedWorkRemoveView(generic.DeleteView):
    model = RelatedWork

    def get_success_url(self):
        return reverse_lazy('edwoca:work_relations', kwargs={'pk': self.object.source_work.id})


class RelatedManifestationRemoveView(generic.DeleteView):
    model = RelatedManifestation

    def get_success_url(self):
        return reverse_lazy('edwoca:manifestation_relations', kwargs={'pk': self.object.source_work.id})


class ExpressionRelationsUpdateView(RelationsUpdateView):
    template_name = 'edwoca/expression_relations.html'
    model = Expression
    form_class = RelatedExpressionForm


class RelatedExpressionAddView(RelatedEntityAddView):
    template_name = 'edwoca/expression_relations.html'
    model = RelatedExpression


class RelatedExpressionRemoveView(generic.DeleteView):
    model = RelatedExpression

    def get_success_url(self):
        return reverse_lazy('edwoca:expression_relations', kwargs={'pk': self.object.source_work.id})


class ExpressionHistoryUpdateView(generic.UpdateView):
    model = Expression
    form_class = ExpressionHistoryForm
    template_name = 'edwoca/simple_form.html'

    def get_success_url(self):
        return reverse_lazy('edwoca:expression_history', kwargs={'pk': self.object.pk})


class ManifestationPrintUpdateView(generic.UpdateView):
    pass
    #model = Manifestation
    #property = 'print'


class ManifestationClassificationUpdateView(SimpleFormView):
    model = Manifestation
    property = 'classification'


class ExpressionCategorisationUpdateView(generic.UpdateView):
    pass


class ExpressionMediumofperformanceUpdateView(generic.UpdateView):
    pass


class ExpressionMovementsUpdateView(FormsetUpdateView):
    model = Expression
    form_class = MovementFormSet
    template_name = 'edwoca/expression_movement.html'
    formset_property = 'movements'

    def get_success_url(self):
        return reverse_lazy('edwoca:expression_movement', kwargs={'pk': self.object.pk})


class ExpressionCommentUpdateView(generic.UpdateView):
    model = Expression
    form_class = ExpressionCommentForm
    template_name = 'edwoca/simple_form.html'

    def get_success_url(self):
        return reverse_lazy('edwoca:expression_history', kwargs={'pk': self.object.pk})


class ExpressionDeleteView(generic.DeleteView):
    model = Expression
    template_name = 'edwoca/simple_form.html'

    def get_success_url(self):
        return reverse_lazy('edwoca:work_update', kwargs={'pk': self.object.work.id})


class ItemUpdateView(generic.UpdateView):
    model = Item
    form_class = ItemForm
    template_name = 'edwoca/item_update.html'


class ItemCreateView(generic.CreateView):
    model = Item
    form_class = ItemForm
    template_name = 'edwoca/create.html'

    def get_success_url(self):
        return reverse_lazy('edwoca:item_update', kwargs = {'pk': self.object.id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['title_formset'] = ItemTitleFormSet(self.request.POST)
        else:
            ItemTitleFormSet.can_delete = False
            context['title_form_set'] = ItemTitleFormSet()
        context['view_title'] = f"Neues Exemplar anlegen"
        context['button_label'] = "speichern"
        context['return_target'] = 'edwoca:index'
        context['return_pk'] = None
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        title_formset = context['title_formset']

        instance = form.save(commit=False)
        instance.manifestation = Manifestation.objects.get(id=self.kwargs['manifestation_id'])

        if title_formset.is_valid():
            instance.save()
            self.object = form.save()
            title_formset.instance = self.object
            title_formset.save()
            return redirect(self.get_success_url())
        else:
            return self.form_invalid(form)


class ItemDeleteView(generic.DeleteView):
    pass


class ItemLocationUpdateView(SimpleFormView):
    model = Item
    property = 'location'


class ItemRelationsUpdateView(RelationsUpdateView):
    template_name = 'edwoca/item_relations.html'
    model = Item
    form_class = RelatedItemForm


class RelatedItemAddView(RelatedEntityAddView):
    template_name = 'edwoca/item_relations.html'
    model = RelatedItem


class RelatedItemRemoveView(generic.DeleteView):
    model = RelatedItem

    def get_success_url(self):
        return reverse_lazy('edwoca:item_relations', kwargs={'pk': self.object.source_item.id})


class ItemContributorsUpdateView(ContributorsUpdateView):
    model = Item


class ItemProvenanceUpdateView(generic.UpdateView):
    pass


class ItemDetailsUpdateView(SimpleFormView):
    model = Item
    property = 'details'


class ItemDescriptionUpdateView(SimpleFormView):
    model = Item
    property = 'description'


class ItemDigcopyUpdateView(SimpleFormView):
    model = Item
    property = 'digcopy'


class ItemCommentUpdateView(SimpleFormView):
    model = Item
    property = 'comment'


class ItemDeleteView(generic.DeleteView):
    model = Item

    def get_success_url(self):
        return reverse_lazy('edwoca:work_update', kwargs={'pk': self.object.work.id})
