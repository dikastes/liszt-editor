from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from dmad_on_django.models import Status, Language

class WemiBaseClass(models.Model):
    class Meta:
        abstract = True

    public_comment = models.TextField(
            null = True
        )

    private_comment = models.TextField(
            null = True
        )

    def get_absolute_url(self):
        model = self.__class__.__name__.lower()
        return reverse(f'edwoca:{model}_update', kwargs={'pk': self.id})

    def get_alt_titles(self):
        return ', '.join(alt_title.title for alt_title in self.titles.filter(status=Status.ALTERNATIVE))

    def get_pref_title(self):
        # Fetch all titles related to this instance in one query
        titles = self.titles.all()

        primary_title = next((t.title for t in titles if t.status == Status.PRIMARY), None)
        if primary_title:
            return primary_title

        temporary_title = next((t.title for t in titles if t.status == Status.TEMPORARY), None)
        if temporary_title:
            return f"{temporary_title.title} (T)"

        alternative_title = next((t.title for t in titles if t.status == Status.ALTERNATIVE), None)
        if alternative_title:
            return f"{alternative_title.title} (A)"

        return '<ohne Titel>'


class BaseContributor(models.Model):
    class Meta:
        abstract = True

    class Role(models.TextChoices):
        COMPOSER = 'CP', _('Composer')
        WRITER = 'WR', _('Writer')
        TRANSLATOR = 'TR', _('Translator')
        POET = 'PT', _('Poet')
        DEDICATEE = 'DD', _('Dedicatee')

    person = models.ForeignKey(
        'dmad.Person',
        on_delete=models.CASCADE,
        related_name='%(class)s_set' # Added dynamic related_name
    )
    role = models.CharField(max_length=10, choices=Role, default=Role.COMPOSER)

    def to_mei(self):
        contributor = ET.Element('persName')
        contributor.attrib['role'] = self.role
        contributor.attrib['auth'] = 'GND'
        contributor.attrib['auth.uri'] = 'd-nb.info/gnd'
        contributor.attrib['codedval'] = self.person.gnd_id
        contributor.text = self.person.name

        return contributor

    def __str__(self):
        return f"{self.person} ({self.role})"


class BaseBib(models.Model):
    class Meta:
        abstract = True

    bib = models.ForeignKey(
        'bib.ZotItem',
        on_delete=models.CASCADE,
        #related_name='contributed_to'
    )


class RelatedEntity(models.Model):
    class Meta:
        abstract = True

    class Label(models.TextChoices):
        PARENT = 'PR', _('Parent')
        RELATED = 'RE', _('Related')

    comment = models.TextField(
            null=True,
            blank=True
        )
    label = models.CharField(max_length=2,choices=Label,default=Label.PARENT)

    def is_upperclass(self):
        return self.label in {
            self.Label.PARENT,
            self.Label.RELATED
        }


class EventContributor(models.Model):
    class Role(models.TextChoices):
        COMPOSER = 'CP', _('Composer')
        WRITER = 'WR', _('Writer')
        TRANSLATOR = 'TR', _('Translator')
        POET = 'PT', _('Poet')
        DEDICATEE = 'DD', _('Dedicatee')

    event = models.ForeignKey(
        'Event',
        on_delete=models.CASCADE
    )
    person = models.ForeignKey(
        'dmad.Person',
        on_delete=models.CASCADE
    )
    role = models.CharField(max_length=10, choices=Role, default=Role.COMPOSER)


class WemiTitle(models.Model):
    class Meta:
        ordering = ['title']
        abstract = True

    title = models.CharField(max_length=100)
    status = models.CharField(max_length=1,choices=Status,default=Status.PRIMARY)
    language = models.CharField(max_length=15, choices=Language, default=Language['DE'])

    def __str__(self):
        return self.title

    def to_mei(self):
        title = ET.Element('title')
        if self.status == Status.ALTERNATIVE:
            title.attrib['type'] = 'alternative'
        title.text = self.title
        title.attrib['lang'] = to_iso639_1(self.language)
        return title


class Event(models.Model):
    class Type(models.TextChoices):
        PUBLISHED = 'PUB', _('Published')

    period = models.OneToOneField(
            'dmad.Period',
            on_delete=models.SET_NULL,
            null = True,
            blank = True,
            related_name = 'event'
        )
    event_type = models.CharField(
            max_length=10,
            choices=Type,
            default=Type.PUBLISHED
        )
    contributors = models.ManyToManyField(
            'dmad.Person',
            through = 'EventContributor'
        )
    place = models.ForeignKey(
            'dmad.Place',
            on_delete=models.SET_NULL,
            null = True
        )
