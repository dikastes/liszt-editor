from .base import *
from django.db import models
from dmrism.models import BaseBib
from django.utils.translation import gettext_lazy as _


class CompositeManifestationRelation(models.Model):
    composite = models.ForeignKey(
            'Composite',
            on_delete = models.CASCADE
        )
    manifestation = models.ForeignKey(
            'Manifestation',
            on_delete = models.CASCADE
        )


class CompositeItemRelation(models.Model):
    composite = models.ForeignKey(
            'Composite',
            on_delete = models.CASCADE
        )
    item = models.ForeignKey(
            'Item',
            on_delete = models.CASCADE
        )


class CompositeBibRelation(models.Model):
    composite = models.ForeignKey(
            'Composite',
            on_delete = models.CASCADE
        )
    bib = models.ForeignKey(
            'bib.ZotItem',
            on_delete = models.CASCADE
        )


class Composite(models.Model):
    period = models.OneToOneField(
            'dmad.Period',
            on_delete = models.SET_NULL,
            blank = True,
            null = True
        )
    places = models.ManyToManyField(
            'dmad.Place'
        )
    manifestations = models.ManyToManyField(
            'Manifestation',
            through = 'CompositeManifestationRelation',
            related_name = 'composites'
        )
    items = models.ManyToManyField(
            'Item',
            through = 'CompositeItemRelation',
            related_name = 'composites'
        )
    history = models.TextField(
            blank = True,
            null = True
        )
    bib = models.ManyToManyField(
            'bib.ZotItem',
            through = 'CompositeBibRelation',
            related_name = 'composites'
        )
    private_head_comment = models.TextField(
            blank = True,
            null = True,
            verbose_name = _('private head comment')
        )
    private_relations_comment = models.TextField(
            blank = True,
            null = True
        )
    private_title_comment = models.TextField(
            blank = True,
            null = True
        )
    private_history_comment = models.TextField(
            blank = True,
            null = True
        )
    rism_id = models.CharField(
            max_length=20,
            null = True,
            blank = True
        )
    public_provenance_comment = models.TextField(
            blank = True,
            null = True
        )
    extent = models.TextField(
            blank = True,
            null = True
        )
    measure = models.TextField(
            blank = True,
            null = True
        )
    private_manuscript_comment = models.TextField(
            blank = True,
            null = True
        )


class CompositeTitle(WemiTitle):
    composite = models.ForeignKey(
            'Composite',
            on_delete=models.CASCADE,
            related_name='titles'
        )


class CompositeBib(BaseBib):
    composite = models.ForeignKey(
        'Composite',
        on_delete=models.CASCADE,
        related_name='bib_set'
    )


