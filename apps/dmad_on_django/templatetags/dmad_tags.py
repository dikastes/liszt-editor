from django import template
from django.conf import settings
from django.template.loader import render_to_string

register = template.Library()

@register.simple_tag(takes_context=True)
def render_data_for_slot(context, slot_name):
    return render_to_string(
        'app_b/snippets/render_injected_data.html',
        {'items': settings.DATA_INJECTION_SLOTS.get(slot_name, {})}
    )
