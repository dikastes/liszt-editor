from django.db import models
from json import loads

class GeographicAreaCode(models.Model):
    code = models.CharField(max_length=10)

    @staticmethod
    def create_from_string(code, entity):
        entity_class = entity.__class__.__name__
        instance = globals().get(f'{entity_class}GeographicAreaCode')()
        instance.code = code
        setattr(instance, entity_class.lower(), entity)
        return instance

    @staticmethod
    def get_area_code_table(areacodes):
        return [("Geographic Area Code",code.code)
                 for code in areacodes.all()]
    
    @staticmethod
    def create_geographic_area_codes(entity):
        
        json = loads(entity.raw_data)
        class_name = entity.__class__.__name__ 
        instance = globals().get(f'{class_name}GeographicAreaCode')()
        try:
            for code in json['geographicAreaCode']:
                area_code = instance.create_from_string(
                  code['id'].split('#')[1],
                 entity
                )
            area_code.save()
        except KeyError:
            pass

    class Meta:
        abstract = True

class PlaceGeographicAreaCode(GeographicAreaCode):
    place = models.ForeignKey(
        'Place',
        on_delete=models.CASCADE,
        related_name='geographic_area_codes',
        null=True
    )

class PersonGeographicAreaCode(GeographicAreaCode):
    person = models.ForeignKey(
        'Person',
        on_delete=models.CASCADE,
        related_name='geographic_area_codes',
        null=True
    )

class WorkGeographicAreaCode(GeographicAreaCode):
    work = models.ForeignKey(
        'Work',
        on_delete=models.CASCADE,
        related_name='geographic_area_codes',
        null=True
    )