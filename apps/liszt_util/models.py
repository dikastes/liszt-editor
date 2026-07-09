from django.db import models
from django.db.models import Max
from django.utils.translation import gettext_lazy as _
from abc import ABC, abstractmethod

class Sortable(models.Model):
    order_index = models.IntegerField(
        default = 0,
        db_index = True,
        verbose_name = _('sorting index')
    )

    @property
    @abstractmethod
    def _group_field_names(self):
        pass

    def save(self,*args, **kwargs):
        # Index-Zuweisung für neue Items
        reference = None
        current_class = self.__class__

        for group_field_name in self._group_field_names:
            if getattr(self, group_field_name):
                reference = getattr(self, group_field_name)
                field = group_field_name

        if self.pk is None and reference and (self.order_index is None or self.order_index == 0):
            filter = {field: reference}
            max_index = current_class.objects\
                    .filter(**filter)\
                    .aggregate(models.Max('order_index'))\
                    ['order_index__max']

            # Wenn bereits Items existieren, nimm max + 1, sonst bleib bei 0
            if max_index is not None:
                self.order_index = max_index + 1
            else:
                self.order_index = 0

        super().save(*args, **kwargs)

    class Meta:
        abstract = True
        ordering = ['order_index']
        verbose_name = _('sortable model')
