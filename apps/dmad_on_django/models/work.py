from django.db import models
from django.urls import reverse

from django.utils.translation import gettext_lazy as _

from .base import DisplayableModel, Status, max_trials, GNDSubjectCategory
from dmad_on_django.models import Person
from .subjectterm import SubjectTerm
from .geographicareacodes import WorkGeographicAreaCode
from liszt_util.tools import get_model_link

from pylobid.pylobid import PyLobidWork, GNDAPIError
from json import dumps, loads
import requests

class WorkName(models.Model):
    name = models.CharField(max_length=20, null=True)
    work = models.ForeignKey(
        'Work',
        on_delete=models.CASCADE,
        related_name='names',
        null=True
    )

    status = models.CharField(
        max_length=1,
        choices=Status,
        default=Status.PRIMARY,
        null=True
    )

    @staticmethod
    def create_from_string(name, status, work):
        workname = WorkName()
        workname.name = name
        workname.status = status
        workname.work = work
        return workname

    def __str__(self):
        if self.work.gnd_id:
            return f'{self.name} ({self.work.gnd_id})'
        return self.interim_designator


class Work(DisplayableModel):

    date_of_creation = models.CharField(max_length=10,null=True)

    opus = models.CharField(max_length=10,null=True)

    work_catalouge_number = models.CharField(null=True)

    creators = models.ManyToManyField(
        Person,
        blank=True,
        symmetrical=False,
        related_name='authors' #Needed because otherwise it will clash with edwoca
    )

    form_of_work = models.ForeignKey(
        SubjectTerm,
        on_delete=models.SET_NULL,
        related_name='form_of_work_and_expression',
        null=True
    )

    broader_terms = models.ManyToManyField('self', blank=True, symmetrical=False)
    
    def fetch_raw(self):
        trials = max_trials
        url = f"http://d-nb.info/gnd/{self.gnd_id}"
        while trials:
            try:
                pl_work = PyLobidWork(url, fetch_related=False)

            except GNDAPIError:
                trials -= 1
                continue

            break
            
        self.raw_data = dumps(pl_work.ent_dict)

    @staticmethod
    def fetch_or_get(gnd_id):
        shortened_gnd_id = gnd_id.replace('https://d-nb.info/gnd/', '')

        try:
            return Work.objects.get(gnd_id=shortened_gnd_id)
        except Work.DoesNotExist:
            work = Work()
            work.gnd_id = shortened_gnd_id
            work.fetch_raw()
            work.update_from_raw()
            return work

    def update_from_raw(self):
        pl_work = PyLobidWork()
        pl_work.process_data(data=loads(self.raw_data))
        self.date_of_creation = pl_work.date_of_creation

        self.save()

        for item in pl_work.creators:
            self.creators.add(Person.fetch_or_get(item['id']))

        self.names.all().delete()
        pref_name = WorkName.create_from_string(pl_work.pref_name, Status.PRIMARY, self)
        pref_name.save()

        for name in pl_work.alt_names:
            WorkName.create_from_string(name, Status.ALTERNATIVE, self).save()
        
        self.geographic_area_codes.all().delete()
        WorkGeographicAreaCode.create_geographic_area_codes(self)

        if pl_work.broader_terms:
            for term in pl_work.broader_terms:
                self.broader_terms.add(self.fetch_or_get(term['id']))
        
        if pl_work.form_of_work:
            self.form_of_work = SubjectTerm.fetch_or_get(pl_work.form_of_work[0]['id'])
        
        GNDSubjectCategory.create_or_link(self)

        if pl_work.opus:
            self.opus = pl_work.opus
        
        if pl_work.work_catalouge_number:
            self.work_catalouge_number = pl_work.work_catalouge_number

        self.save()

        

    @staticmethod
    def search(search_string):
        lobid_url = f"https://lobid.org/gnd/search?q={search_string}&filter=(type:Work)&size=5&format=json:suggest"
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
        return reverse('dmad_on_django:work_update', kwargs={'pk': self.pk})

    def __str__(self):
        return f'{self.gnd_id}: {self.names.get(status=Status.PRIMARY).name}'
    
    def get_table(self):
        table = []

        if self.date_of_creation:
            table.append((_("date of creation"), self.date_of_creation))

        if self.opus:
            table.append((_("opus"), self.opus))

        if self.work_catalouge_number:
            table.append((_("work catalog number"), self.work_catalouge_number))

        
        match self.form_of_work:
            case work_form if work_form: 
                table.append((_("category"), get_model_link(work_form)))

        match self.creators:
            case creators if creators.exists():
                for creator in creators.all():
                    table.append((_("creator"), get_model_link(creator)))
            case _:
                pass

        match self.broader_terms:
            case terms if terms.exists():
                for term in terms.all():
                    table.append((_("broader terms"), get_model_link(term)))
            case _:
                pass

        table += GNDSubjectCategory.get_subject_category_table(self) + \
                WorkGeographicAreaCode.get_area_code_table(self.geographic_area_codes)

        return table

    
    def get_overview_title(self):
        
        return _("description")
    




