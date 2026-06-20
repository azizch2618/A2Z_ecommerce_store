"""API v1 URL routing."""
from django.urls import include, path

from api.health import views as health_views

urlpatterns = [
    path("health/", health_views.health_check, name="health"),
    path("ready/", health_views.readiness_check, name="ready"),
    # Identity
    path("auth/", include(("apps.accounts.urls", "accounts"), namespace="accounts")),
    # Catalog
    path("", include("apps.catalog.urls")),
    # Commerce
    path("cart/", include("apps.orders.urls_cart")),
    path("wishlist/", include("apps.orders.urls_wishlist")),
    path("orders/", include("apps.orders.urls")),
    path("payments/", include("apps.payments.urls")),
    # Customers (addresses under auth in API spec — also exposed here)
    path("customers/", include("apps.customers.urls")),
    # Trade B2B
    path("trade-accounts/", include("apps.trade_accounts.urls")),
    # Operations
    path("inventory/", include("apps.inventory.urls")),
    path("suppliers/", include("apps.suppliers.urls")),
    path("pricing/", include("apps.pricing.urls")),
    # Content & analytics
    path("cms/", include("apps.cms.urls")),
    path("analytics/", include("apps.analytics.urls")),
]
