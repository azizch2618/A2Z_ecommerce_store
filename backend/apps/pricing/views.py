from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.pricing.serializers import CouponSerializer
from apps.pricing.services import PricingService


class CouponValidateView(APIView):
    permission_classes = [AllowAny]
    throttle_scope = "coupon"

    def post(self, request):
        code = request.data.get("code", "")
        coupon = PricingService.validate_coupon(code)
        return Response(CouponSerializer(coupon).data)
