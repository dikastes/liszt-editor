# -*- coding: utf-8 -*-
from django.urls import path
from . import views
from . import dal_views

app_name = 'bib'

urlpatterns = [
    path('', views.Dashboard.as_view(), name="dashboard"),
    path('update/', views.update, name="update"),
    path('delete/', views.delete, name="delete"),
    path('import/', views.import_complete, name="import"),
    path('import_bulk/<int:bulk>/', views.import_bulk, name="import_bulk"),
    path('dashboard_info/', views.dashboard_info, name="dashboard_info"),
    path('zotitem-autocomplete/', dal_views.ZotItemAC.as_view(),
        name='zotitem-autocomplete',
    ),
]
