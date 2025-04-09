from django.db import models
from django.utils.translation import gettext_lazy as _
from iso639 import data as iso639_data
from pylobid.pylobid import PyLobidClient, GNDIdError, GNDNotFoundError, GNDAPIError, PyLobidPerson, PyLobidPlace, PyLobidOrg
from json import dumps, loads

# Create your models here.

max_trials = 3

languages = { iso_data['iso639_1'].upper() : iso_data['name'] for iso_data in iso639_data }
Language = {}
for key in ['DE', 'FR', 'HU', 'EN']:
    Language[key] = languages[key]
for key in languages:
    Language[key] = languages[key]

class Status(models.TextChoices):
    PRIMARY = 'P', _('Primary')
    ALTERNATIVE = 'A', _('Alternative')

class PlaceName(models.Model):
    name = models.CharField(
            max_length=20,
            null=True
        )
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

    def create_from_string(name, status, place):
        place_name = PlaceName()
        place_name.name = name
        place_name.status = status
        place_name.place = place
        return place_name

class Place(models.Model):
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
            default = 0,
            null=True
        )
    lat = models.DecimalField(
            max_digits=9,
            decimal_places=6,
            default = 0,
            null=True
        )
    description = models.TextField(
            null=True
        )
    raw_data = models.TextField(
            null=True
        )

    def update_from_raw(self):
        pl_place = PyLobidPlace()
        pl_place.process_data(data=loads(self.raw_data))
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

            #except GNDIdError:
            #except GNDNotFoundError:
            except GNDAPIError:
                trials -= 1
                pass
            break
        self.raw_data = dumps(pl_place.ent_dict)

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

    def __str__(self):
        return f'{self.gnd_id}: {self.names.get(status=Status.PRIMARY).name}'

class PersonName(models.Model):
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    language = models.CharField(
            max_length=15,
            choices = Language,
            default = Language['DE'],
            null=True
        )
    person = models.ForeignKey(
            'Person',
            on_delete = models.CASCADE,
            related_name = 'names',
            null=True
        )
    status = models.CharField(
            max_length = 1,
            choices = Status,
            default = Status.PRIMARY,
            null=True
        )

    def parse_comma_separated_string(self, comma_separated_string):
        names = comma_separated_string.split(',')
        self.last_name = names[0]
        if len(names) > 1:
            self.first_name = ' '.join([ name.strip() for name in names[1:]])
        return self

    def create_from_comma_separated_string(comma_separated_string, status, person):
        name = PersonName()
        name.status = status
        name.person = person
        return name.parse_comma_separated_string(comma_separated_string)


    def __str__(self):
        return f'{self.first_name} {self.last_name}'

class Person(models.Model):
    class Gender(models.TextChoices):
        MALE = 'm', _('male')
        FEMALE = 'f', _('female')
        NULL = '', _('null')

    raw_data = models.TextField(
            null=True
        )
    gnd_id = models.CharField(max_length=20)
    gender = models.CharField(
            max_length=1,
            choices=Gender,
            default=Gender.NULL,
            null=True
        )
    geographic_area_code = models.CharField(
            max_length=10,
            null=True
        )
    description = models.TextField(
            null=True
        )
    birth_date = models.DateField(
            null=True,
            blank=True
        )
    death_date = models.DateField(
            null=True,
            blank=True
        )
    birth_place = models.ForeignKey(
            'Place',
            on_delete=models.SET_NULL,
            null=True,
            blank=True,
            related_name='birth_place_of'
        )
    death_place = models.ForeignKey(
            'Place',
            on_delete=models.SET_NULL,
            null=True,
            blank=True,
            related_name='death_place_of'
        )
    activity_places = models.ManyToManyField(
            'Place'
        )

    def update_from_raw(self):
        pl_person = PyLobidPerson()
        pl_person.process_data(data=loads(self.raw_data))
        #PersonName.create_from_comma_separated_string(
                #comma_separated_string = pl_person.pref_name,
                #status = Status.PRIMARY,
                #person = self
            #)
            #PersonName.create_from_comma_separated_string(
                    #comma_separated_string = name,
                    #status = Status.PRIMARY,
                    #person = self
                #)
        #self.date_of_birth, self.date_of_death = pl_person.life_span.values()
        self.birth_date = Person.map_date(pl_person.life_span['birth_date_str'])
        self.birth_date = Person.map_date(pl_person.life_span['death_date_str'])
        if 'gender' in pl_person.ent_dict:
            self.gender = Person.map_gender(pl_person.ent_dict['gender'][0]['id'])
        if 'geographicAreaCode' in pl_person.ent_dict:
            self.geographic_area_code = ', '.join([
                    area_code['id'].split('#')[1] for
                    area_code in
                    pl_person.ent_dict['geographicAreaCode']
                ])
        if pl_person.birth_place['id'] != '':
            self.birth_place = Place.fetch_or_get(pl_person.birth_place['id'])
            self.birth_place.save()
        if pl_person.death_place['id'] != '':
            self.death_place = Place.fetch_or_get(pl_person.death_place['id'])
            self.death_place.save()
        self.save()
        self.activity_places.clear()
        if 'placeOfActivity' in pl_person.ent_dict:
            for place in pl_person.ent_dict['placeOfActivity']:
                activity_place = Place.fetch_or_get(place['id'])
                self.activity_places.add(activity_place)
                activity_place.save()
        self.save()
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

    def fetch_raw(self):
        trials = max_trials
        url = f"http://d-nb.info/gnd/{self.gnd_id}"
        while trials:
            try:
                pl_person = PyLobidPerson(url, fetch_related=True)

            #except GNDIdError:
            #except GNDNotFoundError:
            except GNDAPIError:
                trials -= 1
                pass
            break
        self.raw_data = dumps(pl_person.ent_dict)

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

    def get_default_name(self):
        return self.names.get(status=Status.PRIMARY).__str__()

    def __str__(self):
        return f'{self.gnd_id}: {self.get_default_name()}'

    def map_gender(gnd_gender):
        print(gnd_gender)
        if gnd_gender ==  'https://d-nb.info/standards/vocab/gnd/gender#male':
            return Person.Gender.MALE
        if gnd_gender ==  'https://d-nb.info/standards/vocab/gnd/gender#female':
            return Person.Gender.FEMALE
        return Person.Gender.NULL

    def map_date(date_string):
        print(date_string)
        date_list = date_string.split('-')
        if len(date_list) > 3:
            raise Exception('Unknown date format: %s ' % date_string)
        month = '1'
        day = '1'
        if date_list[0].isnumeric():
            year = date_list[0]
        else:
            return null
        if len(date_list) > 1 and date_list[1].isnumeric():
            month = date_list[1]
        if len(date_list) > 2 and date_list[2].isnumeric():
            day = date_list[2]
        return '-'.join([year, month, day])

class Period(models.Model):
    not_before = models.DateField(
            null=True,
            blank=True
        )
    not_after = models.DateField(
            null=True,
            blank=True
        )
    display = models.TextField()

    def render_detailed(self):
        if self.not_before == self.not_after:
            return f"{self.display} ({self.not_before})"
        return f"{self.display} ({self.not_before}&ndash;{self.not_after})"

    def __str__(self):
        return self.display
