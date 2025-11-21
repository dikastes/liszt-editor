from django.apps import AppConfig
from django.conf import settings
from django.db.models.signals import post_delete

class EdwocaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'edwoca'
    label = 'edwoca'

    def ready(self):

        super().ready()

        from edwoca.signals import close_gap_on_delete
        from liszt_util.models import Sortable

        for model in self.get_models():
            if issubclass(model, Sortable):
                post_delete.connect(close_gap_on_delete, sender=model)
