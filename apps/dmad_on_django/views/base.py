from django import forms
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView
from haystack.generic_views import SearchView
from json import dumps
from django.http import JsonResponse
import dmad_on_django.models as dmad_models
from dmad_on_django.models import Person, Work, Place
from dmad_on_django.forms import formWidgets

def form_invalid(self, form):
        if self.request.htmx:
            context = self.get_context_data(**{
                    self.form_name: form,
                    'object_list': self.get_queryset()
                })
            return render(self.request, 'dmad_on_django/partials/search_results.html', context)
        return super().form_invalid(form)

def form_valid(self, form):
        if self.request.htmx:
            self.queryset = form.search()
            context = self.get_context_data(**{
                    self.form_name: form,
                    'query': form.cleaned_data.get(self.search_field),
                    'object_list': self.queryset
                })
            return render(self.request, 'dmad_on_django/partials/search_results.html', context)
        return super().form_valid(form)

def search_gnd(request, search_string, entity_type):
    response = getattr(dmad_models, entity_type.capitalize()).search(search_string)
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


class DmadCreateView(CreateView):
    template_name = 'dmad_on_django/create.html'
    fields = ['interim_designator', 'gnd_id', 'comment']

    def get_form_class(self):
        return forms.modelform_factory(
            self.model,
            fields=self.fields,
            widgets=formWidgets
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entity_type'] = self.model.__name__.lower()
        context['view_title'] = 'Datensatz anlegen'
        return context


class DmadUpdateView(UpdateView):
    template_name = 'dmad_on_django/form_view.html'

    def get_form_class(self):
        return forms.modelform_factory(
            self.model,
            fields=self.get_form_fields(),
            widgets=formWidgets
        )

    def get_form_fields(self):
        if not self.object.gnd_id:
            return ['interim_designator', 'comment', 'rework_in_gnd']
        return ['comment', 'rework_in_gnd']

    def get_success_url(self):
        class_name = self.object.__class__.__name__.lower()
        return reverse_lazy(f"dmad_on_django:{class_name}_update", kwargs={'pk': self.object.id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object'] = self.object
        return context


class DeleteView(DeleteView):
    template_name = 'dmad_on_django/form_view.html'


class LinkView(UpdateView):
    template_name = 'dmad_on_django/create.html'
    fields = ['interim_designator', 'gnd_id', 'comment']

    def get_form_class(self):
        return forms.modelform_factory(
            self.model,
            fields=self.fields,
            widgets=formWidgets
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entity_type'] = self.model.__name__.lower()
        context['view_title'] = 'Datensatz mit der GND verknüpfen'
        return context

    def post(self, request, **kwargs):
        response = super().post(self, request, **kwargs)
        self.object.fetch_raw()
        self.object.update_from_raw()
        return response

    def get_success_url(self):
        class_name = self.object.__class__.__name__.lower()
        return reverse_lazy(f"dmad_on_django:{class_name}_update", kwargs={'pk': self.object.id})


class UnlinkView(UpdateView):
    template_name = 'dmad_on_django/unlink.html'
    fields = []

    def post(self, request, **kwargs):
        response = super().post(self, request, **kwargs)
        self.object.gnd_id = ''
        self.object.save()
        return response

    def get_success_url(self):
        class_name = self.object.__class__.__name__.lower()
        return reverse_lazy(f"dmad_on_django:{class_name}_update", kwargs={'pk': self.object.id})


class PullView(UpdateView):
    template_name = 'dmad_on_django/form_view.html'
    fields = []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object'] = self.object
        return context

    def post(self, request, **kwargs):
        self.object.update()
        return super().post(self, request, **kwargs)

class DmadSearchView(SearchView):
    def form_invalid(self, form):
        if self.request.htmx:
            context = self.get_context_data(**{
                    self.form_name: form,
                    'object_list': self.get_queryset()
                })
            return render(self.request, 'dmad_on_django/partials/search_results.html', context)
        return super().form_invalid(form)

    def form_valid(self, form):
        if self.request.htmx:
            self.queryset = form.search()
            context = self.get_context_data(**{
                    self.form_name: form,
                    'query': form.cleaned_data.get(self.search_field),
                    'object_list': self.queryset
                })
            return render(self.request, 'dmad_on_django/partials/search_results.html', context)
        return super().form_valid(form)
