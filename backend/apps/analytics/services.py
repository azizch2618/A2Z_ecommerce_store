from django.utils import timezone

from apps.analytics.models import AnalyticsEvent, SearchLog


class AnalyticsService:
    @staticmethod
    def track_event(*, event_type: str, properties: dict | None = None, user=None, session_id: str = "") -> AnalyticsEvent:
        return AnalyticsEvent.objects.create(
            event_type=event_type,
            properties=properties or {},
            user=user,
            session_id=session_id,
            occurred_at=timezone.now(),
        )

    @staticmethod
    def log_search(*, query: str, results_count: int, session_id: str = "", user=None) -> SearchLog:
        return SearchLog.objects.create(
            query=query,
            results_count=results_count,
            session_id=session_id,
            user=user,
        )
