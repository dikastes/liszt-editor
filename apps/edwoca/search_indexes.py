from haystack import indexes
from .models import Work, Expression

class WorkIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.NgramField(
            document=True,
            use_template=True
        )

    def get_model(self):
        return Work

    def index_queryset(self, using=None):
        return self.get_model().objects


class ExpressionIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.NgramField(
            document=True,
            use_template=True
        )

    def get_model(self):
        return Expression

    def index_queryset(self, using=None):
        return self.get_model().objects
