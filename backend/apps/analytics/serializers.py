from rest_framework import serializers

from apps.analytics.models import AnalyticsEvent


class AnalyticsEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalyticsEvent
        fields = ("event_type", "properties", "session_id", "occurred_at")
        read_only_fields = ("occurred_at",)
