from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from .base import Status, Language, max_trials, DisplayableModel, GNDSubjectCategory
from json import loads, dumps
from pylobid.pylobid import PyLobidClient, GNDAPIError
import requests

class SubjectTermName(models.Model):
    name = models.CharField(max_length=40)
    status = models.CharField(
        max_length=1,
        choices=Status,
        default=Status.PRIMARY
    )
    subject_term = models.ForeignKey(
        'SubjectTerm',
        on_delete=models.CASCADE,
        related_name='names',
        null=True
    )

    def __str__(self):
        return self.name

    @staticmethod
    def create_from_string(name, status, subject_term):
        return SubjectTermName(
            name=name,
            status=status,
            subject_term=subject_term
        )

class SubjectTerm(DisplayableModel):

    parent_subjects = models.ManyToManyField('self', blank=True, symmetrical=False)

    def get_parent_subject_table(self):
        return [
        (
            "Übergeordnetes Sachschlagwort",
            f'<a href="{s.get_absolute_url()}"class = "link link-primary">{s.get_default_name()} ({s.gnd_id})</a>'
        )
        for s in self.parent_subjects.all()
    ]

    @staticmethod
    def fetch_or_get(gnd_id):
        shortened_gnd_id = gnd_id.replace('https://d-nb.info/gnd/', '')
        try:
            return SubjectTerm.objects.get(gnd_id=shortened_gnd_id)
        except:
            subject_term = SubjectTerm()
            subject_term.gnd_id = shortened_gnd_id
            subject_term.fetch_raw()
            subject_term.update_from_raw()
            return subject_term

    def fetch_raw(self):
        trials = max_trials
        url = f"http://d-nb.info/gnd/{self.gnd_id}"
        while trials:
            try:
                pl_subjectterm = PyLobidClient(url, fetch_related=False)
            except GNDAPIError:
                trials -= 1
                continue
            break
        self.raw_data=dumps(pl_subjectterm.ent_dict)

    def update_from_raw(self):
        self.save()
        raw_data = loads(self.raw_data)
        GNDSubjectCategory.create_or_link(self)
        self.names.all().delete()
        pref_name = SubjectTermName.create_from_string(
                raw_data['preferredName'],
                Status.PRIMARY,
                self
            )
        pref_name.save()

        try:
            for name in raw_data['variantName']:
                alt_name = SubjectTermName.create_from_string(
                    name,
                    Status.ALTERNATIVE,
                    self
                )
                alt_name.save()

        except KeyError:
            pass

        try:
            for parent in raw_data['broaderTermGeneral']:
                self.parent_subjects.add(self.fetch_or_get(parent['id']))
        except KeyError:
            pass

        try:
            for parent in raw_data['broaderTermGeneric']:
                self.parent_subjects.add(self.fetch_or_get(parent['id']))
        except KeyError:
            pass

        self.save()

    @staticmethod
    def search(search_string):
        lobid_url = f"https://lobid.org/gnd/search?q={search_string}&filter=(type:SubjectHeading)&size=5&format=json:suggest"
        lobid_response = requests.get(lobid_url)
        return lobid_response.json()

    def get_default_name(self):
        if self.names.count() > 0:
            return self.names.get(status=Status.PRIMARY).__str__()
        return _("without name")

    def get_designator(self):
        if self.gnd_id:
            return self.get_default_name()
        return getattr(self, 'interim_designator', '') or ''

    def get_absolute_url(self):
        return reverse('dmad_on_django:subject_term_update', kwargs={'pk': self.pk})

    def __str__(self):
        return f'{self.gnd_id}: {self.names.get(status=Status.PRIMARY).name}'

    def get_table(self):
            
            return GNDSubjectCategory.get_subject_category_table(self) +\
            self.get_parent_subject_table()
    
    def get_overview_title(self):
        return _("description")
