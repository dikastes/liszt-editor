from .base import *
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from dmad_on_django.models import Status


class Item(WemiBaseClass):
    cover = models.TextField(
            null = True,
            blank = True
        )
    handwriting = models.CharField(
            max_length=20,
            null=True,
            blank=True
        )
    location = models.TextField(
            null = True,
            blank = True
        )
    iiif_manifest = models.URLField(
            null = True,
            blank = True
        )
    manifestation = models.ForeignKey(
            'Manifestation',
            on_delete = models.CASCADE,
            related_name = 'items'
        )
    rism_id = models.CharField(
            unique=True,
            max_length=20,
            null = True,
            blank = True
        )

    def __str__(self):
        title = self.get_pref_title() or '<ohne Titel>'
        return f'{self.rism_id}: {title}'


class ItemTitle(WemiTitle):
    item = models.ForeignKey('Item', on_delete=models.CASCADE, related_name='titles')


class RelatedItem(RelatedEntity):
    source_item = models.ForeignKey(
            'Item',
            on_delete=models.CASCADE,
            related_name="source_item_of"
        )
    target_item = models.ForeignKey(
            'Item',
            on_delete=models.CASCADE,
            related_name="target_item_of"
        )


class ItemContributor(BaseContributor):
    item = models.ForeignKey(
        'Item',
        on_delete=models.CASCADE,
        #related_name='contributors'
    )


class ProvenanceState(models.Model):
    owner = models.ForeignKey(
            'dmad.Person',
            on_delete = models.CASCADE
        )
    item = models.ForeignKey(
            'Item',
            on_delete = models.CASCADE,
            related_name = 'provenance'
        )
    comment = models.TextField(
            null = True,
            blank = True
        )
    start = models.ForeignKey(
            'dmad.Period',
            on_delete = models.SET_NULL,
            blank = True,
            null = True,
            related_name = 'provenance_start'
            )
    end = models.ForeignKey(
            'dmad.Period',
            on_delete = models.SET_NULL,
            blank = True,
            null = True,
            related_name = 'provenance_end'
            )

    def __str__(self):
        return f"{ self.owner } (von { self.start } bis { self.end })"
