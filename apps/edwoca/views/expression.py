from .base import *
from ..forms.expression import *
from django.forms.models import formset_factory
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import DeleteView
from django.views.generic.edit import CreateView, UpdateView


class ExpressionListView(EdwocaListView):
    model = Expression


class ExpressionSearchView(EdwocaSearchView):
    model = Expression


class ExpressionCreateView(EntityMixin, CreateView):
    model = Expression
    form_class = ExpressionForm
    template_name = 'edwoca/create.html'

    def get_success_url(self):
        return reverse_lazy('edwoca:expression_update', kwargs = {'pk': self.object.id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'title_formset' not in context:
            if self.request.POST:
                context['title_formset'] = ExpressionTitleFormSet(self.request.POST, self.request.FILES)
            else:
                ExpressionTitleFormSet.can_delete = False
                context['title_form_set'] = ExpressionTitleFormSet()
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.work = Work.objects.get(id=self.kwargs['work_id'])
        title_formset = ExpressionTitleFormSet(self.request.POST, self.request.FILES, instance=self.object)

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


class ExpressionUpdateView(EntityMixin, UpdateView):
    model = Expression
    form_class = ExpressionForm
    template_name = 'edwoca/expression_update.html'


class ExpressionTitleUpdateView(EntityMixin, TitleUpdateView):
    model = Expression
    form_class = ExpressionTitleFormSet
    formset_property = 'titles'

    def get_success_url(self):
        return reverse_lazy('edwoca:expression_title', kwargs = {'pk': self.object.id})


class ExpressionContributorsUpdateView(EntityMixin, ContributorsUpdateView):
    model = Expression
    form_class = ExpressionContributorForm


class ExpressionContributorAddView(ContributorAddView):
    model = ExpressionContributor


class ExpressionContributorRemoveView(DeleteView):
    model = ExpressionContributor

    def get_success_url(self):
        return reverse_lazy('edwoca:expression_contributors', kwargs={'pk': self.object.expression.id})


class ExpressionRelationsUpdateView(EntityMixin, RelationsUpdateView):
    template_name = 'edwoca/expression_relations.html'
    model = Expression
    form_class = RelatedExpressionForm


class RelatedExpressionAddView(EntityMixin, RelatedEntityAddView):
    template_name = 'edwoca/expression_relations.html'
    model = RelatedExpression


class RelatedExpressionRemoveView(DeleteView):
    model = RelatedExpression

    def get_success_url(self):
        return reverse_lazy('edwoca:expression_relations', kwargs={'pk': self.object.source_work.id})


class ExpressionHistoryUpdateView(EntityMixin, UpdateView):
    model = Expression
    form_class = ExpressionHistoryForm
    template_name = 'edwoca/simple_form.html'

    def get_success_url(self):
        return reverse_lazy('edwoca:expression_history', kwargs={'pk': self.object.pk})


class ExpressionCategorisationUpdateView(EntityMixin, UpdateView):
    pass


class ExpressionMediumofperformanceUpdateView(EntityMixin, UpdateView):
    pass


class ExpressionMovementsUpdateView(EntityMixin, FormsetUpdateView):
    model = Expression
    form_class = MovementFormSet
    template_name = 'edwoca/expression_movement.html'
    formset_property = 'movements'

    def get_success_url(self):
        return reverse_lazy('edwoca:expression_movement', kwargs={'pk': self.object.pk})


class ExpressionCommentUpdateView(EntityMixin, UpdateView):
    model = Expression
    form_class = ExpressionCommentForm
    template_name = 'edwoca/simple_form.html'

    def get_success_url(self):
        return reverse_lazy('edwoca:expression_comment', kwargs={'pk': self.object.pk})


class ExpressionDeleteView(EntityMixin, DeleteView):
    model = Expression
    template_name = 'edwoca/simple_form.html'

    def get_success_url(self):
        return reverse_lazy('edwoca:work_update', kwargs={'pk': self.object.work.id})
