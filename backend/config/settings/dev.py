"""Development settings."""
import socket

from .base import *  # noqa: F403

DEBUG = True

INSTALLED_APPS += [  # noqa: F405
    "debug_toolbar",
]

MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")  # noqa: F405

hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
INTERNAL_IPS = ["127.0.0.1", "localhost", "0.0.0.0"] + [
    ip[: ip.rfind(".")] + ".1" for ip in ips
]

REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = [  # noqa: F405
    "rest_framework.renderers.JSONRenderer",
    "rest_framework.renderers.BrowsableAPIRenderer",
]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Frontend (:3000) and API (:8000) are different sites in local dev; SameSite=Lax
# HttpOnly cookies are not sent on cross-origin XHR. Return JWTs in the response body
# so the browser client can use Authorization: Bearer headers.
JWT_AUTH_COOKIE_ONLY = False

DEMO_AUTO_COMPLETE_PAYMENTS = True
