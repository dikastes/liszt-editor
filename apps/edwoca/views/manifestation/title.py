from ...forms.dedication import *
from ...forms.item import *
from ...forms.manifestation import *
from ...models.base import *
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _


def manifestation_title_update(request, pk):
    manifestation = get_object_or_404(Manifestation, pk=pk)
    context = {
        'object': manifestation,
        'entity_type': 'manifestation'
    }

    if request.method == 'POST':
        # collect any invalid forms and create a global render method in case one is invalid
        form = ManifestationTitleDedicationForm(request.POST, instance=manifestation)
        if form.is_valid():
            form.save()
        context['form'] = form

        print_form = ManifestationPrintForm(request.POST, instance=manifestation)
        if print_form.is_valid():
            print_form.save()

        if 'remove-title' in request.POST:
            manifestation_title = get_object_or_404(ManifestationTitle, pk = request.POST.get('remove-title'))
            manifestation_title.delete()

        if 'remove-manifestation-title-handwriting' in request.POST:
            title_handwriting = get_object_or_404(ManifestationTitleHandwriting, pk = request.POST.get('remove-manifestation-title-handwriting'))
            title_handwriting.delete()

        if 'remove-manifestationtitlehandwriting-writer' in request.POST:
            title_handwriting = get_object_or_404(ManifestationTitleHandwriting, pk = request.POST.get('remove-manifestationtitlehandwriting-writer'))
            title_handwriting.writer = None
            title_handwriting.save()

        if 'add-manifestation-title-handwriting' in request.POST:
            manifestation_title= get_object_or_404(ManifestationTitle, pk = request.POST.get('add-manifestation-title-handwriting'))
            ManifestationTitleHandwriting.objects.create(manifestation_title = manifestation_title)

        title_forms = []
        for title_obj in manifestation.titles.all():
            prefix = f'title_{title_obj.id}'
            title_form = ManifestationTitleForm(request.POST, instance=title_obj, prefix=prefix)
            if title_form.is_valid():
                title_form.save()

            # Handle existing ManifestationTitleHandwriting forms for this title
            for handwriting_obj in title_obj.handwritings.all():
                handwriting_prefix = f'title_handwriting_{handwriting_obj.id}'
                data = request.POST.copy()
                if f'{handwriting_prefix}-medium' not in data:
                    data[f'{handwriting_prefix}-medium'] = handwriting_obj.medium
                handwriting_form = ManifestationTitleHandwritingForm(data, instance=handwriting_obj, prefix=handwriting_prefix)
                if handwriting_form.is_valid():
                    handwriting_form.save()
            title_forms.append(title_form)

        if 'create-title' in request.POST:
            manifestation_title = ManifestationTitle.objects.create(
                    manifestation = manifestation
                )
            prefix = f'title_{manifestation_title.id}'
            title_forms += ManifestationTitleForm(instance=manifestation_title, prefix=prefix)

        context['title_forms'] = title_forms

        # Handle adding new ManifestationTitleHandwriting
        if 'add_title_handwriting' in request.POST:
            title_id_to_add_handwriting = request.POST.get('add_title_handwriting_to_title_id')
            if title_id_to_add_handwriting:
                title_obj = get_object_or_404(ManifestationTitle, pk=title_id_to_add_handwriting)
                ManifestationTitleHandwriting.objects.create(manifestation_title=title_obj)

        if 'remove-person-dedication' in request.POST:
            person_dedication = get_object_or_404(ManifestationPersonDedication, pk = request.POST.get('remove-person-dedication'))
            person_dedication.delete()

        person_dedication_forms = []
        for person_dedication in manifestation.manifestation_person_dedications.all():
            prefix = f'person_dedication_{person_dedication.id}'
            form = ManifestationPersonDedicationForm(request.POST, instance=person_dedication, prefix=prefix)
            if form.is_valid():
                form.save()
            if f'{prefix}-calculate-machine-readable-date' in request.POST:
                period = person_dedication.period
                period.parse_display()
                period.save()
                form = ManifestationPersonDedicationForm(instance=person_dedication, prefix=prefix)
            if f'{prefix}-clear-machine-readable-date' in request.POST:
                period = person_dedication.period
                period.not_before = None
                period.not_after = None
                period.inferred = False
                period.assumed = False
                period.save()
                form = ManifestationPersonDedicationForm(instance=person_dedication, prefix=prefix)
            person_dedication_forms.append(form)

        if 'create-person-dedication' in request.POST:
            person_dedication = ManifestationPersonDedication.objects.create(
                    manifestation = manifestation
                )
            prefix = f'title_{person_dedication.id}'
            person_dedication_forms += ManifestationPersonDedicationForm(instance=person_dedication, prefix=prefix)

        context['person_dedication_forms'] = person_dedication_forms

        if 'remove-corporation-dedication' in request.POST:
            corporation_dedication = get_object_or_404(ManifestationCorporationDedication, pk = request.POST.get('remove-corporation-dedication'))
            corporation_dedication.delete()

        corporation_dedication_forms = []
        for corporation_dedication in manifestation.manifestation_corporation_dedications.all():
            prefix = f'corporation_dedication_{corporation_dedication.id}'
            form = ManifestationCorporationDedicationForm(request.POST, instance=corporation_dedication, prefix=prefix)
            if form.is_valid():
                form.save()
            if f'{prefix}-calculate-machine-readable-date' in request.POST:
                period = corporation_dedication.period
                period.parse_display()
                period.save()
                form = ManifestationCorporationDedicationForm(instance=corporation_dedication, prefix=prefix)
            if f'{prefix}-clear-machine-readable-date' in request.POST:
                period = corporation_dedication.period
                period.not_before = None
                period.not_after = None
                period.inferred = False
                period.assumed = False
                period.save()
                form = ManifestationCorporationDedicationForm(instance=corporation_dedication, prefix=prefix)
            corporation_dedication_forms.append(form)

        if 'create-corporation-dedication' in request.POST:
            corporation_dedication = ManifestationCorporationDedication.objects.create(
                    manifestation = manifestation
                )
            prefix = f'title_{corporation_dedication.id}'
            corporation_dedication_forms += ManifestationCorporationDedicationForm(instance=corporation_dedication, prefix=prefix)

        context['corporation_dedication_forms'] = corporation_dedication_forms

        return redirect('edwoca:manifestation_title', pk = manifestation.id)

    else:
        # Initialize forms for existing titles
        form = ManifestationTitleDedicationForm(instance=manifestation)
        context['form'] = form

        title_forms = []
        for title_obj in manifestation.titles.all():
            prefix = f'title_{title_obj.id}'
            title_form = ManifestationTitleForm(instance=title_obj, prefix=prefix) # Get the form instance

            # Initialize forms for existing ManifestationTitleHandwriting for this title
            handwriting_forms = []
            for handwriting_obj in title_obj.handwritings.all():
                handwriting_prefix = f'title_handwriting_{handwriting_obj.id}'
                handwriting_forms.append(ManifestationTitleHandwritingForm(instance=handwriting_obj, prefix=handwriting_prefix))
            title_form.handwriting_forms = handwriting_forms # Attach to the form instance

            title_forms.append(title_form) # Append the form instance to the list

        context['title_forms'] = title_forms

        # Initialize forms for existing PersonDedication
        person_dedication_forms = []
        for person_dedication in manifestation.manifestation_person_dedications.all():
            prefix = f'person_dedication_{person_dedication.id}'
            person_dedication_forms.append(ManifestationPersonDedicationForm(instance=person_dedication, prefix=prefix))
        context['person_dedication_forms'] = person_dedication_forms

        # Initialize forms for existing CorporationDedication
        corporation_dedication_forms = []
        for corporation_dedication in manifestation.manifestation_corporation_dedications.all():
            prefix = f'corporation_dedication_{corporation_dedication.id}'
            corporation_dedication_forms.append(ManifestationCorporationDedicationForm(instance=corporation_dedication, prefix=prefix))
        context['corporation_dedication_forms'] = corporation_dedication_forms

    context['print_form'] = ManifestationPrintForm(instance=manifestation)

    q_dedicatee = request.GET.get('dedicatee-q')
    q_place = request.GET.get('place-q')

    if q_dedicatee:
        dedicatee_search_form = FramedSearchForm(request.GET, prefix='dedicatee', placeholder=_('search persons'))
        if dedicatee_search_form.is_valid():
            context['query_dedicatee'] = dedicatee_search_form.cleaned_data.get('q')
            context['found_persons'] = dedicatee_search_form.search().models(Person)
            context['found_corporations'] = dedicatee_search_form.search().models(Corporation)
    else:
        dedicatee_search_form = FramedSearchForm(prefix='dedicatee', placeholder=_('search persons'))

    if q_place:
        place_search_form = FramedSearchForm(request.GET, prefix='place', placeholder=_('search place'))
        if place_search_form.is_valid():
            context['query_place'] = place_search_form.cleaned_data.get('q')
            context['found_places'] = place_search_form.search().models(Place)
    else:
        place_search_form = FramedSearchForm(prefix='place', placeholder=_('search place'))

    context['dedicatee_search_form'] = dedicatee_search_form
    context['place_search_form'] = place_search_form

    if request.GET.get('person_dedication_id'):
        context['person_dedication_id'] = int(request.GET.get('person_dedication_id'))
    if request.GET.get('corporation_dedication_id'):
        context['corporation_dedication_id'] = int(request.GET.get('corporation_dedication_id'))

    search_form = FramedSearchForm(request.GET or None, placeholder=_('search persons'))
    context['search_form'] = search_form

    if search_form.is_valid() and search_form.cleaned_data.get('q'):
        context['query'] = search_form.cleaned_data.get('q')
        context[f"found_persons"] = search_form.search().models(Person)

    return render(request, 'edwoca/manifestation_title.html', context)


def manifestation_title_add_handwriting_writer(request, pk, title_handwriting_pk, person_pk):
    title_handwriting = get_object_or_404(ManifestationTitleHandwriting, pk=title_handwriting_pk)
    person = get_object_or_404(Person, pk=person_pk)
    title_handwriting.writer = person
    title_handwriting.save()
    return redirect(reverse('edwoca:manifestation_title', kwargs={'pk': pk}))


def manifestation_title_remove_handwriting_writer(request, pk, title_handwriting_pk):
    title_handwriting = get_object_or_404(ManifestationTitleHandwriting, pk=title_handwriting_pk)
    title_handwriting.writer = None
    title_handwriting.save()
    return redirect(reverse('edwoca:manifestation_title', kwargs={'pk': pk}))


def manifestation_person_dedication_add_dedicatee(request, pk, dedication_id, person_id):
    dedication = get_object_or_404(ManifestationPersonDedication, pk=dedication_id)
    person = get_object_or_404(Person, pk=person_id)
    dedication.dedicatee.add(person)
    dedication.save()
    return redirect('edwoca:manifestation_title', pk=pk)


def manifestation_person_dedication_remove_dedicatee(request, pk, dedication_id, person_id):
    dedication = get_object_or_404(ManifestationPersonDedication, pk=dedication_id)
    person = get_object_or_404(Person, pk=person_id)
    dedication.dedicatee.remove(person)
    dedication.save()
    return redirect('edwoca:manifestation_title', pk=pk)


def manifestation_corporation_dedication_add_dedicatee(request, pk, dedication_id, corporation_id):
    dedication = get_object_or_404(ManifestationCorporationDedication, pk=dedication_id)
    corporation = get_object_or_404(Corporation, pk=corporation_id)
    dedication.dedicatee.add(corporation)
    dedication.save()
    return redirect('edwoca:manifestation_title', pk=pk)


def manifestation_corporation_dedication_remove_dedicatee(request, pk, dedication_id, corporation_id):
    dedication = get_object_or_404(ManifestationCorporationDedication, pk=dedication_id)
    corporation = get_object_or_404(Corporation, pk=corporation_id)
    dedication.dedicatee.remove(corporation)
    dedication.save()
    return redirect('edwoca:manifestation_title', pk=pk)


def manifestation_person_dedication_add_place(request, pk, dedication_id, place_id):
    dedication = ManifestationPersonDedication.objects.get(pk=dedication_id)
    place = get_object_or_404(Place, pk=place_id)
    dedication.place = place
    dedication.save()
    return redirect('edwoca:manifestation_title', pk=pk)


def manifestation_person_dedication_remove_place(request, pk, dedication_id):
    dedication = ManifestationPersonDedication.objects.get(pk=dedication_id)
    dedication.place = None
    dedication.save()
    return redirect('edwoca:manifestation_title', pk=pk)


def manifestation_corporation_dedication_add_place(request, pk, dedication_id, place_id):
    dedication = get_object_or_404(ManifestationCorporationDedication, pk=dedication_id)
    place = get_object_or_404(Place, pk=place_id)
    dedication.place = place
    dedication.save()
    return redirect('edwoca:manifestation_title', pk=pk)


def manifestation_corporation_dedication_remove_place(request, pk, dedication_id):
    dedication = get_object_or_404(ManifestationCorporationDedication, pk=dedication_id)
    dedication.place = None
    dedication.save()
    return redirect('edwoca:manifestation_title', pk=pk)
