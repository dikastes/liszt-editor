from .base import *
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from dmad_on_django.models import Status
from dmrism.models import BaseContributor, BaseBib, RelatedEntity


class Expression(WeBaseClass):
    work_catalog_number = models.CharField(
            max_length=20,
            unique=True,
            null=True,
            blank=True
        )
    incipit_music = models.TextField()
    incipit_text = models.TextField()
    period = models.OneToOneField(
            'dmad.Period',
            on_delete=models.SET_NULL,
            null = True,
            blank = True,
            related_name = 'expression'
        )
    period_comment = models.TextField()
    history = models.TextField()
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
            'dmrism.Manifestation'
        )

    def __str__(self):
        if self.get_pref_title():
            return self.get_pref_title()
        return '<ohne Titel>'


class ExpressionTitle(WemiTitle):
    expression = models.ForeignKey(
            'Expression',
            on_delete=models.CASCADE,
            related_name='titles'
        )


class RelatedExpression(RelatedEntity):
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
            default=Value.QUARTER
        )
    bpm = models.IntegerField(
            null = True,
            blank = True
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
            blank=True
        )
    tempo = models.CharField(
            max_length=10,
            unique=True,
            null=True,
            blank=True
        )
    meter = models.CharField(
            max_length=10,
            unique=True,
            null=True,
            blank=True
        )


class IndexNumber(models.Model):
    class Indexes(models.TextChoices):
        RAABE = 'RAABE', _('Raabe')
        MULLER = 'MULLER', _('Müller/Eckhardt')
        SEARLE = 'SEARLE', _('Searle')
        CHIAPPARI = 'CHIAPPARI', _('Chiappari')

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
            default=Indexes.RAABE
        )
    number = models.CharField(
            max_length=10,
            null=True,
            blank=True
        )


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
        NULL = '', _('')
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
            default=Note.C
        )
    accidental = models.CharField(
            max_length=2,
            choices=Acc,
            default=Acc.NULL
        )
    mode = models.CharField(
            max_length=2,
            choices=Mode,
            default=Mode.MAJOR
        )
