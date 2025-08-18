from .base import *
from ..forms.item import *
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import DeleteView, ListView
from django.views.generic.edit import CreateView, UpdateView
from ..models import Item as EdwocaItem


class ItemListView(EdwocaListView):
    model = EdwocaItem


class ItemSearchView(EdwocaSearchView):
    model = EdwocaItem


"""
class ItemTitleUpdateView(EntityMixin, TitleUpdateView):
    model = Item
    form_class = ItemTitleFormSet
    formset_property = 'titles'

    def get_success_url(self):
        return reverse_lazy('edwoca:item_title', kwargs = {'pk': self.object.id})
"""


class ItemUpdateView(EntityMixin, UpdateView):
    model = EdwocaItem
    #form_class = ItemForm
    template_name = 'edwoca/item_update.html'


class ItemCreateView(EntityMixin, CreateView):
    model = EdwocaItem
    #form_class = ItemForm
    template_name = 'edwoca/create.html'

    def get_success_url(self):
        return reverse_lazy('edwoca:item_update', kwargs = {'pk': self.object.id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'title_formset' not in context:
            if self.request.POST:
                context['title_formset'] = ItemTitleFormSet(self.request.POST, self.request.FILES)
            else:
                ItemTitleFormSet.can_delete = False
                context['title_form_set'] = ItemTitleFormSet()
        context['view_title'] = f"Neues Exemplar anlegen"
        context['button_label'] = "speichern"
        context['return_target'] = 'edwoca:index'
        context['return_pk'] = None
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.manifestation = Manifestation.objects.get(id=self.kwargs['manifestation_id'])
        title_formset = ItemTitleFormSet(self.request.POST, self.request.FILES, instance=self.object)

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


class ItemLocationUpdateView(SimpleFormView):
    model = EdwocaItem
    property = 'location'


class ItemRelationsUpdateView(EntityMixin, RelationsUpdateView):
    template_name = 'edwoca/item_relations.html'
    model = EdwocaItem
    form_class = RelatedItemForm


class RelatedItemAddView(RelatedEntityAddView):
    template_name = 'edwoca/item_relations.html'
    model = RelatedItem


class RelatedItemRemoveView(DeleteView):
    model = RelatedItem

    def get_success_url(self):
        return reverse_lazy('edwoca:item_relations', kwargs={'pk': self.object.source_item.id})


class ItemContributorsUpdateView(EntityMixin, ContributorsUpdateView):
    model = EdwocaItem
    form_class = ItemContributorForm


class ItemContributorAddView(ContributorAddView):
    model = ItemContributor


class ItemContributorRemoveView(DeleteView):
    model = ItemContributor

    def get_success_url(self):
        return reverse_lazy('edwoca:item_contributors', kwargs={'pk': self.object.item.id})


class ItemProvenanceUpdateView(EntityMixin, UpdateView):
    pass


class ItemDetailsUpdateView(SimpleFormView):
    model = EdwocaItem
    property = 'details'


class ItemDescriptionUpdateView(SimpleFormView):
    model = EdwocaItem
    property = 'description'


class ItemDigcopyUpdateView(SimpleFormView):
    model = EdwocaItem
    property = 'digcopy'


class ItemCommentUpdateView(SimpleFormView):
    model = EdwocaItem
    property = 'comment'


class ItemDeleteView(EntityMixin, DeleteView):
    model = EdwocaItem

    def get_success_url(self):
        return self.object.manifestation.get_absolute_url()


class LibraryListView(EdwocaListView):
    model = Library


class LibrarySearchView(EdwocaSearchView):
    model = Library


class LibraryCreateView(CreateView):
    model = Library
    #fields = ['siglum', 'name']
    template_name = 'edwoca/simple_form.html'
    form_class = LibraryForm


class LibraryUpdateView(UpdateView):
    model = Library
    #fields = ['siglum', 'name']
    template_name = 'edwoca/simple_form.html'
    form_class = LibraryForm


class LibraryDeleteView(DeleteView):
    model = Library
    template_name = 'edwoca/simple_form.html'
