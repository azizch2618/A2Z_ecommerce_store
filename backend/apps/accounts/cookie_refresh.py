"""Cookie-aware JWT refresh endpoint."""
from django.conf import settings
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenRefreshSerializer

from apps.accounts.auth_cookies import clear_auth_cookies, set_auth_cookies
from apps.accounts.views import AuthAnonThrottle


class CookieJWTRefreshView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AuthAnonThrottle]

    def post(self, request):
        refresh = (
            request.COOKIES.get(settings.JWT_AUTH_REFRESH_COOKIE)
            or request.data.get("refresh")
        )
        if not refresh:
            return Response(
                {"detail": "Refresh token required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = TokenRefreshSerializer(data={"refresh": refresh})
        serializer.is_valid(raise_exception=True)
        tokens = serializer.validated_data

        new_refresh = tokens.get("refresh", refresh)
        response_data = {"access": tokens["access"]}
        if not settings.JWT_AUTH_COOKIE_ONLY:
            response_data["refresh"] = new_refresh

        response = Response(response_data)
        set_auth_cookies(
            response,
            access=tokens["access"],
            refresh=new_refresh,
        )
        return response

    def delete(self, request):
        """Clear auth cookies without requiring a valid refresh token."""
        response = Response(status=status.HTTP_204_NO_CONTENT)
        clear_auth_cookies(response)
        return response
