from ..forms import ManifestationForm
from ..models.manifestation import Manifestation
from copy import deepcopy as clone
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DeleteView, DetailView
from django.views.generic.edit import CreateView, UpdateView
from haystack.generic_views import SearchView
from liszt_util.forms import SearchForm


class ManifestationListView(ListView):
    template_name = 'dmrism/list.html'
    model = Manifestation
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = SearchForm()
        return context


class ManifestationSearchView(SearchView):
    template_name = 'dmrism/list.html'
    model = Manifestation
    paginate_by = 10

    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', '')

        # redirect to list view if empty query
        if not query or query == '':
            return redirect(f'dmrism:manifestation_list')

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


class ManifestationDetailView(DetailView):
    model = Manifestation
    template_name = 'dmrism/detail.html'


class ManifestationUpdateView(UpdateView):
    model = Manifestation
    form_class = ManifestationForm
    template_name = 'dmrism/form.html'

    def form_valid(self, form):
        old_manifestation = Manifestation.objects.get(id = self.object.id)
        if old_manifestation.rism_id != self.object.rism_id:
            self.object.rism_id_unaligned = True
        return super().form_valid(form)


class ManifestationDeleteView(DeleteView):
    model = Manifestation
    success_url = reverse_lazy('dmrism:manifestation_list')
    template_name = 'dmrism/delete.html'


def manifestation_pull(request, pk):
    existing_temporary_manifestation = Manifestation.objects.filter(temporary_target = pk).first()
    if existing_temporary_manifestation:
        existing_temporary_manifestation.delete()

    manifestation = Manifestation.objects.get(id = pk)
    temporary_manifestation = Manifestation.objects.create(rism_id = manifestation.rism_id)
    temporary_manifestation.pull_rism_data()
    temporary_manifestation.temporary = True
    temporary_manifestation.temporary_target = manifestation
    temporary_manifestation.save()

    # do we need the temp flag on items as well?
    context = {}
    context['object'] = manifestation
    context['compare_object'] = temporary_manifestation

    return render(request, 'dmrism/confirm_pull.html', context)


def manifestation_confirm_pull(request, pk):
    temporary_manifestation = Manifestation.objects.get(temporary_target = pk)
    manifestation = Manifestation.objects.get(id = pk)

    manifestation.items.all().delete()
    for item in temporary_manifestation.items.all():
        manifestation.items.add(item)

    manifestation.related_manifestations.all().delete()
    for manifestation_relation in temporary_manifestation.related_manifestations.all():
        manifestation.related_manifestations.add(manifestation_relation)

    manifestation.manifestation_form = temporary_manifestation.manifestation_form
    manifestation.dedication = temporary_manifestation.dedication
    manifestation.handwriting = temporary_manifestation.handwriting
    manifestation.extent = temporary_manifestation.extent
    manifestation.paper = temporary_manifestation.paper
    manifestation.private_comment = temporary_manifestation.private_comment

    manifestation.save()
    temporary_manifestation.delete()

    return redirect('dmrism:manifestation_detail', pk = pk)


def manifestation_reject_pull(request, pk):
    temporary_manifestation = Manifestation.objects.get(temporary_target = pk)
    manifestation = Manifestation.objects.get(id = pk)
    temporary_manifestation.delete()

    return redirect('dmrism:manifestation_detail', pk = pk)
