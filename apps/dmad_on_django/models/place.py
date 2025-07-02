from django.db import models
from django.urls import reverse
from json import dumps, loads
from .geographicareacodes import PlaceGeographicAreaCode

from .base import Status, Language, max_trials, DisplayableModel
from pylobid.pylobid import PyLobidPlace, GNDAPIError
import requests

class PlaceName(models.Model):
    name = models.CharField(max_length=20, null=True)
    language = models.CharField(
        max_length=15,
        choices=Language,
        default=Language['DE'],
        null=True
    )
    place = models.ForeignKey(
        'Place',
        on_delete=models.CASCADE,
        related_name='names',
        null=True #TODO: Lösung finden
    )
    status = models.CharField(
        max_length=1,
        choices=Status,
        default=Status.PRIMARY,
        null=True
    )

    def __str__(self):
        return self.name

    @staticmethod
    def create_from_string(name, status, place):
        place_name = PlaceName()
        place_name.name = name
        place_name.status = status
        place_name.place = place
        return place_name


class Place(DisplayableModel):
    parent_place = models.ForeignKey(
        'Place',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='child_places'
    )
    long = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        default=0,
        null=True
    )
    lat = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        default=0,
        null=True
    )

    description = models.TextField(null=True)

    def update_from_raw(self):
        pl_place = PyLobidPlace()
        pl_place.process_data(data=loads(self.raw_data))
        if len(pl_place.coords) > 1:
            self.long = pl_place.coords[0]
            self.lat = pl_place.coords[1]
        self.save()
        self.names.all().delete()
        pref_name = PlaceName.create_from_string(pl_place.pref_name, Status.PRIMARY, self)
        pref_name.save()
        for name in pl_place.alt_names:
            alt_name = PlaceName.create_from_string(name, Status.ALTERNATIVE, self)
            alt_name.save()

        self.geographic_area_codes.all().delete()
        PlaceGeographicAreaCode.create_geographic_area_codes(self)


    def fetch_raw(self):
        trials = max_trials
        url = f"http://d-nb.info/gnd/{self.gnd_id}"
        while trials:
            try:
                pl_place = PyLobidPlace(url, fetch_related=True)
            except GNDAPIError:
                trials -= 1
                continue
            break
        self.raw_data = dumps(pl_place.ent_dict)

    @staticmethod
    def fetch_or_get(gnd_id):
        shortened_gnd_id = gnd_id.replace('https://d-nb.info/gnd/', '')
        try:
            return Place.objects.get(gnd_id=shortened_gnd_id)
        except Place.DoesNotExist:
            place = Place()
            place.gnd_id = shortened_gnd_id
            place.fetch_raw()
            place.update_from_raw()
            return place
        
    @staticmethod
    def search(search_string):
        lobid_url = f"https://lobid.org/gnd/search?q={search_string}&filter=(type:PlaceOrGeographicName)&size=5&format=json:suggest"
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
        return reverse('dmad_on_django:place_update', kwargs={'pk': self.pk})

    def __str__(self):
        return f'{self.gnd_id}: {self.names.get(status=Status.PRIMARY).name}'
    
    def get_table(self):

        return [("Long", self.long),
                ("Lat", self.lat)]+\
                PlaceGeographicAreaCode.get_area_code_table(self.geographic_area_codes)
    
    def get_overview_title(self):

        return "Angaben"

