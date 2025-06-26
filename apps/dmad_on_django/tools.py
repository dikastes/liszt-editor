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
