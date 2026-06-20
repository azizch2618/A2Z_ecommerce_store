"""Inventory module tests."""
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.constants import RoleSlug
from apps.accounts.services import RoleService
from apps.catalog.models import Brand, Product, ProductVariant
from apps.inventory.models import InventoryLevel, InventoryTransaction, Warehouse
from apps.suppliers.models import Supplier

User = get_user_model()


class InventoryModuleTestCase(APITestCase):
    def setUp(self):
        self.staff = User.objects.create_user(
            email="warehouse@example.com",
            password="StaffPass123!",
            is_staff=True,
        )
        RoleService.assign_role(self.staff, RoleSlug.WAREHOUSE_MANAGER)
        self.client.force_authenticate(self.staff)

        self.warehouse_syd = Warehouse.objects.create(
            code="SYD1",
            name="Sydney DC",
            warehouse_type=Warehouse.WarehouseType.DISTRIBUTION,
        )
        self.warehouse_mel = Warehouse.objects.create(
            code="MEL1",
            name="Melbourne DC",
            warehouse_type=Warehouse.WarehouseType.DISTRIBUTION,
        )
        brand = Brand.objects.create(name="DeWalt", slug="dewalt")
        product = Product.objects.create(
            brand=brand,
            name="Impact Driver",
            slug="impact-driver",
            is_active=True,
        )
        self.variant = ProductVariant.objects.create(
            product=product,
            sku="IMP-100",
            is_default=True,
            is_active=True,
        )
        self.supplier = Supplier.objects.create(
            code="SUP-01",
            name="Tool Distributors",
        )

    def test_stock_in_stock_out_flow(self):
        stock_in = self.client.post(
            reverse("inventory:stock-in"),
            {
                "sku": "IMP-100",
                "warehouse_code": "SYD1",
                "quantity": 50,
                "cost_price_cents": 12000,
                "sale_price_cents": 19900,
                "supplier_id": str(self.supplier.public_id),
            },
            format="json",
        )
        self.assertEqual(stock_in.status_code, status.HTTP_201_CREATED)
        self.assertEqual(stock_in.data["inventory"]["quantity_on_hand"], 50)
        self.assertEqual(stock_in.data["movement"]["cost_price_cents"], 12000)

        stock_out = self.client.post(
            reverse("inventory:stock-out"),
            {
                "sku": "IMP-100",
                "warehouse_code": "SYD1",
                "quantity": 10,
                "sale_price_cents": 19900,
                "reason": "sale",
            },
            format="json",
        )
        self.assertEqual(stock_out.status_code, status.HTTP_201_CREATED)
        self.assertEqual(stock_out.data["inventory"]["quantity_on_hand"], 40)

    def test_stock_transfer_between_warehouses(self):
        self.client.post(
            reverse("inventory:stock-in"),
            {
                "sku": "IMP-100",
                "warehouse_code": "SYD1",
                "quantity": 30,
                "cost_price_cents": 10000,
            },
            format="json",
        )

        transfer = self.client.post(
            reverse("inventory:stock-transfer"),
            {
                "sku": "IMP-100",
                "from_warehouse_code": "SYD1",
                "to_warehouse_code": "MEL1",
                "quantity": 12,
            },
            format="json",
        )
        self.assertEqual(transfer.status_code, status.HTTP_201_CREATED)
        self.assertEqual(transfer.data["inventory"]["quantity_on_hand"], 18)
        self.assertIsNotNone(transfer.data["paired_movement"])
        self.assertEqual(
            transfer.data["movement"]["transfer_group_id"],
            transfer.data["paired_movement"]["transfer_group_id"],
        )

        mel_level = InventoryLevel.objects.get(
            warehouse=self.warehouse_mel,
            variant=self.variant,
        )
        self.assertEqual(mel_level.quantity_on_hand, 12)
        self.assertEqual(mel_level.average_cost_cents, 10000)

    def test_list_inventory_and_movements(self):
        self.client.post(
            reverse("inventory:stock-in"),
            {
                "sku": "IMP-100",
                "warehouse_code": "SYD1",
                "quantity": 5,
                "cost_price_cents": 8000,
            },
            format="json",
        )

        levels = self.client.get(
            reverse("inventory:inventory-list"),
            {"sku": "IMP-100"},
        )
        self.assertEqual(levels.status_code, status.HTTP_200_OK)
        self.assertEqual(len(levels.data["data"]), 1)

        movements = self.client.get(
            reverse("inventory:movement-list"),
            {"sku": "IMP-100", "transaction_type": InventoryTransaction.TransactionType.RECEIPT},
        )
        self.assertEqual(movements.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(movements.data["data"]), 1)

    def test_insufficient_stock_blocks_transfer(self):
        response = self.client.post(
            reverse("inventory:stock-transfer"),
            {
                "sku": "IMP-100",
                "from_warehouse_code": "SYD1",
                "to_warehouse_code": "MEL1",
                "quantity": 5,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
