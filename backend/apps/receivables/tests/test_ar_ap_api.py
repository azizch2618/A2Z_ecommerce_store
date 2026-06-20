"""AR/AP integration tests."""
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounting.constants import StandardAccountCode
from apps.accounting.models import JournalEntry
from apps.accounts.constants import RoleSlug
from apps.accounts.services import RoleService
from apps.catalog.models import Brand, Product, ProductVariant
from apps.customers.models import Customer
from apps.inventory.models import Warehouse
from apps.orders.models import Order, OrderItem
from apps.payables.constants import SupplierInvoiceStatus
from apps.payables.models import SupplierInvoice
from apps.receivables.constants import CustomerInvoiceStatus
from apps.receivables.models import CustomerInvoice
from apps.receivables.services import CustomerInvoiceService
from apps.suppliers.models import PurchaseOrder, PurchaseOrderLine, Supplier
from apps.suppliers.services import PurchaseOrderService

User = get_user_model()


class ReceivablesPayablesTests(APITestCase):
    def setUp(self):
        RoleService.ensure_system_roles()
        call_command("seed_erp_foundation", verbosity=0)
        call_command("seed_accounting_foundation", verbosity=0)

        self.finance_user = User.objects.create_user(
            email="fin-user@example.com", password="SecurePass123!", is_staff=True
        )
        RoleService.assign_role(self.finance_user, RoleSlug.FINANCE_USER)

        self.finance_manager = User.objects.create_user(
            email="fin-mgr@example.com", password="SecurePass123!", is_staff=True
        )
        RoleService.assign_role(self.finance_manager, RoleSlug.FINANCE_MANAGER)

        self.customer_user = User.objects.create_user(
            email="ar-customer@example.com", password="SecurePass123!"
        )
        self.customer = Customer.objects.create(user=self.customer_user, payment_terms_days=30)

        brand = Brand.objects.create(name="ARBrand", slug="ar-brand")
        product = Product.objects.create(brand=brand, name="Tool", slug="tool-ar", is_active=True)
        self.variant = ProductVariant.objects.create(
            product=product, sku="TOOL-AR-001", is_default=True, is_active=True
        )

        self.order = Order.objects.create(
            order_number="SO-TEST-AR-001",
            customer=self.customer,
            status=Order.Status.PAID,
            payment_status=Order.PaymentStatus.PAID,
            subtotal_ex_gst_cents=10000,
            gst_total_cents=1000,
            total_inc_gst_cents=11000,
            placed_at=timezone.now(),
        )
        OrderItem.objects.create(
            order=self.order,
            variant=self.variant,
            sku=self.variant.sku,
            product_name="Tool",
            quantity=2,
            unit_price_ex_gst_cents=5000,
            unit_gst_cents=500,
            line_total_ex_gst_cents=10000,
            line_gst_cents=1000,
            line_total_inc_gst_cents=11000,
        )

        self.supplier = Supplier.objects.create(
            code="SUP-AP-1", name="AP Supplier", email="ap@example.com", is_active=True
        )
        self.warehouse = Warehouse.objects.create(code="SYD1", name="Sydney", is_active=True)

    def test_customer_invoice_from_order_and_issue(self):
        self.client.force_authenticate(user=self.finance_user)
        create = self.client.post(
            "/api/v1/receivables/admin/invoices/",
            {"customerId": str(self.customer.public_id), "orderId": str(self.order.public_id)},
            format="json",
        )
        self.assertEqual(create.status_code, status.HTTP_201_CREATED)
        self.assertEqual(create.data["totalIncGstCents"], 11000)
        inv_id = create.data["id"]

        issue = self.client.post(f"/api/v1/receivables/admin/invoices/{inv_id}/issue/", format="json")
        self.assertEqual(issue.status_code, status.HTTP_200_OK)
        self.assertEqual(issue.data["status"], CustomerInvoiceStatus.ISSUED)

        journal = JournalEntry.objects.filter(source_id=inv_id, source_event="ar.invoice.issued").first()
        self.assertIsNotNone(journal)
        self.assertEqual(journal.status, "posted")

    def test_customer_payment_and_aging(self):
        inv = CustomerInvoiceService.create_from_order(order=self.order, actor=self.finance_user)
        CustomerInvoiceService.issue(invoice=inv, actor=self.finance_manager)

        self.client.force_authenticate(user=self.finance_user)
        pay = self.client.post(
            "/api/v1/receivables/admin/payments/",
            {
                "customerId": str(self.customer.public_id),
                "amountCents": 11000,
                "paymentDate": timezone.now().date().isoformat(),
                "allocations": [{"invoiceId": str(inv.public_id), "amountCents": 11000}],
            },
            format="json",
        )
        self.assertEqual(pay.status_code, status.HTTP_201_CREATED)
        inv.refresh_from_db()
        self.assertEqual(inv.status, CustomerInvoiceStatus.PAID)

        aging = self.client.get("/api/v1/receivables/admin/reports/aging/")
        self.assertEqual(aging.status_code, status.HTTP_200_OK)

        summary = self.client.get("/api/v1/receivables/admin/summary/")
        self.assertEqual(summary.status_code, status.HTTP_200_OK)

    def test_ap_invoice_match_and_approve(self):
        po = PurchaseOrderService.create(
            supplier_id=self.supplier.public_id,
            warehouse_code="SYD1",
            lines=[{"sku": self.variant.sku, "quantity": 10, "unit_cost_cents": 5000}],
            user=self.finance_user,
        )
        PurchaseOrderService.confirm(po=po, user=self.finance_user)
        po_line = po.lines.first()
        po_line.quantity_received = 10
        po_line.save(update_fields=["quantity_received"])
        po.status = PurchaseOrder.Status.RECEIVED
        po.total_ex_gst_cents = 50000
        po.save(update_fields=["status", "total_ex_gst_cents"])

        self.client.force_authenticate(user=self.finance_user)
        create = self.client.post(
            "/api/v1/payables/admin/invoices/",
            {"poId": str(po.public_id), "supplierInvoiceRef": "SUP-INV-001"},
            format="json",
        )
        self.assertEqual(create.status_code, status.HTTP_201_CREATED)
        inv_id = create.data["id"]

        submit = self.client.post(f"/api/v1/payables/admin/invoices/{inv_id}/submit/", format="json")
        self.assertEqual(submit.status_code, status.HTTP_200_OK)

        match = self.client.post(f"/api/v1/payables/admin/invoices/{inv_id}/match/", format="json")
        self.assertEqual(match.status_code, status.HTTP_200_OK)
        self.assertEqual(match.data["matchStatus"], "matched")

        self.client.force_authenticate(user=self.finance_manager)
        approve = self.client.post(f"/api/v1/payables/admin/invoices/{inv_id}/approve/", format="json")
        self.assertEqual(approve.status_code, status.HTTP_200_OK)
        self.assertEqual(approve.data["status"], SupplierInvoiceStatus.APPROVED)

        journal = JournalEntry.objects.filter(source_id=inv_id, source_event="ap.invoice.approved").first()
        self.assertIsNotNone(journal)

    def test_ap_summary_and_statement(self):
        self.client.force_authenticate(user=self.finance_user)
        summary = self.client.get("/api/v1/payables/admin/summary/")
        self.assertEqual(summary.status_code, status.HTTP_200_OK)

        stmt = self.client.get(f"/api/v1/payables/admin/suppliers/{self.supplier.public_id}/statement/")
        self.assertEqual(stmt.status_code, status.HTTP_200_OK)

        aging = self.client.get("/api/v1/payables/admin/reports/aging/")
        self.assertEqual(aging.status_code, status.HTTP_200_OK)
