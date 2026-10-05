from ...forms.manifestation import *
from ...models import Manifestation as EdwocaManifestation
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _
from dmrism.models import ItemSignature, Publication

def singleton_collection_create(request):
    if request.method == 'POST':
        form = SingletonCreateForm(request.POST, show_source_title = True)

        forms_valid = True
        if form.is_valid():
            manifestation = EdwocaManifestation.objects.create()

            item = Item.objects.create(manifestation=manifestation)

            library = form.cleaned_data['library']
            signature = ItemSignature.objects.create(
                library=library,
                signature=form.cleaned_data['signature']
            )
            item.signatures.add(signature)

            manifestation.is_singleton=True
            manifestation.source_title = form.cleaned_data.get('source_title')
            manifestation.save()

            RelatedExpression.objects.create(
                    manifestation = manifestation,
                    working_title = form.cleaned_data.get('working_title')
                )

            return redirect('edwoca:manifestation_update', pk=manifestation.pk)
        return render(request, 'edwoca/create_singleton.html', {
            'form': form,
            'page_title': _('create manuscript collection')
        })
    else:
        form = SingletonCreateForm(show_source_title = True)

    return render(request, 'edwoca/create_singleton.html', {
        'form': form,
        'page_title': _('create manuscript collection')
    })


def singleton_create(request):
    if request.method == 'POST':
        form = SingletonCreateForm(request.POST)
        if form.is_valid():
            manifestation = EdwocaManifestation.objects.create()

            item = Item.objects.create(manifestation=manifestation)

            library = form.cleaned_data['library']
            signature = ItemSignature.objects.create(
                library=library,
                signature=form.cleaned_data['signature']
            )
            item.signatures.add(signature)

            manifestation.is_singleton=True
            manifestation.source_type=form.cleaned_data.get('source_type')
            manifestation.save()

            RelatedExpression.objects.create(
                    manifestation = manifestation,
                    working_title = form.cleaned_data.get('working_title')
                )

            return redirect('edwoca:manifestation_update', pk=manifestation.pk)
        return render(request, 'edwoca/create_singleton.html', {
            'form': form,
            'page_title': _('create manuscript')
        })
    else:
        form = SingletonCreateForm()

    return render(request, 'edwoca/create_singleton.html', {
        'form': form,
        'page_title': _('create manuscript')
    })


def manifestation_collection_create(request, publisher_pk=None):
    publisher = get_object_or_404(Corporation, pk=publisher_pk) if publisher_pk else None

    if request.method == 'POST':

        data = request.POST.copy()
        if publisher:
            data['publisher'] = publisher.pk

        form = ManifestationCreateForm(data)
        if form.is_valid():

            display = form.cleaned_data.get('display')
            period = Period.objects.create(
                display=display,
            )

            try:
                period.parse_display()
                period.save()
            except Exception as e:
                print(e)

            manifestation = EdwocaManifestation.objects.create(
                    source_title = form.cleaned_data.get('source_title'),
                    source_type = EdwocaManifestation.SourceType.PRINT,
                    plate_number = form.cleaned_data.get('plate_number'),
                    period = period,
                    is_collection = True
            )

            RelatedExpression.objects.create(
                    manifestation = manifestation,
                    working_title = form.cleaned_data.get('working_title')
                )

            chosen_publisher = form.cleaned_data.get('publisher')
            if chosen_publisher:
                chosen_publisher = Corporation.objects.get(pk=chosen_publisher)
                Publication.objects.create(
                        publisher = chosen_publisher,
                        manifestation = manifestation
                )

            return redirect('edwoca:manifestation_update', pk=manifestation.pk)
        else:
            context = {
                'form': ManifestationCreateForm(is_collection = True),
                'referrer': 'manifestation_collection_create',
                'page_title': _('create print collection'),
                'view_title': _('create print collection')
            }

            return render(request, 'edwoca/create_manifestation.html', context)
    else:

        context = {
            'form': ManifestationCreateForm(is_collection = True),
            'referrer': 'manifestation_collection_create',
            'page_title': _('create print collection'),
            'view_title': _('create print collection')
        }

        return render(request, 'edwoca/create_manifestation.html', context)


def manifestation_create(request, publisher_pk=None):
    publisher = get_object_or_404(Corporation, pk=publisher_pk) if publisher_pk else None

    if request.method == 'POST':

        data = request.POST.copy()
        if publisher:
            data['publisher'] = publisher.pk

        form = ManifestationCreateForm(data)
        if form.is_valid():

            display = form.cleaned_data.get('display')
            period = Period.objects.create(
                display=display,
            )

            try:
                period.parse_display()
                period.save()
            except Exception as e:
                print(e)

            manifestation = EdwocaManifestation.objects.create(
                    source_title = form.cleaned_data.get('source_title'),
                    source_type = EdwocaManifestation.SourceType.PRINT,
                    plate_number = form.cleaned_data.get('plate_number'),
                    period = period
            )

            RelatedExpression.objects.create(
                    manifestation = manifestation,
                    working_title = form.cleaned_data.get('working_title')
                )

            chosen_publisher = form.cleaned_data.get('publisher')
            if chosen_publisher:
                chosen_publisher = Corporation.objects.get(pk=chosen_publisher)
                Publication.objects.create(
                        publisher = chosen_publisher,
                        manifestation = manifestation
                )

            return redirect('edwoca:manifestation_update', pk=manifestation.pk)
        else:
            context = {
                'form': ManifestationCreateForm(),
                'referrer': 'manifestation_create',
                'page_title': _('create print'),
                'view_title': _('create print')
            }
    else:
        context = {
            'form': ManifestationCreateForm(),
            'referrer': 'manifestation_create',
            'page_title': _('create print'),
            'view_title': _('create print')
        }

        return render(request, 'edwoca/create_manifestation.html', context)


def modified_print_create(request):
    if request.method == 'POST':
        data = request.POST.copy()
        form = ModifiedPrintCreateForm(data)

        if form.is_valid():
            manifestation = EdwocaManifestation.objects.create(
                    source_type = Manifestation.SourceType.MODIFIED_PRINT
                )
            first_item = Item.objects.create(
                    source_type = Item.SourceType.MODIFIED_PRINT,
                    manifestation = manifestation
                )

            library_id = form.cleaned_data.get('library')
            library = get_object_or_404(Library, pk=library_id)
            signature = ItemSignature.objects.create(
                    item = first_item,
                    signature = form.cleaned_data.get('signature'),
                    library = library
                )

            if target_manifestation_id := form.cleaned_data.get('related_print'):
                target_manifestation = get_object_or_404(EdwocaManifestation, pk=target_manifestation_id)
                RelatedManifestation.objects.create(
                        source_manifestation = manifestation,
                        target_manifestation = target_manifestation,
                        label = RelatedManifestation.Label.DERIVATIVE
                    )
                manifestation.source_title = target_manifestation.source_title
                manifestation.save()
            else:
                manifestation.manifestation_form = EdwocaManifestation.ManifestationForm.PROOF
                manifestation.save()

            return redirect('edwoca:manifestation_update', pk=manifestation.pk)
        else:
            context = {
                'form': form,
                'referrer': 'modified_print_create',
                'page_title': _('create modified print'),
                'view_title': _('create modified print')
            }

            return render(request, 'edwoca/create_manifestation.html', context)
    else:
        context = {
            'form': ModifiedPrintCreateForm(),
            'referrer': 'modified_print_create',
            'page_title': _('create modified print'),
            'view_title': _('create modified print')
        }

        return render(request, 'edwoca/create_manifestation.html', context)

