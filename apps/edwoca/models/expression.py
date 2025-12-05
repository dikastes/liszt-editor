from .base import *
from django.db import models
from django.db.models import Max
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from dmad_on_django.models import Status
from liszt_util.models import Sortable
from dmrism.models import BaseContributor, BaseBib, RelatedEntity, BasePersonDedication, BaseCorporationDedication

class Expression(Sortable,WeBaseClass):
    work_catalog_number = models.CharField(
            max_length=20,
            unique=True,
            null=True,
            blank=True,
            verbose_name=_('work catalog number')
        )
    incipit_music = models.TextField(
        verbose_name=_('incipit music')
    )
    incipit_text = models.TextField(
        verbose_name=_('incipit text')
    )
    period = models.OneToOneField(
            'dmad.Period',
            on_delete=models.SET_NULL,
            null = True,
            blank = True,
            related_name = 'expression'
        )
    period_comment = models.TextField(
        verbose_name=_('period comment')
    )
    history = models.TextField(
        verbose_name=_('history')
    )
    contributors = models.ManyToManyField(
            'dmad.Person',
            through = 'ExpressionContributor'
        )
    work = models.ForeignKey(
            'Work',
            on_delete=models.CASCADE,
            null=True,
            blank=True,
            related_name='expressions'
        )
    related_expressions = models.ManyToManyField(
            'Expression',
            through='RelatedExpression'
        )
    manifestations = models.ManyToManyField(
            'Manifestation',
            related_name = 'expressions'
        )

    _group_field_name = 'work'

    def __str__(self):
        #return ' | '.join(str(index_number) for index_number in self.index_numbers.all()) or 'ohne WV-Nr.'
        if temp_titles := self.titles.filter(status = Status.TEMPORARY):
            return temp_titles.first().title
        return '<ohne Titel>'

    def save(self, *args, **kwargs):

        if self.pk is None:
            max_index = (
                Expression.objects
                .filter(work=self.work)
                .aggregate(Max('order_index'))['order_index__max']
            )

            if max_index is not None:
                self.order_index = max_index+1
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['work', 'order_index']
        unique_together = ('work', 'order_index')

class ExpressionTitle(WemiTitle):
    expression = models.ForeignKey(
            'Expression',
            on_delete=models.CASCADE,
            related_name='titles'
        )


class RelatedExpression(RelatedEntity):
    class Label(models.TextChoices):
        IS_COMPONENT_OF = 'CP', _('is componnt of'),
        IS_PART_OF = 'PA', _('is part of'),
        IS_DERIVATIVE_OF = 'DE', _('is derivative of')
        IS_INCORPORATED_IN = 'IN', _('is incorporated in')
        HAS_ALTERNATIVE = 'AL', _('has alternative')

    label = models.CharField(
            max_length = 2,
            choices = Label,
            default = Label.IS_PART_OF,
            verbose_name = _('label')
            )
    source_expression = models.ForeignKey(
            'Expression',
            on_delete=models.CASCADE,
            related_name="source_expression_of"
        )
    target_expression = models.ForeignKey(
            'Expression',
            on_delete=models.CASCADE,
            related_name="target_expression_of"
        )


class ExpressionContributor(BaseContributor):
    expression = models.ForeignKey(
        'Expression',
        on_delete=models.CASCADE,
        related_name='contributor_relations'
    )


class Metronom(models.Model):
    class Value(models.TextChoices):
        EIGHTH = '1/8', _('1/8')
        QUARTER = '1/4', _('1/4')
        DOTTED_QUARTER = '1/4.', _('1/4.')
        HALF = '1/2', _('1/2')
        DOTTED_HALF = '1/2.', _('1/2.')

    expression = models.ForeignKey(
            'Expression',
            on_delete=models.CASCADE,
            null=True,
            blank=True,
            related_name='metronom'
        )
    reference_value = models.CharField(
            max_length=4,
            choices=Value,
            default=Value.QUARTER,
            verbose_name=_('reference value')
        )
    bpm = models.IntegerField(
            null = True,
            blank = True,
            verbose_name=_('bpm')
        )


class Movement(models.Model):
    expression = models.ForeignKey(
            'Expression',
            on_delete=models.CASCADE,
            null=True,
            blank=True,
            related_name='movements'
        )
    title = models.CharField(
            max_length=100,
            unique=True,
            null=True,
            blank=True,
            verbose_name=_('title')
        )
    tempo = models.CharField(
            max_length=10,
            unique=True,
            null=True,
            blank=True,
            verbose_name=_('tempo')
        )
    meter = models.CharField(
            max_length=10,
            unique=True,
            null=True,
            blank=True,
            verbose_name=_('meter')
        )


class IndexNumber(models.Model):
    class Indexes(models.TextChoices):
        RAABE = 'RAABE', _('Raabe')
        MULLER = 'MULLER', _('Müller/Eckhardt')
        SEARLE = 'SEARLE', _('Searle')
        CHIAPPARI = 'CHIAPPARI', _('Chiappari')
        LQWV = 'LQWV', _('LQWV')

    expression = models.ForeignKey(
            'Expression',
            on_delete=models.CASCADE,
            null=True,
            blank=True,
            related_name='index_numbers'
        )
    index = models.CharField(
            max_length=10,
            choices=Indexes,
            default=Indexes.LQWV,
            verbose_name=_('index')
        )
    number = models.CharField(
            max_length=10,
            null=True,
            blank=True,
            verbose_name=_('number')
        )

    def __str__(self):
        return f"{self.index}: {self.number}"


class Key(models.Model):
    class Mode(models.TextChoices):
        MAJOR = 'MA', _('Major')
        MINOR = 'MI', _('Minor')

    class Note(models.TextChoices):
        A = 'A', _('A')
        B = 'B', _('B')
        C = 'C', _('C')
        D = 'D', _('D')
        E = 'E', _('e')
        F = 'F', _('F')
        G = 'G', _('G')

    class Acc(models.TextChoices):
        NULL = '', ''
        SHARP = '#', _('#')
        DOUBLE_SHARP = '##', _('##')
        FLAT = 'b', _('b')
        DOUBLE_FLAT = 'bb', _('bb')

    movement = models.OneToOneField(
            'Movement',
            on_delete=models.CASCADE,
            null = True,
            blank = True,
            related_name = 'key'
        )
    note = models.CharField(
            max_length=1,
            choices=Note,
            default=Note.C,
            verbose_name=_('note')
        )
    accidental = models.CharField(
            max_length=2,
            choices=Acc,
            default=Acc.NULL,
            verbose_name=_('accidental')
        )
    mode = models.CharField(
            max_length=2,
            choices=Mode,
            default=Mode.MAJOR,
            verbose_name=_('mode')
        )


class ExpressionPersonDedication(BasePersonDedication):
    expression = models.ForeignKey(
            'Expression',
            on_delete = models.CASCADE
        )


class ExpressionCorporationDedication(BaseCorporationDedication):
    expression = models.ForeignKey(
            'Expression',
            on_delete = models.CASCADE
        )
