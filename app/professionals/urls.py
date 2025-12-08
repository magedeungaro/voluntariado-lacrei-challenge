from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ProfessionalViewSet

app_name = "professionals"

router = DefaultRouter()
router.register("", ProfessionalViewSet, basename="professional")

urlpatterns = [
    path("", include(router.urls)),
]
