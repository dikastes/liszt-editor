from django import template

register = template.Library()

@register.simple_tag
def get_message_colors(tag):
    """
    Gibt ein Dictionary mit Hex-Farben für Inline-Styles zurück,
    basierend auf dem Django Message-Tag.
    """
    # Mapping von Django-Tags auf Farbpaletten (Background, Text, Border)
    colors = {
        'success': {
            'bg': '#dcfce7', # Hellgrün
            'cl': '#166534', # Dunkelgrün
            'br': '#bbf7d0'  # Mittelgrün
        },
        'error': {
            'bg': '#fee2e2', # Hellrot
            'cl': '#991b1b', # Dunkelrot
            'br': '#fecaca'  # Mittelrot
        },
        'warning': {
            'bg': '#fef9c3', # Hellgelb
            'cl': '#854d0e', # Braun/Dunkelgelb
            'br': '#fef08a'  # Mittelgelb
        },
        'info': {
            'bg': '#dbeafe', # Hellblau
            'cl': '#1e40af', # Dunkelblau
            'br': '#bfdbfe'  # Mittelblau
        }
    }
    
    # Falls ein unbekannter Tag kommt, nimm 'info' als Fallback
    return colors.get(tag, colors['info'])