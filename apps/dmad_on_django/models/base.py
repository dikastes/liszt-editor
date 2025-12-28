from django.db import models
from django.urls import reverse_lazy
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from dominate.tags import div, table, tr, td
from dominate.util import raw
from iso639 import data as iso639_data
from json import loads
from liszt_util.tools import RenderRawJSONMixin


languages = { iso_data['iso639_1'].upper(): iso_data['name'] for iso_data in iso639_data }
Language = {key: languages[key] for key in ['DE', 'FR', 'HU', 'EN']}
max_trials = 3


for key in languages:
    Language[key] = languages[key]


class Status(models.TextChoices):
    PRIMARY = 'P', _('Primary')
    ALTERNATIVE = 'A', _('Alternative')
    TEMPORARY = 'T', _('Temporary')


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


class DisplayableModel(RenderRawJSONMixin, models.Model):
    class Meta:
        abstract = True

    raw_data = models.TextField(null=True)
    rework_in_gnd = models.BooleanField(default=False)
    gnd_id = models.CharField(max_length=20, null=True, blank=True, unique=True)
    comment = models.TextField(null=True, blank=True)
    interim_designator = models.CharField(
        max_length=150,
        null=True,
        blank=True
    )
    gnd_subject_category = models.ManyToManyField(GNDSubjectCategory)

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

    class Meta:
        abstract = True
