from django.urls import path, include

from .. import views

app_name='edwoca'

urlpatterns = [
    path('', views.index, name = 'index'),
    path('works/', include('edwoca.urls.work')),
    path('expressions/', include('edwoca.urls.expression')),
    path('manifestations/', include('edwoca.urls.manifestation')),
    path('items/', include('edwoca.urls.item')),
    path('composites/', include('edwoca.urls.composite')),
    path('letters/', include('edwoca.urls.letter')),
    path('libraries/', include('edwoca.urls.library')),
    path('htmx/search', views.htmx_search, name = 'htmx_search'),
    path('htmx/update', views.htmx_update, name = 'htmx_update'),
]
