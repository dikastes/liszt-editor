from django import template
from django.conf import settings
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag(takes_context=True)
def render_editor_mode_warning(context):
    prefix = '<span> Editor-Modus: </span>'
    mode = f'<em class="ml-5"> {settings.EDITOR_MODE.upper()} </em>'
    message = '<span> Ihre Daten werden nicht gesichert. </span>'
    if settings.EDITOR_MODE.lower() == 'production':
        return ''
    return mark_safe(f'<div class="bg-primary text-primary-content px-5 flex"><div class="flex-1">{prefix}{mode}</div><div class="flex-0">{message}</div></div>')

