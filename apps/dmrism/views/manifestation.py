from ..forms import ManifestationForm
from ..models.manifestation import Manifestation
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

    unchanged_fields = True
    for field in _field_list:
        old_value = getattr(manifestation, field)
        new_value = getattr(temporary_manifestation, field)
        if old_value != new_value:
            unchanged_fields = False
            break

    unchanged_relations = True
    if manifestation.related_manifestations.count() != temporary_manifestation.related_manifestations.count():
        unchanged_relations = False
    else:
        for related_manifestation in manifestation.related_manifestations.all():
            if temporary_manifestation.related_manifestations.all().filter(id = related_manifestation.id).count() == 0:
                unchanged_relations = False

    if manifestation.items.all()[0].__str__() == temporary_manifestation.items.all()[0].__str__():
        unchanged_items = True
    else:
        unchanged_items = False

    context = {}
    context['object'] = manifestation
    context['unchanged_relations'] = unchanged_relations

    if unchanged_fields and unchanged_relations and unchanged_items:
        temporary_manifestation.delete()
        context['unchanged'] = True
    else:
        context['unchanged'] = False
        context['compare_object'] = temporary_manifestation

    return render(request, 'dmrism/confirm_pull.html', context)


_field_list = [
        'manifestation_form',
        'dedication',
        'handwriting',
        'extent',
        'paper',
        'private_comment'
    ]

_foreign_key_list = [
        'items',
        'related_manifestations'
        ]


def manifestation_confirm_pull(request, pk):
    temporary_manifestation = Manifestation.objects.get(temporary_target = pk)
    manifestation = Manifestation.objects.get(id = pk)

    for foreign_key in _foreign_key_list:
        getattr(manifestation, foreign_key).all().delete()
        for target in getattr(temporary_manifestation, foreign_key).all():
            getattr(manifestation, foreign_key).add(target)

    for field in _field_list:
        value = getattr(temporary_manifestation, field)
        setattr(manifestation, field, value)

    manifestation.rism_id_unaligned = False

    manifestation.save()
    temporary_manifestation.delete()

    return redirect('dmrism:manifestation_detail', pk = pk)


def manifestation_reject_pull(request, pk):
    temporary_manifestation = Manifestation.objects.get(temporary_target = pk)
    temporary_manifestation.delete()

    return redirect('dmrism:manifestation_detail', pk = pk)
