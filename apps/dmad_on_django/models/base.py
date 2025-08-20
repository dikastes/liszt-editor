from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse_lazy
from django.utils.safestring import mark_safe
from iso639 import data as iso639_data
from dominate.tags import div, table, tr, td
from dominate.util import raw
from json import dumps, loads


max_trials = 3


languages = { iso_data['iso639_1'].upper(): iso_data['name'] for iso_data in iso639_data }

Language = {key: languages[key] for key in ['DE', 'FR', 'HU', 'EN']}

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
    def create_or_link(json):

        try:
            category = json['gndSubjectCategory'][0]

        except KeyError:
            return None
        

        try:
            return GNDSubjectCategory.objects.get(link=category['id'])
        except GNDSubjectCategory.DoesNotExist:
            subjectcategory = GNDSubjectCategory()
            subjectcategory.link = category['id']
            subjectcategory.label = category['label']
            subjectcategory.save()
            return subjectcategory

    def get_subject_category_table(entity):

        try:
            link = entity.link
            label = entity.label
        except AttributeError:
            return []
        
        return [("GND Sachgruppe",
                  f'<a href="{link}"target = "_blank" class = "link link-primary">{label}</a>')]

    def __str__(self):
        return self.label
    
class DisplayableModel(models.Model):
    
    raw_data = models.TextField(null=True)
    rework_in_gnd = models.BooleanField(default=False)
    gnd_id = models.CharField(max_length=20, null=True, blank=True, unique=True)
    comment = models.TextField(null=True, blank=True)
    interim_designator = models.CharField(
        max_length=150,
        null=True,
        blank=True
    )
    gnd_subject_category = models.ForeignKey(
        GNDSubjectCategory,
        on_delete=models.SET_NULL,
        null=True
    )

    def render_raw(self):
        return dumps(loads(self.raw_data), indent=2, ensure_ascii=False)

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
        raise NotImplemented("Please override get_table")

    
    class Meta:
        abstract = True
        
