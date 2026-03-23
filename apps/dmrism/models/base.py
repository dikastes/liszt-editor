from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe


class WemiBaseClass(models.Model):
    class Meta:
        abstract = True

    public_comment = models.TextField(
            null = True,
            blank = True,
            verbose_name = _('public comment')
        )

    private_comment = models.TextField(
            null = True,
            blank = True,
            verbose_name = _('private comment')
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
    role = models.CharField(
            max_length=10,
            choices=Role,
            default=Role.COMPOSER,
            verbose_name = _('role')
        )

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
    class LocationType(models.TextChoices):
        PAGE = 'P', _('page')
        COLUMN = 'C', _('column')
        LOT = 'L', _('lot')

    bib = models.ForeignKey(
            'bib.ZotItem',
            on_delete=models.CASCADE,
        )
    location = models.CharField(
            max_length = 20,
            null = True,
            blank = True,
            verbose_name = _('bib location')
        )
    location_type = models.CharField(
            max_length = 1,
            choices = LocationType,
            default = LocationType.PAGE,
            verbose_name = _('bib location type')
        )


class RelatedEntity(models.Model):
    class Meta:
        abstract = True

    class Label(models.TextChoices):
        PARENT = 'PR', _('Parent')
        RELATED = 'RE', _('Related')

    comment = models.TextField(
            null=True,
            blank=True,
            verbose_name = _('comment')
        )
    label = models.CharField(
            max_length=2,
            choices=Label,
            default=Label.PARENT,
            verbose_name = _('label')
        )

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
            blank = True,
            verbose_name = _('medium')
        )
    dubious_writer = models.BooleanField(
            default = False,
            verbose_name = _('dubious writer')
        )

    def str_with_link(self):
        try:
            if self.dubious_writer:
                return f"[{self.writer.str_with_link()}] ({self.medium})"
            return f"{self.writer.str_with_link()} ({self.medium})"
        except AttributeError:
            if self.dubious_writer:
                return f'[{self.writer.__str__()}] ({self.medium})'
            return f'{self.writer.__str__()} ({self.medium})'

    def __str__(self):
        if self.dubious_writer:
            return f"[{self.writer.__str__()}] ({self.medium})"
        return f"{self.writer.__str__()} ({self.medium})"


class BaseDedication(models.Model):
    class Meta:
        abstract = True

    period = models.OneToOneField(
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
            blank = True,
            verbose_name = _('dedication text')
        )

    def __str__(self):
        diplomatic_dedication = self.diplomatic_dedication or _('<< new dedication >>')

        colon = ''
        if self.place or self.period and self.period.display:
            colon = ':'

        if self.period and self.period.display:
            if self.place:
                period = f' ({self.period})'
            else:
                period = str(self.period)
        else:
            period = ''

        place = ''
        if self.place:
            place = self.place.get_default_name()

        return f'{place}{period}{colon} {diplomatic_dedication}'


class BasePersonDedication(BaseDedication):
    class Meta:
        abstract = True

    dedicatee = models.ForeignKey(
            'dmad.Person',
            on_delete = models.SET_NULL,
            null = True,
            related_name = '%(class)s'
        )

    def __str__(self):
        super_str = super().__str__()

        if self.dedicatee:
            return f'{super_str} ({self.dedicatee.get_default_name()})'

        return super_str


class BaseCorporationDedication(BaseDedication):
    class Meta:
        abstract = True

    dedicatee = models.ForeignKey(
            'dmad.Corporation',
            on_delete = models.SET_NULL,
            null = True,
            related_name = '%(class)s'
        )

    def __str__(self):
        super_str = super().__str__()

        if self.dedicatee:
            return f'{super_str} ({self.dedicatee.get_default_name()})'

        return super_str
