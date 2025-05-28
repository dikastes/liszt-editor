from django.db import models
from django.urls import reverse
from json import dumps, loads
import requests

from .base import Status, Language, max_trials, DisplayableModel
from .place import Place
from pylobid.pylobid import PyLobidPerson, GNDAPIError


class PersonName(models.Model):
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    language = models.CharField(
        max_length=15,
        choices=Language,
        default=Language['DE'],
        null=True
    )
    person = models.ForeignKey(
        'Person',
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
    interim_designator = models.CharField(
        max_length=150,
        null=True,
        blank=True
    )

    def parse_comma_separated_string(self, comma_separated_string):
        names = comma_separated_string.split(',')
        self.last_name = names[0].strip()
        if len(names) > 1:
            self.first_name = ' '.join([name.strip() for name in names[1:]])
        return self

    @staticmethod
    def create_from_comma_separated_string(comma_separated_string, status, person):
        name = PersonName()
        name.status = status
        name.person = person
        return name.parse_comma_separated_string(comma_separated_string)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Person(DisplayableModel):
    class Gender(models.TextChoices):
        MALE = 'm', 'male'
        FEMALE = 'f', 'female'
        NULL = '', 'null'

    raw_data = models.TextField(null=True)
    rework_in_gnd = models.BooleanField(default=False)
    gnd_id = models.CharField(max_length=20, null=True, blank=True)
    gender = models.CharField(
        max_length=1,
        choices=Gender,
        default=Gender.NULL,
        null=True
    )
    geographic_area_code = models.CharField(max_length=10, null=True)
    description = models.TextField(null=True)
    birth_date = models.DateField(null=True, blank=True)
    death_date = models.DateField(null=True, blank=True)
    birth_place = models.ForeignKey(
        Place,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='birth_place_of'
    )
    death_place = models.ForeignKey(
        Place,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='death_place_of'
    )
    activity_places = models.ManyToManyField(Place)
    comment = models.TextField(null=True, blank=True)
    interim_designator = models.CharField(max_length=150, null=True, blank=True)

    def get_absolute_url(self):
        return reverse('dmad_on_django:person_update', kwargs={'pk': self.id})


    def get_description(self):
        birth_date = self.birth_date.strftime('%d.%m.%Y') if self.birth_date else 'o.D.'
        death_date = self.death_date.strftime('%d.%m.%Y') if self.death_date else 'o.D.'

        birth_place = self.birth_place.get_default_name() if self.birth_place else '?'
        death_place = self.death_place.get_default_name() if self.death_place else '?'

        return f"{birth_date} ({birth_place})–{death_date} ({death_place})"

    def update_from_raw(self):
        pl_person = PyLobidPerson()
        pl_person.process_data(data=loads(self.raw_data))

        self.birth_date = Person.map_date(pl_person.life_span['birth_date_str'])
        self.death_date = Person.map_date(pl_person.life_span['death_date_str'])

        if 'gender' in pl_person.ent_dict:
            self.gender = Person.map_gender(pl_person.ent_dict['gender'][0]['id'])

        if 'geographicAreaCode' in pl_person.ent_dict:
            self.geographic_area_code = ', '.join([
                area_code['id'].split('#')[1]
                for area_code in pl_person.ent_dict['geographicAreaCode']
            ])

        if pl_person.birth_place['id']:
            self.birth_place = Place.fetch_or_get(pl_person.birth_place['id'])
            self.birth_place.save()

        if pl_person.death_place['id']:
            self.death_place = Place.fetch_or_get(pl_person.death_place['id'])
            self.death_place.save()

        self.save()

        self.activity_places.clear()
        if 'placeOfActivity' in pl_person.ent_dict:
            for place in pl_person.ent_dict['placeOfActivity']:
                activity_place = Place.fetch_or_get(place['id'])
                self.activity_places.add(activity_place)
                activity_place.save()

        self.names.all().delete()
        pref_name = PersonName()
        pref_name.status = Status.PRIMARY
        pref_name.person = self
        pref_name.parse_comma_separated_string(pl_person.pref_name)
        pref_name.save()

        for name in pl_person.alt_names:
            alt_name = PersonName()
            alt_name.status = Status.ALTERNATIVE
            alt_name.person = self
            alt_name.parse_comma_separated_string(name)
            alt_name.save()

        self.save()

    def fetch_raw(self):
        trials = max_trials
        url = f"http://d-nb.info/gnd/{self.gnd_id}"
        while trials:
            try:
                pl_person = PyLobidPerson(url, fetch_related=True)
            except GNDAPIError:
                trials -= 1
                continue
            break
        self.raw_data = dumps(pl_person.ent_dict)

    @staticmethod
    def fetch_or_get(gnd_id):
        shortened_gnd_id = gnd_id.replace('https://d-nb.info/gnd/', '')
        try:
            return Person.objects.get(gnd_id=shortened_gnd_id)
        except Person.DoesNotExist:
            person = Person()
            person.gnd_id = shortened_gnd_id
            person.fetch_raw()
            person.update_from_raw()
            return person

    def get_designator(self):
        if self.gnd_id:
            return self.get_default_name()
        return self.interim_designator or ''

    def get_default_name(self):
        if self.names.count() > 0:
            return self.names.get(status=Status.PRIMARY).__str__()
        return 'ohne Name'
    
    def get_table(self):
            
            rows = [
            ("Ländercode", self.geographic_area_code),
            ("Geschlecht", self.gender),
            ("Geburtsort", self.birth_place),
            ("Sterbeort", self.death_place),
            ("Geburtsdatum", self.birth_date),
            ("Sterbedatum", self.death_date),
            ("Charakteristischer Beruf", "todo"),
            ("GND-ID", self.gnd_id),
            ]

            if(len(self.activity_places.all()) > 0):
                for place in self.activity_places.all():
                    rows.append(("Wirkungsort", str(place)))

            return rows
    def get_overview_title(self):
        return "Biografie"
        
    @staticmethod
    def search(search_string):
        lobid_url = f"https://lobid.org/gnd/search?q={search_string}&filter=(type:Person)&size=5&format=json:suggest"
        lobid_response = requests.get(lobid_url)
        return lobid_response.json()

    def __str__(self):
        return f'{self.gnd_id}: {self.get_default_name()}'

    @staticmethod
    def map_gender(gnd_gender):
        if gnd_gender == 'https://d-nb.info/standards/vocab/gnd/gender#male':
            return Person.Gender.MALE
        if gnd_gender == 'https://d-nb.info/standards/vocab/gnd/gender#female':
            return Person.Gender.FEMALE
        return Person.Gender.NULL

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


