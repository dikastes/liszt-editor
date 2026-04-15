from django.db import models
from django.db.models import Max
from django.utils.translation import gettext_lazy as _
from abc import ABC, abstractproperty

class Sortable(ABC, models.Model):
    order_index = models.IntegerField(
        default = 0,
        db_index = True,
        verbose_name = _('sorting index')
    )

    @abstractproperty
    def _group_field_names(self):
        pass

    def save(self,*args, **kwargs):
        if self.order_index is None:
            raise NotImplementedError('Please override save in your model')
        super().save(*args, **kwargs)

    class Meta:
        abstract = True
        ordering = ['order_index']
        verbose_name = _('sortable model')
