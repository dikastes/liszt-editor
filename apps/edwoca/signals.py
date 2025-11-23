from django.db.models.signals import post_delete
from liszt_util.models import Sortable
from django.db.models import F

def close_gap_on_delete(sender, instance, **kwargs):
    if not issubclass(sender, Sortable):
        return

    group_field_name = instance._group_field_name

    try:
        group_object = getattr(instance, group_field_name)
    except AttributeError:
        return
    
    group_filter = {group_field_name: group_object}

    sender.objects.filter(
        **group_filter,
        order_index__gt=instance.order_index
    ).update(order_index=F('order_index') - 1)
