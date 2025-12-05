from django import template
from django.utils.translation import gettext as _

register = template.Library()

@register.filter
def entity_label(value):
    """
    Wandelt interne Entity-Typen (z. B. 'work', 'expression')
    in übersetzbare Labels um.
    """
    mapping = {
        "work": _("work"),
        "expression": _("expression"),
        "singleton": _("singleton"),
        "manifestation": _("manifestation"),
        "item": _("item"),
        "library": _("library"),
        "letter": _("letter"),
    }
    return mapping.get(value, value)
