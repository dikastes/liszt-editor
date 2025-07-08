from haystack.signals import RealtimeSignalProcessor
from bib.models import ZotItem
from django.db import models
from django.apps import apps

class CustomRealtimeSignalProcessor(RealtimeSignalProcessor):
    def setup(self):
        # Connect signals only for models that are not ZotItem
        for app_config in apps.get_app_configs():
            for model in app_config.get_models():
                if model != ZotItem:
                    models.signals.post_save.connect(self.handle_save, sender=model)
                    models.signals.post_delete.connect(self.handle_delete, sender=model)

    def teardown(self):
        # Disconnect signals for all models (including ZotItem, as it's safer to disconnect all)
        for app_config in apps.get_app_configs():
            for model in app_config.get_models():
                models.signals.post_save.disconnect(self.handle_save, sender=model)
                models.signals.post_delete.disconnect(self.handle_delete, sender=model)