from json import dumps, loads
from django.db import transaction
from django.db.models import Max
from django.utils.safestring import mark_safe

class RenderRawJSONMixin:
    def render_raw(self):
        if self.raw_data:
            return dumps(loads(self.raw_data), indent=2, ensure_ascii=False)
        return ''


def snake_to_camel_case(snake_str):
    return ''.join(w.capitalize() for w in snake_str.split('_'))


def camel_to_snake_case(camel_string):
    return ''.join(
            '_' + c.lower()
            if c.isupper() and i > 0
            else c.lower()
            for i, c
            in enumerate(camel_string)
        )

def get_model_link(model):
    if not model:
        return "—"
    if not hasattr(model, 'get_absolute_url'):
        raise NotImplementedError("model does not implement get_absolute_url")
    return mark_safe((
        f'<a href="{model.get_absolute_url()}" '
        f'class=link link-primary>'
        f'{model}</a>'
    )
    )
def swap_order(obj, group_field_name, direction):
    
    ModelClass = obj.__class__
    current_index = obj.order_index
    
    try:
        group_value = getattr(obj, group_field_name)
    except AttributeError:
        return False
    group_filter = {group_field_name: group_value}
    

    if direction == 'up':
        # Objekt mit dem nächstkleineren Index
        # ... (neighbour-Suche) ...
        neighbour = (ModelClass.objects
                     .filter(order_index__lt=current_index, **group_filter)
                     .order_by('-order_index').first()
                     )
    
    elif direction == 'down':
        
        neighbour = (ModelClass.objects
                     .filter(order_index__gt=current_index, **group_filter)
                     .order_by('order_index').first()
                     )
    else:
        return False

    if not neighbour:
        return False
    
    with transaction.atomic():
        
        neighbour_index = neighbour.order_index
        
        # Max-Index in der Gruppe ermitteln und +1 addieren, um Eindeutigkeit zu garantieren
        max_index = ModelClass.objects.filter(**group_filter).aggregate(Max('order_index'))['order_index__max']
        
        # Sicherer temporärer Index: Maximaler Index + 1
        temp_index = max_index + 1
        
        # 1. Item A (obj) auf TEMP setzen (um UNIQUE & CHECK zu umgehen)
        ModelClass.objects.filter(pk=obj.pk).update(order_index=temp_index)

        # 2. Item B (neighbour) auf den alten Index von A setzen
        ModelClass.objects.filter(pk=neighbour.pk).update(order_index=current_index)
        
        # 3. Item A (obj) vom TEMP-Wert auf den alten Index von B setzen
        ModelClass.objects.filter(pk=obj.pk).update(order_index=neighbour_index)
        
    return True
    
