from django.db import models
from django.urls import reverse
from .base import Status, Language, max_trials, DisplayableModel
from json import loads, dumps
from pylobid.pylobid import PyLobidClient, GNDAPIError
import requests


class GNDSubjectCategory(models.Model):
    link = models.CharField(max_length=200,unique=True)
    label = models.CharField(max_length=50)

    @staticmethod
    def create_or_link(json):
        category = json['gndSubjectCategory'][0]

        try:
            return GNDSubjectCategory.objects.get(link=category['id'])
        except GNDSubjectCategory.DoesNotExist:
            subjectcategory = GNDSubjectCategory()
            subjectcategory.link = category['id']
            subjectcategory.label = category['label']
            subjectcategory.save()
            return subjectcategory

    def __str__(self):
        return self.label

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
    gnd_subject_category = models.ForeignKey(
        GNDSubjectCategory,
        on_delete=models.SET_NULL,
        null=True
    )

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
                pl_subjectterm = PyLobidClient(url, fetch_related=True)
            except GNDAPIError:
                trials -= 1
                continue
            break
        self.raw_data=dumps(pl_subjectterm.ent_dict)

    def update_from_raw(self):
        raw_data = loads(self.raw_data)
        self.gnd_subject_category = GNDSubjectCategory.create_or_link(raw_data)
        self.save()
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
        lobid_url = f"https://lobid.org/gnd/search?q={search_string}&filter=(type:AuthorityResource)&size=5&format=json:suggest"
        lobid_response = requests.get(lobid_url)
        return lobid_response.json()

    def get_default_name(self):
        if self.names.count() > 0:
            return self.names.get(status=Status.PRIMARY).__str__()
        return 'ohne Name'

    def get_designator(self):
        if self.gnd_id:
            return self.get_default_name()
        return getattr(self, 'interim_designator', '') or ''

    def get_absolute_url(self):
        return reverse('dmad_on_django:subject_term_update', kwargs={'pk': self.pk})

    def __str__(self):
        return f'{self.gnd_id}: {self.names.get(status=Status.PRIMARY).name}'

    def get_table(self):
            category_label = self.gnd_subject_category.label
            category_link = self.gnd_subject_category.link
            return [("GND-Sachgruppe",
                    f'<a href="{category_link}"target = "_blank" class = "link link-primary">{category_label}</a>')] +\
            self.get_parent_subject_table()

    def get_overview_title(self):
        return "Angaben"
