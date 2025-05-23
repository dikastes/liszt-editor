from haystack import indexes
from .models import Person

class PersonIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.NgramField(
            document=True,
            use_template=True
        )
    entity_type = indexes.CharField(
            use_template=True,
            faceted=True
        )
    rework_in_gnd = indexes.BooleanField(
            model_attr='rework_in_gnd',
            faceted=True,
            indexed=False
        )
    is_stub = indexes.BooleanField(
            use_template=True,
            faceted=True
        )

    def get_model(self):
        return Person

    def index_queryset(self, using=None):
        return self.get_model().objects
