from django.urls import path

from . import views

urlpatterns = [
    # ex: /deeds/
    path("", views.deeds_list, name="deeds_list"),
    path("deed/<str:deed_address>/", views.deed_detail, name="deed_detail"),
    path("saved-searches", views.saved_searches, name="saved_isap_searches"),
    path(
        'search-detail/<int:id>/', views.search_isap_detail, name='search_isap_detail'
    ),
    path(
        'search-result-detail/<int:id>/',
        views.search_isap_result_detail,
        name='search_isap_result_detail',
    ),
    path(
        'saved-search-delete/<int:id>/',
        views.saved_search_delete,
        name='saved_search_delete',
    ),
    path(
        'send_new_isap_search_result_email/<int:id>/',
        views.send_new_isap_search_result_email_view,
        name='send_new_isap_search_result_email_view',
    ),
]
