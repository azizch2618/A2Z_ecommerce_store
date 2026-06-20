"""Production inventory API tests."""

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.constants import RoleSlug
from apps.accounts.services import RoleService
from apps.catalog.models import Brand, Product, ProductVariant
from apps.inventory.models import InventoryAlert, InventoryLevel, Warehouse

User = get_user_model()


class ProductionInventoryTestCase(APITestCase):
    def setUp(self):
        RoleService.ensure_system_roles()
        self.user = User.objects.create_user(
            email="inv@example.com",
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
        brand = Brand.objects.create(name="Test", slug="test")
        product = Product.objects.create(
            brand=brand, name="Widget", slug="widget", is_active=True
        )
        self.variant = ProductVariant.objects.create(
            product=product, sku="WDG-01", is_default=True, is_active=True
        )
        self.level = InventoryLevel.objects.create(
            warehouse=self.warehouse,
            variant=self.variant,
            quantity_on_hand=4,
            average_cost_cents=1000,
            reorder_point=10,
            reorder_quantity=25,
        )

    def test_update_reorder_levels(self):
        response = self.client.patch(
            f"/api/v1/inventory/levels/{self.level.public_id}/",
            {"reorder_point": 5, "reorder_quantity": 20},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["reorder_point"], 5)
        self.assertEqual(response.data["reorder_quantity"], 20)

    def test_stock_movement_creates_notification(self):
        response = self.client.post(
            "/api/v1/inventory/stock-out/",
            {
                "sku": "WDG-01",
                "warehouse_code": "SYD1",
                "quantity": 4,
                "notes": "Write off",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            InventoryAlert.objects.filter(
                inventory_level=self.level,
                alert_type=InventoryAlert.AlertType.OUT_OF_STOCK,
            ).exists()
        )

        notif_response = self.client.get("/api/v1/inventory/notifications/")
        self.assertEqual(notif_response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(notif_response.data["data"]), 1)

    def test_valuation_summary(self):
        response = self.client.get("/api/v1/inventory/valuation/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["currency_code"], "AUD")
        self.assertIn("amount_ex_gst_cents", response.data)
        self.assertIn("gst_cents", response.data)
        self.assertEqual(response.data["valuation_method"], "weighted_average_cost_ex_gst")

    def test_ledger_summary(self):
        self.client.post(
            "/api/v1/inventory/stock-in/",
            {
                "sku": "WDG-01",
                "warehouse_code": "SYD1",
                "quantity": 10,
                "cost_price_cents": 1000,
            },
            format="json",
        )
        response = self.client.get("/api/v1/inventory/ledger/summary/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(response.data["total_movements"], 0)
        self.assertEqual(response.data["currency_code"], "AUD")

    def test_acknowledge_notification(self):
        self.client.post(
            "/api/v1/inventory/stock-out/",
            {"sku": "WDG-01", "warehouse_code": "SYD1", "quantity": 4},
            format="json",
        )
        alert = InventoryAlert.objects.filter(inventory_level=self.level).first()
        response = self.client.post(
            f"/api/v1/inventory/notifications/{alert.public_id}/acknowledge/"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "acknowledged")
