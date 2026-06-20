"""WMS API tests."""
from django.contrib.auth import get_user_model
from django.core.management import call_command
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.constants import RoleSlug
from apps.accounts.rbac import PermissionCodename
from apps.accounts.services import PermissionService, RoleService
from apps.catalog.models import Brand, Product, ProductVariant
from apps.inventory.models import InventoryLevel, Warehouse
from apps.inventory.services import InventoryService
from apps.wms.models import BinInventory, PutawayTask, WarehouseBin
from apps.wms.services import BinLocationService, CycleCountService, StockTransferService

User = get_user_model()


class WmsApiTests(APITestCase):
    def setUp(self):
        RoleService.ensure_system_roles()
        call_command("seed_erp_foundation", verbosity=0)

        self.manager = User.objects.create_user(
            email="wh-mgr@example.com", password="SecurePass123!", is_staff=True
        )
        RoleService.assign_role(self.manager, RoleSlug.WAREHOUSE_MANAGER)

        self.operator = User.objects.create_user(
            email="wh-op@example.com", password="SecurePass123!", is_staff=True
        )
        RoleService.assign_role(self.operator, RoleSlug.WAREHOUSE_OPERATOR)

        self.warehouse = Warehouse.objects.create(
            code="SYD1", name="Sydney", warehouse_type=Warehouse.WarehouseType.DISTRIBUTION
        )
        brand = Brand.objects.create(name="WmsBrand", slug="wms-brand")
        product = Product.objects.create(
            brand=brand, name="Hammer", slug="hammer-wms", is_active=True
        )
        self.variant = ProductVariant.objects.create(
            product=product, sku="HMR-WMS-001", is_default=True, is_active=True
        )
        InventoryService.stock_in(
            sku="HMR-WMS-001",
            warehouse_code="SYD1",
            quantity=100,
            unit_cost_cents=2500,
        )
        self.bin_a = BinLocationService.create_bin_hierarchy(
            warehouse_code="SYD1",
            zone_code="Z1",
            zone_name="Zone 1",
            aisle_code="A1",
            aisle_name="Aisle 1",
            bin_code="B01",
            bin_name="Bin 01",
        )
        self.bin_b = BinLocationService.create_bin_hierarchy(
            warehouse_code="SYD1",
            zone_code="Z1",
            zone_name="Zone 1",
            aisle_code="A1",
            aisle_name="Aisle 1",
            bin_code="B02",
            bin_name="Bin 02",
        )

    def test_wms_dashboard(self):
        self.client.force_authenticate(user=self.manager)
        resp = self.client.get("/api/v1/wms/admin/dashboard/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("inventoryValueCents", resp.data)

    def test_bin_to_bin_transfer(self):
        from apps.wms.services import BinInventoryService

        BinInventoryService.move_bin_qty(
            from_bin=None,
            to_bin=self.bin_a,
            variant_id=self.variant.id,
            quantity=20,
        )
        tr = StockTransferService.create(
            actor=self.manager,
            transfer_type="bin",
            from_warehouse_code="SYD1",
            to_warehouse_code="SYD1",
            from_bin_id=self.bin_a.public_id,
            to_bin_id=self.bin_b.public_id,
            requires_approval=False,
        )
        StockTransferService.add_line(transfer=tr, sku="HMR-WMS-001", quantity=10)
        StockTransferService.submit(transfer=tr, actor=self.manager)
        tr.refresh_from_db()
        self.assertEqual(tr.status, "completed")
        self.assertEqual(
            BinInventory.objects.get(bin=self.bin_b, variant=self.variant).quantity_on_hand,
            10,
        )

    def test_cycle_count_variance(self):
        cc = CycleCountService.create(warehouse_code="SYD1", actor=self.manager)
        line = CycleCountService.add_line(cc=cc, sku="HMR-WMS-001")
        level = InventoryLevel.objects.get(warehouse=self.warehouse, variant=self.variant)
        CycleCountService.record_count(
            cc=cc, line_id=line.public_id, counted_qty=level.quantity_on_hand - 5, actor=self.manager
        )
        CycleCountService.complete(cc=cc, actor=self.manager)
        level.refresh_from_db()
        self.assertEqual(level.quantity_on_hand, 95)

    def test_rbac_permissions(self):
        self.assertTrue(
            PermissionService.has_permission(self.manager, PermissionCodename.WMS_APPROVE)
        )
        self.assertTrue(
            PermissionService.has_permission(self.operator, PermissionCodename.WMS_EXECUTE)
        )
        self.assertFalse(
            PermissionService.has_permission(self.operator, PermissionCodename.WMS_APPROVE)
        )

    def test_putaway_task_list(self):
        self.client.force_authenticate(user=self.operator)
        resp = self.client.get("/api/v1/wms/admin/putaway/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("data", resp.data)
