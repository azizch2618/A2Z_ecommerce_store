"""JWT authentication from HttpOnly cookies with Authorization header fallback."""
from django.conf import settings
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken


class JWTCookieAuthentication(JWTAuthentication):
    """
    Authenticate using HttpOnly access cookie first, then Bearer header.
    Header fallback supports tests, mobile clients, and migration.
    """

    def authenticate(self, request):
        cookie_token = request.COOKIES.get(settings.JWT_AUTH_COOKIE)
        if cookie_token:
            try:
                validated = self.get_validated_token(cookie_token)
                return self.get_user(validated), validated
            except InvalidToken:
                return None
        return super().authenticate(request)
