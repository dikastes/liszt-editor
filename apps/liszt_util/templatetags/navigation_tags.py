from django import template
from django.conf import settings
from django.urls import reverse_lazy
from django.utils.safestring import mark_safe

register = template.Library()

@register.inclusion_tag('tags/daisy_main_menu.html', takes_context=True)
def render_main_menu(context):
    """
    Rendert das Hauptmenü basierend auf der GLOBAL_NAVIGATION in den Settings.
    Ermittelt die aktuell aktive App, um den Menüpunkt hervorzuheben.
    """
    request = context.get('request')
    current_app = None
    if request and hasattr(request, 'resolver_match') and request.resolver_match:
        current_app = request.resolver_match.app_name

    return {
        'menu_items': settings.GLOBAL_NAVIGATION,
        'request': request,
        'current_app': current_app, # Für den aktiven Zustand der unteren Navbar
    }

@register.simple_tag(takes_context=True)
def render_main_navbar_link(context):
    """
    Rendert den Link für den App-Namen in der oberen Navbar.
    Verwendet das Label und den Link aus GLOBAL_NAVIGATION für die aktuelle App.
    """
    request = context.get('request')
    current_app = None
    if request and hasattr(request, 'resolver_match') and request.resolver_match:
        current_app = request.resolver_match.app_name

    # Bestimme, welche App-Informationen für den Link verwendet werden sollen.
    # Fallback auf 'edwoca', wenn current_app None ist oder nicht in GLOBAL_NAVIGATION gefunden wird.
    app_key_to_use = current_app
    if app_key_to_use is None or app_key_to_use not in settings.GLOBAL_NAVIGATION:
        app_key_to_use = 'edwoca' # Standard-Fallback-App

    app_info = settings.GLOBAL_NAVIGATION.get(app_key_to_use, {})
    
    # Hole Label und href, mit Fallbacks, falls nicht explizit in den Settings definiert.
    label = app_info.get('label', app_key_to_use) # Fallback auf app_key, falls Label fehlt
    href = app_info.get('href', '#') # Fallback auf '#', falls href fehlt oder None ist

    return mark_safe(f'<a class="btn btn-ghost text-xl rounded-none min-h-inherit" href="{href}">{label}</a>')
