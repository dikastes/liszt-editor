from .base import *
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from dmad_on_django.models import Status


class Manifestation(WemiBaseClass):
    class ManifestationType(models.TextChoices):
        MANUSCRIPT = 'MS', _('Parent')

    class EditionType(models.TextChoices):
        PIANO_REDUCTION = 'PR', _('Piano Reduction')
        SCORE = 'SC', _('Score')

    class State(models.TextChoices):
        COMPLETE= 'CP', _('complete')
        INCOMPLETE= 'INC', _('incomplete')

    rism_id = models.CharField(
            unique=True,
            max_length=20,
            null = True,
            blank = True
        )
    plate_number = models.CharField(
            max_length = 10,
            null = True,
            blank = True
        )
    period = models.OneToOneField(
            'dmad.Period',
            on_delete = models.SET_NULL,
            blank = True,
            null = True
        )
    place = models.ForeignKey(
            'dmad.Place',
            on_delete = models.SET_NULL,
            blank = True,
            null = True
        )
    contributors = models.ManyToManyField(
            'dmad.Person',
            through = 'ManifestationContributor'
        )
    related_manifestations = models.ManyToManyField(
            'Manifestation',
            through = 'RelatedManifestation'
        )
    manifestation_type = models.CharField(
            max_length=10,
            choices=ManifestationType,
            default=ManifestationType.MANUSCRIPT
        )
    edition_type = models.CharField(
            max_length=10,
            choices=EditionType,
            default=EditionType.SCORE
        )
    state = models.CharField(
            max_length=10,
            choices=State,
            default=State.COMPLETE
        )
    history = models.TextField(
            blank = True,
            null = True
        )
    bib = models.ManyToManyField(
            'bib.ZotItem',
            through = 'ManifestationBib'
        )

    def __str__(self):
        title = self.get_pref_title() or '<ohne Titel>'
        return f'{self.rism_id}: {title}'


class ManifestationTitle(WemiTitle):
    manifestation = models.ForeignKey(
            'Manifestation',
            on_delete=models.CASCADE,
            related_name='titles'
        )


class ManifestationBib(BaseBib):
    manifestation = models.ForeignKey(
        'Manifestation',
        on_delete=models.CASCADE
    )


class ManifestationContributor(BaseContributor):
    manifestation = models.ForeignKey(
        'Manifestation',
        on_delete=models.CASCADE
    )


class RelatedManifestation(RelatedEntity):
    source_manifestation = models.ForeignKey(
            'Manifestation',
            on_delete=models.CASCADE,
            related_name="source_manifestation_of"
        )
    target_manifestation = models.ForeignKey(
            'Manifestation',
            on_delete=models.CASCADE,
            related_name="target_manifestation_of"
        )
