"""Health check endpoints for load balancers and orchestration."""
from django.db import connection
from django.http import JsonResponse


def health_check(request):
    """Liveness probe — confirms the API process is running."""
    return JsonResponse({"status": "ok"})


def readiness_check(request):
    """Readiness probe — confirms database connectivity."""
    try:
        connection.ensure_connection()
        db_status = "ok"
    except Exception:
        db_status = "error"
        return JsonResponse(
            {"status": "error", "database": db_status},
            status=503,
        )
    return JsonResponse({"status": "ok", "database": db_status})
