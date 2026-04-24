from django.utils.translation import gettext_lazy as _
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

    edition_receiver_person = models.ManyToManyField(
            'dmad.Person',
            through = 'EditionReceiverPerson',
            related_name = 'edition_receiver_of'
        )
    source_receiver_person = models.ManyToManyField(
            'dmad.Person',
            through = 'SourceReceiverPerson',
            related_name = 'source_receiver_of'
        )
    edition_sender_person = models.ManyToManyField(
            'dmad.Person',
            through = 'EditionSenderPerson',
            related_name = 'edition_sender_of'
        )
    source_sender_person = models.ManyToManyField(
            'dmad.Person',
            through = 'SourceSenderPerson',
            related_name = 'source_sender_of'
        )
    edition_receiver_corporation = models.ManyToManyField(
            'dmad.Corporation',
            through = 'EditionReceiverCorporation',
            related_name = 'edition_receiver_of'
        )
    source_receiver_corporation = models.ManyToManyField(
            'dmad.Corporation',
            through = 'SourceReceiverCorporation',
            related_name = 'source_receiver_of'
        )
    edition_sender_corporation = models.ManyToManyField(
            'dmad.Corporation',
            through = 'EditionSenderCorporation',
            related_name = 'edition_sender_of'
        )
    source_sender_corporation = models.ManyToManyField(
            'dmad.Corporation',
            through = 'SourceSenderCorporation',
            related_name = 'source_sender_of'
        )
    receiver_place = models.ManyToManyField(
            'dmad.Place',
            through = 'ReceiverPlace',
            related_name = 'receiver_place_of'
        )
    sender_place = models.ManyToManyField(
            'dmad.Place',
            through = 'SenderPlace',
            related_name = 'sender_place_of'
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
    comment = models.TextField(
            null = True,
            blank = True,
            verbose_name = _('comment')
        )
    work = models.ManyToManyField(
            'Work',
            related_name = 'letters'
        )
    manifestation = models.ManyToManyField(
            'Manifestation',
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
    diplomatic_date = models.CharField(
            max_length = 100,
            blank = True,
            verbose_name = _('diplomatic date on source')
        )
    source_period = models.CharField(
            'dmad.Period',
            null = True,
            blank = True
        )

    def get_first_mentioning(self):
        if self.lettermentioning_set.all():
            return str(self.lettermentioning_set.first())
        return f'<{_("no proof")}>'

    def get_absolute_url(self):
        return reverse('edwoca:letter_update', kwargs={'pk': self.id})

    def __str__(self):
        if self.sender_person:
            if self.sender_corporation:
                sender = self.sender_person.get_default_name() + ' u. a.'
            else:
                sender = self.sender_person.get_default_name()
        else:
            if self.sender_corporation:
                sender = self.sender_corporation.get_default_name()
            else:
                sender = 'unbekannt'

        if self.receiver_person:
            if self.receiver_corporation:
                receiver = self.receiver_person.get_default_name() + ' u. a.'
            else:
                receiver = self.receiver_person.get_default_name()
        else:
            if self.receiver_corporation:
                receiver = self.receiver_corporation.get_default_name()
            else:
                receiver = 'unbekannt'

        return f'{sender} an {receiver}, {self.period} ({self.get_first_mentioning()})'


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


class BaseLetterPlace(models.Model):
    class Meta:
        abstract = True

    letter = models.ForeignKey(
            'Letter',
            on_delete = models.CASCADE,
            related_name = '%(class)s'
        )


class SenderPlace(BaseLetterPlace):
    place = models.ForeignKey(
            'dmad.Place',
            on_delete = models.CASCADE,
            related_name = '+'
        )


class ReceiverPlace(BaseLetterPlace):
    place = models.ForeignKey(
            'dmad.Place',
            on_delete = models.CASCADE,
            related_name = '+'
        )


class BaseLetterContributor(models.Model):
    class Meta:
        abstract = True

    letter = models.ForeignKey(
            'Letter',
            on_delete = models.CASCADE,
            related_name = '%(class)s'
        )
    # status


class EditionSenderPerson(BaseLetterContributor):
    edition_person = models.ForeignKey(
            'dmad.Person',
            on_delete = models.CASCADE,
            related_name = '+'
        )


class SourceSenderPerson(BaseLetterContributor):
    source_person = models.ForeignKey(
            'dmad.Person',
            on_delete = models.CASCADE,
            related_name = '+'
        )


class EditionReceiverPerson(BaseLetterContributor):
    edition_person = models.ForeignKey(
            'dmad.Person',
            on_delete = models.CASCADE,
            related_name = '+'
        )


class SourceReceiverPerson(BaseLetterContributor):
    source_person = models.ForeignKey(
            'dmad.Person',
            on_delete = models.CASCADE,
            related_name = '+'
        )


class EditionSenderCorporation(BaseLetterContributor):
    edition_corporation = models.ForeignKey(
            'dmad.Corporation',
            on_delete = models.CASCADE,
            related_name = '+'
        )


class SourceSenderCorporation(BaseLetterContributor):
    source_corporation = models.ForeignKey(
            'dmad.Corporation',
            on_delete = models.CASCADE,
            related_name = '+'
        )


class EditionReceiverCorporation(BaseLetterContributor):
    edition_corporation = models.ForeignKey(
            'dmad.Corporation',
            on_delete = models.CASCADE,
            related_name = '+'
        )


class SourceReceiverCorporation(BaseLetterContributor):
    source_corporation = models.ForeignKey(
            'dmad.Corporation',
            on_delete = models.CASCADE,
            related_name = '+'
        )

class BaseLetterPlace(models.Model):
    class Meta:
        abstract = True

    source_place_name = models.CharField(
            max_length = 50,
            blank = True,
            verbose_name = _('place according to edition')
        )
    edition_place_name = models.CharField(
            max_length = 50,
            blank = True,
            verbose_name = _('place according to edition')
        )
    # status source
    # status edition
