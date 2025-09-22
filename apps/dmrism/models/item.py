from .base import *
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q, UniqueConstraint
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


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
    dedication = models.TextField(
            blank=True,
            null=True
        )
    dedicatees = models.ManyToManyField(
            'dmad.Person',
            related_name='item_dedicatees'
        )
    private_dedication_comment = models.TextField(
            blank = True,
            null = True
        )
    private_provenance_comment = models.TextField(
            blank = True,
            null = True
        )
    public_provenance_comment = models.TextField(
            blank = True,
            null = True
        )
    is_template = models.BooleanField(default=False)


    def __str__(self):
        #title = self.get_pref_title() or '<ohne Titel>'
        #return f'{self.rism_id}: {title}'
        if self.manifestation.is_singleton:
            return self.manifestation.__str__()
        return self.get_current_signature()

    def get_siblings(self):
        return self.manifestation.items.exclude(id = self.id)

    def get_pref_title(self):
        return self.__str__()

    def signature_with_former(self):
        former_string = ''
        if self.signatures.filter(status = Signature.Status.FORMER):
            former_string = ', '.join(
                    former_signature.__str__() for 
                    former_signature in
                    self.signatures.filter(status = Signature.Status.FORMER)
                )
        return self.get_current_signature() + ', vormalig ' + former_string

    def get_current_signature(self):
        return next(self.signatures.filter(status = Signature.Status.CURRENT).iterator(), 'ohne Signatur').__str__()

    def save(self, *args, **kwargs):
        if self.manifestation.is_singleton and self.manifestation.items.count() > 1:
            raise ValidationError("Cannot add another item to a singleton manifestation.")
        super().save(*args, **kwargs)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['manifestation'],
                condition=models.Q(is_template=True),
                name='unique_template_item_per_manifestation'
            )
        ]


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
                name='unique_current_item_signature'
            )
        ]

    def __str__(self):
        return f"{self.library.siglum} {self.signature}"


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


class ProvenanceStationRenderMixin:
    def __str__(self):
        owner_string = self.owner or 'unbekannt'
        period_string = self.period or 'ohne Zeitraum'
        return f'{str(owner_string)} ({str(period_string)})'


class PersonProvenanceStation(ProvenanceStationRenderMixin, models.Model):
    item = models.ForeignKey(
            'Item',
            on_delete = models.CASCADE,
            related_name = 'person_provenance_stations'
        )
    owner = models.ForeignKey(
            'dmad.Person',
            on_delete = models.CASCADE,
            related_name = 'provenance_stations',
            null = True
        )
    bib = models.ForeignKey(
            'bib.ZotItem',
            on_delete = models.SET_NULL,
            related_name = 'person_provenance_stations',
            null = True,
            blank = True
        )
    period = models.ForeignKey(
            'dmad.Period',
            on_delete = models.SET_NULL,
            blank = True,
            null = True,
            related_name = 'person_provenance_stations'
            )


class CorporationProvenanceStation(ProvenanceStationRenderMixin, models.Model):
    item = models.ForeignKey(
            'Item',
            on_delete = models.CASCADE,
            related_name = 'corporation_provenance_stations'
        )
    owner = models.ForeignKey(
            'dmad.Corporation',
            on_delete = models.CASCADE,
            related_name = 'provenance_stations',
            null = True
        )
    bib = models.ForeignKey(
            'bib.ZotItem',
            on_delete = models.SET_NULL,
            related_name = 'corporation_provenance_stations',
            null = True,
            blank = True
        )
    period = models.ForeignKey(
            'dmad.Period',
            on_delete = models.SET_NULL,
            blank = True,
            null = True,
            related_name = 'corporation_provenance_stations'
            )


class DigitalCopy(models.Model):
    class LinkType(models.TextChoices):
        DIGITIZED = 'Dig', _('Digitized')
        IIIF_MANIFEST = 'IIIF', _('IIIF Manifest')

        def parse(string):
            if 'iiif' in string:
                return DigitalCopy.LinkType.IIIF_MANIFEST
            if 'digitized' in string:
                return DigitalCopy.LinkType.DIGITIZED
            return None

    item = models.ForeignKey(
            'Item',
            on_delete = models.CASCADE,
            related_name = 'digital_copies'
        )
    url = models.URLField()
    link_type = models.TextField(
            max_length = 20,
            null = True,
            blank = True,
            choices=LinkType,
            default=LinkType.DIGITIZED
        )

