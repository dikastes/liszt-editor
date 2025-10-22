from json import dumps, loads
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
    ))