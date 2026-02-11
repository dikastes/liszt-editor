from haystack import indexes
from .models import Work, Expression, Manifestation, Item, Letter


class WorkIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(
            document=True,
            use_template=True
        )

    def get_model(self):
        return Work

    def index_queryset(self, using=None):
        return self.get_model().objects


class ManifestationIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.NgramField(
            document=True,
            use_template=True
        )
    signature = indexes.CharField(
            model_attr = 'get_current_signature'
        )
    is_singleton = indexes.BooleanField(model_attr = 'is_singleton')
    is_collection = indexes.BooleanField(model_attr = 'is_collection')

    def get_model(self):
        return Manifestation

    def index_queryset(self, using=None):
        return self.get_model().objects


class ExpressionIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(
            document=True,
            use_template=True
        )

    def get_model(self):
        return Expression

    def index_queryset(self, using=None):
        return self.get_model().objects


class ItemIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.NgramField(
            document=True,
            use_template=True
        )
    manifestation_is_singleton = indexes.BooleanField(model_attr = 'manifestation__is_singleton')

    def get_model(self):
        return Item

    def index_queryset(self, using=None):
        return self.get_model().objects


class LetterIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.NgramField(
            document=True,
            use_template=True
        )

    def get_model(self):
        return Letter

    def index_queryset(self, using=None):
        return self.get_model().objects
