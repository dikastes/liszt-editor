from django.db import models
from django.db.models import Max
from abc import ABC, abstractproperty

# Create your models here.
class Sortable(models.Model):
    order_index = models.PositiveIntegerField(
        default=0,
        db_index=True,
        verbose_name="Sortier-Index"
    )
    
    @abstractproperty
    def _group_field_name(self):
        pass

    def save(self,*args, **kwargs):
        if self.order_index is None:
            raise NotImplementedError('Please override save in your model')
        super().save(*args, **kwargs)

    class Meta:
        abstract = True
        ordering = ['order_index']
        verbose_name = "Sortierbares Model"