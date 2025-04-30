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