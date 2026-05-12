from django.urls import path
from .. import views

urlpatterns = [
    path('', views.LetterListView.as_view(), name = 'letter_list'),
    path('search', views.LetterSearchView.as_view(), name = 'letter_search'),
    path('create', views.LetterCreateView.as_view(), name = 'letter_create'),
    path('<int:pk>/update', views.letter_update, name = 'letter_update'),
    path('<int:pk>/delete', views.LetterDeleteView.as_view(), name = 'letter_delete'),

    path('<int:pk>/add_sender_person/<int:person_id>', views.letter_add_sender_person, name='letter_add_sender_person'),
    path('<int:pk>/remove_sender_person', views.letter_remove_sender_person, name='letter_remove_sender_person'),
    path('<int:pk>/add_receiver_person/<int:person_id>', views.letter_add_receiver_person, name='letter_add_receiver_person'),
    path('<int:pk>/remove_receiver_person', views.letter_remove_receiver_person, name='letter_remove_receiver_person'),
    path('<int:pk>/add_sender_corporation/<int:corporation_id>', views.letter_add_sender_corporation, name='letter_add_sender_corporation'),
    path('<int:pk>/remove_sender_corporation', views.letter_remove_sender_corporation, name='letter_remove_sender_corporation'),
    path('<int:pk>/add_receiver_corporation/<int:corporation_id>', views.letter_add_receiver_corporation, name='letter_add_receiver_corporation'),
    path('<int:pk>/remove_receiver_corporation', views.letter_remove_receiver_corporation, name='letter_remove_receiver_corporation'),
    path('<int:pk>/add_sender_place/<int:place_id>', views.letter_add_sender_place, name='letter_add_sender_place'),
    path('<int:pk>/remove_sender_place', views.letter_remove_sender_place, name='letter_remove_sender_place'),
    path('<int:pk>/add_receiver_place/<int:place_id>', views.letter_add_receiver_place, name='letter_add_receiver_place'),
    path('<int:pk>/remove_receiver_place', views.letter_remove_receiver_place, name='letter_remove_receiver_place'),
    path('<int:pk>/add_edition/<str:zotitem_id>', views.letter_add_edition, name='letter_add_edition'),
    path('<int:pk>/remove_edition/<str:zotitem_id>', views.letter_remove_edition, name='letter_remove_edition'),
]
