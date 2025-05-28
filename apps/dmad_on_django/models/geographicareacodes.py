from django.db import models

class GeographicAreaCode(models.Model):
    code = models.CharField(max_length=10)

    @staticmethod
    def create_from_string(code, entity):
        entity_class = entity.__class__.__name__
        instance = globals().get(f'{entity_class}GeographicAreaCode')()
        instance.code = code
        setattr(instance, entity_class.lower(), entity)
        return instance

    class Meta:
        abstract = True

class PlaceGeographicAreaCode(GeographicAreaCode):
    place = models.ForeignKey(
        'Place',
        on_delete=models.CASCADE,
        related_name='geographic_area_codes',
        null=True
    )