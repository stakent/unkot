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
]
