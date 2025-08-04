from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views import defaults as default_views
from django.views.generic import TemplateView

urlpatterns = [
    path("", TemplateView.as_view(template_name="pages/home.html"), name="home"),
    path(
        "about/", TemplateView.as_view(template_name="pages/about.html"), name="about"
    ),
    path(
        "kontakt/",
        TemplateView.as_view(template_name="pages/contact.html"),
        name="kontakt",
    ),
    path(
        "polityka-prywatnosci/",
        TemplateView.as_view(template_name="pages/polityka-prywatnosci.html"),
        name="polityka-prywatnosci",
    ),
    # Terms of service removed
    # Django Admin, use {% url 'admin:index' %}
    path(settings.ADMIN_URL, admin.site.urls),
    # User management
    path("users/", include("unkot.users.urls", namespace="users")),
    # Account registration disabled
    # Your stuff: custom urls includes go here
    path("isap/", include("unkot.isap.urls")),
    # Newsletter functionality removed
    path('i18n/', include('django.conf.urls.i18n')),
    path("maintenance-mode/", include("maintenance_mode.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
