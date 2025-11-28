from .base import *
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q, UniqueConstraint
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from liszt_util.models import Sortable


class Item(Sortable, WemiBaseClass):
    rism_id = models.CharField(
            max_length=20,
            null = True,
            blank = True,
            verbose_name = _('RISM id')
        )
    manifestation = models.ForeignKey(
            'Manifestation',
            on_delete = models.CASCADE,
            related_name = 'items',
        )
    private_dedication_comment = models.TextField(
            blank = True,
            null = True,
            verbose_name = _('private dedication comment')
        )
    private_provenance_comment = models.TextField(
            blank = True,
            null = True,
            verbose_name = _('private provenance comment')
        )
    public_provenance_comment = models.TextField(
            blank = True,
            null = True,
            verbose_name = _('public provenance comment')
        )
    is_template = models.BooleanField(default=False)
    extent = models.TextField(
            blank = True,
            null = True,
            verbose_name = _('extent')
        )
    measure = models.TextField(
            blank = True,
            null = True,
            verbose_name = _('measure')
        )
    private_manuscript_comment = models.TextField(
            blank = True,
            null = True,
            verbose_name = _('private manuscript comment')
        )
    taken_information = models.TextField(
            blank = True,
            null = True,
            verbose_name = _('taken information')
        )

    _group_field_name = 'manifestation'

    def render_handwritings(self):
        return ', '.join(handwriting.__str__() for handwriting in self.handwritings)

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
        return next(self.signatures.filter(status = BaseSignature.Status.CURRENT).iterator(), 'ohne Signatur').__str__()

    def current_signature(self):
        return self.signatures.filter(status=BaseSignature.Status.CURRENT).first()

    def save(self, *args, **kwargs):
        if self.manifestation.is_singleton and self.manifestation.items.count() > 1:
            raise ValidationError("Cannot add another item to a singleton manifestation.")
        
        if self.pk is None:
            max_index = (
                Item.objects
                .filter(manifestation=self.manifestation)
                .aggregate(models.Max('order_index'))['order_index__max']
            )

            if max_index is not None:
                self.order_index = max_index + 1

        super().save(*args, **kwargs)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['manifestation'],
                condition=models.Q(is_template=True),
                name='unique_template_item_per_manifestation'
            )
        ]
        ordering = ['manifestation', 'order_index']
        unique_together = ('manifestation', 'order_index')


class Library(models.Model):
    name = models.CharField(
            unique=True,
            max_length=100,
            null = True,
            blank = True,
            verbose_name = _('name')
        )
    siglum = models.CharField(
            unique=True,
            max_length=20,
            null = True,
            blank = True,
            verbose_name = _('siglum')
        )

    def get_absolute_url(self):
        return reverse('edwoca:library_update', kwargs = {'pk' : self.id})

    def __str__(self):
        return f"{self.name} ({self.siglum})"


class BaseSignature(models.Model):
    class Meta:
        abstract = True

    class Status(models.TextChoices):
        CURRENT = 'C', _('Current')
        FORMER = 'F', _('Former')

    library = models.ForeignKey(
            'dmrism.Library',
            on_delete = models.SET_NULL,
            related_name = '%(class)s',
            null = True,
            blank = True
        )
    signature = models.CharField(
            max_length=20,
            null = True,
            blank = True,
            verbose_name = _('signature')
        )
    status = models.CharField(
            max_length=1,
            choices=Status,
            default=Status.CURRENT,
            verbose_name = _('status')
        )

    def __str__(self):
        return f"{self.library.siglum} {self.signature}"


class ItemSignature(BaseSignature):
    item = models.ForeignKey(
            'Item',
            on_delete = models.CASCADE,
            related_name = 'signatures',
            null = True
        )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['item'],
                condition=Q(status='C'),
                name='unique_current_item_signature'
            )
        ]


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
        
        parts = [f'{str(owner_string)} ({str(period_string)})']
        
        if hasattr(self, 'bib') and self.bib:
            parts.append(f'Bib: {self.bib}')
        
        if hasattr(self, 'letters') and self.letters.exists():
            letter_strings = ', '.join(str(letter) for letter in self.letters.all())
            parts.append(f'Letter: {letter_strings}')
            
        return ' | '.join(parts)


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


class BaseDigitalCopy(models.Model):
    class Meta:
        abstract = True

    class LinkType(models.TextChoices):
        DIGITIZED = 'Dig', _('Digitized')
        IIIF_MANIFEST = 'IIIF', _('IIIF Manifest')
        PRIVATE = 'Prv', _('Private')

        def parse(string):
            if 'iiif' in string:
                return BaseDigitalCopy.LinkType.IIIF_MANIFEST
            if 'digitized' in string:
                return BaseDigitalCopy.LinkType.DIGITIZED
            return None

    url = models.URLField(verbose_name = _('URL'))
    link_type = models.TextField(
            max_length = 20,
            null = True,
            blank = True,
            choices=LinkType,
            default=LinkType.DIGITIZED,
            verbose_name = _('link type')
        )


class ItemDigitalCopy(BaseDigitalCopy):
    item = models.ForeignKey(
            'Item',
            on_delete = models.CASCADE,
            related_name = 'digital_copies'
        )


class ItemHandwriting(BaseHandwriting):
    item = models.ForeignKey(
            'item',
            related_name = 'handwritings',
            on_delete = models.CASCADE
        )


class ItemPersonDedication(BasePersonDedication):
    item = models.ForeignKey(
            'Item',
            on_delete = models.CASCADE
        )


class ItemCorporationDedication(BaseCorporationDedication):
    item = models.ForeignKey(
            'Item',
            on_delete = models.CASCADE
        )
