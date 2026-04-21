from django import forms
from django.shortcuts import redirect, render
from django.urls import reverse_lazy, reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, UpdateView, DeleteView, ListView
from django.http import JsonResponse, HttpResponseRedirect
from liszt_util.forms import FramedSearchForm
import dmad_on_django.models as dmad_models
from dmad_on_django.models import Person, Work, Place, SubjectTerm, Corporation
from haystack.generic_views import SearchView
from haystack.query import SearchQuerySet
from json import dumps
from dmad_on_django.forms import formWidgets, DmadCreateForm, DmadUpdateForm
from liszt_util.tools import camel_to_snake_case, snake_to_camel_case
from pylobid.pylobid import GNDNotFoundError


def search_gnd(request, search_string, entity_type):
    response = getattr(dmad_models, snake_to_camel_case(entity_type)).search(search_string)
    return JsonResponse(response, safe=False)


def json_search(request, entity_type, hash=''):
    context = {
        'objects': dumps([
            {
                'id': person.id,
                'designator': person.get_designator(),
                'rendered_link': get_link(person, 'person'),
                'rework_in_gnd': person.rework_in_gnd,
                'gnd_id': person.gnd_id
            }
            for person in Person.objects.all()
        ]),
        'active': 'person',
        'person_count': Person.objects.count(),
        'work_count': Work.objects.count(),
        'place_count': Place.objects.count(),
        'corporation_count' : Corporation.objects.count()
    }
    return JsonResponse(context)


def index(request):
    return redirect('dmad_on_django:person_list')


def get_link(model_object, model):
    link = reverse_lazy(f"dmad_on_django:{model}_update", kwargs={'pk': model_object.id})
    title = model_object.get_designator()
    if model_object.gnd_id == '':
        title += ' (R)'
    return f"<li><a href={link}>{title}</a></li>"


class NavbarContextMixin:
    '''
    If you want to use the default navbar in your view use it like this:
    class MyView(NavbarContextMixin, ...)
    '''
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model = self.get_model()
        context.update({
            'active': camel_to_snake_case(model.__name__),
            'person_count': Person.objects.count(),
            'work_count': Work.objects.count(),
            'place_count': Place.objects.count(),
            'subjectterm_count': SubjectTerm.objects.count(),
            'corporation_count': Corporation.objects.count()
        })
        return context

    def get_model(self):
            raise NotImplementedError("Subclass must override get_model()")


class DmadBaseViewMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entity_type'] = camel_to_snake_case(self.model.__name__)
        return context

    def get_success_url(self):
        return reverse_lazy(f'dmad_on_django:{camel_to_snake_case(self.model.__name__)}_update',
               kwargs={'pk': self.object.id})


class DmadCreateView(DmadBaseViewMixin, CreateView):
    template_name = 'dmad_on_django/create.html'
    fields = ['interim_designator', 'gnd_id', 'comment']

    def get_form_class(self):
        return forms.modelform_factory(
            self.model,
            form=DmadCreateForm,
            fields=self.fields,
            widgets=formWidgets
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['view_title'] = 'Datensatz anlegen'
        return context

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        try:
            if self.object.gnd_id:
                self.object.fetch_raw()
                self.object.update_from_raw()
                self.object.save()
        except AttributeError:
            pass
        return response


class DmadUpdateView(DmadBaseViewMixin, NavbarContextMixin, UpdateView):
    template_name = 'dmad_on_django/form_view.html'

    def get_form_class(self):
        return forms.modelform_factory(
            self.model,
            form=DmadCreateForm,
            fields=self.get_form_fields(),
            widgets=formWidgets
        )

    def get_form_fields(self):
        if not self.object.gnd_id:
            return ['interim_designator', 'comment', 'rework_in_gnd']
        return ['comment', 'rework_in_gnd']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # braucht man das?
        context['object'] = self.object
        return context

    def get_model(self):
        return self.model


class LinkView(DmadBaseViewMixin, UpdateView):
    template_name = 'dmad_on_django/create.html'
    fields = ['interim_designator', 'gnd_id', 'comment']

    def get_form_class(self):
        return forms.modelform_factory(
            self.model,
            form=AsDaisyModelForm,
            fields=self.fields,
            widgets=formWidgets
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['view_title'] = 'Datensatz mit der GND verknüpfen'
        return context

    def post(self, request, **kwargs):
        response = super().post(self, request, **kwargs)
        self.object.fetch_raw()
        self.object.update_from_raw()
        return response


class UnlinkView(DmadBaseViewMixin, UpdateView):
    template_name = 'dmad_on_django/unlink.html'
    fields = []

    def post(self, request, **kwargs):
        response = super().post(self, request, **kwargs)
        self.object.gnd_id = ''
        self.object.save()
        return response


class PullView(UpdateView):
    template_name = 'dmad_on_django/form_view.html'
    fields = []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # braucht man das?
        context['object'] = self.object
        return context

    def post(self, request, **kwargs):
        self.object.update()
        return super().post(self, request, **kwargs)


class ListContextMixin(NavbarContextMixin):
    def get_model_name(self):
        return camel_to_snake_case(self.get_model().__name__)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        context.update({
            'active': camel_to_snake_case(self.model.__name__),
            'type': self.kwargs.get('type'),
            'search_url': reverse_lazy(f'dmad_on_django:{self.get_model_name()}_search')
        })
        if hasattr(self, 'sqs'):
            context.update({
                'rework_count': self.sqs.filter(rework_in_gnd=True).count(),
                'stub_count': self.sqs.filter(is_stub=True).count(),
            })
        else:
            context.update({
                'rework_count': self.model.objects.filter(rework_in_gnd=True).count(),
                'stub_count': self.model.objects.filter(gnd_id__isnull=True).count(),
            })


        return context


class DmadListView(ListContextMixin, ListView):
    template_name = 'dmad_on_django/list.html'
    paginate_by = 10

    def get_model(self):
        return self.model

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        placeholder = self.model.get_search_placeholder()
        context['form'] = FramedSearchForm(placeholder=placeholder)

        return context

    def get_queryset(self):
        qs = super().get_queryset()

        type_ = self.kwargs.get('type')
        if type_ == 'rework':
            qs = qs.filter(rework_in_gnd = True)
        if type_ == 'stub':
            qs = qs.filter(gnd_id__isnull = True)

        return qs

    def get(self, *args, **kwargs):
        response = super().get(*args, **kwargs)

        if self.request.htmx:
            context = self.get_context_data()
            return render(
                    self.request,
                    'dmad_on_django/partials/list_htmx.html',
                    context
                )
        return response


class DmadSearchView(ListContextMixin, NavbarContextMixin, SearchView):
    template_name = 'dmad_on_django/list.html'
    form_class = FramedSearchForm
    paginate_by = 10
    filter_type = None

    def get(self, requet, *args, **kwargs):
        query = self.request.GET.get('q', '')

        self.filter_type = self.kwargs.get('type', None)

        if not query or query == '':
            if self.filter_type:
                return redirect(
                        f'dmad_on_django:{camel_to_snake_case(self.model.__name__)}_list',
                        type=self.filter_type
                    )
            return redirect(
                    f'dmad_on_django:{camel_to_snake_case(self.model.__name__)}_list'
                )

        return super().get(self.request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['object_list'] = [r.object for r in context['object_list']]

        return context

    def form_valid(self, form):
        self.sqs = form.search().models(self.model)

        if self.filter_type == 'rework':
            self.sqs = self.sqs.filter(rework_in_gnd = True)
        if self.filter_type == 'stub':
            self.sqs = self.sqs.filter(is_stub = True)

        context = self.get_context_data(**{
                self.form_name: form,
                'query': form.cleaned_data.get(self.search_field),
                'object_list': self.sqs
            })

        if self.request.htmx:
            return render(
                    self.request,
                    'dmad_on_django/partials/list_htmx.html',
                    context
                )

        return self.render_to_response(context)

    def get_model(self):
        return self.model
