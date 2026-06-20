"""Accounting foundation API tests."""
from django.contrib.auth import get_user_model
from django.core.management import call_command
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounting.constants import JournalLineSide, JournalStatus, StandardAccountCode
from apps.accounting.models import JournalEntry
from apps.accounting.services import ChartOfAccountService, JournalEngine
from apps.accounts.constants import RoleSlug
from apps.accounts.services import RoleService
from apps.erp.constants import DocumentType, DomainEventType
from apps.erp.models import Company
from apps.erp.services.document_sequence import DocumentSequenceService
from apps.erp.services.events import DomainEventPublisher

User = get_user_model()


class AccountingApiTests(APITestCase):
    def setUp(self):
        RoleService.ensure_system_roles()
        call_command("seed_erp_foundation", verbosity=0)
        call_command("seed_accounting_foundation", verbosity=0)

        self.finance_user = User.objects.create_user(
            email="finance-user@example.com", password="SecurePass123!", is_staff=True
        )
        RoleService.assign_role(self.finance_user, RoleSlug.FINANCE_USER)

        self.finance_manager = User.objects.create_user(
            email="finance-manager@example.com", password="SecurePass123!", is_staff=True
        )
        RoleService.assign_role(self.finance_manager, RoleSlug.FINANCE_MANAGER)

        self.company = Company.objects.filter(is_default=True).first()

    def test_chart_of_accounts_list(self):
        self.client.force_authenticate(user=self.finance_user)
        resp = self.client.get("/api/v1/accounting/admin/chart-of-accounts/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        codes = {row["code"] for row in resp.data["data"]}
        self.assertIn(StandardAccountCode.BANK, codes)
        self.assertIn(StandardAccountCode.SALES_REVENUE, codes)

    def test_journal_entry_lifecycle(self):
        bank = ChartOfAccountService.get_by_code(company=self.company, code=StandardAccountCode.BANK)
        revenue = ChartOfAccountService.get_by_code(
            company=self.company, code=StandardAccountCode.SALES_REVENUE
        )

        self.client.force_authenticate(user=self.finance_user)
        create = self.client.post(
            "/api/v1/accounting/admin/journals/",
            {"description": "Manual adjustment test"},
            format="json",
        )
        self.assertEqual(create.status_code, status.HTTP_201_CREATED)
        entry_id = create.data["id"]
        self.assertTrue(create.data["entryNumber"].startswith("JE-"))

        line1 = self.client.post(
            f"/api/v1/accounting/admin/journals/{entry_id}/lines/",
            {
                "accountId": str(bank.public_id),
                "side": JournalLineSide.DEBIT,
                "amountCents": 11000,
            },
            format="json",
        )
        self.assertEqual(line1.status_code, status.HTTP_201_CREATED)

        line2 = self.client.post(
            f"/api/v1/accounting/admin/journals/{entry_id}/lines/",
            {
                "accountId": str(revenue.public_id),
                "side": JournalLineSide.CREDIT,
                "amountCents": 11000,
            },
            format="json",
        )
        self.assertEqual(line2.status_code, status.HTTP_201_CREATED)
        self.assertTrue(line2.data["isBalanced"])

        post_attempt = self.client.post(
            f"/api/v1/accounting/admin/journals/{entry_id}/post/", format="json"
        )
        self.assertEqual(post_attempt.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(user=self.finance_manager)
        posted = self.client.post(
            f"/api/v1/accounting/admin/journals/{entry_id}/post/", format="json"
        )
        self.assertEqual(posted.status_code, status.HTTP_200_OK)
        self.assertEqual(posted.data["status"], JournalStatus.POSTED)

    def test_trial_balance_after_posting(self):
        bank = ChartOfAccountService.get_by_code(company=self.company, code=StandardAccountCode.BANK)
        revenue = ChartOfAccountService.get_by_code(
            company=self.company, code=StandardAccountCode.SALES_REVENUE
        )
        entry = JournalEngine.create_draft(description="TB test", actor=self.finance_manager)
        JournalEngine.add_line(
            entry=entry, account=bank, side=JournalLineSide.DEBIT, amount_cents=5000
        )
        JournalEngine.add_line(
            entry=entry, account=revenue, side=JournalLineSide.CREDIT, amount_cents=5000
        )
        JournalEngine.post(entry=entry, actor=self.finance_manager)

        self.client.force_authenticate(user=self.finance_user)
        resp = self.client.get("/api/v1/accounting/admin/reports/trial-balance/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        codes = {row["accountCode"]: row for row in resp.data["data"]}
        self.assertEqual(codes[StandardAccountCode.BANK]["debitCents"], 5000)

    def test_gst_tax_calculate(self):
        self.client.force_authenticate(user=self.finance_user)
        resp = self.client.post(
            "/api/v1/accounting/admin/tax/calculate/",
            {"amountCents": 11000, "taxTreatment": "gst_inclusive"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["amountIncGstCents"], 11000)
        self.assertEqual(resp.data["gstCents"], 1000)

    def test_order_paid_event_creates_journal(self):
        DomainEventPublisher.publish(
            event_type=DomainEventType.ORDER_PAID,
            aggregate_type="order",
            aggregate_id="order-test-001",
            payload={
                "order_number": "SO-2026-000001",
                "total_inc_gst_cents": 11000,
                "total_ex_gst_cents": 10000,
                "gst_cents": 1000,
            },
            idempotency_key="order.paid:order-test-001",
        )
        entry = JournalEntry.objects.filter(source_id="order-test-001").first()
        self.assertIsNotNone(entry)
        self.assertTrue(entry.entry_number.startswith("JE-"))
        self.assertEqual(entry.status, JournalStatus.POSTED)

    def test_journal_entry_document_number_format(self):
        number = DocumentSequenceService.next_number(DocumentType.JOURNAL_ENTRY)
        self.assertRegex(number, r"^JE-\d{4}-\d{6}$")
