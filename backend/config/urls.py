"""URL configuration for A2Z Tools."""
from django.conf import settings
from django.contrib import admin
from django.urls import include, path

from apps.core.schema_views import StaffSpectacularAPIView, StaffSpectacularSwaggerView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include(("apps.accounts.urls", "accounts"), namespace="auth")),
    path("api/v1/", include("api.v1.urls")),
    path("api/schema/", StaffSpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        StaffSpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
]

if settings.DEBUG:
    urlpatterns = [
        path("__debug__/", include("debug_toolbar.urls")),
    ] + urlpatterns
