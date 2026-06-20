"""
Base Django settings for A2Z Tools.
"""
import os
from datetime import timedelta
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent

DEBUG = os.environ.get("DJANGO_DEBUG", "False").lower() in ("true", "1", "yes")

_secret_key = os.environ.get("DJANGO_SECRET_KEY", "")
_INSECURE_SECRET_DEFAULTS = {
    "django-insecure-change-me",
    "change-me-to-a-secure-random-string",
    "dev-only-a2z-tools-secret-key-change-in-production-xK9mP2vL7nQ4",
}
if not DEBUG:
    if not _secret_key or _secret_key in _INSECURE_SECRET_DEFAULTS:
        raise ImproperlyConfigured(
            "DJANGO_SECRET_KEY must be set to a strong unique value when DEBUG=False."
        )
    SECRET_KEY = _secret_key
else:
    SECRET_KEY = _secret_key or "django-insecure-change-me"

ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
    if host.strip()
]

# Application definition
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
    "django_filters",
    "drf_spectacular",
]

LOCAL_APPS = [
    "apps.core",
    "apps.erp",
    "apps.crm",
    "apps.quotes",
    "apps.accounts",
    "apps.customers",
    "apps.trade_accounts",
    "apps.catalog",
    "apps.inventory",
    "apps.suppliers",
    "apps.procurement",
    "apps.wms",
    "apps.accounting",
    "apps.receivables",
    "apps.payables",
    "apps.pricing",
    "apps.orders",
    "apps.payments",
    "apps.analytics",
    "apps.cms",
]

AUTH_USER_MODEL = "accounts.User"

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DB", "a2z_tools"),
        "USER": os.environ.get("POSTGRES_USER", "a2z"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "changeme"),
        "HOST": os.environ.get("POSTGRES_HOST", "localhost"),
        "PORT": os.environ.get("POSTGRES_PORT", "5432"),
    }
}

# Cache
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": os.environ.get("REDIS_URL", "redis://localhost:6379/0"),
    }
}

# Celery
CELERY_BROKER_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "Australia/Sydney"

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Internationalization
LANGUAGE_CODE = "en-au"
TIME_ZONE = "Australia/Sydney"
USE_I18N = True
USE_TZ = True

# Static & media
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Django REST Framework
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "apps.accounts.authentication.JWTCookieAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.CursorPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "EXCEPTION_HANDLER": "apps.core.exceptions.a2z_exception_handler",
    "DATETIME_FORMAT": "%Y-%m-%dT%H:%M:%S%z",
}

# JWT
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(
        minutes=int(os.environ.get("JWT_ACCESS_TOKEN_LIFETIME_MINUTES", 15))
    ),
    "REFRESH_TOKEN_LIFETIME": timedelta(
        days=int(os.environ.get("JWT_REFRESH_TOKEN_LIFETIME_DAYS", 7))
    ),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# CORS — credentials required for HttpOnly JWT cookies
CORS_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get(
        "DJANGO_CORS_ALLOWED_ORIGINS", "http://localhost:3000"
    ).split(",")
    if origin.strip()
]
CORS_ALLOW_CREDENTIALS = True

# CSRF trusted origins (required for cookie auth from browser clients)
CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get("CSRF_TRUSTED_ORIGINS", "http://localhost:3000").split(",")
    if origin.strip()
]

# HttpOnly JWT cookies
JWT_AUTH_COOKIE = os.environ.get("JWT_AUTH_COOKIE", "a2z_access")
JWT_AUTH_REFRESH_COOKIE = os.environ.get("JWT_AUTH_REFRESH_COOKIE", "a2z_refresh")
JWT_AUTH_COOKIE_HTTP_ONLY = True
JWT_AUTH_COOKIE_SECURE = os.environ.get("JWT_AUTH_COOKIE_SECURE", "False").lower() in (
    "true",
    "1",
    "yes",
)
JWT_AUTH_COOKIE_SAMESITE = os.environ.get("JWT_AUTH_COOKIE_SAMESITE", "Lax")
JWT_AUTH_COOKIE_DOMAIN = os.environ.get("JWT_COOKIE_DOMAIN", "") or None
JWT_AUTH_COOKIE_ONLY = os.environ.get("JWT_AUTH_COOKIE_ONLY", "True").lower() in (
    "true",
    "1",
    "yes",
)

# OpenAPI / Swagger
SPECTACULAR_SETTINGS = {
    "TITLE": "A2Z Tools API",
    "DESCRIPTION": "Australian Hardware & Networking Ecommerce Platform",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

# A2Z Tools — Australian defaults
A2Z_CURRENCY_CODE = "AUD"
A2Z_GST_RATE = "0.1000"
A2Z_DEFAULT_COUNTRY = "AU"
# Quotes above this total (inc GST, cents) require manager approval before sending
QUOTE_APPROVAL_THRESHOLD_CENTS = int(os.environ.get("QUOTE_APPROVAL_THRESHOLD_CENTS", "500000"))
DEMO_AUTO_COMPLETE_PAYMENTS = False

# Stripe (Payment Intents + webhooks)
STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY", "")
STRIPE_PUBLISHABLE_KEY = os.environ.get("STRIPE_PUBLIC_KEY", "")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")

# Auth / frontend integration
FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:3000")
PASSWORD_RESET_TIMEOUT = int(os.environ.get("PASSWORD_RESET_TIMEOUT", 3600))
EMAIL_VERIFICATION_TIMEOUT = int(os.environ.get("EMAIL_VERIFICATION_TIMEOUT", 259200))

REST_FRAMEWORK["DEFAULT_THROTTLE_CLASSES"] = [  # noqa: F405
    "rest_framework.throttling.AnonRateThrottle",
    "rest_framework.throttling.UserRateThrottle",
    "rest_framework.throttling.ScopedRateThrottle",
]
REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"] = {  # noqa: F405
    "anon": os.environ.get("DRF_THROTTLE_ANON", "120/hour"),
    "user": os.environ.get("DRF_THROTTLE_USER", "1000/hour"),
    "auth": os.environ.get("DRF_THROTTLE_AUTH", "20/minute"),
    "auth_user": os.environ.get("DRF_THROTTLE_AUTH_USER", "60/minute"),
    "analytics": os.environ.get("DRF_THROTTLE_ANALYTICS", "60/hour"),
    "coupon": os.environ.get("DRF_THROTTLE_COUPON", "30/hour"),
}
