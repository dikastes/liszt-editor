from .base import *
from ..forms.item import *
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import DeleteView
from django.views.generic.edit import CreateView, UpdateView


class ItemTitleUpdateView(FormsetUpdateView):
    model = Item
    form_class = ItemTitleFormSet
    formset_property = 'titles'

    def get_success_url(self):
        return reverse_lazy('edwoca:item_title', kwargs = {'pk': self.object.id})


class ItemUpdateView(UpdateView):
    model = Item
    form_class = ItemForm
    template_name = 'edwoca/item_update.html'


class ItemCreateView(CreateView):
    model = Item
    form_class = ItemForm
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


class ItemDeleteView(DeleteView):
    pass


class ItemLocationUpdateView(SimpleFormView):
    model = Item
    property = 'location'


class ItemRelationsUpdateView(RelationsUpdateView):
    template_name = 'edwoca/item_relations.html'
    model = Item
    form_class = RelatedItemForm


class RelatedItemAddView(RelatedEntityAddView):
    template_name = 'edwoca/item_relations.html'
    model = RelatedItem


class RelatedItemRemoveView(DeleteView):
    model = RelatedItem

    def get_success_url(self):
        return reverse_lazy('edwoca:item_relations', kwargs={'pk': self.object.source_item.id})


class ItemContributorsUpdateView(ContributorsUpdateView):
    model = Item


class ItemProvenanceUpdateView(UpdateView):
    pass


class ItemDetailsUpdateView(SimpleFormView):
    model = Item
    property = 'details'


class ItemDescriptionUpdateView(SimpleFormView):
    model = Item
    property = 'description'


class ItemDigcopyUpdateView(SimpleFormView):
    model = Item
    property = 'digcopy'


class ItemCommentUpdateView(SimpleFormView):
    model = Item
    property = 'comment'


class ItemDeleteView(DeleteView):
    model = Item

    def get_success_url(self):
        return reverse_lazy('edwoca:work_update', kwargs={'pk': self.object.work.id})
