from django.utils.translation import gettext_lazy as _
from dmad_on_django.models.base import DocumentationStatusMixin
from django.db.models import OuterRef, Subquery, Value, Case, When, CharField
from django.db.models.functions import Coalesce, Lower, NullIf, Concat, StrIndex, Substr, Length, LPad
from dmrism.models import TrackedModel, BaseBib
from .base import *
from bib.models import ZotItem
from liszt_util.tools import DisplayableQuerySet


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


class Letter(TrackedModel):
    class Category(models.TextChoices):
        SKETCH = 'S', _('Sketch')
        LETTER = 'L', _('Letter')
        POSTCARD = 'P', _('Postcard')
        COPY = 'C', _('Copy')

    class Meta:
        ordering = ['-needs_review', 'edition_period__not_before']

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
    work_mentionings = models.TextField(
            null = True,
            blank = True,
            verbose_name = _('work mentionings')
        )
    work = models.ManyToManyField(
            'Work',
            related_name = 'letters'
        )
    item = models.ManyToManyField(
            'Item',
            related_name = 'letters'
        )
    manifestation = models.ManyToManyField(
            'Manifestation',
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

    objects = DisplayableQuerySet.as_manager()

    ordering_fields = {
        'sort_edition': (['sort_edition'], _('letter edition'), _('A-Z'), _('Z-A'))
    }

    @classmethod
    def get_ordering_annotations(cls):
        location_type_choices = LetterMentioning._meta.get_field('location_type').choices or []
        location_type_display_cases = [
            When(location_type=val, then=Value(str(label)))
            for val, label in location_type_choices
        ]
        location_type_label = Case(
            *location_type_display_cases,
            default='location_type'
        )
        dash_pos = StrIndex('location', Value('-'))

        first_num_str = Case(
            When(
                location__contains='-',
                then=Substr('location', 1, dash_pos - 1)
            ),
            default='location',
            output_field=CharField()
        )

        rest_str = Case(
            When(
                location__contains='-',
                then=Substr('location', dash_pos)
            ),
            default=Value(''),
            output_field=CharField()
        )

        padded_location = Concat(
            LPad(first_num_str, 5, Value('0')),
            rest_str,
            output_field=CharField()
        )

        first_mentioning = Subquery(
                LetterMentioning.objects.filter(
                        letter = OuterRef('pk')
                    ).order_by('id').annotate(
                        str_repr=Case(
                            When(
                                location__isnull=False,
                                location__gt='',
                                then=Concat(
                                    'bib__zot_short_title',
                                    Value(', '),
                                    location_type_label,
                                    Value(' '),
                                    padded_location,
                                    output_field=CharField()
                                )
                            ),
                            default='bib__zot_short_title',
                            output_field=CharField()
                        )
                    ).values('str_repr')[:1]
            )
        return {
            'sort_edition': Lower(
                Coalesce(
                    NullIf(first_mentioning, Value('')),
                    Value('zzz')
                )
            ),
        }

    def get_first_mentioning(self):
        if self.lettermentioning_set.all():
            return str(self.lettermentioning_set.first())
        no_proof = _('no proof')
        return f'<{no_proof}>'

    def get_absolute_url(self):
        return reverse('edwoca:letter_update', kwargs={'pk': self.id})

    def __str__(self):
        return self.title_body

    @property
    def title_body(self):
        unknown = _('unknown')
        to = _('writing to')
        etal = ' ' + _('et al.')
        if self.sender_persons.count():
            if self.sender_corporations.count() or self.sender_persons.count() > 1:
                sender = self.sender_persons.first().get_natural_name() + etal
            else:
                sender = self.sender_persons.first().get_natural_name()
        else:
            if self.sender_corporations.count():
                if self.sender_corporations.count() > 1:
                    sender = self.sender_corporations.first().get_designator() + etal
                else:
                    sender = self.sender_corporations.first().get_designator()
            else:
                sender = unknown

        if self.receiver_persons.count():
            if self.receiver_corporations.count() or self.receiver_persons.count() > 1:
                receiver = self.receiver_persons.first().get_natural_name() + etal
            else:
                receiver = self.receiver_persons.first().get_natural_name()
        else:
            if self.receiver_corporations.count():
                if self.receiver_corporations.count() > 1:
                    receiver = self.receiver_corporations.first().get_designator() + etal
                else:
                    receiver = self.receiver_corporations.first().get_designator()
            else:
                receiver = unknown

        return self.mark_needs_review(f'{sender} {to} {receiver}, {self.edition_period} ({self.get_first_mentioning()})')


class LetterMentioning(BaseBib):
    letter = models.ForeignKey(
            'Letter',
            on_delete = models.CASCADE
        )
    letter_number = models.CharField(
            max_length = 20,
            null = True,
            blank = True,
            verbose_name = _('letter number')
        )

    def __str__(self):
        if self.location:
            return f'{self.bib.zot_short_title}, {self.get_location_type_display()} {self.location}'
        return self.bib.zot_short_title


class DocumentedEntityName(DocumentationStatusMixin):
    name = models.CharField(
            max_length = 100,
            blank = True
        )


class BaseLetterContributor(DocumentationStatusMixin):
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
