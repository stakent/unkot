from django.urls import path

from . import views

urlpatterns = [
    # ex: /deeds/
    path("", views.deeds_list, name="deeds_list"),
    path("deed/<str:deed_address>/", views.deed_detail, name="deed_detail"),
]
