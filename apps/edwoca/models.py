from django.urls import reverse
from django.db import models
from django.utils.translation import gettext_lazy as _
from dmad_on_django.models import Language, Status, Person, Period
from bib.models import ZotItem
from xml.etree import ElementTree as ET
from iso639 import to_iso639_1

# Create your models here.
class Work(models.Model):
    class Meta:
        ordering = ['work_catalog_number']

    gnd_id = models.CharField(
            max_length=20,
            unique=True,
            null=True,
            blank=True
        )
    work_catalog_number = models.CharField(
            max_length=20,
            unique=True,
            null=True,
            blank=True
        )
    related_work = models.ManyToManyField(
            'Work',
            through='RelatedWork'
        )
    history = models.TextField(
            null = True,
            blank = True
        )
    contributors = models.ManyToManyField(
            'dmad.Person',
            through = 'WorkContributor'
        )
    bib = models.ManyToManyField(
            'bib.ZotItem',
            through = 'WorkBib'
        )

    def get_absolute_url(self):
        return reverse('edwoca:work_detail', kwargs={'pk': self.id})

    def get_alt_titles(self):
        return ', '.join(alt_title.title for alt_title in self.titles.filter(status=Status.ALTERNATIVE))

    def get_pref_title(self):
        try:
            return self.titles.get(status=Status.PRIMARY).title
        except:
            return '<ohne Titel>'

    def __str__(self):
        return f"{self.work_catalog_number}: {self.get_pref_title()}"

    def to_mei(self):
        work = ET.Element('work')

        for title in self.titles.all():
            work.append(title.to_mei())

        gnd_id = ET.Element('identifier')
        gnd_id.attrib['label'] = 'GND'
        gnd_id.text = self.gnd_id

        work_catalog_number = ET.Element('identifier')
        work_catalog_number.attrib['label'] = 'LQWV'
        work_catalog_number.text = self.work_catalog_number

        history = ET.Element('history')
        history.text = self.history

        contributors = ET.Element('contributor')
        for contributor in self.contributors.all():
            contributors.append(contributor)

        work.append(gnd_id)
        work.append(work_catalog_number)
        work.append(history)

        return work


class WorkContributor(models.Model):
    class Role(models.TextChoices):
        COMPOSER = 'CP', _('Composer')
        WRITER = 'WR', _('Writer')
        TRANSLATOR = 'TR', _('Translator')
        POET = 'PT', _('Poet')
        DEDICATEE = 'DD', _('Dedicatee')

    work = models.ForeignKey(
        'Work',
        on_delete=models.CASCADE,
        #related_name='contributors'
    )
    person = models.ForeignKey(
        'dmad.Person',
        on_delete=models.CASCADE,
        #related_name='contributed_to'
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


class WorkBib(models.Model):
    work = models.ForeignKey(
        'Work',
        on_delete=models.CASCADE,
        #related_name='contributors'
    )
    bib = models.ForeignKey(
        'bib.ZotItem',
        on_delete=models.CASCADE,
        #related_name='contributed_to'
    )


class ExpressionContributor(models.Model):
    class Role(models.TextChoices):
        COMPOSER = 'CP', _('Composer')
        WRITER = 'WR', _('Writer')
        TRANSLATOR = 'TR', _('Translator')
        POET = 'PT', _('Poet')
        DEDICATEE = 'DD', _('Dedicatee')

    expression = models.ForeignKey(
        'Expression',
        on_delete=models.CASCADE
    )
    person = models.ForeignKey(
        'dmad.Person',
        on_delete=models.CASCADE
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


class RelatedWork(models.Model):
    class Label(models.TextChoices):
        PARENT = 'PR', _('Parent')
        RELATED = 'RE', _('Related')

    source_work = models.ForeignKey(
            'Work',
            on_delete=models.CASCADE,
            related_name="source_work_of"
        )
    target_work = models.ForeignKey(
            'Work',
            on_delete=models.CASCADE,
            related_name="target_work_of"
        )
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


class WorkTitle(models.Model):
    class Meta:
        ordering = ['title']

    title = models.CharField(max_length=100)
    status = models.CharField(max_length=1,choices=Status,default=Status.PRIMARY)
    language = models.CharField(max_length=15, choices=Language, default=Language['DE'])
    work = models.ForeignKey('Work', on_delete=models.CASCADE, related_name='titles')


    def __str__(self):
        return self.title

    def to_mei(self):
        title = ET.Element('title')
        if self.status == Status.ALTERNATIVE:
            title.attrib['type'] = 'alternative'
        title.text = self.title
        title.attrib['lang'] = to_iso639_1(self.language)
        return title


class Expression(models.Model):
    incipit_music = models.TextField()
    incipit_text = models.TextField()
    period = models.OneToOneField(
            'dmad.Period',
            on_delete=models.SET_NULL,
            null = True,
            blank = True,
            related_name = 'expression'
        )
    period_comment = models.TextField()
    history = models.TextField()
    contributors = models.ManyToManyField(
            'dmad.Person',
            through = 'ExpressionContributor'
        )
    work = models.ForeignKey(
            'Work',
            on_delete=models.CASCADE,
            null=True,
            blank=True,
            related_name='expressions'
        )
    expressions = models.ManyToManyField(
            'Manifestation'
        )

    def __str__(self):
        try:
            pref_title = self.titles.get(status=Status.PRIMARY).title
        except:
            pref_title = '<ohne Titel>'
        return pref_title


class ExpressionTitle(models.Model):
    class Meta:
        ordering = ['title']

    title = models.CharField(
            max_length=100
        )
    status = models.CharField(
            max_length=1,
            choices=Status,
            default=Status.PRIMARY
        )
    language = models.CharField(
            max_length=15,
            choices=Language,
            default=Language['DE']
        )
    expression = models.ForeignKey(
            'Expression',
            on_delete=models.CASCADE,
            related_name='titles'
        )

    def __str__(self):
        return self.title

    def to_mei(self):
        title = ET.Element('title')
        if self.status == Status.ALTERNATIVE:
            title.attrib['type'] = 'alternative'
        title.text = self.title
        title.attrib['lang'] = to_iso639_1(self.language)
        return title


class Manifestation(models.Model):
    rism_id = models.CharField(
            unique=True,
            max_length=20,
            null = True,
            blank = True
        )
    plate_number = models.CharField(
            max_length = 10,
            null = True,
            blank = True
        )
    period = models.ForeignKey(
            'dmad.Period',
            on_delete = models.SET_NULL,
            blank = True,
            null = True
        )
    place = models.ForeignKey(
            'dmad.Place',
            on_delete = models.SET_NULL,
            blank = True,
            null = True
        )
    contributors = models.ManyToManyField(
            'dmad.Person',
            through = 'ManifestationContributor'
        )
    manifestations = models.ManyToManyField(
            'Manifestation',
            through = 'RelatedManifestation'
        )


class RelatedManifestation(models.Model):
    class Label(models.TextChoices):
        PARENT = 'PR', _('Parent')
        RELATED = 'RE', _('Related')

    source_manifestation = models.ForeignKey(
            'Manifestation',
            on_delete=models.CASCADE,
            related_name="source_manifestation_of"
        )
    target_manifestation = models.ForeignKey(
            'Manifestation',
            on_delete=models.CASCADE,
            related_name="target_manifestation_of"
        )
    comment = models.TextField(
            null=True,
            blank=True
        )
    label = models.CharField(max_length=2,choices=Label,default=Label.PARENT)


class Item(models.Model):
    cover = models.TextField(
            null = True,
            blank = True
        )
    handwriting = models.CharField(
            max_length=20,
            null=True,
            blank=True
        )
    history = models.TextField(
            null = True,
            blank = True
        )
    iiif_manifest = models.CharField(
            max_length = 50,
            null = True,
            blank = True
        )
    manifestation = models.ForeignKey(
            'Manifestation',
            on_delete = models.CASCADE,
            related_name = 'items'
        )


class ProvenanceState(models.Model):
    owner = models.ForeignKey(
            'dmad.Person',
            on_delete = models.CASCADE
        )
    item = models.ForeignKey(
            'Item',
            on_delete = models.CASCADE,
            related_name = 'provenance'
        )
    comment = models.TextField(
            null = True,
            blank = True
        )
    start = models.ForeignKey(
            'dmad.Period',
            on_delete = models.SET_NULL,
            blank = True,
            null = True,
            related_name = 'provenance_start'
            )
    end = models.ForeignKey(
            'dmad.Period',
            on_delete = models.SET_NULL,
            blank = True,
            null = True,
            related_name = 'provenance_end'
            )

    def __str__(self):
        return f"{ self.owner } (von { self.start } bis { self.end })"


class ManifestationContributor(models.Model):
    class Role(models.TextChoices):
        COMPOSER = 'CP', _('Composer')
        WRITER = 'WR', _('Writer')
        TRANSLATOR = 'TR', _('Translator')
        POET = 'PT', _('Poet')
        DEDICATEE = 'DD', _('Dedicatee')

    manifestation = models.ForeignKey(
        'Manifestation',
        on_delete=models.CASCADE
    )
    person = models.ForeignKey(
        'dmad.Person',
        on_delete=models.CASCADE
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


class RelatedItem(models.Model):
    class Label(models.TextChoices):
        PARENT = 'PR', _('Parent')
        RELATED = 'RE', _('Related')

    source_item = models.ForeignKey(
            'Item',
            on_delete=models.CASCADE,
            related_name="source_item_of"
        )
    target_item = models.ForeignKey(
            'Item',
            on_delete=models.CASCADE,
            related_name="target_item_of"
        )
    comment = models.TextField(
            null=True,
            blank=True
        )
    label = models.CharField(max_length=2,choices=Label,default=Label.PARENT)


