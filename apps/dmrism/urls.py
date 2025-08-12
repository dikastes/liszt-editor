from django.urls import path

from . import views

app_name='dmrism'

urlpatterns = [
        path('', views.index, name = 'index'),
        path('manifestations', views.ManifestationListView.as_view(), name = 'manifestation_list'),
        path('manifestations/search', views.ManifestationSearchView.as_view(), name = 'manifestation_search'),
        path('manifestations/create', views.ManifestationCreateView.as_view(), name = 'manifestation_create'),
        path('manifestations/<int:pk>', views.ManifestationDetailView.as_view(), name = 'manifestation_detail'),
        path('manifestations/<int:pk>/update', views.ManifestationUpdateView.as_view(), name = 'manifestation_update'),
        path('manifestations/<int:pk>/pull', views.manifestation_pull, name = 'manifestation_pull'),
        path('manifestations/<int:pk>/reject_pull', views.manifestation_reject_pull, name = 'manifestation_reject_pull'),
        path('manifestations/<int:pk>/confirm_pull', views.manifestation_confirm_pull, name = 'manifestation_confirm_pull')
    ]
