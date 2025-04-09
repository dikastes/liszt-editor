from django.urls import path

from . import views

app_name='edwoca'

entities = {
        'work': '',
        'work_title': 'work',
        'work_bib': 'work',
        'related_work': 'work',
        'work_contributor': 'work',
        'expression': 'work',
        'expression_title': 'expression',
        'expression_period': 'expression',
        'expression_contributor': 'expression',
        'manifestation': '',
        'manifestation_contributor': 'manifestation',
        #'manifestation_title': 'manifestation',
        'related_manifestation': 'manifestation',
        'item': 'manifestation',
        'item_contributor': 'item',
        #'item_title': 'item',
        'provenance_state': 'item'
    }

urlpatterns = [
        path('', views.IndexView.as_view(), name = 'index'),
        path('persons', views.person_list, name = 'person_list'),
        path('works/<int:pk>', views.WorkDetailView.as_view(), name = 'work_detail'),
        path('manifestations/<int:pk>', views.ManifestationDetailView.as_view(), name = 'manifestation_detail')
    ]

for entity in entities:
    entity_class = ''.join(e.capitalize() for e in entity.split('_'))
    if entities[entity] == '':
        related_class_id = ''
    else:
        related_class_id = f"/<int:{entities[entity]}_id>"

    urlpatterns.append(
        path(
                f"{entity}/create{related_class_id}",
                getattr(views, f"{entity_class}CreateView").as_view(),
                name = f"{entity}_create"
            )
        )

    for action in ['update', 'delete']:
        urlpatterns.append(
            path(
                    f"{entity}/{action}/<int:pk>",
                    getattr(views, f"{entity_class}{action.capitalize()}View").as_view(),
                    name = f"{entity}_{action}"
                )
            )
"""
urlpatterns = [
        path('', views.IndexView.as_view(), name = 'index'),
        path('works/<int:pk>', views.WorkDetailView.as_view(), name = 'work_detail'),
        path('works/update/<int:pk>', views.WorkUpdateView.as_view(), name = 'work_update'),
        path('works/new', views.WorkCreateView.as_view(), name = 'work_create'),
        path('works/delete/<int:pk>', views.WorkDeleteView.as_view(), name = 'work_delete'),
        path('worktitles/new/<int:work_id>', views.WorkTitleCreateView.as_view(), name = 'work_title_create'),
        path('worktitles/update/<int:pk>', views.WorkTitleUpdateView.as_view(), name = 'work_title_update'),
        path('worktitles/delete/<int:pk>', views.WorkTitleDeleteView.as_view(), name = 'work_title_delete'),
        path('relatedwork/new/<int:work_id>', views.RelatedWorkCreateView.as_view(), name = 'related_work_create'),
        path('relatedwork/update/<int:pk>', views.RelatedWorkUpdateView.as_view(), name = 'related_work_update'),
        path('relatedwork/delete/<int:pk>', views.RelatedWorkDeleteView.as_view(), name = 'related_work_delete'),
        path('contributor/new/<int:work_id>', views.ContributorCreateView.as_view(), name = 'contributor_create'),
        path('contributor/update/<int:pk>', views.ContributorUpdateView.as_view(), name = 'contributor_update'),
        path('contributor/delete/<int:pk>', views.ContributorDeleteView.as_view(), name = 'contributor_delete'),
        path('expression_period/new/<int:expression_id>', views.ExpressionPeriodCreateView.as_view(), name = 'expression_period_create'),
        path('expression_period/update/<int:pk>', views.ExpressionPeriodUpdateView.as_view(), name = 'expression_period_update'),
        path('expression_period/delete/<int:pk>', views.ExpressionPeriodDeleteView.as_view(), name = 'expression_period_delete'),
        path('expression_title/new/<int:expression_id>', views.ExpressionTitleCreateView.as_view(), name = 'expression_title_create'),
        path('expression_title/update/<int:pk>', views.ExpressionTitleUpdateView.as_view(), name = 'expression_title_update'),
        path('expression_title/delete/<int:pk>', views.ExpressionTitleDeleteView.as_view(), name = 'expression_title_delete'),
        path('expression_contributor/new/<int:expression_id>', views.ExpressionContributorCreateView.as_view(), name = 'expression_contributor_create'),
        path('expression_contributor/update/<int:pk>', views.ExpressionContributorUpdateView.as_view(), name = 'expression_contributor_update'),
        path('expression_contributor/delete/<int:pk>', views.ExpressionContributorDeleteView.as_view(), name = 'expression_contributor_delete'),
        path('expression/new/<int:work_id>', views.ExpressionCreateView.as_view(), name = 'expression_create'),
        path('expression/update/<int:pk>', views.ExpressionUpdateView.as_view(), name = 'expression_update'),
        path('expression/delete/<int:pk>', views.ExpressionDeleteView.as_view(), name = 'expression_delete'),
    ]
"""
