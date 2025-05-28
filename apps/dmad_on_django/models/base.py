from django.db.models import TextChoices, Model
from django.utils.translation import gettext_lazy as _
from django.urls import reverse_lazy
from iso639 import data as iso639_data
from dominate.tags import div, table, tr, td
from json import dumps, loads

max_trials = 3

languages = { iso_data['iso639_1'].upper(): iso_data['name'] for iso_data in iso639_data }
Language = {key: languages[key] for key in ['DE', 'FR', 'HU', 'EN']}
for key in languages:
    Language[key] = languages[key]

class Status(TextChoices):
    PRIMARY = 'P', _('Primary')
    ALTERNATIVE = 'A', _('Alternative')

class DisplayableModel(Model):

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
                    else:
                        tr(td(label), td(str(value) or "—"))

        return str(doc)
    
    class Meta:
        abstract = True
