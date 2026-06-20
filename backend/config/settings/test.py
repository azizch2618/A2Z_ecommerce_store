"""Test settings."""
import os

from .base import *  # noqa: F403

DEBUG = False

os.environ.setdefault("DJANGO_SECRET_KEY", "test-secret-key-not-for-production-use-only")

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

USE_SQLITE = os.environ.get("USE_SQLITE_FOR_TESTS") == "1"

if USE_SQLITE:
    DATABASES = {  # noqa: F405
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
        }
    }
else:
    # Connect to the service/app database; Django creates a *separate* test database.
    # Never set TEST["NAME"] equal to the connection database — that causes bootstrap hangs.
    _pg_db = os.environ.get("POSTGRES_DB", "a2z_tools")
    _pg_test_db = os.environ.get("POSTGRES_TEST_DB", f"test_{_pg_db}")

    DATABASES = {  # noqa: F405
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": _pg_db,
            "USER": os.environ.get("POSTGRES_USER", "a2z"),
            "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "changeme"),
            "HOST": os.environ.get("POSTGRES_HOST", "localhost"),
            "PORT": os.environ.get("POSTGRES_PORT", "5432"),
            "CONN_MAX_AGE": 0,
            "OPTIONS": {
                "connect_timeout": int(os.environ.get("POSTGRES_CONNECT_TIMEOUT", "10")),
            },
            "TEST": {
                "NAME": _pg_test_db,
                "MIRROR": None,
            },
        }
    }

CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
DEMO_AUTO_COMPLETE_PAYMENTS = False

# Return JWTs in response body during tests (cookie-only mode tested in test_security.py).
JWT_AUTH_COOKIE_ONLY = False
