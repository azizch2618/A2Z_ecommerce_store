from django.urls import path

from apps.orders.views import (
    CartClearView,
    CartItemCreateView,
    CartItemDetailView,
    CartMergeView,
    CartView,
)

app_name = "orders_cart"

urlpatterns = [
    path("", CartView.as_view(), name="cart"),
    path("items/", CartItemCreateView.as_view(), name="cart-item-create"),
    path("items/<uuid:public_id>/", CartItemDetailView.as_view(), name="cart-item-detail"),
    path("clear/", CartClearView.as_view(), name="cart-clear"),
    path("merge/", CartMergeView.as_view(), name="cart-merge"),
]
