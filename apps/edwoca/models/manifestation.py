from .base import *
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from dmad_on_django.models import Status


class Manifestation(WemiBaseClass):
    class ManifestationType(models.TextChoices):
        MANUSCRIPT = 'MS', _('Parent')

    class EditionType(models.TextChoices):
        SCORE = 'SC', _('Score')
        PARTS = 'PA', _('Parts')

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
    dedicatee = models.ForeignKey(
            'dmad.Person',
            on_delete=models.SET_NULL,
            related_name='dedicated_manifestations',
            blank=True,
            null=True
        )
    dedication = models.TextField(
            max_length=100,
            blank=True,
            null=True
        )
    watermark = models.TextField(
            max_length=100,
            blank=True,
            null=True
        )
    watermark_url = models.URLField(
            blank=True,
            null=True
        )

    def __str__(self):
        title = self.get_pref_title() or '<ohne Titel>'
        return f'{self.rism_id}: {title}'


class ManifestationTitle(models.Model):
    class TitleTypes(models.TextChoices):
        ENVELOPE = 'EN', _('Envelope')
        TITLE_PAGE = 'TP', _('Title Page')
        HEAD_TITLE = 'HT', _('Head Title')

    title = models.CharField(
            max_length=100,
            null=True,
            blank=True
        )
    title_type = models.CharField(
            max_length=2,
            choices=TitleTypes,
            default=TitleTypes.ENVELOPE
        )
    writer = models.ForeignKey(
            'dmad.Person',
            on_delete=models.SET_NULL,
            related_name='written_manifestation_titles',
            blank=True,
            null=True
        )
    medium = models.CharField(
            max_length=100,
            null=True,
            blank=True
        )
    manifestation = models.ForeignKey(
            'Manifestation',
            on_delete=models.CASCADE,
            related_name='titles',
        )


class ManifestationBib(BaseBib):
    manifestation = models.ForeignKey(
        'Manifestation',
        on_delete=models.CASCADE
    )


class ManifestationContributor(BaseContributor):
    manifestation = models.ForeignKey(
        'Manifestation',
        on_delete=models.CASCADE,
        related_name='contributor_relations'
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
