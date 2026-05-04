from django.urls import path
from .. import views

urlpatterns = [
    path('', views.ExpressionListView.as_view(), name = 'expression_list'),
    path('search', views.ExpressionSearchView.as_view(), name = 'expression_search'),
    path('<int:pk>/update', views.expression_update, name = 'expression_update'),
    path('<int:pk>/detail', views.ExpressionDetailView.as_view(), name = 'expression_detail'),
    path('<int:pk>/index_number_create', views.index_number_create, name = 'index_number_create'),
    path('index_number/<int:pk>/delete', views.IndexNumberDeleteView.as_view(), name = 'index_number_delete'),
    path('<int:pk>/delete', views.ExpressionDeleteView.as_view(), name = 'expression_delete'),
    path('<int:pk>/title', views.ExpressionTitleUpdateView.as_view(), name = 'expression_title'),
    path('<int:pk>/relations', views.ExpressionRelationsUpdateView.as_view(), name = 'expression_relations'),
    path('<int:pk>/relations/addrelatedexpression/<int:target_expression>', views.RelatedExpressionAddView.as_view(), name = 'related_expression_add'),
    path('removerelatedexpression/<int:pk>', views.RelatedExpressionRemoveView.as_view(), name = 'related_expression_remove'),
    path('<int:pk>/contributors', views.ExpressionContributorsUpdateView.as_view(), name = 'expression_contributors'),
    path('<int:pk>/contributors/addcontributor/<int:person>', views.ExpressionContributorAddView.as_view(), name = 'expression_contributor_add'),
    path('removecontributor/<int:pk>', views.ExpressionContributorRemoveView.as_view(), name = 'expression_contributor_remove'),
    path('<int:pk>/history', views.ExpressionHistoryUpdateView.as_view(), name = 'expression_history'),
    path('<int:pk>/categorisation', views.ExpressionCategorisationUpdateView.as_view(), name = 'expression_categorisation'),
    path('<int:pk>/mediumofperformance', views.ExpressionMediumofperformanceUpdateView.as_view(), name = 'expression_mediumofperformance'),
    path('<int:pk>/movements', views.ExpressionMovementsUpdateView.as_view(), name = 'expression_movements'),
    path('<int:pk>/comment', views.ExpressionCommentUpdateView.as_view(), name = 'expression_comment'),
    path('<int:pk>/<str:direction>/swap', views.expression_swap_view, name='expression_swap_order'),
    path('<int:pk>/delete', views.ExpressionDeleteView.as_view(), name = 'expression_delete'),
]
