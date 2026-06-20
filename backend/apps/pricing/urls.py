from django.urls import path

from apps.pricing.views import CouponValidateView

app_name = "pricing"

urlpatterns = [
    path("coupons/validate/", CouponValidateView.as_view(), name="coupon-validate"),
]
