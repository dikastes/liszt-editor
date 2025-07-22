from .base import *
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q, UniqueConstraint
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
            max_length=20,
            null = True,
            blank = True
        )

    def __str__(self):
        #title = self.get_pref_title() or '<ohne Titel>'
        #return f'{self.rism_id}: {title}'
        return self.get_current_signature().__str__()

    def get_current_signature(self):
        return next(self.signatures.filter(status = Signature.Status.CURRENT).iterator(), 'ohne Signatur')

    def save(self, *args, **kwargs):
        if self.manifestation.is_singleton and self.manifestation.items.exclude(pk=self.pk).exists():
            raise ValidationError("Cannot add another item to a singleton manifestation.")
        super().save(*args, **kwargs)


class Library(models.Model):
    name = models.CharField(
            unique=True,
            max_length=100,
            null = True,
            blank = True
        )
    siglum = models.CharField(
            unique=True,
            max_length=20,
            null = True,
            blank = True
        )

    def get_absolute_url(self):
        return reverse('edwoca:library_update', kwargs = {'pk' : self.id})

    def __str__(self):
        return f"{self.name} ({self.siglum})"


class Signature(models.Model):
    class Status(models.TextChoices):
        CURRENT = 'C', _('Current')
        FORMER = 'F', _('Former')

    item = models.ForeignKey(
            'Item',
            on_delete = models.CASCADE,
            related_name = 'signatures',
            null = True
        )
    library = models.ForeignKey(
            'Library',
            on_delete = models.SET_NULL,
            related_name = 'signatures',
            null = True
        )
    signature = models.CharField(
            max_length=20,
            null = True,
            blank = True
        )
    status = models.CharField(
            max_length=1,
            choices=Status,
            default=Status.CURRENT
        )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['item'],
                condition=Q(status='C'),
                name='unique_current_signature'
            )
        ]

    def __str__(self):
        return f"{self.library.siglum} {self.signature}"


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
        related_name='contributor_relations'
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
