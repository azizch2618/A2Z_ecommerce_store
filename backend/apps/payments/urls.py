from django.urls import path

from apps.payments.views import PaymentConfigView, StripeWebhookView

app_name = "payments"

urlpatterns = [
    path("config/", PaymentConfigView.as_view(), name="payment-config"),
    path("webhook/", StripeWebhookView.as_view(), name="stripe-webhook"),
]
