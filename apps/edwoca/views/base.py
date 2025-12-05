from django.forms import inlineformset_factory
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse_lazy
from django.views.generic import ListView
from django.views.generic.edit import UpdateView, FormView, CreateView, DeleteView
from django.db.models import Case, When
from liszt_util.forms import SearchForm
from dmad_on_django.models import Person, Status, Corporation, Place
from bib.models import ZotItem
from ..forms import LetterForm, LetterMentioningForm
from liszt_util.tools import snake_to_camel_case, camel_to_snake_case
from haystack.generic_views import SearchView
from ..models import Work, Expression, Manifestation, Item, Letter, LetterMentioning
from dmrism.models import Library
from edwoca import forms as edwoca_forms
from edwoca import models as edwoca_models


def index(request):
    return redirect('edwoca:work_search')


class EdwocaListView(ListView):
    template_name = 'edwoca/list.html'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = SearchForm()
        context['work_count'] = Work.objects.count()
        context['expression_count'] = Expression.objects.count()
        context['manifestation_count'] = Manifestation.objects.filter(is_singleton = False).count()
        context['singleton_count'] = Manifestation.objects.filter(is_singleton = True).count()
        context['item_count'] = Item.objects.filter(manifestation__is_singleton = False).count()
        context['library_count'] = Library.objects.count()
        context['letter_count'] = Letter.objects.count()
        context['list_entity_type'] = self.model.__name__.lower()
        return context


class EntityMixin:
    def get_model_name(self):
        if not self.model:
            raise ImproperlyConfigured(f"{self.__class__.__name__} requires a 'model' attribute.")
        return camel_to_snake_case(self.model.__name__)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entity_type'] = self.get_model_name()
        return context


class EdwocaSearchView(SearchView):
    template_name = 'edwoca/list.html'
    form_class = SearchForm
    paginate_by = 10

    def get_model_name(self):
        return self.model.__name__

    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', '')

        # redirect to list view if empty query
        if not query or query == '':
            return redirect(f'edwoca:{camel_to_snake_case(self.get_model_name())}_list')

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['work_count'] = Work.objects.count()
        context['expression_count'] = Expression.objects.count()
        context['manifestation_count'] = Manifestation.objects.filter(is_singleton = False).count()
        context['singleton_count'] = Manifestation.objects.filter(is_singleton = True).count()
        context['item_count'] = Item.objects.filter(manifestation__is_singleton = False).count()
        context['library_count'] = Library.objects.count()
        context['letter_count'] = Letter.objects.count()
        context['object_list'] = [ result.object for result in context['object_list'] ]

        total_results = context['form'].search().count()
        current_page = int(self.request.GET.get('page', 1))
        first_result_on_page = (current_page - 1) * 10 + 1 if total_results > 0 else 0
        last_result_on_page = first_result_on_page + 9 if first_result_on_page + 9 <= total_results else total_results

        context['total_results'] = total_results
        context['first_result_on_page'] = first_result_on_page
        context['last_result_on_page'] = last_result_on_page
        context['list_entity_type'] = self.get_model_name().lower()
        context['query'] = self.request.GET.get('q', '')

        return context

    def get_queryset(self):
        qs = super().get_queryset()

        return qs.models(getattr(edwoca_models, self.get_model_name()))


class SimpleFormView(EntityMixin, UpdateView):
    template_name = 'edwoca/simple_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['property'] = self.property
        return context

    def get_form_class(self):
        class_name = f"{snake_to_camel_case(self.get_model_name())}{snake_to_camel_case(self.get_property())}Form"
        return getattr(edwoca_forms, class_name)

    def get_success_url(self):
        return reverse_lazy(f"edwoca:{camel_to_snake_case(self.get_model_name())}_{self.get_property()}", kwargs={'pk': self.object.pk})

    def get_property(self):
        if not self.property:
            raise ImproperlyConfigured(f"{self.__class__.__name__} requires a 'property' attribute.")

        return self.property


class FormsetUpdateView(UpdateView):
    template_name = 'edwoca/simple_formset.html'

    def get_context_data(self, **kwargs):
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
            # Language default is now handled by the formset factory's initial parameter
            form = self.form_class(data, instance=self.object)
            return self.render_to_response(self.get_context_data(form=form))

        form = self.form_class(request.POST, instance=self.object)

        if form.is_valid():
            form.save()
            return redirect(self.get_success_url())

        return self.render_to_response(self.get_context_data(form=form))


class TitleUpdateView(FormsetUpdateView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'form' not in kwargs and hasattr(self, 'object') and self.object:
            manager = getattr(self.object, self.formset_property)
            queryset = manager.order_by(
                Case(
                    When(status=Status.PRIMARY, then=0),
                    When(status=Status.ALTERNATIVE, then=1),
                    When(status=Status.TEMPORARY, then=2),
                    default=3
                )
            )
            context['form'] = self.form_class(instance=self.object, queryset=queryset)
        return context


class RelationsUpdateView(UpdateView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_form = SearchForm(self.request.GET or None)
        context['searchform'] = search_form
        context['show_search_form'] = True

        if search_form.is_valid() and search_form.cleaned_data.get('q'):
            context['query'] = search_form.cleaned_data.get('q')
            target_model = getattr(edwoca_models, snake_to_camel_case(self.request.GET['target_model']))
            context[f"found_{camel_to_snake_case(target_model.__name__)}s"] = search_form.search().models(target_model)

        return context


class RelatedEntityAddView(FormView):

    def get_form_name(self):
        return f"{self.model.__name__}Form"

    def get_model_name(self):
        return self.get_related_model_name().replace('related_', '')

    def get_related_model_name(self):
        return camel_to_snake_case(self.model.__name__)

    def get_form_class(self):
        return getattr(edwoca_forms, self.get_form_name())

    def get_success_url(self):
        return reverse_lazy(f"edwoca:{self.get_model_name()}_relations", kwargs={'pk': self.kwargs['pk']})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        kwargs['initial'] = {
            f"source_{self.get_model_name()}": self.kwargs['pk'],
            f"target_{self.get_model_name()}": self.kwargs[f"target_{self.get_related_model_name()}"],
        }
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model = getattr(edwoca_models, snake_to_camel_case(self.get_model_name()))
        context['show_search_form'] = False
        context[f"target_{self.get_related_model_name()}"] = model.objects.get(pk=self.kwargs[f"target_{self.get_related_model_name()}"])
        context['entity_type'] = self.get_model_name()
        context['object'] = model.objects.get(pk=self.kwargs["pk"])
        return context

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class ContributorsUpdateView(UpdateView):
    template_name = 'edwoca/contributor_update.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_form = SearchForm(self.request.GET or None)
        context['searchform'] = search_form
        context['show_search_form'] = True

        if search_form.is_valid() and search_form.cleaned_data.get('q'):
            context['query'] = search_form.cleaned_data.get('q')
            context[f"found_contributors"] = search_form.search().models(Person)

        return context


class ContributorAddView(EntityMixin, FormView):
    template_name = 'edwoca/contributor_update.html'

    def get_form_name(self):
        return f"{self.model.__name__}Form"

    def get_form_class(self):
        return getattr(edwoca_forms, self.get_form_name())

    def get_success_url(self):
        return reverse_lazy(f"edwoca:{self.get_model_name()}_contributors", kwargs={'pk': self.kwargs['pk']})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        kwargs['initial'] = {
            f"{self.get_model_name()}": self.kwargs['pk'],
            'person': self.kwargs['person'],
        }
        return kwargs

    def get_model_name(self):
        return camel_to_snake_case(super().get_model_name()).replace('_contributor', '')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model = getattr(edwoca_models, snake_to_camel_case(self.get_model_name()))
        context['show_search_form'] = False
        context['person'] = Person.objects.get(pk=self.kwargs['person'])
        context['object'] = model.objects.get(pk=self.kwargs["pk"])
        context['entity_type'] = self.get_model_name()
        return context

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class LetterListView(EdwocaListView):
    model = Letter


class LetterSearchView(EdwocaSearchView):
    model = Letter


class LetterCreateView(CreateView):
    model = Letter
    template_name = 'edwoca/simple_form.html'
    form_class = LetterForm


class LetterDeleteView(DeleteView):
    model = Letter
    template_name = 'edwoca/delete.html'
    success_url = reverse_lazy('edwoca:letter_list')


def letter_update(request, pk):
    letter = get_object_or_404(Letter, pk=pk)
    LetterMentioningFormSet = inlineformset_factory(Letter, LetterMentioning, form=LetterMentioningForm, extra=0)
    context = {
        'object': letter,
        'entity_type': 'letter'
    }

    if request.method == 'POST':
        form = LetterForm(request.POST, instance=letter)
        letter_mentioning_forms = []
        for letter_mentioning in letter.lettermentioning_set.all():
            prefix = f'letter_mentioning_{letter_mentioning.id}'
            letter_mentioning_form = LetterMentioningForm(
                    request.POST,
                    instance = letter_mentioning,
                    prefix = prefix
                )
            letter_mentioning_forms.append(letter_mentioning_form)
            if letter_mentioning_form.is_valid():
                letter_mentioning_form.save()
    else:
        form = LetterForm(instance=letter)
        letter_mentioning_forms = []
        for letter_mentioning in letter.lettermentioning_set.all():
            prefix = f'letter_mentioning_{letter_mentioning.id}'
            letter_mentioning_forms.append(
                LetterMentioningForm(
                    instance = letter_mentioning,
                    prefix = prefix
                ))

    context['form'] = form
    context['letter_mentioning_forms'] = letter_mentioning_forms

    # Search forms
    q_sender_person = request.GET.get('sender_person-q')
    q_receiver_person = request.GET.get('receiver_person-q')
    q_sender_corporation = request.GET.get('sender_corporation-q')
    q_receiver_corporation = request.GET.get('receiver_corporation-q')
    q_sender_place = request.GET.get('sender_place-q')
    q_receiver_place = request.GET.get('receiver_place-q')
    q_edition = request.GET.get('edition-q')

    if q_sender_person:
        sender_person_search_form = SearchForm(request.GET, prefix='sender_person')
        if sender_person_search_form.is_valid():
            context['query_sender_person'] = sender_person_search_form.cleaned_data.get('q')
            context['found_sender_persons'] = sender_person_search_form.search().models(Person)
    else:
        sender_person_search_form = SearchForm(prefix='sender_person')

    if q_receiver_person:
        receiver_person_search_form = SearchForm(request.GET, prefix='receiver_person')
        if receiver_person_search_form.is_valid():
            context['query_receiver_person'] = receiver_person_search_form.cleaned_data.get('q')
            context['found_receiver_persons'] = receiver_person_search_form.search().models(Person)
    else:
        receiver_person_search_form = SearchForm(prefix='receiver_person')

    if q_sender_corporation:
        sender_corporation_search_form = SearchForm(request.GET, prefix='sender_corporation')
        if sender_corporation_search_form.is_valid():
            context['query_sender_corporation'] = sender_corporation_search_form.cleaned_data.get('q')
            context['found_sender_corporations'] = sender_corporation_search_form.search().models(Corporation)
    else:
        sender_corporation_search_form = SearchForm(prefix='sender_corporation')

    if q_receiver_corporation:
        receiver_corporation_search_form = SearchForm(request.GET, prefix='receiver_corporation')
        if receiver_corporation_search_form.is_valid():
            context['query_receiver_corporation'] = receiver_corporation_search_form.cleaned_data.get('q')
            context['found_receiver_corporations'] = receiver_corporation_search_form.search().models(Corporation)
    else:
        receiver_corporation_search_form = SearchForm(prefix='receiver_corporation')

    if q_sender_place:
        sender_place_search_form = SearchForm(request.GET, prefix='sender_place')
        if sender_place_search_form.is_valid():
            context['query_sender_place'] = sender_place_search_form.cleaned_data.get('q')
            context['found_sender_places'] = sender_place_search_form.search().models(Place)
    else:
        sender_place_search_form = SearchForm(prefix='sender_place')

    if q_receiver_place:
        receiver_place_search_form = SearchForm(request.GET, prefix='receiver_place')
        if receiver_place_search_form.is_valid():
            context['query_receiver_place'] = receiver_place_search_form.cleaned_data.get('q')
            context['found_receiver_places'] = receiver_place_search_form.search().models(Place)
    else:
        receiver_place_search_form = SearchForm(prefix='receiver_place')

    if q_edition:
        edition_search_form = SearchForm(request.GET, prefix='edition')
        if edition_search_form.is_valid():
            context['query_edition'] = edition_search_form.cleaned_data.get('q')
            context['found_editions'] = edition_search_form.search().models(ZotItem)
    else:
        edition_search_form = SearchForm(prefix='edition')

    context['sender_person_search_form'] = sender_person_search_form
    context['receiver_person_search_form'] = receiver_person_search_form
    context['sender_corporation_search_form'] = sender_corporation_search_form
    context['receiver_corporation_search_form'] = receiver_corporation_search_form
    context['sender_place_search_form'] = sender_place_search_form
    context['receiver_place_search_form'] = receiver_place_search_form
    context['edition_search_form'] = edition_search_form

    return render(request, 'edwoca/letter_update.html', context)

def letter_add_sender_person(request, pk, person_id):
    letter = get_object_or_404(Letter, pk=pk)
    person = get_object_or_404(Person, pk=person_id)
    letter.sender_person = person
    letter.save()
    return redirect('edwoca:letter_update', pk=pk)

def letter_remove_sender_person(request, pk):
    letter = get_object_or_404(Letter, pk=pk)
    letter.sender_person = None
    letter.save()
    return redirect('edwoca:letter_update', pk=pk)

def letter_add_receiver_person(request, pk, person_id):
    letter = get_object_or_404(Letter, pk=pk)
    person = get_object_or_404(Person, pk=person_id)
    letter.receiver_person = person
    letter.save()
    return redirect('edwoca:letter_update', pk=pk)

def letter_remove_receiver_person(request, pk):
    letter = get_object_or_404(Letter, pk=pk)
    letter.receiver_person = None
    letter.save()
    return redirect('edwoca:letter_update', pk=pk)

def letter_add_sender_corporation(request, pk, corporation_id):
    letter = get_object_or_404(Letter, pk=pk)
    corporation = get_object_or_404(Corporation, pk=corporation_id)
    letter.sender_corporation = corporation
    letter.save()
    return redirect('edwoca:letter_update', pk=pk)

def letter_remove_sender_corporation(request, pk):
    letter = get_object_or_404(Letter, pk=pk)
    letter.sender_corporation = None
    letter.save()
    return redirect('edwoca:letter_update', pk=pk)

def letter_add_receiver_corporation(request, pk, corporation_id):
    letter = get_object_or_404(Letter, pk=pk)
    corporation = get_object_or_404(Corporation, pk=corporation_id)
    letter.receiver_corporation = corporation
    letter.save()
    return redirect('edwoca:letter_update', pk=pk)

def letter_remove_receiver_corporation(request, pk):
    letter = get_object_or_404(Letter, pk=pk)
    letter.receiver_corporation = None
    letter.save()
    return redirect('edwoca:letter_update', pk=pk)

def letter_add_sender_place(request, pk, place_id):
    letter = get_object_or_404(Letter, pk=pk)
    place = get_object_or_404(Place, pk=place_id)
    letter.sender_place = place
    letter.save()
    return redirect('edwoca:letter_update', pk=pk)

def letter_remove_sender_place(request, pk):
    letter = get_object_or_404(Letter, pk=pk)
    letter.sender_place = None
    letter.save()
    return redirect('edwoca:letter_update', pk=pk)

def letter_add_receiver_place(request, pk, place_id):
    letter = get_object_or_404(Letter, pk=pk)
    place = get_object_or_404(Place, pk=place_id)
    letter.receiver_place = place
    letter.save()
    return redirect('edwoca:letter_update', pk=pk)

def letter_remove_receiver_place(request, pk):
    letter = get_object_or_404(Letter, pk=pk)
    letter.receiver_place = None
    letter.save()
    return redirect('edwoca:letter_update', pk=pk)

def letter_add_edition(request, pk, zotitem_id):
    letter = get_object_or_404(Letter, pk=pk)
    zotitem = get_object_or_404(ZotItem, pk=zotitem_id)
    letter.edition.add(zotitem)
    return redirect('edwoca:letter_update', pk=pk)

def letter_remove_edition(request, pk, zotitem_id):
    letter = get_object_or_404(Letter, pk=pk)
    zotitem = get_object_or_404(ZotItem, pk=zotitem_id)
    letter.edition.remove(zotitem)
    return redirect('edwoca:letter_update', pk=pk)
