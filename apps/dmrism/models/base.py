from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


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
        return reverse(f'dmrism:{model}_update', kwargs={'pk': self.id})


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


"""
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
"""


class BaseHandwriting(models.Model):
    class Meta:
        abstract = True

    writer = models.ForeignKey(
            'dmad.Person',
            on_delete = models.SET_NULL,
            null = True
        )
    medium = models.CharField(
            max_length = 100,
            null = True,
            blank = True
        )
    dubious_writer = models.BooleanField(default = False)

    def __str__(self):
        if self.dubious_writer:
            return f"[{self.writer.__str__()}] ({self.medium})"
        return f"{self.writer.__str__()} ({self.medium})"


class BaseDedication(models.Model):
    class Meta:
        abstract = True

    period = models.ForeignKey(
            'dmad.Period',
            on_delete = models.SET_NULL,
            null = True,
            related_name = '%(class)s'
        )
    place = models.ForeignKey(
            'dmad.Place',
            on_delete = models.SET_NULL,
            null = True,
            related_name = '%(class)s'
        )
    diplomatic_dedication = models.TextField(
            null = True,
            blank = True
        )


class BasePersonDedication(BaseDedication):
    class Meta:
        abstract = True

    dedicatee = models.ForeignKey(
            'dmad.Person',
            on_delete = models.SET_NULL,
            null = True,
            related_name = '%(class)s'
        )


class BaseCorporationDedication(BaseDedication):
    class Meta:
        abstract = True

    dedicatee = models.ForeignKey(
            'dmad.Corporation',
            on_delete = models.SET_NULL,
            null = True,
            related_name = '%(class)s'
        )
