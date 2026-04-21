from django.urls import path
from .. import views

urlpatterns = [
    path('', views.CompositeListView.as_view(), name = 'composite_list'),
    path('search', views.CompositeSearchView.as_view(), name = 'composite_search'),
    path('<int:pk>/delete', views.CompositeDeleteView.as_view(), name = 'composite_delete'),
    path('new', views.composite_create, name = 'composite_create'),
    path('<int:pk>/title', views.composite_title_update, name = 'composite_title'),
    path('composite_title/<int:pk>/delete', views.CompositeTitleDeleteView.as_view(), name = 'composite_title_delete'),
    path('<int:pk>/add_title', views.composite_title_create, name = 'composite_title_add'),
    path('<int:pk>/relations', views.CompositeRelationsUpdateView.as_view(), name = 'composite_relations'),
    path('<int:pk>/history/', views.CompositeHistoryUpdateView.as_view(), name='composite_history'),
    path('<int:pk>/provenance/', views.composite_provenance, name='composite_provenance'),
]
