from django.db import models
from django.db.models import Max

# Create your models here.
class Sortable(models.Model):
    order_index = models.PositiveIntegerField(
        default=0,
        db_index=True,
        verbose_name="Sortier-Index"
    )

    def save(self,*args, **kwargs):
        if self.order_index is None:
            raise NotImplementedError('Please override save in your model')
        super().save(*args, **kwargs)

    class Meta:
        abstract = True
        ordering = ['order_index']
        verbose_name = "Sortierbares Model"