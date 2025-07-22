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
        path('works/<int:pk>/relations/addrelatedwork/<int:target_related_work>', views.RelatedWorkAddView.as_view(), name = 'related_work_add'),
        path('works/removerelatedwork/<int:pk>', views.RelatedWorkRemoveView.as_view(), name = 'related_work_remove'),
        path('works/<int:pk>/contributors', views.WorkContributorsUpdateView.as_view(), name = 'work_contributors'),
        path('works/<int:pk>/contributors/addcontributor/<int:person>', views.WorkContributorAddView.as_view(), name = 'work_contributor_add'),
        path('works/removecontributor/<int:pk>', views.WorkContributorRemoveView.as_view(), name = 'work_contributor_remove'),
        path('works/<int:pk>/relatedworks', views.WorkRelatedWorksUpdateView.as_view(), name = 'work_relatedworks'),
        path('works/<int:pk>/history', views.WorkHistoryUpdateView.as_view(), name = 'work_history'),
        path('works/<int:pk>/bibliography', views.WorkBibliographyUpdateView.as_view(), name = 'work_bibliography'),
        path('works/<int:pk>/bibliography/addbib/<str:zotitem_key>', views.WorkBibAddView.as_view(), name = 'work_bib_add'),
        path('works/removebib/<int:pk>', views.WorkBibDeleteView.as_view(), name = 'work_bib_remove'),
        path('works/<int:pk>/comment', views.WorkCommentUpdateView.as_view(), name = 'work_comment'),
        path('works/<int:pk>/delete', views.WorkDeleteView.as_view(), name = 'work_delete'),
        path('expressions', views.ExpressionListView.as_view(), name = 'expression_list'),
        path('expressions/search', views.ExpressionSearchView.as_view(), name = 'expression_search'),
        path('expressions/<int:pk>/update', views.ExpressionUpdateView.as_view(), name = 'expression_update'),
        path('expressions/<int:pk>/delete', views.ExpressionDeleteView.as_view(), name = 'expression_delete'),
        path('expressions/<int:pk>/title', views.ExpressionTitleUpdateView.as_view(), name = 'expression_title'),
        path('expressions/<int:pk>/relations', views.ExpressionRelationsUpdateView.as_view(), name = 'expression_relations'),
        path('expressions/<int:pk>/relations/addrelatedexpression/<int:target_expression>', views.RelatedExpressionAddView.as_view(), name = 'related_expression_add'),
        path('expressions/removerelatedexpression/<int:pk>', views.RelatedExpressionRemoveView.as_view(), name = 'related_expression_remove'),
        path('expressions/<int:pk>/contributors', views.ExpressionContributorsUpdateView.as_view(), name = 'expression_contributors'),
        path('expressions/<int:pk>/contributors/addcontributor/<int:person>', views.ExpressionContributorAddView.as_view(), name = 'expression_contributor_add'),
        path('expressions/removecontributor/<int:pk>', views.ExpressionContributorRemoveView.as_view(), name = 'expression_contributor_remove'),
        path('expressions/<int:pk>/history', views.ExpressionHistoryUpdateView.as_view(), name = 'expression_history'),
        path('expressions/<int:pk>/categorisation', views.ExpressionCategorisationUpdateView.as_view(), name = 'expression_categorisation'),
        path('expressions/<int:pk>/mediumofperformance', views.ExpressionMediumofperformanceUpdateView.as_view(), name = 'expression_mediumofperformance'),
        path('expressions/<int:pk>/movements', views.ExpressionMovementsUpdateView.as_view(), name = 'expression_movements'),
        path('expressions/<int:pk>/comment', views.ExpressionCommentUpdateView.as_view(), name = 'expression_comment'),
        path('expressions/<int:work_id>/createexpression', views.ExpressionCreateView.as_view(), name = 'expression_create'),
        path('expressions/<int:pk>/delete', views.ExpressionDeleteView.as_view(), name = 'expression_delete'),
        path('manifestations', views.ManifestationListView.as_view(), name = 'manifestation_list'),
        path('manifestations/search', views.ManifestationSearchView.as_view(), name = 'manifestation_search'),
        path('manifestations', views.ManifestationListView.as_view(), name = 'manifestation_list'),
        path('manifestations/<int:pk>', views.manifestation_update, name = 'manifestation_update'),
        path('manifestations/<int:pk>/set_singleton', views.manifestation_set_singleton, name = 'manifestation_set_singleton'),
        path('manifestations/<int:pk>/unset_singleton', views.manifestation_unset_singleton, name = 'manifestation_unset_singleton'),
        path('manifestations/<int:pk>/set_missing', views.manifestation_set_missing, name = 'manifestation_set_missing'),
        path('manifestations/<int:pk>/unset_missing', views.manifestation_unset_missing, name = 'manifestation_unset_missing'),
        path('manifestations/new', views.ManifestationCreateView.as_view(), name = 'manifestation_create'),
        path('manifestations/<int:pk>/delete', views.ManifestationDeleteView.as_view(), name = 'manifestation_delete'),
        path('manifestations/<int:pk>/title', views.ManifestationTitleUpdateView.as_view(), name = 'manifestation_title'),
        path('manifestations/<int:pk>/relations', views.ManifestationRelationsUpdateView.as_view(), name = 'manifestation_relations'),
        path('manifestations/<int:pk>/relations/addrelatedmanifestation/<int:target_manifestation>', views.RelatedManifestationAddView.as_view(), name = 'related_manifestation_add'),
        path('manifestations/removerelatedmanifestation/<int:pk>', views.RelatedManifestationRemoveView.as_view(), name = 'related_manifestation_remove'),
        path('manifestations/<int:pk>/contributors', views.ManifestationContributorsUpdateView.as_view(), name = 'manifestation_contributors'),
        path('manifestations/<int:pk>/contributors/addcontributor/<int:person>', views.ManifestationContributorAddView.as_view(), name = 'manifestation_contributor_add'),
        path('manifestations/removecontributor/<int:pk>', views.ManifestationContributorRemoveView.as_view(), name = 'manifestation_contributor_remove'),
        path('manifestations/<int:pk>/history', views.ManifestationHistoryUpdateView.as_view(), name = 'manifestation_history'),
        path('manifestations/<int:pk>/bibliography', views.ManifestationBibliographyUpdateView.as_view(), name = 'manifestation_bibliography'),
        path('manifestations/<int:pk>/bibliography/addbib/<str:zotitem_key>', views.ManifestationBibAddView.as_view(), name = 'manifestation_bib_add'),
        path('manifestations/removebib/<int:pk>', views.ManifestationBibDeleteView.as_view(), name = 'manifestation_bib_remove'),
        path('manifestations/<int:pk>/comment', views.ManifestationCommentUpdateView.as_view(), name = 'manifestation_comment'),
        path('manifestations/<int:pk>/classification', views.ManifestationClassificationUpdateView.as_view(), name = 'manifestation_classification'),
        path('manifestations/<int:pk>/print', views.ManifestationPrintUpdateView.as_view(), name = 'manifestation_print'),
        path('manifestations/<int:pk>/delete', views.ManifestationDeleteView.as_view(), name = 'manifestation_delete'),
        path('manifestations/<int:pk>/addplace/<int:place_id>', views.manifestation_add_place_view, name = 'manifestation_place_add'),
        path('manifestations/<int:pk>/remove_place', views.manifestation_remove_place_view, name = 'manifestation_remove_place'),
        path('items', views.ItemListView.as_view(), name = 'item_list'),
        path('items/search', views.ItemSearchView.as_view(), name = 'item_search'),
        path('items/<int:pk>', views.ItemUpdateView.as_view(), name = 'item_update'),
        path('items/<int:manifestation_id>/createitem', views.ItemCreateView.as_view(), name = 'item_create'),
        path('items/<int:pk>/delete', views.ItemDeleteView.as_view(), name = 'item_delete'),
        path('items/<int:pk>/title', views.ItemTitleUpdateView.as_view(), name = 'item_title'),
        path('items/<int:pk>/location', views.ItemLocationUpdateView.as_view(), name = 'item_location'),
        path('items/<int:pk>/relations', views.ItemRelationsUpdateView.as_view(), name = 'item_relations'),
        path('items/<int:pk>/relations/addrelatedmanifestation/<int:target_item>', views.RelatedItemAddView.as_view(), name = 'related_item_add'),
        path('items/removerelatedmanifestation/<int:pk>', views.RelatedItemRemoveView.as_view(), name = 'related_item_remove'),
        path('items/<int:pk>/contributors', views.ItemContributorsUpdateView.as_view(), name = 'item_contributors'),
        path('items/<int:pk>/contributors/addcontributor/<int:person>', views.ItemContributorAddView.as_view(), name = 'item_contributor_add'),
        path('items/removecontributor/<int:pk>', views.ItemContributorRemoveView.as_view(), name = 'item_contributor_remove'),
        path('items/<int:pk>/provenance', views.ItemProvenanceUpdateView.as_view(), name = 'item_provenance'),
        path('items/<int:pk>/details', views.ItemDetailsUpdateView.as_view(), name = 'item_details'),
        path('items/<int:pk>/description', views.ItemDescriptionUpdateView.as_view(), name = 'item_description'),
        path('items/<int:pk>/digcopy', views.ItemDigcopyUpdateView.as_view(), name = 'item_digcopy'),
        path('items/<int:pk>/comment', views.ItemCommentUpdateView.as_view(), name = 'item_comment'),
        path('items/<int:pk>/delete', views.ItemDeleteView.as_view(), name = 'item_delete'),
        path('libraries', views.LibraryListView.as_view(), name = 'library_list'),
        path('libraries/search', views.LibrarySearchView.as_view(), name = 'library_search'),
        path('libraries/create', views.LibraryCreateView.as_view(), name = 'library_create'),
        path('libraries/<int:pk>/update', views.LibraryUpdateView.as_view(), name = 'library_update'),
        path('libraries/<int:pk>/delete', views.LibraryDeleteView.as_view(), name = 'library_delete'),
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
