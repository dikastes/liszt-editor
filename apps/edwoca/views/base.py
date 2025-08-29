from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView
from django.views.generic.edit import UpdateView, FormView
from django.db.models import Case, When
from liszt_util.forms import SearchForm
from dmad_on_django.models import Person, Status
from liszt_util.tools import snake_to_camel_case, camel_to_snake_case
from haystack.generic_views import SearchView
from ..models import Work, Expression, Manifestation, Item
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
        context['manifestation_count'] = Manifestation.objects.count()
        context['item_count'] = Item.objects.count()
        context['library_count'] = Library.objects.count()
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
        context['manifestation_count'] = Manifestation.objects.count()
        context['item_count'] = Item.objects.count()
        context['library_count'] = Library.objects.count()
        context['object_list'] = [ result.object for result in SearchForm(self.request.GET).search().models(self.model) ]
        context['list_entity_type'] = self.get_model_name().lower()

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
