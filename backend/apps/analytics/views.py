from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.analytics.serializers import AnalyticsEventSerializer
from apps.analytics.services import AnalyticsService


class EventCreateView(APIView):
    permission_classes = [AllowAny]
    throttle_scope = "analytics"

    def post(self, request):
        serializer = AnalyticsEventSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user if request.user.is_authenticated else None
        session_id = request.headers.get("X-Session-Key", "")
        event = AnalyticsService.track_event(
            event_type=serializer.validated_data["event_type"],
            properties=serializer.validated_data.get("properties", {}),
            user=user,
            session_id=session_id,
        )
        return Response(AnalyticsEventSerializer(event).data, status=status.HTTP_201_CREATED)
