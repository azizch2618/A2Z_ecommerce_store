"""HttpOnly JWT cookie helpers for secure browser authentication."""
from __future__ import annotations

from django.conf import settings
from django.http import HttpResponseBase
from rest_framework.response import Response


def _cookie_params() -> dict:
    return {
        "httponly": settings.JWT_AUTH_COOKIE_HTTP_ONLY,
        "secure": settings.JWT_AUTH_COOKIE_SECURE,
        "samesite": settings.JWT_AUTH_COOKIE_SAMESITE,
        "domain": settings.JWT_AUTH_COOKIE_DOMAIN or None,
        "path": "/",
    }


def set_auth_cookies(response: HttpResponseBase, *, access: str, refresh: str) -> None:
    """Attach access and refresh JWTs as HttpOnly cookies."""
    params = _cookie_params()
    response.set_cookie(
        settings.JWT_AUTH_COOKIE,
        access,
        max_age=int(settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds()),
        **params,
    )
    response.set_cookie(
        settings.JWT_AUTH_REFRESH_COOKIE,
        refresh,
        max_age=int(settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds()),
        **params,
    )


def clear_auth_cookies(response: HttpResponseBase) -> None:
    """Remove JWT cookies from the client."""
    params = _cookie_params()
    response.delete_cookie(settings.JWT_AUTH_COOKIE, path="/", domain=params["domain"])
    response.delete_cookie(
        settings.JWT_AUTH_REFRESH_COOKIE,
        path="/",
        domain=params["domain"],
    )


def attach_auth_cookies(response: Response, tokens: dict) -> Response:
    """Set HttpOnly cookies on a DRF response; omit tokens from body when configured."""
    set_auth_cookies(response, access=tokens["access"], refresh=tokens["refresh"])
    if settings.JWT_AUTH_COOKIE_ONLY and isinstance(response.data, dict):
        response.data.pop("tokens", None)
    return response
