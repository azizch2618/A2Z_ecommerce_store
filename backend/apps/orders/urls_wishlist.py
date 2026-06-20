from django.urls import path

from apps.orders.views import WishlistItemCreateView, WishlistItemDetailView, WishlistView

app_name = "orders_wishlist"

urlpatterns = [
    path("", WishlistView.as_view(), name="wishlist"),
    path("items/", WishlistItemCreateView.as_view(), name="wishlist-item-create"),
    path("items/<uuid:public_id>/", WishlistItemDetailView.as_view(), name="wishlist-item-detail"),
]
