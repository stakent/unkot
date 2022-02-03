from django.urls import path

from . import views

urlpatterns = [
    # path("", views.deeds_list, name="deeds_list"),
    path("subscribe/", views.subscribe, name="newsletter_subscribe"),
    path(
        "a-email-sent/",
        views.activation_email_sent,
        name="newsletter_activation_email_sent",
    ),
    path("<str:email>/", views.subscriber, name="newsletter_subscriber"),
    path("activate/<str:token>/", views.activate, name="newsletter_activate"),
    path(
        "unsubscribe/<str:email>/",
        views.unsubscribe,
        name="newsletter_unsubscribe",
    ),
]
