from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView
from django.views.generic.edit import UpdateView, FormView
from dmad_on_django.forms import SearchForm
from haystack.generic_views import SearchView
from ..models import Work, Manifestation
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
        context['work_count'] = Work.objects.all().count()
        context['manifestation_count'] = Manifestation.objects.all().count()
        return context


class ModelMustBeSetMixin:
    def get_model(self):
        if not self.model:
            raise ImproperlyConfigured(f"{self.__class__.__name__} requires a 'model' attribute.")

        return self.model.__name__


class EdwocaSearchView(SearchView, ModelMustBeSetMixin):
    template_name = 'edwoca/list.html'
    form_class = SearchForm

    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', '')

        # redirect to list view if empty query
        if not query or query == '':
            return redirect(f'edwoca:{self.get_model().lower()}_list')

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['work_count'] = Work.objects.all().count()
        context['manifestation_count'] = Manifestation.objects.all().count()
        context['object_list'] = [ result.object for result in context['object_list'] ]

        return context

    def get_queryset(self):
        qs = super().get_queryset()

        return qs.models(getattr(edwoca_models, self.get_model()))


class SimpleFormView(UpdateView, ModelMustBeSetMixin):
    template_name = 'edwoca/simple_form.html'

    def get_form_class(self):
        class_name = f"{self.get_model()}{self.get_property().capitalize()}Form"
        return getattr(edwoca_forms, class_name)

    def get_success_url(self):
        return reverse_lazy(f"edwoca:{self.get_model().lower()}_{self.get_property()}", kwargs={'pk': self.object.pk})

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


class RelationsUpdateView(UpdateView):

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


class RelatedEntityAddView(FormView):

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


class ContributorsUpdateView(UpdateView):
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
