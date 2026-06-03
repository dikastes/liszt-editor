from haystack import indexes
from .models import ZotItem

class BibIndex(indexes.SearchIndex, indexes.Indexable):
    auto_update = False
    text = indexes.CharField(
            document=True,
            use_template=True
        )
    short_title_normalized = indexes.CharField(
            model_attr = 'get_short_title_normalized',
            indexed = True,
            stored = True
        )

    def get_model(self):
        return ZotItem

    def index_queryset(self, using=None):
        return self.get_model().objects
