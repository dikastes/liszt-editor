from django.db import models
from django.urls import reverse
from json import dumps, loads
import requests

from .base import Status, Language, max_trials, DisplayableModel, GNDSubjectCategory
from .place import Place
from .geographicareacodes import CorporationGeographicAreaCode
from .subjectterm import SubjectTerm
from .period import Period
from pylobid.pylobid import PyLobidOrg, GNDAPIError


class CorporationName(models.Model):
    name = models.CharField(max_length=50)
    language = models.CharField(
        max_length=15,
        choices=Language,
        default=Language['DE'],
        null=True
    )
    corporation = models.ForeignKey(
        'Corporation',
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
    def create_from_string(string, status, corporation):
        name = CorporationName()
        name.status = status
        name.corporation = corporation
        name.name = string
        return name

    def __str__(self):
        return self.name


class Corporation(DisplayableModel):

    # broaderTermInstantial -> bisher nur für Verlage überprüft
    category = models.ForeignKey(
        SubjectTerm,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='corporations'
    )
    # placeOfBusiness
    place = models.ForeignKey(
        Place,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='corporations'
    )
    # period not before: dateOfEstablishment,
    # period not after: dateOfTermination,
    # period display: something like 1880-1882
    period = models.OneToOneField(
        Period,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='corporations'
    )

    def get_absolute_url(self):
        return reverse('dmad_on_django:corporation_update', kwargs={'pk': self.id})


    def update_from_raw(self):
        GNDSubjectCategory.create_or_link(self.raw_data)

    def fetch_raw(self):
        trials = max_trials
        url = f"http://d-nb.info/gnd/{self.gnd_id}"
        while trials:
            try:
                pl_corporation = PyLobidOrg(url, fetch_related=True)
            except GNDAPIError:
                trials -= 1
                continue
            break
        self.raw_data = dumps(pl_corporation.ent_dict)

    @staticmethod
    def fetch_or_get(gnd_id):
        shortened_gnd_id = gnd_id.replace('https://d-nb.info/gnd/', '')
        try:
            return Corporation.objects.get(gnd_id=shortened_gnd_id)
        except Corporation.DoesNotExist:
            corporation = Corporation()
            corporation.gnd_id = shortened_gnd_id
            corporation.fetch_raw()
            corporation.update_from_raw()
            return corporation

    def get_designator(self):
        if self.gnd_id:
            return self.get_default_name()
        return self.interim_designator or ''

    def get_default_name(self):
        if self.names.count() > 0:
            return self.names.get(status=Status.PRIMARY).__str__()
        return 'ohne Name'

    def get_table(self):
        return CorporationGeographicAreaCode.get_area_code_table(self.geographic_area_codes) +\
        GNDSubjectCategory.get_subject_category_table(self.gnd_subject_category)
        
    
    @staticmethod
    def search(search_string):
        lobid_url = f"https://lobid.org/gnd/search?q={search_string}&filter=(type:Company OR type:CorporateBody)&size=5&format=json:suggest"
        lobid_response = requests.get(lobid_url)
        return lobid_response.json()

    def __str__(self):
        return f'{self.gnd_id}: {self.get_default_name()}'

    @staticmethod
    def map_date(date_string):
        date_list = date_string.split('-')
        if len(date_list) > 3:
            raise Exception(f'Unknown date format: {date_string}')
        year = date_list[0] if date_list[0].isnumeric() else None
        month = date_list[1] if len(date_list) > 1 and date_list[1].isnumeric() else '1'
        day = date_list[2] if len(date_list) > 2 and date_list[2].isnumeric() else '1'
        if not year:
            return None
        return '-'.join([year, month, day])

    def get_model(self):
        return self

    def get_overview_title(self):
        return "Angaben"