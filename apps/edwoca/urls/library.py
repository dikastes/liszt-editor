from django.urls import path
from .. import views

urlpatterns = [
    path('', views.LibraryListView.as_view(), name = 'library_list'),
    path('search', views.LibrarySearchView.as_view(), name = 'library_search'),
    path('create', views.LibraryCreateView.as_view(), name = 'library_create'),
    path('<int:pk>/update', views.LibraryUpdateView.as_view(), name = 'library_update'),
    path('<int:pk>/delete', views.LibraryDeleteView.as_view(), name = 'library_delete'),
    path('<int:pk>/manuscripts', views.LibraryManuscriptsView.as_view(), name = 'library_manuscripts'),
    path('<int:pk>/prints', views.LibraryPrintsView.as_view(), name = 'library_prints'),
]
