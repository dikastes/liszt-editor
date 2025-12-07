from .base import *
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from dmad_on_django.models import Status
from dmrism.models import BaseContributor, BaseBib, RelatedEntity, BasePersonDedication, BaseCorporationDedication


class Work(WeBaseClass):
    class Meta:
        ordering = ['work_catalog_number']

    gnd_id = models.CharField(
            max_length=20,
            unique=True,
            null=True,
            blank=True
        )
    work_catalog_number = models.CharField(
            max_length=20,
            unique=True,
            null=True,
            blank=True
        )
    related_work = models.ManyToManyField(
            'Work',
            through='RelatedWork'
        )
    history = models.TextField(
            null = True,
            blank = True
        )
    contributors = models.ManyToManyField(
            'dmad.Person',
            through = 'WorkContributor'
        )
    bib = models.ManyToManyField(
            'bib.ZotItem',
            through = 'WorkBib'
        )
    private_head_comment = models.TextField(
            blank = True,
            null = True,
            verbose_name = _('private head comment')
        )

    def __str__(self):
        if self.titles.filter(status = Status.TEMPORARY).first():
            return self.titles.filter(status = Status.TEMPORARY).first().title
        return "< ohne Titel >"
        #return f"{self.work_catalog_number}: {self.get_pref_title()}"

    def to_mei(self):
        work = ET.Element('work')

        for title in self.titles.all():
            work.append(title.to_mei())

        gnd_id = ET.Element('identifier')
        gnd_id.attrib['label'] = 'GND'
        gnd_id.text = self.gnd_id

        work_catalog_number = ET.Element('identifier')
        work_catalog_number.attrib['label'] = 'LQWV'
        work_catalog_number.text = self.work_catalog_number

        history = ET.Element('history')
        history.text = self.history

        contributors = ET.Element('contributor')
        for contributor in self.contributors.all():
            contributors.append(contributor)

        work.append(gnd_id)
        work.append(work_catalog_number)
        work.append(history)

        return work


class WorkContributor(BaseContributor):
    work = models.ForeignKey(
        'Work',
        on_delete=models.CASCADE,
        related_name='contributor_relations'
    )


class WorkBib(BaseBib):
    work = models.ForeignKey(
        'Work',
        on_delete=models.CASCADE,
        related_name='bib_set'
    )


class RelatedWork(RelatedEntity):
    class Label(models.TextChoices):
        IS_PART_OF = 'PA', _('is part of'),
        IS_DERIVATIVE_OF = 'DE', _('is derivative of')
        IS_SUCCESSOR_OF = 'SU', _('is successor of')
        IS_INSPIRED_BY = 'IN', _('is inspired by')
        USES_EXPRESSION_OF = 'EX', _('uses expression of')
        ACCOMPANIES_OR_COMPLEMENTS = 'AC', _('accompanies or complements')

    source_work = models.ForeignKey(
            'Work',
            on_delete=models.CASCADE,
            related_name="source_work_of"
        )
    target_work = models.ForeignKey(
            'Work',
            on_delete=models.CASCADE,
            related_name="target_work_of"
        )
    label = models.CharField(
            max_length = 2,
            choices = Label,
            default = Label.IS_PART_OF
            )


class WorkTitle(WemiTitle):
    work = models.ForeignKey('Work', on_delete=models.CASCADE, related_name='titles')


class BaseWorkReference(models.Model):
    class Meta:
        abstract = True

    work = models.ForeignKey(
            'Work',
            on_delete = models.CASCADE
        )


class WorkWorkReference(BaseWorkReference):
    reference_work = models.ForeignKey(
            'dmad.Work',
            on_delete = models.CASCADE,
            related_name = 'referencing_works'
        )


class PersonWorkReference(BaseWorkReference):
    person = models.ForeignKey(
            'dmad.Person',
            on_delete = models.CASCADE,
            related_name = 'referencing_works'
        )


class PlaceWorkReference(BaseWorkReference):
    place = models.ForeignKey(
            'dmad.Place',
            on_delete = models.CASCADE,
            related_name = 'referencing_works'
        )


class SubjectTermWorkReference(BaseWorkReference):
    subject_term = models.ForeignKey(
            'dmad.SubjectTerm',
            on_delete = models.CASCADE,
            related_name = 'referencing_works'
        )


class CorporationWorkReference(BaseWorkReference):
    corporation = models.ForeignKey(
            'dmad.Corporation',
            on_delete = models.CASCADE,
            related_name = 'referencing_works'
        )


class WorkPersonDedication(BasePersonDedication):
    work = models.ForeignKey(
            'Work',
            on_delete = models.CASCADE
        )


class WorkCorporationDedication(BaseCorporationDedication):
    work = models.ForeignKey(
            'Work',
            on_delete = models.CASCADE
        )
