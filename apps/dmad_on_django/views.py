from django.urls import reverse_lazy
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views import generic
from .models import Person, Work
import dmad_on_django.models as dmad_models
from django import forms
from json import dumps
from haystack.generic_views import FacetedSearchView

# Create your views here.
def index(request):
    return redirect('dmad_on_django:person_list')


def get_link(model_object, model):
    link = reverse_lazy(f"dmad_on_django:{model}_update", kwargs = {'pk': model_object.id})
    title = model_object.get_designator()
    if model_object.gnd_id == '':
        title += ' (R)'
    return f"<li><a href={link}>{title}</a></li>"

class WorkSearchView(FacetedSearchView):
    pass

class PersonSearchView(FacetedSearchView):
    facet_fields = ['rework_in_gnd', 'entity_type', 'is_stub']
    template_name = 'dmad_on_django/person_list.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['active'] = 'person'
        context['person_count'] = Person.objects.count()
        context['work_count'] = Work.objects.count()
        return context

def person_list(request):
    context = {}
    context['objects'] = dumps([
            {
                'id': person.id,
                'designator': person.get_designator(),
                'rendered_link': get_link(person, 'person'),
                'rework_in_gnd': person.rework_in_gnd,
                'gnd_id': person.gnd_id
            }
            for person
            in Person.objects.all()
        ])
    context['active'] = 'person'
    context['person_count'] = Person.objects.count()
    context['work_count'] = Work.objects.count()
    return render(request, 'dmad_on_django/person_list.html', context)


def work_list(request):
    context = {}
    context['objects'] = [ { 'id': work['id'], 'designator': work.designator() } for work in Work.objects.all() ]
    context['active'] = 'work'
    return render(request, 'dmad_on_django/work_list.html', context)


class UnlinkView(generic.UpdateView):
    template_name = 'dmad_on_django/unlink.html'
    fields = []

    def post(self, request, **kwargs):
        response = super().post(self, request, **kwargs)
        self.object.gnd_id = ''
        self.object.save()
        return response

    def get_success_url(self):
        class_name = self.object.__class__.__name__.lower()
        return reverse_lazy(f"dmad_on_django:{class_name}_update", kwargs = {'pk': self.object.id})


class WorkUnlinkView(UnlinkView):
    model = Work


class PersonUnlinkView(UnlinkView):
    model = Person


class CreateView(generic.CreateView):
    template_name = 'dmad_on_django/create.html'
    fields = ['interim_designator', 'gnd_id', 'comment']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entity_type'] = self.model.__name__.lower()
        context['view_title'] = 'Datensatz anlegen'
        return context


class PersonCreateView(CreateView):
    model = Person

    def get_success_url(self):
        return reverse_lazy('dmad_on_django:person_update', kwargs = {'pk': self.object.id})

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if self.object.gnd_id:
            self.object.fetch_raw()
            self.object.update_from_raw()
            self.object.save()
        return response


class WorkCreateView(CreateView):
    model = Person

    def get_success_url(self):
        return reverse_lazy('dmad_on_django:work_update', kwargs = {'pk': self.object.id})


class UpdateView(generic.UpdateView):
    template_name = 'dmad_on_django/form_view.html'

    def get_form_class(self):
        return forms.modelform_factory(
            self.object.__class__,
            fields = self.get_form_fields()
        )

    # it is not possible to edit an interim designator once
    # a person data set is linked to GND
    def get_form_fields(self):
        if not self.object.gnd_id:
            return ['interim_designator', 'comment', 'rework_in_gnd']
        return ['comment', 'rework_in_gnd']

    def get_success_url(self):
        class_name = self.object.__class__.__name__.lower()
        return reverse_lazy(f"dmad_on_django:{class_name}_update", kwargs = {'pk': self.object.id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object'] = self.object
        return context


class WorkUpdateView(UpdateView):
    model = Person


class PersonUpdateView(UpdateView):
    model = Person


class DeleteView(generic.DeleteView):
    template_name = 'dmad_on_django/form_view.html'


class PersonDeleteView(DeleteView):
    model = Person
    success_url = reverse_lazy('dmad_on_django:list_person')


class WorkDeleteView(DeleteView):
    model = Person
    success_url = reverse_lazy('dmad_on_django:list_person')


class LinkView(generic.UpdateView):
    template_name = 'dmad_on_django/create.html'
    fields = ['interim_designator', 'gnd_id', 'comment']

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
        return reverse_lazy(f"dmad_on_django:{class_name}_update", kwargs = {'pk': self.object.id})


class WorkLinkView(LinkView):
    model = Work
    def get_success_url():
        return reverse_lazy('dmad_on_django:update_work', self.object)


class PersonLinkView(LinkView):
    model = Person
    #success_url = reverse_lazy('dmad_on_django:update_person', self.object)

    def get_success_url(self):
        return reverse_lazy('dmad_on_django:person_update', kwargs = {'pk': self.object.id})



class PullView(generic.UpdateView):
    template_name = 'dmad_on_django/form_view.html'
    fields = []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object'] = self.object
        return context

    def post(self, request, **kwargs):
        self.object.update()
        return super().post(self, request, **kwargs)


class WorkPullView(PullView):
    model = Work
    #success_url = reverse_lazy('dmad_on_django:update_work', self.object)


class PersonPullView(PullView):
    model = Person
    #success_url = reverse_lazy('dmad_on_django:update_person', self.object)

def search_gnd(request, search_string, entity_type):
    response = getattr(dmad_models, entity_type.capitalize()).search(search_string)
    return JsonResponse(response, safe=False)

def json_search(request, entity_type, hash=''):
    objects = dumps([
            {
                'id': person.id,
                'designator': person.get_designator(),
                'rendered_link': get_link(person, 'person'),
                'rework_in_gnd': person.rework_in_gnd,
                'gnd_id': person.gnd_id
            }
            for person
            in Person.objects.all()
        ])
    #hash = 

    context = {}
    context['objects'] = dumps([
            {
                'id': person.id,
                'designator': person.get_designator(),
                'rendered_link': get_link(person, 'person'),
                'rework_in_gnd': person.rework_in_gnd,
                'gnd_id': person.gnd_id
            }
            for person
            in Person.objects.all()
        ])
    context['active'] = 'person'
    context['person_count'] = Person.objects.count()
    context['work_count'] = Work.objects.count()
