from django.db import models
from django.urls import reverse
from json import dumps, loads

from .base import Status, Language, max_trials, DisplayableModel
from pylobid.pylobid import PyLobidPlace, GNDAPIError


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
        null=True
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
    gnd_id = models.CharField(max_length=20)
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
    comment = models.TextField(null=True, blank=True)
    rework_in_gnd = models.BooleanField(default=False)
    description = models.TextField(null=True)
    raw_data = models.TextField(null=True)

    def update_from_raw(self):
        pl_place = PyLobidPlace()
        pl_place.process_data(data=loads(self.raw_data))
        if len(pl_place.coords) > 1:
            self.long = pl_place.coords[0]
            self.lat = pl_place.coords[1]
        self.save()
        pref_name = PlaceName.create_from_string(pl_place.pref_name, Status.PRIMARY, self)
        pref_name.save()
        for name in pl_place.alt_names:
            alt_name = PlaceName.create_from_string(name, Status.ALTERNATIVE, self)
            alt_name.save()

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
                ("Lat", self.lat)]
    
    def get_overview_title(self):

        return "Angaben"
