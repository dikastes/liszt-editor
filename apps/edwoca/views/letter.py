from django.forms import inlineformset_factory
from django.utils.translation import gettext_lazy as _
from django.shortcuts import redirect, get_object_or_404, render
from edwoca.models.letter import *
from .base import *
from ..forms.letter import *


class LetterListView(EdwocaListView):
    model = Letter


class LetterSearchView(EdwocaSearchView):
    model = Letter


class LetterCreateView(CreateView):
    model = Letter
    template_name = 'edwoca/simple_form.html'
    form_class = LetterForm


class LetterDeleteView(DeleteView):
    model = Letter
    template_name = 'edwoca/delete.html'
    success_url = reverse_lazy('edwoca:letter_list')


def letter_update(request, pk):
    letter = get_object_or_404(Letter, pk=pk)
    context = {
        'object': letter,
        'entity_type': 'letter'
    }

    if request.method == 'POST':
        form = LetterForm(request.POST, instance=letter)
        edition_period_form = LetterEditionPeriodForm(request.POST, instance=letter, prefix='edition_period')
        source_period_form = LetterSourcePeriodForm(request.POST, instance=letter, prefix='source_period')

        roles = ['sender', 'receiver']
        models = ['person', 'place', 'corporation']

        remove_signature_string = 'remove-signature'
        if remove_signature_string in request.POST:
            pk = request.POST.get(remove_signature_string)
            signature = LetterSignature.objects.get(id = pk)
            signature.delete()

        remove_digcopy_string = 'remove-letter-digcopy'
        if remove_digcopy_string in request.POST:
            pk = request.POST.get(remove_digcopy_string)
            digcopy = LetterDigitalCopy.objects.get(id = pk)
            digcopy.delete()

        for role in roles:
            for model in models:
                # handle removing the contributor links in the lettercontributor entries
                remove_submodel_string = f'{role}-{model}-remove-{model}'
                if remove_submodel_string in request.POST:
                    pk = request.POST.get(remove_submodel_string)
                    contributor_model = apps.get_model('edwoca', role + model)
                    entity = contributor_model.objects.get(id = pk)
                    setattr(entity, model, None)
                    entity.save()
                # handle removing lettercontributor entries
                remove_model_string = f'remove-{role}-{model}'
                if remove_model_string in request.POST:
                    pk = request.POST.get(remove_model_string)
                    contributor_model = apps.get_model('edwoca', role + model)
                    entity = contributor_model.objects.get(id = pk)
                    entity.delete()

        letter_signature_forms = []
        for letter_signature in letter.signatures.all():
            prefix = f'signature_{letter_signature.id}'
            letter_signature_form = LetterSignatureForm(request.POST, instance = letter_signature, prefix = prefix)
            letter_signature_forms.append(letter_signature_form)

        sender_person_forms = []
        for sender_person in letter.senderperson_relations.all():
            prefix = f'sender_person_{sender_person.id}'
            sender_person_form = SenderPersonForm(request.POST, instance = sender_person, prefix = prefix)
            sender_person_forms.append(sender_person_form)

        receiver_person_forms = []
        for receiver_person in letter.receiverperson_relations.all():
            prefix = f'receiver_person_{receiver_person.id}'
            receiver_person_form = ReceiverPersonForm(request.POST, instance = receiver_person, prefix = prefix)
            receiver_person_forms.append(receiver_person_form)

        sender_corporation_forms = []
        for sender_corporation in letter.sendercorporation_relations.all():
            prefix = f'sender_corporation_{sender_corporation.id}'
            sender_corporation_form = SenderCorporationForm(request.POST, instance = sender_corporation, prefix = prefix)
            sender_corporation_forms.append(sender_corporation_form)

        receiver_corporation_forms = []
        for receiver_corporation in letter.receivercorporation_relations.all():
            prefix = f'receiver_corporation_{receiver_corporation.id}'
            receiver_corporation_form = ReceiverCorporationForm(request.POST, instance = receiver_corporation, prefix = prefix)
            receiver_corporation_forms.append(receiver_corporation_form)

        sender_place_forms = []
        for sender_place in letter.senderplace_relations.all():
            prefix = f'sender_place_{sender_place.id}'
            sender_place_form = SenderPlaceForm(request.POST, instance = sender_place, prefix = prefix)
            sender_place_forms.append(sender_place_form)

        receiver_place_forms = []
        for receiver_place in letter.receiverplace_relations.all():
            prefix = f'receiver_place_{receiver_place.id}'
            receiver_place_form = ReceiverPlaceForm(request.POST, instance = receiver_place, prefix = prefix)
            receiver_place_forms.append(receiver_place_form)

        letter_mentioning_forms = []
        for letter_mentioning in letter.lettermentioning_set.all():
            prefix = f'letter_mentioning_{letter_mentioning.id}'
            letter_mentioning_form = LetterMentioningForm(
                    request.POST,
                    instance = letter_mentioning,
                    prefix = prefix
                )
            letter_mentioning_forms.append(letter_mentioning_form)

        letter_digitized_copy_forms = []
        for digital_copy in letter.digital_copies.all():
            prefix = f'letter_digcopy_{digital_copy.id}'
            letter_digitized_copy_form = LetterDigitizedCopyForm(
                    request.POST,
                    instance = digital_copy,
                    prefix = prefix
                )
            letter_digitized_copy_forms.append(letter_digitized_copy_form)

        if 'add-digcopy' in request.POST:
            LetterDigitalCopy.objects.create(letter=letter)
        if 'add-sender-person' in request.POST:
            SenderPerson.objects.create(letter=letter)
        if 'add-receiver-person' in request.POST:
            ReceiverPerson.objects.create(letter=letter)
        if 'add-sender-corporation' in request.POST:
            SenderCorporation.objects.create(letter=letter)
        if 'add-receiver-corporation' in request.POST:
            ReceiverCorporation.objects.create(letter=letter)
        if 'add-sender-place' in request.POST:
            SenderPlace.objects.create(letter=letter)
        if 'add-receiver-place' in request.POST:
            ReceiverPlace.objects.create(letter=letter)
        if 'add-signature' in request.POST:
            status = LetterSignature.Status.CURRENT
            if letter.signatures.count():
                status = LetterSignature.Status.FORMER
            signature = LetterSignature.objects.create(
                    letter = letter,
                    status = status
                )

        all_forms = (sender_person_forms +
            receiver_person_forms +
            sender_corporation_forms +
            receiver_corporation_forms+
            sender_place_forms +
            receiver_place_forms +
            letter_mentioning_forms +
            letter_digitized_copy_forms +
            letter_signature_forms +
            [ form, edition_period_form, source_period_form ])

        if all(f.is_valid() for f in all_forms):
            for form in all_forms:
                form.save()
        else:
            context = {
                    'form': form,
                    'edition_period_form': edition_period_form,
                    'source_period_form': source_period_form,
                    'sender_person_forms': receiver_person_forms,
                    'receiver_person_forms': receiver_person_forms,
                    'sender_corporation_forms': receiver_corporation_forms,
                    'receiver_corporation_forms': receiver_corporation_forms,
                    'sender_place_forms': receiver_place_forms,
                    'receiver_place_forms': receiver_place_forms,
                    'letter_signature_forms': letter_signature_forms
                }
            return render(request, 'edwoca/letter_update.html', context)

        if 'edition_period-calculate-machine-readable-date' in request.POST:
            letter.edition_period.parse_display()
            letter.edition_period.save()
        if 'source_period-calculate-machine-readable-date' in request.POST:
            letter.source_period.parse_display()
            letter.source_period.save()

        return redirect('edwoca:letter_update', pk = letter.pk)

    else:
        form = LetterForm(instance=letter)
        letter_mentioning_forms = []
        edition_period_form = LetterEditionPeriodForm(instance=letter, prefix='edition_period')
        source_period_form = LetterSourcePeriodForm(instance=letter, prefix='source_period')
        for letter_mentioning in letter.lettermentioning_set.all():
            prefix = f'letter_mentioning_{letter_mentioning.id}'
            letter_mentioning_forms.append(
                LetterMentioningForm(
                    instance = letter_mentioning,
                    prefix = prefix
                ))

        letter_signature_forms = []
        for letter_signature in letter.signatures.all():
            prefix = f'signature_{letter_signature.id}'
            letter_signature_form = LetterSignatureForm(instance = letter_signature, prefix = prefix)
            letter_signature_forms.append(letter_signature_form)

        sender_person_forms = []
        for sender_person in letter.senderperson_relations.all():
            prefix = f'sender_person_{sender_person.id}'
            sender_person_form = SenderPersonForm(instance = sender_person, prefix = prefix)
            sender_person_forms.append(sender_person_form)

        receiver_person_forms = []
        for receiver_person in letter.receiverperson_relations.all():
            prefix = f'receiver_person_{receiver_person.id}'
            receiver_person_form = ReceiverPersonForm(instance = receiver_person, prefix = prefix)
            receiver_person_forms.append(receiver_person_form)

        sender_corporation_forms = []
        for sender_corporation in letter.sendercorporation_relations.all():
            prefix = f'sender_corporation_{sender_corporation.id}'
            sender_corporation_form = SenderCorporationForm(instance = sender_corporation, prefix = prefix)
            sender_corporation_forms.append(sender_corporation_form)

        receiver_corporation_forms = []
        for receiver_corporation in letter.receivercorporation_relations.all():
            prefix = f'receiver_corporation_{receiver_corporation.id}'
            receiver_corporation_form = ReceiverCorporationForm(instance = receiver_corporation, prefix = prefix)
            receiver_corporation_forms.append(receiver_corporation_form)

        sender_place_forms = []
        for sender_place in letter.senderplace_relations.all():
            prefix = f'sender_place_{sender_place.id}'
            sender_place_form = SenderPlaceForm(instance = sender_place, prefix = prefix)
            sender_place_forms.append(sender_place_form)

        receiver_place_forms = []
        for receiver_place in letter.receiverplace_relations.all():
            prefix = f'receiver_place_{receiver_place.id}'
            receiver_place_form = ReceiverPlaceForm(instance = receiver_place, prefix = prefix)
            receiver_place_forms.append(receiver_place_form)

        letter_digitized_copy_forms = []
        for digital_copy in letter.digital_copies.all():
            prefix = f'letter_digcopy_{digital_copy.id}'
            letter_digitized_copy_form = LetterDigitizedCopyForm(instance = digital_copy, prefix = prefix)
            letter_digitized_copy_forms.append(letter_digitized_copy_form)

        # Search forms
        q_sender_person = request.GET.get('sender_person-q')
        q_receiver_person = request.GET.get('receiver_person-q')
        q_sender_corporation = request.GET.get('sender_corporation-q')
        q_receiver_corporation = request.GET.get('receiver_corporation-q')
        q_sender_place = request.GET.get('sender_place-q')
        q_receiver_place = request.GET.get('receiver_place-q')
        q_edition = request.GET.get('edition-q')

        if q_sender_person:
            sender_person_search_form = SearchForm(request.GET, prefix='sender_person')
            if sender_person_search_form.is_valid():
                context['query_sender_person'] = sender_person_search_form.cleaned_data.get('q')
                context['found_sender_persons'] = sender_person_search_form.search().models(Person)
        else:
            sender_person_search_form = SearchForm(prefix='sender_person')

        if q_receiver_person:
            receiver_person_search_form = SearchForm(request.GET, prefix='receiver_person')
            if receiver_person_search_form.is_valid():
                context['query_receiver_person'] = receiver_person_search_form.cleaned_data.get('q')
                context['found_receiver_persons'] = receiver_person_search_form.search().models(Person)
        else:
            receiver_person_search_form = SearchForm(prefix='receiver_person')

        if q_sender_corporation:
            sender_corporation_search_form = SearchForm(request.GET, prefix='sender_corporation')
            if sender_corporation_search_form.is_valid():
                context['query_sender_corporation'] = sender_corporation_search_form.cleaned_data.get('q')
                context['found_sender_corporations'] = sender_corporation_search_form.search().models(Corporation)
        else:
            sender_corporation_search_form = SearchForm(prefix='sender_corporation')

        if q_receiver_corporation:
            receiver_corporation_search_form = SearchForm(request.GET, prefix='receiver_corporation')
            if receiver_corporation_search_form.is_valid():
                context['query_receiver_corporation'] = receiver_corporation_search_form.cleaned_data.get('q')
                context['found_receiver_corporations'] = receiver_corporation_search_form.search().models(Corporation)
        else:
            receiver_corporation_search_form = SearchForm(prefix='receiver_corporation')

        if q_sender_place:
            sender_place_search_form = SearchForm(request.GET, prefix='sender_place')
            if sender_place_search_form.is_valid():
                context['query_sender_place'] = sender_place_search_form.cleaned_data.get('q')
                context['found_sender_places'] = sender_place_search_form.search().models(Place)
        else:
            sender_place_search_form = SearchForm(prefix='sender_place')

        if q_receiver_place:
            receiver_place_search_form = SearchForm(request.GET, prefix='receiver_place')
            if receiver_place_search_form.is_valid():
                context['query_receiver_place'] = receiver_place_search_form.cleaned_data.get('q')
                context['found_receiver_places'] = receiver_place_search_form.search().models(Place)
        else:
            receiver_place_search_form = SearchForm(prefix='receiver_place')

        if q_edition:
            edition_search_form = SearchForm(request.GET, prefix='edition')
            if edition_search_form.is_valid():
                context['query_edition'] = edition_search_form.cleaned_data.get('q')
                context['found_editions'] = edition_search_form.search().models(ZotItem)
        else:
            edition_search_form = SearchForm(prefix='edition')

        context.update({
                'form': form,
                'edition_period_form': edition_period_form,
                'source_period_form': source_period_form,
                'sender_person_forms': sender_person_forms,
                'receiver_person_forms': receiver_person_forms,
                'sender_corporation_forms': sender_corporation_forms,
                'receiver_corporation_forms': receiver_corporation_forms,
                'sender_place_forms': sender_place_forms,
                'receiver_place_forms': receiver_place_forms,
                'letter_mentioning_forms': letter_mentioning_forms,
                'letter_signature_forms': letter_signature_forms,
                'letter_digitized_copy_forms': letter_digitized_copy_forms
            })

        return render(request, 'edwoca/letter_update.html', context)


def letter_add_sender_person(request, pk, person_id):
    letter = get_object_or_404(Letter, pk=pk)
    person = get_object_or_404(Person, pk=person_id)
    letter.sender_person = person
    letter.save()
    return redirect('edwoca:letter_update', pk=pk)


def letter_remove_sender_person(request, pk):
    letter = get_object_or_404(Letter, pk=pk)
    letter.sender_person = None
    letter.save()
    return redirect('edwoca:letter_update', pk=pk)


def letter_add_receiver_person(request, pk, person_id):
    letter = get_object_or_404(Letter, pk=pk)
    person = get_object_or_404(Person, pk=person_id)
    letter.receiver_person = person
    letter.save()
    return redirect('edwoca:letter_update', pk=pk)


def letter_remove_receiver_person(request, pk):
    letter = get_object_or_404(Letter, pk=pk)
    letter.receiver_person = None
    letter.save()
    return redirect('edwoca:letter_update', pk=pk)


def letter_add_sender_corporation(request, pk, corporation_id):
    letter = get_object_or_404(Letter, pk=pk)
    corporation = get_object_or_404(Corporation, pk=corporation_id)
    letter.sender_corporation = corporation
    letter.save()
    return redirect('edwoca:letter_update', pk=pk)


def letter_remove_sender_corporation(request, pk):
    letter = get_object_or_404(Letter, pk=pk)
    letter.sender_corporation = None
    letter.save()
    return redirect('edwoca:letter_update', pk=pk)


def letter_add_receiver_corporation(request, pk, corporation_id):
    letter = get_object_or_404(Letter, pk=pk)
    corporation = get_object_or_404(Corporation, pk=corporation_id)
    letter.receiver_corporation = corporation
    letter.save()
    return redirect('edwoca:letter_update', pk=pk)


def letter_remove_receiver_corporation(request, pk):
    letter = get_object_or_404(Letter, pk=pk)
    letter.receiver_corporation = None
    letter.save()
    return redirect('edwoca:letter_update', pk=pk)


def letter_add_sender_place(request, pk, place_id):
    letter = get_object_or_404(Letter, pk=pk)
    place = get_object_or_404(Place, pk=place_id)
    letter.sender_place = place
    letter.save()
    return redirect('edwoca:letter_update', pk=pk)


def letter_remove_sender_place(request, pk):
    letter = get_object_or_404(Letter, pk=pk)
    letter.sender_place = None
    letter.save()
    return redirect('edwoca:letter_update', pk=pk)


def letter_add_receiver_place(request, pk, place_id):
    letter = get_object_or_404(Letter, pk=pk)
    place = get_object_or_404(Place, pk=place_id)
    letter.receiver_place = place
    letter.save()
    return redirect('edwoca:letter_update', pk=pk)


def letter_remove_receiver_place(request, pk):
    letter = get_object_or_404(Letter, pk=pk)
    letter.receiver_place = None
    letter.save()
    return redirect('edwoca:letter_update', pk=pk)


def letter_add_edition(request, pk, zotitem_id):
    letter = get_object_or_404(Letter, pk=pk)
    zotitem = get_object_or_404(ZotItem, pk=zotitem_id)
    letter.edition.add(zotitem)
    return redirect('edwoca:letter_update', pk=pk)


def letter_remove_edition(request, pk, zotitem_id):
    letter = get_object_or_404(Letter, pk=pk)
    zotitem = get_object_or_404(ZotItem, pk=zotitem_id)
    letter.edition.remove(zotitem)
    return redirect('edwoca:letter_update', pk=pk)
