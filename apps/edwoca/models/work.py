from .base import *
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from dmad_on_django.models import Status


class Work(WemiBaseClass):
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

    def __str__(self):
        return f"{self.work_catalog_number}: {self.get_pref_title()}"

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


class WorkTitle(WemiTitle):
    work = models.ForeignKey('Work', on_delete=models.CASCADE, related_name='titles')
