from django.db import models
from django.db.models import QuerySet, FilteredRelation, Q, Value
from django.db.models.functions import Coalesce, Lower, NullIf
from django.urls import reverse_lazy
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from dominate.tags import div, table, tr, td
from dominate.util import raw
from iso639 import data as iso639_data
from json import loads
from liszt_util.tools import RenderRawJSONMixin, DisplayableQuerySet


languages = { iso_data['iso639_1'].upper(): iso_data['name'] for iso_data in iso639_data }
Language = {key: languages[key] for key in ['DE', 'FR', 'HU', 'EN']}
max_trials = 3


for key in languages:
    Language[key] = languages[key]


class Status(models.TextChoices):
    PRIMARY = 'P', _('Primary')
    ALTERNATIVE = 'A', _('Alternative')
    TEMPORARY = 'T', _('Temporary')


#class DocumentationStatus(models.TextChoices):
    #DOCUMENTED = 'D', _('documented')
    #INFERRED = 'I', _('inferred')
    #ASSUMED = 'A', _('assumed')


class DocumentationStatusMixin(models.Model):
    class Meta:
        abstract = True

    inferred = models.BooleanField(
            default=False,
            verbose_name = _("inferred")
        )
    assumed = models.BooleanField(
            default=False,
            verbose_name = _("assumed")
        )


class GNDSubjectCategory(models.Model):
    link = models.CharField(max_length=200,unique=True)
    label = models.CharField(max_length=50)

    @staticmethod
    def create_or_link(entity):

        try:
            category = loads(entity.raw_data)['gndSubjectCategory']
        except KeyError:
            return

        for c in category:
            try:
                subject_category = GNDSubjectCategory.objects.get(link=c['id'])
            except GNDSubjectCategory.DoesNotExist:
                subject_category = GNDSubjectCategory()
                subject_category.link = c['id']
                subject_category.label = c['label']
                subject_category.save()

            entity.gnd_subject_category.add(subject_category)

    def get_subject_category_table(entity):

        table = []

        for category in entity.gnd_subject_category.all():

            try:
                link = category.link
                label = category.label

            except AttributeError:
                return []

            table.append(("GND Sachgruppe",
                  f'<a href="{link}"target = "_blank" class = "link link-primary">{label}</a>'))

        return table

    def __str__(self):
        return self.label


class TimestampedModel(models.Model):
    class Meta:
        abstract = True
    first_save = models.DateTimeField(
            auto_now_add = True,
            verbose_name = _('first save'),
            null = True
        )
    last_save = models.DateTimeField(
            auto_now = True,
            verbose_name = _('last save'),
            null = True
        )
    first_editor = models.CharField(
            max_length = 50,
            blank = True,
            verbose_name = _('first editor'),
            default = ''
        )


class DisplayableModel(RenderRawJSONMixin, TimestampedModel):
    class Meta:
        abstract = True

    objects = DisplayableQuerySet.as_manager()

    raw_data = models.TextField(
            null = True,
            verbose_name = _('raw data')
        )
    rework_in_gnd = models.BooleanField(
            default = False,
            verbose_name = _('rework in GND')
        )
    gnd_id = models.CharField(
            max_length = 20,
            null = True,
            blank = True,
            unique = True,
            verbose_name = _('GND ID')
        )
    comment = models.TextField(
            null = True,
            blank = True,
            verbose_name = _('comment')
        )
    interim_designator = models.CharField(
        max_length = 150,
        null = True,
        blank = True,
        verbose_name = _('interim designator')
    )
    gnd_subject_category = models.ManyToManyField(GNDSubjectCategory)

    ordering_fields = {
        'name': (['sort_name'], _('name'), _('A-Z'), _('Z-A')),
        'modified': (['last_save'], _('last save'), _('oldest first'), _('newest first')),
    }

    @classmethod
    def get_ordering_annotations(cls):
        return {
            'primary_name': FilteredRelation(
                'names',
                condition=Q(names__status=Status.PRIMARY)
            ),
            'sort_name': Lower(
                Coalesce(
                    NullIf('primary_name__name', Value('')),
                    NullIf('interim_designator', Value('')),
                    Value('zzz')
                )
            ),
        }
    def get_index_title(self):
        return ' '.join(str(name) for name in list(self.names.all()) + [ self.interim_designator ])

    @property
    def name(self):
        if hasattr(self, 'names'):
            return self.names.filter(status=Status.PRIMARY).first()

        raise Exception(f'Class {self.__class__.__name__} has no names property.')

    def is_stub(self):
        if self.gnd_id and self.gnd_id != '':
            return False
        return True

    def concise(self):
        if (name := self.names.filter(status=Status.PRIMARY).first()):
            if hasattr(name, 'name'):
                return name.name
            return f'{name.first_name} {name.last_name}'

    def get_alt_names(self):
        return self.names.filter(status=Status.ALTERNATIVE)

    def as_daisy(self):
        doc = div(_class="collapse-content")

        with doc:
            with table(cls="table table-zebra"):
                for label, value in self.get_table():
                    if str(value) == "None":
                        tr(td(label), td("—"))
                    elif isinstance(value, str) and value.strip().startswith("<a "):
                       tr(td(label), td(raw(value)))
                    else:
                      tr(td(label), td(str(value) or "—"))

        return mark_safe(str(doc))

    def get_table(self):
        raise NotImplementedError("Please override get_table")

    def get_search_placeholder():
        raise NotImplementedError("Please override get_search_placeholder")

    def __str__(self):
        if self.gnd_id:
            if self.get_default_name():
                return f'{self.get_default_name()} ({self.gnd_id})'
            error = _('<< error >>')
            return f'{error} ({self.gnd_id})'

        stub = _('(stub)')
        return f'{self.interim_designator} {stub}'

    class Meta:
        abstract = True
