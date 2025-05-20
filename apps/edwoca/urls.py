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
        path('', views.index, name = 'index'),
        path('works', views.WorkListView.as_view(), name = 'work_list'),
        path('works/search', views.WorkSearchView.as_view(), name = 'work_search'),
        path('works/new', views.WorkCreateView.as_view(), name = 'work_create'),
        path('works/update/<int:pk>', views.WorkUpdateView.as_view(), name = 'work_update'),
        path('works/<int:pk>/title', views.WorkTitleUpdateView.as_view(), name = 'work_title'),
        path('works/<int:pk>/relations', views.WorkRelationsUpdateView.as_view(), name = 'work_relations'),
        path('works/<int:pk>/relations/addrelatedwork/<int:target_work>', views.RelatedWorkAddView.as_view(), name = 'related_work_add'),
        path('works/removerelatedwork/<int:pk>', views.RelatedWorkRemove.as_view(), name = 'related_work_remove'),
        path('works/<int:pk>/contributors', views.WorkContributorsUpdateView.as_view(), name = 'work_contributors'),
        path('works/<int:pk>/relatedworks', views.WorkRelatedWorksUpdateView.as_view(), name = 'work_relatedworks'),
        path('works/<int:pk>/history', views.WorkHistoryUpdateView.as_view(), name = 'work_history'),
        path('works/<int:pk>/bibliography', views.WorkBibliographyUpdateView.as_view(), name = 'work_bibliography'),
        path('works/<int:pk>/comment', views.WorkCommentUpdateView.as_view(), name = 'work_comment'),
        path('expressions/<int:pk>/update', views.ExpressionUpdateView.as_view(), name = 'expression_update'),
        path('expressions/<int:pk>/delete', views.ExpressionDeleteView.as_view(), name = 'expression_delete'),
        path('expressions/<int:pk>/title', views.ExpressionTitleUpdateView.as_view(), name = 'expression_title'),
        path('expressions/<int:pk>/relations', views.ExpressionRelationsUpdateView.as_view(), name = 'expression_relations'),
        path('expressions/<int:pk>/relations/addrelatedexpression/<int:target_expression>', views.RelatedExpressionAddView.as_view(), name = 'related_expression_add'),
        path('expressions/removerelatedexpression/<int:pk>', views.RelatedExpressionRemoveView.as_view(), name = 'related_expression_remove'),
        path('expressions/<int:pk>/contributors', views.ExpressionContributorsUpdateView.as_view(), name = 'expression_contributors'),
        path('expressions/<int:pk>/history', views.ExpressionHistoryUpdateView.as_view(), name = 'expression_history'),
        path('expressions/<int:pk>/categorisation', views.ExpressionCategorisationUpdateView.as_view(), name = 'expression_categorisation'),
        path('expressions/<int:pk>/mediumofperformance', views.ExpressionMediumofperformanceUpdateView.as_view(), name = 'expression_mediumofperformance'),
        path('expressions/<int:pk>/movements', views.ExpressionMovementsUpdateView.as_view(), name = 'expression_movements'),
        path('expressions/<int:pk>/comment', views.ExpressionCommentUpdateView.as_view(), name = 'expression_comment'),
        path('expressions/<int:work_id>/createexpression', views.ExpressionCreateView.as_view(), name = 'expression_create'),
        path('manifestations', views.ManifestationSearchView.as_view(), name = 'manifestation_search'),
        path('persons', views.person_list, name = 'person_list'),
        path('works/<int:pk>', views.WorkDetailView.as_view(), name = 'work_detail'),
        path('manifestations/<int:pk>', views.ManifestationDetailView.as_view(), name = 'manifestation_detail'),
        path('manifestations/new', views.ManifestationCreateView.as_view(), name = 'manifestation_create'),
    ]

"""
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
