from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _
from iso639 import data as iso639_data

max_trials = 3

languages = { iso_data['iso639_1'].upper(): iso_data['name'] for iso_data in iso639_data }
Language = {key: languages[key] for key in ['DE', 'FR', 'HU', 'EN']}
for key in languages:
    Language[key] = languages[key]

class Status(TextChoices):
    PRIMARY = 'P', _('Primary')
    ALTERNATIVE = 'A', _('Alternative')
