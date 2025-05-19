from django.urls import reverse_lazy
from django.shortcuts import render, get_object_or_404, redirect
from django.core import serializers
from django.http import JsonResponse
from django.views import generic
from django.views.generic import ListView
from django.forms import HiddenInput, formset_factory
from django.forms.models import inlineformset_factory
from .forms import WorkTitleForm, WorkForm, WorkTitleFormSet, WorkContributorForm, WorkContributorFormSet, \
        WorkHistoryForm, WorkCommentForm, WorkBibFormSet, ExpressionTitleFormSet, RelatedWorkForm
from .models import Work, WorkTitle, RelatedWork, WorkContributor, Expression, ExpressionContributor, ExpressionTitle, \
    Manifestation, RelatedManifestation, Item, RelatedItem, ManifestationContributor, ProvenanceState, WorkBib#, ManifestationTitle, ItemTitle
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

class WorkRelationsUpdateView(generic.UpdateView):
    fields = []
    template_name = 'edwoca/work_relations.html'
    model = Work

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_form = SearchForm(self.request.GET or None)
        context['searchform'] = search_form
        context['show_search_form'] = True

        if search_form.is_valid() and search_form.cleaned_data.get('q'):
            context['query'] = search_form.cleaned_data.get('q')
            context['found_works'] = search_form.search()

        return context


class ReturnButtonView(generic.detail.SingleObjectTemplateResponseMixin):
    template_name = 'edwoca/base_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['return_target'] = 'edwoca:work_detail'
        try:
            context['return_pk'] = self.get_work().id
        except:
            context['return_pk'] = self.get_manifestation().id
        context['button_label'] = 'anlegen'
        return context


class WorkRelationCreateView(generic.edit.CreateView, ReturnButtonView):
    def get_success_url(self):
        return reverse_lazy('edwoca:work_detail', kwargs = {'pk': self.get_work().id})

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        form = super().get_form(form_class)
        for entity in ['work', 'source_work']:
            if entity in form.fields:
                form.fields[entity].initial = self.get_work()
                form.fields[entity].widget = HiddenInput()
                form.fields[entity].label = ''
        return form

    def get_work(self):
        return Work.objects.get(id=self.kwargs['work_id'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['button_label'] = 'anlegen'
        return context


class ExpressionRelationCreateView(generic.edit.CreateView, ReturnButtonView):
    def get_success_url(self):
        return reverse_lazy('edwoca:work_detail', kwargs = {'pk': self.get_work().id})

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        form = super().get_form(form_class)
        for entity in ['expression', 'source_expression']:
            if entity in form.fields:
                form.fields[entity].initial = self.get_expression()
                form.fields[entity].widget = HiddenInput()
                form.fields[entity].label = ''
        return form

    def get_expression(self):
        return Expression.objects.get(id=self.kwargs['expression_id'])

    def get_work(self):
        return self.get_expression().work

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['button_label'] = 'anlegen'
        return context


class WorkRelationUpdateView(generic.edit.UpdateView, ReturnButtonView):
    def get_success_url(self):
        return reverse_lazy('edwoca:work_detail', kwargs = {'pk': self.get_work().id})

    def get_work(self):
        try:
            return self.object.work
        except:
            return self.object.source_work

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['button_label'] = 'speichern'
        return context


class ExpressionRelationUpdateView(generic.edit.UpdateView, ReturnButtonView):
    def get_success_url(self):
        return reverse_lazy('edwoca:work_detail', kwargs = {'pk': self.get_work().id})

    def get_expression(self):
        try:
            return self.object.expression
        except:
            return self.object.source_expression

    def get_work(self):
        return self.get_expression().work

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['button_label'] = 'speichern'
        return context


class WorkRelationDeleteView(generic.edit.DeleteView, ReturnButtonView):
    def get_success_url(self):
        return reverse_lazy('edwoca:work_detail', kwargs = {'pk': self.get_work().id})

    def get_work(self):
        try:
            return self.object.work
        except:
            return self.object.source_work

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['button_label'] = 'löschen'
        return context


class ExpressionRelationDeleteView(generic.edit.DeleteView, ReturnButtonView):
    def get_success_url(self):
        return reverse_lazy('edwoca:work_detail', kwargs = {'pk': self.get_work().id})

    def get_expression(self):
        try:
            return self.object.expression
        except:
            return self.object.source_expression

    def get_work(self):
        return self.get_expression().work

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['button_label'] = 'löschen'
        return context


class WorkSearchView(SearchView):
    template_name = 'edwoca/list.html'
    form_class = SearchForm

    # redirect to list view if empty query
    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', '')
        if not query or query == '':
            return redirect('edwoca:work_list')
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['work_count'] = Work.objects.all().count()
        context['manifestation_count'] = Manifestation.objects.all().count()
        context['object_list'] = [ result.object for result in context['object_list'] ]
        return context


class WorkListView(ListView):
    template_name = 'edwoca/list.html'
    model = Work
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = SearchForm()
        context['work_count'] = Work.objects.all().count()
        context['manifestation_count'] = Manifestation.objects.all().count()
        return context


class ManifestationSearchView(SearchView):
    template_name = 'edwoca/index.html'
    form_class = SearchForm


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
            self.object = form.save()
            title_formset.instance = self.object
            title_formset.save()
            return redirect(self.get_success_url())
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
    template_name = 'edwoca/base_form.html'
    context_object_name = 'work'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['view_title'] = f"Werk {self.object} löschen"
        context['button_label'] = "löschen"
        context['return_target'] = 'edwoca:index'
        context['return_pk'] = None
        return context


class WorkBibView(generic.edit.ModelFormMixin):
    model = WorkBib
    fields = [
            'bib',
            'work'
        ]


class WorkBibCreateView(WorkRelationCreateView, WorkBibView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['view_title'] = f"Neue Literaturangabe für {self.get_work()} anlegen"
        return context


class WorkBibUpdateView(WorkRelationUpdateView, WorkBibView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['view_title'] = f"Literaturangabe { self.object.bib } des Werks { self.get_work() } bearbeiten"
        return context


class WorkBibDeleteView(WorkRelationDeleteView):
    model = WorkBib

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['view_title'] = f"Literaturangabe { self.object.bib } des Werks { self.get_work() } löschen"
        return context


class WorkTitleView(generic.edit.ModelFormMixin):
    model = WorkTitle
    fields = [
            'title',
            'status',
            'language',
            'work'
        ]


class WorkTitleCreateView(WorkRelationCreateView, WorkTitleView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['view_title'] = f"Neuen Titel für {self.get_work()} anlegen"
        return context


class WorkContributorView(generic.edit.ModelFormMixin):
    model = WorkContributor
    fields = [
            'work',
            'person',
            'role'
        ]


class WorkContributorCreateView(WorkRelationCreateView, WorkContributorView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['view_title'] = f"Neuen Beteiligten für Werk {self.get_work()} anlegen"
        return context


class WorkContributorUpdateView(WorkRelationUpdateView, WorkContributorView):
    pass

class WorkContributorsUpdateView(generic.edit.UpdateView):
    model = Work
    fields = []
    template_name = 'edwoca/work_contributor_update.html'

    def get_success_url(self):
        return reverse_lazy('edwoca:work_contributors', kwargs = {'pk': self.get_object().id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['view_title'] = f"Beteiligte am Werk {self.object} bearbeiten"
        if 'form' not in kwargs:
            context['form'] = WorkContributorFormSet(instance = self.object)
        else:
            context['form'] = kwargs['form']
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        if 'add-form' in request.POST:
            data = request.POST.copy()
            total_forms = int(data.get('workcontributor_set-TOTAL_FORMS', 0))
            data['workcontributor_set-TOTAL_FORMS'] = str(total_forms + 1)
            form = WorkContributorFormSet(data, instance=self.object)
            return self.render_to_response(self.get_context_data(form=form))

        formset = WorkContributorFormSet(
                request.POST,
                instance = self.object,
                queryset = WorkContributor.objects.filter(work = self.object)
            )
        for form in formset:
            if not form.instance.work:
                form.instance.work = self.get_object()

        if formset.is_valid():
            for form in formset:
                formset.instance.save()
            return self.form_valid(formset)
        else:
            return self.form_invalid(formset)


class WorkContributorDeleteView(WorkRelationDeleteView):
    model = WorkContributor

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['view_title'] = f"Beteiligten {self.object.person} am Werk {self.object.work} löschen"
        return context


class RelatedWorkView(generic.edit.ModelFormMixin):
    model = RelatedWork
    fields = [
            'source_work',
            'target_work',
            'comment',
            'label'
        ]


class RelatedWorkCreateView(WorkRelationCreateView, RelatedWorkView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['view_title'] = f"Werkrelation für {self.get_work()} anlegen"
        return context


class RelatedWorkUpdateView(WorkRelationUpdateView, RelatedWorkView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['view_title'] = f"Werkrelation zwischen Werk {self.object.source_work} und {self.object.target_work} bearbeiten"
        return context


class RelatedWorkDeleteView(WorkRelationDeleteView):
    model = RelatedWork

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['view_title'] = f"Werkrelation zwischen Werk {self.object.source_work} und {self.object.target_work} löschen"
        return context


class ExpressionPeriodView(generic.edit.ModelFormMixin):
    model = Period
    fields = [
            'not_before',
            'not_after',
            'display'
        ]


class ExpressionPeriodCreateView(ExpressionRelationCreateView, ExpressionPeriodView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['view_title'] = f"Datumsangabe für Expression { self.get_expression() } von Werk { self.get_work() } anlegen"
        return context

    def form_valid(self, form):
        period = form.save()
        expression = self.get_expression()
        expression.period = period
        expression.save()
        return super().form_valid(form)


class ExpressionPeriodUpdateView(ExpressionRelationUpdateView, ExpressionPeriodView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['view_title'] = f"Datumsangabe für Expession {self.object.expression} bearbeiten"
        return context


class ExpressionPeriodDeleteView(ExpressionRelationDeleteView):
    model = Period

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['view_title'] = f"Datumsangabe von Expression {self.object.expression} löschen"
        return context


class ExpressionTitleView(generic.edit.ModelFormMixin):
    model = ExpressionTitle
    fields = [
            'title',
            'language',
            'status',
            'expression'
        ]


class ExpressionTitleCreateView(ExpressionRelationCreateView, ExpressionTitleView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['view_title'] = f"Titel für Expression {self.get_expression()} von Werk {self.get_expression().work} anlegen"
        return context


#class ExpressionTitleUpdateView(ExpressionRelationUpdateView, ExpressionTitleView):
    #def get_context_data(self, **kwargs):
        #context = super().get_context_data(**kwargs)
        #context['view_title'] = f"Titel { self.object } der Expression { self.object.expression } bearbeiten"
        #return context


class ExpressionTitleDeleteView(ExpressionRelationDeleteView):
    model = ExpressionTitle

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['view_title'] = f"Titel { self.object } von Expression {self.object.expression} löschen"
        return context


class ExpressionContributorView(generic.edit.ModelFormMixin):
    model = ExpressionContributor
    fields = [
            'expression',
            'person',
            'role'
        ]


class ExpressionContributorCreateView(ExpressionRelationCreateView, ExpressionContributorView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['view_title'] = f"Beteiligten für Expression { self.get_expression() } anlegen"
        return context


class ExpressionContributorUpdateView(ExpressionRelationUpdateView, ExpressionContributorView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['view_title'] = f"Beteiligten { self.object.person } von Expression { self.get_expression() } bearbeiten"
        return context


class ExpressionContributorDeleteView(ExpressionRelationDeleteView):
    model = ExpressionContributor

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['view_title'] = f"Expression { self.object } an Expression { self.get_expression() } löschen"
        return context


class ExpressionView(generic.edit.ModelFormMixin):
    model = Expression
    fields = [
            'incipit_music',
            'incipit_text',
            'period_comment',
            'history',
            'work'
        ]


class ExpressionCreateView(WorkRelationCreateView, ExpressionView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['view_title'] = f"Neue Expression am Werk { self.get_work() } anlegen"
        return context


class ExpressionUpdateView(WorkRelationUpdateView, ExpressionView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['view_title'] = f"Expression { self.object } von Werk { self.get_work() } bearbeiten"
        return context


class ExpressionDeleteView(WorkRelationDeleteView):
    model = Expression

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['view_title'] = f"Expression { self.object } am Werk { self.get_work() } löschen"
        return context


class TitleUpdateView(generic.UpdateView):
    template_name = 'edwoca/title_update.html'

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
            total_forms = int(data.get('titles-TOTAL_FORMS', 0))
            data['titles-TOTAL_FORMS'] = str(total_forms + 1)
            data[f'titles-{total_forms}-language'] = 'de'
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


class ExpressionTitleUpdateView(TitleUpdateView):
    model = Expression
    form_class = ExpressionTitleFormSet

    def get_success_url(self):
        return reverse_lazy('edwoca:expression_title_update', kwargs = {'pk': self.object.id})


class WorkTitleUpdateView(TitleUpdateView):
    model = Work
    form_class = WorkTitleFormSet

    def get_success_url(self):
        return reverse_lazy('edwoca:work_title_update', kwargs = {'pk': self.object.id})


class WorkTitleDeleteView(WorkRelationDeleteView):
    model = WorkTitle

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['view_title'] = f"Titel { self.object } des Werks { self.get_work() } löschen"
        return context


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
    fields = [
            'rism_id',
            'plate_number'
        ]
    template_name = 'edwoca/base_form.html'

    def get_success_url(self):
        return reverse_lazy('edwoca:manifestation_detail', kwargs = {'pk': self.object.id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['view_title'] = f"Neue Manifestation anlegen"
        context['button_label'] = "anlegen"
        context['return_target'] = 'edwoca:index'
        context['return_pk'] = None
        return context


class ManifestationUpdateView(generic.edit.UpdateView):
    model = Manifestation
    fields = [
            'rism_id',
            'plate_number'
        ]
    template_name = 'edwoca/base_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['view_title'] = f"Manifestation { self.object } bearbeiten"
        context['button_label'] = "speichern"
        context['return_target'] = 'edwoca:manifestation_detail'
        context['return_pk'] = self.object.id
        return context


class ManifestationDeleteView(generic.edit.DeleteView):
    model = Manifestation
    success_url = reverse_lazy('edwoca:index')
    template_name = 'edwoca/base_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['view_title'] = f"Manifestation {self.object} löschen"
        context['button_label'] = "löschen"
        context['return_target'] = 'edwoca:index'
        context['return_pk'] = None
        return context


class ManifestationRelationCreateView(generic.edit.CreateView, ReturnButtonView):
    def get_success_url(self):
        return reverse_lazy('edwoca:manifestation_detail', kwargs = {'pk': self.get_manifestation().id})

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        form = super().get_form(form_class)
        for entity in ['manifestation', 'source_manifestation']:
            if entity in form.fields:
                form.fields[entity].initial = self.get_manifestation()
                form.fields[entity].widget = HiddenInput()
                form.fields[entity].label = ''
        return form

    def get_manifestation(self):
        return Manifestation.objects.get(id=self.kwargs['manifestation_id'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['button_label'] = 'anlegen'
        return context


class ItemRelationCreateView(generic.edit.CreateView, ReturnButtonView):
    def get_success_url(self):
        return reverse_lazy('edwoca:manifestation_detail', kwargs = {'pk': self.get_manifestation().id})

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        form = super().get_form(form_class)
        for entity in ['item', 'source_item']:
            if entity in form.fields:
                form.fields[entity].initial = self.get_expression()
                form.fields[entity].widget = HiddenInput()
                form.fields[entity].label = ''
        return form

    def get_item(self):
        return Item.objects.get(id=self.kwargs['item_id'])

    def get_manifestation(self):
        return self.get_item().manifestation

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['button_label'] = 'anlegen'
        return context


class ManifestationRelationUpdateView(generic.edit.UpdateView, ReturnButtonView):
    def get_success_url(self):
        return reverse_lazy('edwoca:manifestation_detail', kwargs = {'pk': self.get_manifestation().id})

    def get_manifestation(self):
        try:
            return self.object.manifestation
        except:
            return self.object.source_manifestation

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['button_label'] = 'speichern'
        return context


class ItemRelationUpdateView(generic.edit.UpdateView, ReturnButtonView):
    def get_success_url(self):
        return reverse_lazy('edwoca:manifestation_detail', kwargs = {'pk': self.get_manifestation().id})

    def get_item(self):
        try:
            return self.object.item
        except:
            return self.object.source_item

    def get_manifestation(self):
        return self.get_item().manifestation

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['button_label'] = 'speichern'
        return context


class ManifestationRelationDeleteView(generic.edit.DeleteView, ReturnButtonView):
    def get_success_url(self):
        return reverse_lazy('edwoca:manifestation_detail', kwargs = {'pk': self.get_manifestation().id})

    def get_manifestation(self):
        try:
            return self.object.manifestation
        except:
            return self.object.source_manifestation

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['button_label'] = 'löschen'
        return context


class ItemRelationDeleteView(generic.edit.DeleteView, ReturnButtonView):
    def get_success_url(self):
        return reverse_lazy('edwoca:manifestation_detail', kwargs = {'pk': self.get_manifestation().id})

    def get_item(self):
        try:
            return self.object.item
        except:
            return self.object.source_item

    def get_manifestation(self):
        return self.get_expression().manifestation

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['button_label'] = 'löschen'
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


class ManifestationContributorCreateView(ManifestationContributorView, ManifestationRelationCreateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['view_title'] = f"Beteiligten für Manifestation { self.get_manifestation() } anlegen"
        return context


class ItemContributorCreateView(ManifestationContributorView, ManifestationRelationCreateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['view_title'] = f"Beteiligten für Exemplar { self.get_item() } anlegen"
        return context


class ManifestationContributorUpdateView(ManifestationContributorView, ManifestationRelationCreateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['view_title'] = f"Beteiligten { self.person } für Manifestation { self.get_manifestation() } bearbeiten"
        return context


class ItemContributorUpdateView(ManifestationContributorView, ManifestationRelationCreateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['view_title'] = f"Beteiligten { self.person } für Exemplar { self.get_item() } bearbeiten"
        return context


class ManifestationContributorDeleteView(WorkRelationDeleteView):
    model = WorkContributor

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['view_title'] = f"Beteiligten {self.object.person} an Manifestation {self.object.manifestation} löschen"
        return context


class ItemContributorDeleteView(WorkRelationDeleteView):
    model = WorkContributor

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['view_title'] = f"Beteiligten {self.object.person} am Item {self.object.item} löschen"
        return context


class RelatedManifestationView(generic.edit.ModelFormMixin):
    model = RelatedManifestation
    fields = [
            'source_manifestation',
            'target_manifestation',
            'comment',
            'label'
        ]


class RelatedManifestationCreateView(RelatedManifestationView, ManifestationRelationCreateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['view_title'] = f"Manifestationsrelation für {self.get_manifestation()} anlegen"
        return context


class RelatedManifestationUpdateView(RelatedManifestationView, ManifestationRelationUpdateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['view_title'] = f"Manifestationsrelation zwischen {self.source_manifestation} und {self.target_manifestation} bearbeiten"
        return context


class RelatedManifestationDeleteView(RelatedManifestationView, ManifestationRelationDeleteView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['view_title'] = f"Manifestationsrelation zwischen {self.source_manifestation} und {self.target_manifestation} löschen"
        return context


class ItemView(generic.edit.ModelFormMixin):
    model = Item
    fields = [
            'cover',
            'handwriting',
            'history',
            'iiif_manifest',
            'manifestation'
        ]

class ItemCreateView(ItemView, ManifestationRelationCreateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['view_title'] = f"Exemplar für {self.get_manifestation()} anlegen"
        return context


class ItemUpdateView(ItemView, ManifestationRelationUpdateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['view_title'] = f"Exemplar {self.object} von {self.get_manifestation()} bearbeiten"
        return context


class ItemDeleteView(ItemView, ManifestationRelationDeleteView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['view_title'] = f"Exemplar {self.object} und {self.get_manifestation()} löschen"
        return context


class ProvenanceStateView(generic.edit.ModelFormMixin):
    model = ProvenanceState
    fields = [
            'item',
            'owner',
            'comment'
        ]


class ProvenanceStateCreateView(ProvenanceStateView, ItemRelationCreateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['view_title'] = f"Provenienzeintrag für {self.get_item()} anlegen"
        return context


class ProvenanceStateUpdateView(ProvenanceStateView, ItemRelationUpdateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['view_title'] = f"Provenienzeintrag von {self.person} für {self.get_item()} bearbeiten"
        return context


class ProvenanceStateDeleteView(ProvenanceStateView, ItemRelationDeleteView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['view_title'] = f"Provenienzeintrag von {self.person} für {self.get_item()} löschen"
        return context


"""
class ManifestationTitleView(generic.edit.ModelFormMixin):
    model = ManifestationTitle
    fields = [
            'title',
            'status',
            'language',
            'manifestation'
        ]


class ManifestationTitleCreateView(ManifestationTitleView, ManifestationRelationCreateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['view_title'] = f"Titel für Manifestation {self.get_manifestation()} anlegen"
        return context


class ManifestationTitleUpdateView(ManifestationTitleView, ManifestationRelationUpdateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['view_title'] = f"Titel {self.object} für Manifestation {self.get_manifestation()} bearbeiten"
        return context


class ManifestationTitleDeleteView(ManifestationTitleView, ManifestationRelationDeleteView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['view_title'] = f"Titel {self.object} für Manifestation {self.get_manifestation()} löschen"
        return context


class ItemTitleView(generic.edit.ModelFormMixin):
    model = ItemTitle
    fields = [
            'title',
            'status',
            'language',
            'item'
        ]


class ItemTitleCreateView(ItemTitleView, ItemRelationCreateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['view_title'] = f"Titel für Exemplar {self.get_item()} anlegen"
        return context


class ItemTitleUpdateView(ItemTitleView, ItemRelationUpdateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['view_title'] = f"Titel {self.object} für Exemplar {self.get_item()} bearbeiten"
        return context


class ItemTitleDeleteView(ItemTitleView, ItemRelationDeleteView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['view_title'] = f"Titel {self.object} für Exemplar {self.get_item()} löschen"
        return context
"""


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


#class WorkRelationsUpdateView(generic.edit.UpdateView):
    #model = Work
    #fields = []
    #template_name = 'edwoca/work_relations.html'

#class WorkContributorsUpdateView(generic.edit.UpdateView):
    #model = Work
    #fields = []
    #template_name = 'edwoca/work_relations.html'

class WorkRelatedWorksUpdateView(generic.edit.UpdateView):
    model = Work
    fields = []
    template_name = 'edwoca/work_related_works.html'

class WorkHistoryUpdateView(generic.edit.UpdateView):
    model = Work
    form_class = WorkHistoryForm
    template_name = 'edwoca/work_history.html'

    def get_success_url(self):
        return reverse_lazy('edwoca:work_history', kwargs={'pk': self.object.pk})

class WorkBibliographyUpdateView(generic.edit.UpdateView):
    model = Work
    fields = []
    template_name = 'edwoca/work_bibliography.html'

    def get_success_url(self):
        return reverse_lazy('edwoca:work_bibliography', kwargs = {'pk': self.get_object().id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['view_title'] = f"Bibliographie für Werk {self.object} bearbeiten"
        if 'form' not in kwargs:
            context['form'] = WorkBibFormSet(instance = self.object)
        else:
            context['form'] = kwargs['form']
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        if 'add-form' in request.POST:
            data = request.POST.copy()
            total_forms = int(data.get('workbib_set-TOTAL_FORMS', 0))
            data['workbib_set-TOTAL_FORMS'] = str(total_forms + 1)
            form = WorkBibFormSet(data, instance=self.object)
            return self.render_to_response(self.get_context_data(form=form))

        formset = WorkBibFormSet(
                request.POST,
                instance = self.object,
                queryset = WorkBib.objects.filter(work = self.object)
            )
        for form in formset:
            if not form.instance.work:
                form.instance.work = self.get_object()

        if formset.is_valid():
            for form in formset:
                formset.instance.save()
            return self.form_valid(formset)
        else:
            return self.form_invalid(formset)

class WorkCommentUpdateView(generic.edit.UpdateView):
    model = Work
    form_class = WorkCommentForm
    template_name = 'edwoca/work_comment.html'

    def get_success_url(self):
        return reverse_lazy('edwoca:work_history', kwargs={'pk': self.object.pk})


class RelatedWorkAddView(generic.edit.UpdateView):
    model = Work
    fields = []
    template_name = 'edwoca/work_relations.html'

    def get_success_url(self):
        return reverse_lazy('edwoca:work_relations', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['show_search_form'] = False
        if self.request.POST:
            context['related_work_form'] = RelatedWorkForm(self.request.POST)
        else:
            context['related_work_form'] = RelatedWorkForm( initial = {
                    'source_work': self.kwargs['pk'],
                    'target_work': self.kwargs['target_work']
                })
        context['target_work'] = Work.objects.get(pk=self.kwargs['target_work'])

        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        form = RelatedWorkForm(request.POST)

        if form.is_valid():
            form.instance.save()
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class RelatedWorkRemove(generic.DeleteView):
    model = RelatedWork

    def get_success_url(self):
        return reverse_lazy('edwoca:work_relations', kwargs={'pk': self.object.source_work.id})
