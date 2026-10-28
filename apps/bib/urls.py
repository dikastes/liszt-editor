# -*- coding: utf-8 -*-
from django.urls import path
from . import views
from . import dal_views
from edwoca.views.manifestation.common import bib_update_view

app_name = 'bib'

urlpatterns = [
    path('', views.Index.as_view(), name="index"),
    path('update/', views.update, name="update"),
    path('delete/', views.delete, name="delete"),
    path('import/', views.import_complete, name="import"),
    path('import_bulk/<int:bulk>/', views.import_bulk, name="import_bulk"),
    path('index_info/', views.index_info, name="index_info"),
    path('zotitem-autocomplete/', dal_views.ZotItemAC.as_view(),
        name='zotitem-autocomplete',
    ),
    path('bibupdate/', bib_update_view, name="bib_update_celery"),
]
