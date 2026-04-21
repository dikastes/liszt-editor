from ...forms.item import *
from ...forms.manifestation import *
from ...forms.modification import *
from ...models.base import *
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _

def manifestation_manuscript_update(request, pk):
    manifestation = get_object_or_404(Manifestation, pk=pk)
    item = manifestation.items.first()
    context = {
        'object': manifestation,
        'entity_type': 'manifestation'
    }
    item_handwriting_ids = [
            handwriting.id
            for handwriting
            in manifestation.get_single_item().handwritings.all()
        ]
    modification_handwriting_ids = [
            handwriting.id
            for modification
            in manifestation.get_single_item().modifications.all()
            for handwriting
            in modification.handwritings.all()
        ]

    if request.method == 'POST':
        form = ItemManuscriptForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
        else:
            return render(request, 'edwoca/manifestation_manuscript.html', context)
        context['form'] = form

        if 'manifestation_handwriting-delete' in request.POST:
            manifestation_handwriting = get_object_or_404(ItemHandwriting, pk = request.POST.get('manifestation_handwriting-delete'))
            manifestation_handwriting.delete()

        handwriting_forms = []
        for handwriting in item.handwritings.all():
            prefix = f'handwriting_{handwriting.id}'
            handwriting_form = ItemHandwritingForm(request.POST, instance=handwriting, prefix=prefix)
            if handwriting_form.is_valid():
                handwriting_form.save()
            handwriting_forms.append(handwriting_form)

        if 'add-manifestation-handwriting' in request.POST:
            item_handwriting = ItemHandwriting.objects.create(item = manifestation.get_single_item())
            prefix = f'handwriting_{item_handwriting.id}'
            handwriting_forms += ItemHandwritingForm(instance=item_handwriting, prefix=prefix)

        context['handwriting_forms'] = handwriting_forms

        modifications = []

        if 'remove-modification' in request.POST:
            modification = get_object_or_404(ItemModification, pk = request.POST.get('remove-modification'))
            modification.delete()

        for modification in item.modifications.all():
            for handwriting in modification.handwritings.all():
                prefix = f'modification_handwriting_{handwriting.id}'
                handwriting_form = ModificationHandwritingForm(request.POST, instance=handwriting, prefix=prefix)
                if handwriting_form.is_valid():
                    handwriting_form.save()

            prefix = f'modification_{modification.id}'
            modification_form = ItemModificationForm(request.POST, instance=modification, prefix=prefix)
            if modification_form.is_valid():
                modification_form.save()

            if f'{prefix}-calculate-machine-readable-date' in request.POST:
                period = modification.period
                period.parse_display()
                period.save()
                modification_form = ItemModificationForm(instance=modification, prefix=prefix)
            if f'{prefix}-clear-machine-readable-date' in request.POST:
                period = modification.period
                period.not_before = None
                period.not_after = None
                period.assumed = False
                period.inferred = False
                period.save()
                modification_form = ItemModificationForm(instance=modification, prefix=prefix)


            handwriting_forms = []
            for handwriting in modification.handwritings.all():
                prefix = f'modification_handwriting_{handwriting.id}'
                handwriting_form = ModificationHandwritingForm(instance=handwriting, prefix = prefix)
                if handwriting_form.is_valid():
                    handwriting_form.save()
                handwriting_forms.append(handwriting_form)

            modifications.append({
                'form': modification_form,
                'handwriting_forms': handwriting_forms
            })

        if 'add-modification' in request.POST:
            modification = ItemModification.objects.create(item = manifestation.get_single_item())
            modifications.append({
                    'form': ItemModificationForm(instance = modification),
                    'handwriting_forms': []
                })

        if 'add_handwriting' in request.POST:
            ItemHandwriting.objects.create(item=item)

        if 'add_modification' in request.POST:
            modification = ItemModification.objects.create(item=item)
            prefix = f'modification_{modification.id}'

            modifications.append({
                'form': ItemModificationForm(instance = modification, prefix = prefix),
                'handwriting_forms': []
            })

        context['modifications'] = modifications

        if 'add_modification_handwriting' in request.POST:
            modification_id = request.POST.get('add_modification_handwriting')
            modification = get_object_or_404(ItemModification, pk=modification_id)
            ModificationHandwriting.objects.create(modification=modification)

        if 'delete_modification' in request.POST:
            modification_id = request.POST.get('delete_modification')
            modification = get_object_or_404(ItemModification, pk=modification_id)
            modification.delete()

        open_modifications = []
        for key in request.POST:
            if key.startswith('collapse_modification_'):
                mod_id = int(key.split('_')[-1])
                open_modifications.append(mod_id)
        request.session['open_modifications'] = open_modifications

        return redirect('edwoca:manifestation_manuscript', pk = manifestation.id)

    else:
        open_modifications = request.session.get('open_modifications', [])
        if 'open_modifications' in request.session:
            del request.session['open_modifications']
        context['open_modifications'] = open_modifications

        for handwriting_id in item_handwriting_ids + modification_handwriting_ids:
            prefix = f'handwriting-{handwriting_id}'
            if f'{prefix}-q' in request.GET:
                search_form = SearchForm(request.GET or None, prefix = prefix)
                if search_form.is_valid() and search_form.cleaned_data.get('q'):
                    context['query'] = search_form.cleaned_data.get('q')
                    context['search_form'] = search_form
                    context['handwriting_found_persons'] = {
                            'handwriting_id': handwriting_id,
                            'results': search_form.search().models(Person)
                        }

        form = ItemManuscriptForm(instance=item)
        handwriting_forms = []
        for handwriting in item.handwritings.all():
            prefix = f'handwriting_{handwriting.id}'
            handwriting_forms.append(ItemHandwritingForm(instance=handwriting, prefix=prefix))
        context['handwriting_forms'] = handwriting_forms

        modifications = []
        for modification in item.modifications.all():
            #modification.ensure_period()
            prefix = f'modification_{modification.id}'
            modification_form = ItemModificationForm(instance=modification, prefix=prefix)

            handwriting_forms = []
            for handwriting in modification.handwritings.all():
                prefix = f'modification_handwriting_{handwriting.id}'
                handwriting_forms.append(ModificationHandwritingForm(instance=handwriting, prefix=prefix))

            modifications.append({
                'form': modification_form,
                'handwriting_forms': handwriting_forms
            })

        context['modifications'] = modifications

    context['form'] = form
    #context['search_form'] = search_form

    if request.GET.get('handwriting_id'):
        context['handwriting_id'] = int(request.GET.get('handwriting_id'))

    if request.GET.get('modification_id'):
        context['add_handwriting_for_modification'] = True
        context['modification_id'] = int(request.GET.get('modification_id'))
        if search_form.is_valid() and search_form.cleaned_data.get('q'):
            context['query'] = search_form.cleaned_data.get('q')
            context[f"modification_found_persons"] = search_form.search().models(Person)

    if request.GET.get('modification_handwriting_id'):
        context['modification_handwriting_id'] = int(request.GET.get('modification_handwriting_id'))

    # Search forms for modifications
    for key in request.GET:
        if key.startswith('modification-') and key.endswith('-q'):
            parts = key.split('-')
            modification_id = int(parts[1])
            model_name = parts[2]

            context['modification_id'] = modification_id
            if modification_id not in open_modifications:
                open_modifications.append(modification_id)

            query = request.GET.get(key)

            search_form = SearchForm({'q': query})

            if model_name == 'work':
                context['query_work'] = query
                context['found_works'] = search_form.search().models(Work)
            elif model_name == 'expression':
                context['query_expression'] = query
                context['found_expressions'] = search_form.search().models(Expression)
            elif model_name == 'manifestation':
                context['query_manifestation'] = query
                context['found_manifestations'] = search_form.search().models(Manifestation)

    work_search_form = SearchForm(prefix='work')
    expression_search_form = SearchForm(prefix='expression')
    manifestation_search_form = SearchForm(prefix='manifestation')

    context['work_search_form'] = work_search_form
    context['expression_search_form'] = expression_search_form
    context['manifestation_search_form'] = manifestation_search_form

    if request.GET.get('modification_id'):
        context['modification_id'] = int(request.GET.get('modification_id'))

    return render(request, 'edwoca/manifestation_manuscript.html', context)


def manifestation_add_handwriting_writer(request, pk, handwriting_pk, person_pk):
    handwriting = get_object_or_404(ItemHandwriting, pk=handwriting_pk)
    person = get_object_or_404(Person, pk=person_pk)
    handwriting.writer = person
    handwriting.save()
    return redirect('edwoca:manifestation_manuscript', pk=pk)


def manifestation_remove_handwriting_writer(request, pk, handwriting_pk):
    handwriting = get_object_or_404(ItemHandwriting, pk=handwriting_pk)
    handwriting.writer = None
    handwriting.save()
    return redirect('edwoca:manifestation_manuscript', pk=pk)


"""
class ModificationHandwritingDeleteView(DeleteView):
    model = ModificationHandwriting

    def get_success_url(self):
        if self.object.modification.item.manifestation.is_singleton:
            return reverse_lazy('edwoca:manifestation_manuscript', kwargs={'pk': self.object.modification.item.manifestation.id})
        else:
            return reverse_lazy('edwoca:item_manuscript', kwargs={'pk': self.object.modification.item.item.id})
"""

def modification_add_related_work(request, modification_pk, work_pk):
    modification = get_object_or_404(ItemModification, pk=modification_pk)
    work = get_object_or_404(Work, pk=work_pk)
    modification.related_work = work
    modification.save()
    if modification.item.manifestation.is_singleton:
        return redirect('edwoca:manifestation_manuscript', pk=modification.item.manifestation.id)
    else:
        return redirect('edwoca:item_manuscript', pk=modification.item.id)


def modification_remove_related_work(request, modification_pk):
    modification = get_object_or_404(ItemModification, pk=modification_pk)
    modification.related_work = None
    modification.save()
    if modification.item.manifestation.is_singleton:
        return redirect('edwoca:manifestation_manuscript', pk=modification.item.manifestation.id)
    else:
        return redirect('edwoca:item_manuscript', pk=modification.item.id)


def modification_add_related_expression(request, modification_pk, expression_pk):
    modification = get_object_or_404(ItemModification, pk=modification_pk)
    expression = get_object_or_404(Expression, pk=expression_pk)
    modification.related_expression = expression
    modification.save()
    if modification.item.manifestation.is_singleton:
        return redirect('edwoca:manifestation_manuscript', pk=modification.item.manifestation.id)
    else:
        return redirect('edwoca:item_manuscript', pk=modification.item.id)


def modification_remove_related_expression(request, modification_pk):
    modification = get_object_or_404(ItemModification, pk=modification_pk)
    modification.related_expression = None
    modification.save()
    if modification.item.manifestation.is_singleton:
        return redirect('edwoca:manifestation_manuscript', pk=modification.item.manifestation.id)
    else:
        return redirect('edwoca:item_manuscript', pk=modification.item.id)


