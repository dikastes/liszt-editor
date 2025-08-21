from django.urls import path, include
from liszt_util.tools import snake_to_camel_case

from . import views

app_name='dmad_on_django'

entities = [
        'person',
        #'org',
        'place',
        'work',
        'subject_term',
        'corporation'
    ]
id_bearing_actions = [ 
        'update', 
        #'delete', 
        'link', 
        'unlink',
        'pull'
    ]
urlpatterns = [
        path('', views.index, name = 'index'),
        path('search-gnd/<str:entity_type>/<str:search_string>', views.search_gnd, name = 'search_gnd'),
        path('search/', include('haystack.urls'))
    ]

for entity in entities:
    urlpatterns.append(
        path(
            f"{entity}s/list",
            getattr(views, f"{snake_to_camel_case(entity)}SearchView").as_view(),
            name = f"{entity}_list"
            )
        )
    urlpatterns.append(
        path(
            f"{entity}s/list/<str:type>",
            getattr(views, f"{snake_to_camel_case(entity)}SearchView").as_view(),
            name = f"{entity}_list"
            )
        )
    urlpatterns.append(
        path(
            f"{entity}s/create",
            getattr(views, f"{snake_to_camel_case(entity)}CreateView").as_view(),
            name = f"{entity}_create"
            )
        )
    for action in id_bearing_actions:
        urlpatterns.append(
            path(
                f"{entity}s/{action}/<int:pk>",
                getattr(views, f"{snake_to_camel_case(entity)}{action.capitalize()}View").as_view(),
                name = f"{entity}_{action}"
                )
            )
