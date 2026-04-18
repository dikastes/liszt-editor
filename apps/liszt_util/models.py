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
        # order-index hat default - wird das je None?
        if self.order_index is None:
            raise NotImplementedError('Please override save in your model')
        super().save(*args, **kwargs)

    class Meta:
        abstract = True
        ordering = ['order_index']
        verbose_name = _('sortable model')
