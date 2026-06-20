"""Procurement API tests."""
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.constants import RoleSlug
from apps.accounts.rbac import PermissionCodename
from apps.accounts.services import PermissionService, RoleService
from apps.catalog.models import Brand, Product, ProductVariant
from apps.inventory.models import Warehouse
from apps.procurement.models import GoodsReceipt, PurchaseRequest, SupplierMembership
from apps.suppliers.models import PurchaseOrder, Supplier

User = get_user_model()


class ProcurementApiTests(APITestCase):
    def setUp(self):
        RoleService.ensure_system_roles()
        call_command("seed_erp_foundation", verbosity=0)

        self.officer = User.objects.create_user(
            email="proc-officer@example.com", password="SecurePass123!", is_staff=True
        )
        RoleService.assign_role(self.officer, RoleSlug.PROCUREMENT_OFFICER)

        self.manager = User.objects.create_user(
            email="proc-manager@example.com", password="SecurePass123!", is_staff=True
        )
        RoleService.assign_role(self.manager, RoleSlug.PROCUREMENT_MANAGER)

        self.wh_manager = User.objects.create_user(
            email="proc-wh@example.com", password="SecurePass123!", is_staff=True
        )
        RoleService.assign_role(self.wh_manager, RoleSlug.WAREHOUSE_MANAGER)

        self.supplier_user = User.objects.create_user(
            email="supplier-portal@example.com", password="SecurePass123!"
        )
        RoleService.assign_role(self.supplier_user, RoleSlug.SUPPLIER_USER)

        self.supplier = Supplier.objects.create(
            code="SUP-PROC-1", name="Proc Supplier", email="vendor@example.com", is_active=True
        )
        SupplierMembership.objects.create(
            user=self.supplier_user, supplier=self.supplier, is_primary=True
        )

        self.warehouse = Warehouse.objects.create(code="SYD1", name="Sydney", is_active=True)
        brand = Brand.objects.create(name="ProcBrand", slug="proc-brand")
        product = Product.objects.create(
            brand=brand, name="Widget", slug="widget-proc", is_active=True
        )
        self.variant = ProductVariant.objects.create(
            product=product, sku="WDG-PROC-001", is_default=True, is_active=True
        )

    def test_procurement_dashboard(self):
        self.client.force_authenticate(user=self.officer)
        resp = self.client.get("/api/v1/procurement/admin/dashboard/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("openRequisitions", resp.data)

    def test_requisition_lifecycle_to_po(self):
        self.client.force_authenticate(user=self.officer)
        create = self.client.post(
            "/api/v1/procurement/admin/requests/",
            {
                "warehouseCode": "SYD1",
                "supplierId": str(self.supplier.public_id),
                "priority": "high",
                "justification": "Restock widgets",
            },
            format="json",
        )
        self.assertEqual(create.status_code, status.HTTP_201_CREATED)
        pr_id = create.data["id"]

        line = self.client.post(
            f"/api/v1/procurement/admin/requests/{pr_id}/lines/",
            {"sku": "WDG-PROC-001", "quantity": 10, "unitCostCents": 5000},
            format="json",
        )
        self.assertEqual(line.status_code, status.HTTP_201_CREATED)

        submit = self.client.post(
            f"/api/v1/procurement/admin/requests/{pr_id}/submit/", format="json"
        )
        self.assertEqual(submit.status_code, status.HTTP_200_OK)
        self.assertEqual(submit.data["status"], PurchaseRequest.Status.SUBMITTED)

        self.client.force_authenticate(user=self.officer)
        reject_attempt = self.client.post(
            f"/api/v1/procurement/admin/requests/{pr_id}/approve/", format="json"
        )
        self.assertEqual(reject_attempt.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(user=self.manager)
        approve = self.client.post(
            f"/api/v1/procurement/admin/requests/{pr_id}/approve/", format="json"
        )
        self.assertEqual(approve.status_code, status.HTTP_200_OK)
        self.assertEqual(approve.data["status"], PurchaseRequest.Status.APPROVED)

        self.client.force_authenticate(user=self.officer)
        convert = self.client.post(
            f"/api/v1/procurement/admin/requests/{pr_id}/convert/", format="json"
        )
        self.assertEqual(convert.status_code, status.HTTP_201_CREATED)
        self.assertTrue(convert.data["poNumber"].startswith("PO-"))
        pr = PurchaseRequest.objects.get(public_id=pr_id)
        self.assertEqual(pr.status, PurchaseRequest.Status.CONVERTED)

    def test_goods_receipt_creates_grn(self):
        from apps.suppliers.services import PurchaseOrderService

        po = PurchaseOrderService.create(
            supplier_id=self.supplier.public_id,
            warehouse_code="SYD1",
            lines=[{"sku": "WDG-PROC-001", "quantity": 5, "unit_cost_cents": 5000}],
            user=self.officer,
        )
        PurchaseOrderService.submit(po=po, user=self.officer)
        PurchaseOrderService.confirm(po=po, user=self.manager)

        self.client.force_authenticate(user=self.wh_manager)
        receive = self.client.post(
            f"/api/v1/suppliers/purchase-orders/{po.public_id}/receive/",
            {"receipts": [{"sku": "WDG-PROC-001", "quantity": 3, "batch_number": "BATCH-1"}]},
            format="json",
        )
        self.assertEqual(receive.status_code, status.HTTP_200_OK)
        self.assertEqual(receive.data["status"], PurchaseOrder.Status.PARTIAL_RECEIVED)
        self.assertTrue(GoodsReceipt.objects.filter(purchase_order=po).exists())

    def test_supplier_portal_acknowledge_and_payment(self):
        from apps.suppliers.services import PurchaseOrderService

        po = PurchaseOrderService.create(
            supplier_id=self.supplier.public_id,
            warehouse_code="SYD1",
            lines=[{"sku": "WDG-PROC-001", "quantity": 2, "unit_cost_cents": 5000}],
            user=self.officer,
        )
        PurchaseOrderService.submit(po=po, user=self.officer)
        PurchaseOrderService.confirm(po=po, user=self.manager)

        self.client.force_authenticate(user=self.supplier_user)
        listing = self.client.get("/api/v1/procurement/portal/purchase-orders/")
        self.assertEqual(listing.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(listing.data["data"]), 1)

        ack = self.client.post(
            f"/api/v1/procurement/portal/purchase-orders/{po.public_id}/acknowledge/",
            format="json",
        )
        self.assertEqual(ack.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(ack.data["acknowledgedAt"])

        payment = self.client.get(
            f"/api/v1/procurement/portal/purchase-orders/{po.public_id}/payment-status/"
        )
        self.assertEqual(payment.status_code, status.HTTP_200_OK)
        self.assertIn("paymentStatus", payment.data)

    def test_rbac_permissions(self):
        self.assertTrue(
            PermissionService.has_permission(self.officer, PermissionCodename.PROCUREMENT_MANAGE)
        )
        self.assertTrue(
            PermissionService.has_permission(self.manager, PermissionCodename.PROCUREMENT_APPROVE)
        )
        self.assertTrue(
            PermissionService.has_permission(self.supplier_user, PermissionCodename.SUPPLIER_PORTAL)
        )
