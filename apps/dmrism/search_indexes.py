from haystack import indexes
from .models import Manifestation, Item

class ManifestationIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.NgramField(
            document=True,
            use_template=True
        )

    def get_model(self):
        return Manifestation

    def index_queryset(self, using=None):
        return self.get_model().objects


class ItemIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.NgramField(
            document=True,
            use_template=True
        )

    def get_model(self):
        return Item

    def index_queryset(self, using=None):
        return self.get_model().objects
