"""Staff-protected OpenAPI schema and Swagger UI views."""
from django.conf import settings
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.permissions import AllowAny

from apps.core.permissions import IsStaffUser


class StaffSpectacularAPIView(SpectacularAPIView):
    def get_permissions(self):
        if settings.DEBUG:
            return [AllowAny()]
        return [IsStaffUser()]


class StaffSpectacularSwaggerView(SpectacularSwaggerView):
    def get_permissions(self):
        if settings.DEBUG:
            return [AllowAny()]
        return [IsStaffUser()]
