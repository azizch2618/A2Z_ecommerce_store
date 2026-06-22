from django.urls import path

from apps.orders.views import (
    OrderCancelView,
    OrderDeliverView,
    OrderDetailView,
    OrderInvoiceView,
    OrderListCreateView,
    OrderPackView,
    OrderRefundView,
    OrderShipView,
    OrderTrackView,
)

app_name = "orders"

urlpatterns = [
    path("", OrderListCreateView.as_view(), name="order-list-create"),
    path("track/", OrderTrackView.as_view(), name="order-track"),
    path("<uuid:public_id>/", OrderDetailView.as_view(), name="order-detail"),
    path("<uuid:public_id>/invoice/", OrderInvoiceView.as_view(), name="order-invoice"),
    path("<uuid:public_id>/pack/", OrderPackView.as_view(), name="order-pack"),
    path("<uuid:public_id>/ship/", OrderShipView.as_view(), name="order-ship"),
    path("<uuid:public_id>/deliver/", OrderDeliverView.as_view(), name="order-deliver"),
    path("<uuid:public_id>/cancel/", OrderCancelView.as_view(), name="order-cancel"),
    path("<uuid:public_id>/refund/", OrderRefundView.as_view(), name="order-refund"),
]
