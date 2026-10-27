from ...models.base import Manifestation as EdwocaManifestation
from ...models.base import *
from ...forms.manifestation import *
from ...forms.item import *
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _


def manifestation_update(request, pk):
    manifestation = EdwocaManifestation.objects.get(id=pk)
    context = {
        'object': manifestation,
        'entity_type': 'manifestation'
    }

    if request.method == 'POST':
        manifestation_form = ManifestationForm(request.POST, instance=manifestation)

        if 'remove-related-expression' in request.POST:
            related_expression_id = request.POST.get('remove-related-expression')
            related_expression = RelatedExpression.objects.get(pk=related_expression_id)
            related_expression.delete()

        related_expression_forms = []
        for related_expression in manifestation.expression_relations.all():
            related_expression_form = RelatedExpressionForm(
                    request.POST,
                    instance = related_expression,
                    prefix = f'related-expression-{related_expression.pk}'
                )
            related_expression_forms += [ related_expression_form ]

        signature_forms = []
        if manifestation.is_singleton:
            item = manifestation.get_single_item()
            signature_forms_valid = True

            for signature in manifestation.get_single_item().signatures.all():
                signature_form = SignatureForm(
                        request.POST,
                        instance = signature,
                        prefix = f"signature-{signature.id}"
                    )
                signature_forms.append(signature_form)

        all_forms = signature_forms + related_expression_forms + [ manifestation_form ]

        if all(f.is_valid() for f in all_forms):
            if manifestation.is_singleton:
                for signature in manifestation.get_single_item().signatures.all():
                    signature.status = ItemSignature.Status.FORMER
                    signature.save()
            for f in all_forms:
                f.save()
        else:
            context['manifestation_form'] = manifestation_form
            context['signature_forms'] = signature_forms

            return render(request, 'edwoca/manifestation_update.html', context)

        if 'add-related-expression' in request.POST:
            RelatedExpression.objects.create(manifestation=manifestation)

        if 'add_signature' in request.POST:
            status = ItemSignature.Status.CURRENT
            if item.signatures.count():
                status = ItemSignature.Status.FORMER
            signature = ItemSignature.objects.create(
                    item = item,
                    status = status
                )
            signature_forms += [ SignatureForm(instance = signature, prefix = f"signature-{signature.id}") ]

        if 'remove-signature' in request.POST:
            signature_pk = request.POST.get('remove-signature')
            item_signature = get_object_or_404(ItemSignature, pk=request.POST.get('remove-signature'))
            item_signature.delete()

        context['signature_forms'] = signature_forms
        context['library_search_form'] = SearchForm()

        return redirect('edwoca:manifestation_update', pk = pk)
    else:
        expression_search_form = FramedSearchForm(request.GET or None, prefix='expression', placeholder = _('search expressions'))
        context['expression_search_form'] = expression_search_form
        if 'expression_link' in request.GET:
            expression_link = get_object_or_404(Expression, pk = request.GET['expression_link'])
            context['expression_link'] = expression_link
        if expression_search_form.is_valid() and expression_search_form.cleaned_data.get('q'):
            context['expression_query'] = expression_search_form.cleaned_data.get('q')
            context['found_expressions'] = expression_search_form.search().models(Expression)

        related_expression_forms = []
        for related_expression in manifestation.expression_relations.all():
            related_expression_form = RelatedExpressionForm(
                    instance = related_expression,
                    prefix = f'related-expression-{related_expression.pk}'
                )
            related_expression_forms += [ related_expression_form ]

        manifestation_form = ManifestationForm(instance=manifestation)
        signature_forms = []
        if manifestation.is_singleton:
            for signature in manifestation.get_single_item().signatures.all():
                signature_form = SignatureForm(
                        instance = signature,
                        prefix = f"signature-{signature.id}"
                    )
                signature_forms.append(signature_form)

        context['signature_forms'] = signature_forms
        context['library_search_form'] = SearchForm()
        context['manifestation_form'] = manifestation_form
        context['related_expression_forms'] = related_expression_forms

    return render(request, 'edwoca/manifestation_update.html', context)


