from django.db import models
from .base import Status, Language, max_trials, DisplayableModel
from json import loads


class GNDSubjectCategory(models.Model):
    link = models.URLField(max_length=200)
    label = models.CharField(max_length=50)

    @staticmethod
    def create(data):
        json = loads(data)

class SubjectTermName(models.Model):
    name = models.CharField(max_length=40)
    status = models.CharField(
        max_length=1,
        choices=Status,
        default=Status.PRIMARY
    )

class SubjectTerm(DisplayableModel):
    gnd_subject_category = models.ForeignKey(
        GNDSubjectCategory,
        on_delete=models.SET_NULL,
        null=True
    )

    parent_subjects = models.ManyToManyField('self', blank=True)

    def fetch_raw():
        pass