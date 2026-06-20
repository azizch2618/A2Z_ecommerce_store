"""Purchase order API tests."""

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.constants import RoleSlug
from apps.accounts.services import RoleService
from apps.catalog.models import Brand, Product, ProductVariant
from apps.inventory.models import Warehouse
from apps.suppliers.models import Supplier

User = get_user_model()


class PurchaseOrderAPITestCase(APITestCase):
    def setUp(self):
        RoleService.ensure_system_roles()
        self.manager = User.objects.create_user(
            email="mgr@example.com",
            password="StaffPass123!",
            is_staff=True,
        )
        RoleService.assign_role(self.manager, RoleSlug.MANAGER)
        self.warehouse_user = User.objects.create_user(
            email="wh@example.com",
            password="StaffPass123!",
            is_staff=True,
        )
        RoleService.assign_role(self.warehouse_user, RoleSlug.WAREHOUSE_MANAGER)

        self.warehouse = Warehouse.objects.create(
            code="SYD1",
            name="Sydney DC",
            warehouse_type=Warehouse.WarehouseType.DISTRIBUTION,
        )
        self.supplier = Supplier.objects.create(code="SUP-01", name="Tool Co")
        brand = Brand.objects.create(name="Bosch", slug="bosch")
        product = Product.objects.create(
            brand=brand,
            name="Angle Grinder",
            slug="angle-grinder",
            is_active=True,
        )
        self.variant = ProductVariant.objects.create(
            product=product,
            sku="GRD-100",
            is_default=True,
            is_active=True,
        )

    def test_create_submit_receive_purchase_order(self):
        self.client.force_authenticate(self.manager)
        create = self.client.post(
            "/api/v1/suppliers/purchase-orders/",
            {
                "supplier_id": str(self.supplier.public_id),
                "warehouse_code": "SYD1",
                "lines": [
                    {
                        "sku": "GRD-100",
                        "quantity": 10,
                        "unit_cost_cents": 12000,
                    }
                ],
            },
            format="json",
        )
        self.assertEqual(create.status_code, status.HTTP_201_CREATED)
        po_id = create.data["id"]
        self.assertEqual(create.data["status"], "draft")

        submit = self.client.post(f"/api/v1/suppliers/purchase-orders/{po_id}/submit/")
        self.assertEqual(submit.status_code, status.HTTP_200_OK)
        self.assertEqual(submit.data["status"], "submitted")

        confirm = self.client.post(f"/api/v1/suppliers/purchase-orders/{po_id}/confirm/")
        self.assertEqual(confirm.status_code, status.HTTP_200_OK)

        self.client.force_authenticate(self.warehouse_user)
        line_id = confirm.data["lines"][0]["id"]
        receive = self.client.post(
            f"/api/v1/suppliers/purchase-orders/{po_id}/receive/",
            {"receipts": [{"line_id": line_id, "quantity": 10}]},
            format="json",
        )
        self.assertEqual(receive.status_code, status.HTTP_200_OK)
        self.assertEqual(receive.data["status"], "received")
        self.assertEqual(receive.data["lines"][0]["quantity_received"], 10)

        stock = self.client.get("/api/v1/inventory/levels/?sku=GRD-100")
        self.assertEqual(stock.status_code, status.HTTP_200_OK)
        self.assertEqual(stock.data["data"][0]["quantity_on_hand"], 10)
