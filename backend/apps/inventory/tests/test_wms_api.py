"""WMS API tests — adjustments, low stock alerts."""

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.constants import RoleSlug
from apps.accounts.services import RoleService
from apps.catalog.models import Brand, Product, ProductVariant
from apps.inventory.models import InventoryLevel, Warehouse

User = get_user_model()


class WMSAPITestCase(APITestCase):
    def setUp(self):
        RoleService.ensure_system_roles()
        self.user = User.objects.create_user(
            email="wms@example.com",
            password="StaffPass123!",
            is_staff=True,
        )
        RoleService.assign_role(self.user, RoleSlug.WAREHOUSE_MANAGER)
        self.client.force_authenticate(self.user)

        self.warehouse = Warehouse.objects.create(
            code="SYD1",
            name="Sydney DC",
            warehouse_type=Warehouse.WarehouseType.DISTRIBUTION,
        )
        brand = Brand.objects.create(name="Makita", slug="makita")
        product = Product.objects.create(
            brand=brand,
            name="Drill",
            slug="drill",
            is_active=True,
        )
        self.variant = ProductVariant.objects.create(
            product=product,
            sku="DRL-001",
            is_default=True,
            is_active=True,
        )
        InventoryLevel.objects.create(
            warehouse=self.warehouse,
            variant=self.variant,
            quantity_on_hand=5,
            reorder_point=10,
            reorder_quantity=20,
        )

    def test_stock_adjustment_positive(self):
        response = self.client.post(
            "/api/v1/inventory/adjustments/",
            {
                "sku": "DRL-001",
                "warehouse_code": "SYD1",
                "quantity_change": 3,
                "cost_price_cents": 5000,
                "notes": "Cycle count correction",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["inventory"]["quantity_on_hand"], 8)

    def test_stock_adjustment_negative(self):
        response = self.client.post(
            "/api/v1/inventory/adjustments/",
            {
                "sku": "DRL-001",
                "warehouse_code": "SYD1",
                "quantity_change": -2,
                "notes": "Shrinkage",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["inventory"]["quantity_on_hand"], 3)

    def test_low_stock_alerts(self):
        response = self.client.get("/api/v1/inventory/alerts/low-stock/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data["data"]), 1)
        alert = response.data["data"][0]
        self.assertEqual(alert["alert_level"], "low_stock")
        self.assertEqual(alert["sku"], "DRL-001")
