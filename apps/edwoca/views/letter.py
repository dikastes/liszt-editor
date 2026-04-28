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
    LetterMentioningFormSet = inlineformset_factory(Letter, LetterMentioning, form=LetterMentioningForm, extra=0)
    context = {
        'object': letter,
        'entity_type': 'letter'
    }

    if request.method == 'POST':
        form = LetterForm(request.POST, instance=letter)
        edition_period_form = LetterEditionPeriodForm(request.POST, instance=letter)
        source_period_form = LetterSourcePeriodForm(request.POST, instance=letter)
        letter_mentioning_forms = []
        for letter_mentioning in letter.lettermentioning_set.all():
            prefix = f'letter_mentioning_{letter_mentioning.id}'
            letter_mentioning_form = LetterMentioningForm(
                    request.POST,
                    instance = letter_mentioning,
                    prefix = prefix
                )
            letter_mentioning_forms.append(letter_mentioning_form)
            if letter_mentioning_form.is_valid():
                letter_mentioning_form.save()

        if all([form.valid(), edition_period_form.valid(), source_period_form.valid()]):
            form.save()
            edition_period_form.save()
            source_period_form.save()
        else:
            context = {
                    'form': form,
                    'edition_period_form': edition_period_form,
                    'edition_source_form': edition_source_form
                }
            return render_to_response('edwoca/letter_update.html', context)

    else:
        form = LetterForm(instance=letter)
        letter_mentioning_forms = []
        edition_period_form = LetterEditionPeriodForm(request.POST, instance=letter)
        source_period_form = LetterSourcePeriodForm(request.POST, instance=letter)
        for letter_mentioning in letter.lettermentioning_set.all():
            prefix = f'letter_mentioning_{letter_mentioning.id}'
            letter_mentioning_forms.append(
                LetterMentioningForm(
                    instance = letter_mentioning,
                    prefix = prefix
                ))

    context['form'] = form
    context['letter_mentioning_forms'] = letter_mentioning_forms

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

    context['sender_person_search_form'] = sender_person_search_form
    context['receiver_person_search_form'] = receiver_person_search_form
    context['sender_corporation_search_form'] = sender_corporation_search_form
    context['receiver_corporation_search_form'] = receiver_corporation_search_form
    context['sender_place_search_form'] = sender_place_search_form
    context['receiver_place_search_form'] = receiver_place_search_form
    context['edition_search_form'] = edition_search_form

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
