from haystack import indexes
from .models import Person, Place, SubjectTerm, Work, Corporation

class FacetsMixin(indexes.Indexable):
    rework_in_gnd = indexes.BooleanField(
            model_attr='rework_in_gnd',
            faceted=True,
            indexed=True
        )
    is_stub = indexes.BooleanField(
            model_attr='is_stub',
            faceted=True,
            indexed=True
        )


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
            indexed=True
        )
    is_stub = indexes.BooleanField(
            model_attr='is_stub',
            faceted=True,
            indexed=True
        )

    def get_model(self):
        return Person

    def index_queryset(self, using=None):
        return self.get_model().objects


class PlaceIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.NgramField(
            document=True,
            use_template=True
        )
    rework_in_gnd = indexes.BooleanField(
            model_attr='rework_in_gnd',
            faceted=True,
            indexed=True
        )
    is_stub = indexes.BooleanField(
            model_attr='is_stub',
            faceted=True,
            indexed=True
        )

    def get_model(self):
        return Place

    def index_queryset(self, using=None):
        return self.get_model().objects


class SubjectTermIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.NgramField(
        document=True,
        use_template=True
    )
    rework_in_gnd = indexes.BooleanField(
            model_attr='rework_in_gnd',
            faceted=True,
            indexed=True
        )
    is_stub = indexes.BooleanField(
            model_attr='is_stub',
            faceted=True,
            indexed=True
        )

    def get_model(self):
        return SubjectTerm

    def index_queryset(self, using=None):
        return self.get_model().objects


class WorkIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.NgramField(
        document=True,
        use_template=True
    )
    rework_in_gnd = indexes.BooleanField(
            model_attr='rework_in_gnd',
            faceted=True,
            indexed=True
        )
    is_stub = indexes.BooleanField(
            model_attr='is_stub',
            faceted=True,
            indexed=True
        )

    def get_model(self):
        return Work

    def index_queryset(self, using=None):
        return self.get_model().objects


class CorporationIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.NgramField(
        document=True,
        use_template=True
    )
    rework_in_gnd = indexes.BooleanField(
            model_attr='rework_in_gnd',
            faceted=True,
            indexed=True
        )
    is_stub = indexes.BooleanField(
            model_attr='is_stub',
            faceted=True,
            indexed=True
        )

    def get_model(self):
        return Corporation

    def index_queryset(self, using=None):
        return self.get_model().objects
