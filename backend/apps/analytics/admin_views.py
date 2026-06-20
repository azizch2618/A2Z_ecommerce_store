"""Admin dashboard and customer list APIs."""

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import CanViewCatalog, CanViewCustomers, CanViewDashboard
from apps.analytics.dashboard import get_cached_dashboard_payload
from apps.customers.models import Customer
from apps.catalog.models import Product
from apps.inventory.models import InventoryLevel


class DashboardView(APIView):
    permission_classes = [IsAuthenticated, CanViewDashboard]

    def get(self, request):
        return Response(get_cached_dashboard_payload())


class AdminCustomerListView(APIView):
    permission_classes = [IsAuthenticated, CanViewCustomers]

    def get(self, request):
        customers = Customer.objects.select_related("user", "user__profile").order_by(
            "-created_at"
        )[:100]
        data = []
        for customer in customers:
            name = "Guest"
            email = ""
            if customer.user_id:
                email = customer.user.email
                profile = getattr(customer.user, "profile", None)
                if profile:
                    name = f"{profile.first_name} {profile.last_name}".strip() or email
            data.append(
                {
                    "id": str(customer.public_id),
                    "name": name,
                    "email": email,
                    "orderCount": customer.total_orders,
                    "tradeStatus": customer.trade_account_status,
                    "joinedAt": customer.created_at.isoformat(),
                }
            )
        return Response({"data": data})


class AdminProductListView(APIView):
    permission_classes = [IsAuthenticated, CanViewCatalog]

    def get(self, request):
        products = Product.objects.select_related("brand").prefetch_related(
            "variants", "categories", "variants__inventory_levels"
        ).filter(is_active=True)[:100]
        rows = []
        for product in products:
            variant = product.variants.filter(is_default=True).first() or product.variants.first()
            if not variant:
                continue
            stock = sum(
                level.quantity_on_hand
                for level in variant.inventory_levels.all()
            )
            from apps.catalog.pricing_helpers import get_variant_unit_price_cents

            price = get_variant_unit_price_cents(variant)
            cat = product.categories.first()
            rows.append(
                {
                    "id": str(product.public_id),
                    "name": product.name,
                    "sku": variant.sku,
                    "brand": product.brand.name,
                    "category": cat.name if cat else "",
                    "priceCents": price,
                    "stock": stock,
                    "status": "active" if product.is_active else "draft",
                }
            )
        return Response({"data": rows})
