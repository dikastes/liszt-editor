from django.views.generic import ListView
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy, reverse
from django.views.generic import DeleteView, DetailView
from django.views.generic.edit import CreateView, UpdateView
from ..models.manifestation import Manifestation
from liszt_util.views.base import *
from ..forms import ManifestationForm


class ManifestationListView(AbstractListView):
    template_name = 'dmrism/list.html'
    model = Manifestation
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = SearchForm()
        return context


class ManifestationSearchView(AbstractSearchView):
    template_name = 'dmrism/list.html'
    model = Manifestation
    paginate_by = 10

    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', '')

        # redirect to list view if empty query
        if not query or query == '':
            return redirect(f'dmrism:{camel_to_snake_case(self.get_model_name())}_list')

        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        qs = super().get_queryset()

        return qs.models(Manifestation)

class ManifestationCreateView(CreateView):
    model = Manifestation
    template_name = 'dmrism/form.html'
    form_class = ManifestationForm

    def form_valid(self, form):
        response = super().form_valid(form)
        self.object.pull_rism_data()
        return response

"""
old edwoca create view
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
"""


class ManifestationDetailView(DetailView):
    model = Manifestation


class ManifestationUpdateView(UpdateView):
    model = Manifestation
    form_class = ManifestationForm
    template_name = 'edwoca/manifestation_update.html'


class ManifestationDeleteView(DeleteView):
    model = Manifestation
    success_url = reverse_lazy('dmrism:manifestation_list')
    template_name = 'dmrism/delete.html'


def manifestation_pull(request, pk):
    pass

def manifestation_confirm_pull(request, pk):
    pass

def manifestation_reject_pull(request, pk):
    pass
