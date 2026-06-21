"""Health check endpoints for load balancers and orchestration."""
from __future__ import annotations

import os

from django.core.cache import cache
from django.db import connection
from django.http import JsonResponse


def _check_database() -> str:
    try:
        connection.ensure_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return "ok"
    except Exception:
        return "error"


def _check_redis() -> str:
    try:
        cache.set("a2z:health:ping", "1", timeout=5)
        if cache.get("a2z:health:ping") != "1":
            return "error"
        return "ok"
    except Exception:
        return "error"


def health_check(request):
    """Liveness probe — confirms the API process is running."""
    return JsonResponse({"status": "ok"})


def readiness_check(request):
    """Readiness probe — database and optional Redis connectivity."""
    checks: dict[str, str] = {"database": _check_database()}
    if os.environ.get("HEALTH_CHECK_REDIS", "true").lower() in ("true", "1", "yes"):
        checks["redis"] = _check_redis()

    failed = [name for name, status in checks.items() if status != "ok"]
    if failed:
        return JsonResponse(
            {"status": "error", "checks": checks, "failed": failed},
            status=503,
        )
    return JsonResponse({"status": "ok", "checks": checks})
