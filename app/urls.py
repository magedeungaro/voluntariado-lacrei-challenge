"""
URL configuration for Lacrei Saúde API.
"""

from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    # OAuth2 endpoints
    path("oauth/", include("oauth2_provider.urls", namespace="oauth2_provider")),
    # API v1
    path("api/v1/", include("app.core.urls")),
    path("api/v1/professionals/", include("app.professionals.urls")),
    path("api/v1/appointments/", include("app.appointments.urls")),
    # API Documentation
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
]
