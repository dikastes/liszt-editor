from django.db import models

from .base import DisplayableModel
from dmad_on_django.models import Person
from .subjectterm import Subjectterm

class Work(DisplayableModel):

    date_of_production = models.CharField(max_length=10,null=True)

    opus_or_other = models.CharField(max_length=10,null=True)

    first_composer = models.ForeignKey(
        Person,
        on_delete=models.SET_NULL,
        related_name='first_composer_of',
        null=True
    )

    form_of_work = models.ForeignKey(
        Subjectterm,
        on_delete=models.SET_NULL,
        related_name='form_of_work_or_expression',
        null=True
    )

