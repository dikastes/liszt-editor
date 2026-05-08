from django.utils.translation import gettext_lazy as _
from dmad_on_django.models.base import DocumentationStatusMixin
from .base import *


class LetterSignature(BaseSignature):
    letter = models.ForeignKey(
            'Letter',
            on_delete = models.CASCADE,
            related_name = 'signatures'
        )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['letter'],
                condition=Q(status='C'),
                name='unique_current_letter_signature'
            )
        ]


class LetterDigitalCopy(BaseDigitalCopy):
    letter = models.ForeignKey(
            'Letter',
            on_delete = models.CASCADE,
            related_name = 'digital_copies'
        )


class Letter(models.Model):
    class Category(models.TextChoices):
        SKETCH = 'S', _('Sketch')
        LETTER = 'L', _('Letter')
        POSTCARD = 'P', _('Postcard')
        COPY = 'C', _('Copy')

    class Meta:
        ordering = ['edition_period__not_before']

    receiver_persons = models.ManyToManyField(
            'dmad.Person',
            through = 'ReceiverPerson',
            related_name = 'edition_receiver_of',
            verbose_name = _('receiver person')
        )
    sender_persons = models.ManyToManyField(
            'dmad.Person',
            through = 'SenderPerson',
            related_name = 'edition_sender_of',
            verbose_name = _('sender person')
        )
    receiver_corporations = models.ManyToManyField(
            'dmad.Corporation',
            through = 'ReceiverCorporation',
            related_name = 'edition_receiver_of',
            verbose_name = _('receiver corporation')
        )
    sender_corporations = models.ManyToManyField(
            'dmad.Corporation',
            through = 'SenderCorporation',
            related_name = 'edition_sender_of',
            verbose_name = _('sender corporation')
        )
    receiver_places = models.ManyToManyField(
            'dmad.Place',
            through = 'ReceiverPlace',
            related_name = 'receiver_place_of',
            verbose_name = _('receiver place')
        )
    sender_places = models.ManyToManyField(
            'dmad.Place',
            through = 'SenderPlace',
            related_name = 'sender_place_of',
            verbose_name = _('sender place')
        )
    edition_period = models.OneToOneField(
            'dmad.Period',
            on_delete=models.SET_NULL,
            null = True,
            blank = True,
            related_name = 'edition_date_for_letter'
        )
    edition = models.ManyToManyField(
            'bib.ZotItem',
            related_name = 'edited_letters',
            through = 'LetterMentioning'
        )
    category = models.CharField(
            max_length = 1,
            choices = Category,
            default = Category.LETTER,
            verbose_name = _('category')
        )
    mentioned_works = models.TextField(
            null = True,
            blank = True,
            verbose_name = _('comment')
        )
    comment = models.TextField(
            null = True,
            blank = True,
            verbose_name = _('comment')
        )
    work = models.ManyToManyField(
            'Work',
            related_name = 'letters'
        )
    expression = models.ManyToManyField(
            'Expression',
            related_name = 'letters'
        )
    person_provenance = models.ManyToManyField(
            'dmrism.PersonProvenanceStation',
            related_name = 'letters'
        )
    corporation_provenance = models.ManyToManyField(
            'dmrism.CorporationProvenanceStation',
            related_name = 'letters'
        )
    diplomatic_source_date = models.CharField(
            max_length = 100,
            blank = True,
            verbose_name = _('diplomatic date on source')
        )
    source_period = models.ForeignKey(
            'dmad.Period',
            null = True,
            on_delete = models.SET_NULL
        )
    sender_edition_corporation_name = models.CharField(
            max_length = 50,
            blank = True,
            verbose_name = _('sender corporation name according to edition')
        )
    sender_source_corporation_name = models.CharField(
            max_length = 50,
            blank = True,
            verbose_name = _('sender corporation name according to source')
        )

    def get_first_mentioning(self):
        if self.lettermentioning_set.all():
            return str(self.lettermentioning_set.first())
        return f'<{_("no proof")}>'

    def get_absolute_url(self):
        return reverse('edwoca:letter_update', kwargs={'pk': self.id})

    def __str__(self):
        unknown = _('unknown')
        to = _('writing to')
        etal = ' ' + _('et al.')
        if self.sender_persons.count():
            if self.sender_corporations or self.sender_persons.count() > 1:
                sender = self.sender_persons.first().get_default_name() + etal
            else:
                sender = self.sender_persons.first().get_default_name()
        else:
            if self.sender_corporations.count():
                if self.sender_corporations.count() > 1:
                    sender = self.sender_corporations.first().get_default_name() + etal
                else:
                    sender = self.sender_corporations.first().get_default_name()
            else:
                sender = unknown

        if self.receiver_persons.count():
            if self.receiver_corporations or self.receiver_persons.count() > 1:
                receiver = self.receiver_persons.first().get_default_name() + etal
            else:
                receiver = self.receiver_persons.first().get_default_name()
        else:
            if self.receiver_corporations.count():
                if self.receiver_corporations.count() > 1:
                    receiver = self.receiver_corporations.first().get_default_name() + etal
                else:
                    receiver = self.receiver_corporations.first().get_default_name()
            else:
                receiver = unknown

        return f'{sender} {to} {receiver}, {self.source_period} ({self.get_first_mentioning()})'


class LetterMentioning(models.Model):
    letter = models.ForeignKey(
            'Letter',
            on_delete = models.CASCADE
        )
    bib = models.ForeignKey(
            'bib.ZotItem',
            on_delete = models.CASCADE
        )
    pages = models.CharField(
            max_length = 20,
            null = True,
            blank = True,
            verbose_name = _('pages')
        )

    def __str__(self):
        return f'{self.bib.zot_short_title}, {self.pages}'


class DocumentedEntityName(DocumentationStatusMixin):
    name = models.CharField(
            max_length = 100,
            blank = True
        )


class BaseLetterContributor(models.Model):
    class Meta:
        abstract = True

    letter = models.ForeignKey(
            'Letter',
            on_delete = models.CASCADE,
            related_name = '%(class)s_relations'
        )
    edition_name = models.OneToOneField(
            'DocumentedEntityName',
            null = True,
            on_delete = models.SET_NULL,
            related_name = '+',
            blank = True
        )
    source_name = models.OneToOneField(
            'DocumentedEntityName',
            null = True,
            on_delete = models.SET_NULL,
            related_name = '+',
            blank = True
        )


class SenderPlace(BaseLetterContributor):
    place = models.ForeignKey(
            'dmad.Place',
            on_delete = models.SET_NULL,
            null = True,
            related_name = '+'
        )


class ReceiverPlace(BaseLetterContributor):
    place = models.ForeignKey(
            'dmad.Place',
            on_delete = models.SET_NULL,
            null = True,
            related_name = '+'
        )


class SenderPerson(BaseLetterContributor):
    person = models.ForeignKey(
            'dmad.Person',
            on_delete = models.SET_NULL,
            null = True,
            related_name = '+'
        )


class ReceiverPerson(BaseLetterContributor):
    person = models.ForeignKey(
            'dmad.Person',
            on_delete = models.SET_NULL,
            null = True,
            related_name = '+'
        )


class SenderCorporation(BaseLetterContributor):
    corporation = models.ForeignKey(
            'dmad.Corporation',
            on_delete = models.SET_NULL,
            null = True,
            related_name = '+'
        )


class ReceiverCorporation(BaseLetterContributor):
    corporation = models.ForeignKey(
            'dmad.Corporation',
            on_delete = models.SET_NULL,
            null = True,
            related_name = '+'
        )
