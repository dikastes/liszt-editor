from ...forms.manifestation import *
from ...models import Manifestation as EdwocaManifestation
from django.shortcuts import get_object_or_404, redirect, render
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
            manifestation.working_title = form.cleaned_data.get('working_title')
            manifestation.source_title = form.cleaned_data.get('source_title')
            manifestation.save()

            return redirect('edwoca:manifestation_update', pk=manifestation.pk)
        return render(request, 'edwoca/create_singleton.html', {'form': form})
    else:
        form = SingletonCreateForm(show_source_title = True)

    return render(request, 'edwoca/create_singleton.html', {
        'form': form,
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
            manifestation.working_title = form.cleaned_data.get('working_title')
            manifestation.save()

            return redirect('edwoca:manifestation_update', pk=manifestation.pk)
    else:
        form = SingletonCreateForm()

    return render(request, 'edwoca/create_singleton.html', {
        'form': form,
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
                    working_title = form.cleaned_data['temporary_title'],
                    period = period,
                    is_collection = True
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
            'referrer': 'manifestation_collection_create'
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
                    working_title = form.cleaned_data['temporary_title'],
                    period = period
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
            'referrer': 'manifestation_create'
        }

        return render(request, 'edwoca/create_manifestation.html', context)

