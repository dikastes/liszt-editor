from json import dumps, loads

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
