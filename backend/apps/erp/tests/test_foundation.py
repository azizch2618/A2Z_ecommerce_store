"""ERP foundation layer tests."""
from django.contrib.auth import get_user_model
from django.core.management import call_command
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.constants import RoleSlug
from apps.accounts.services import RoleService
from apps.customers.models import Customer, Organization
from apps.erp.constants import DocumentType, DomainEventType, WorkflowCode
from apps.erp.models import AuditEvent, Company, DomainEvent, Party, WorkflowInstance
from apps.erp.services.document_sequence import DocumentSequenceService
from apps.erp.services.events import DomainEventPublisher
from apps.erp.services.party import PartyService
from apps.erp.services.workflow import WorkflowEngine
from apps.suppliers.models import Supplier

User = get_user_model()


class ErpFoundationTestCase(APITestCase):
    def setUp(self):
        RoleService.ensure_system_roles()
        call_command("seed_erp_foundation", verbosity=0)

        self.admin = User.objects.create_user(
            email="erp-admin@example.com",
            password="SecurePass123!",
            is_staff=True,
        )
        RoleService.assign_role(self.admin, RoleSlug.ADMIN)

    def test_document_sequence_generates_configurable_numbers(self):
        first = DocumentSequenceService.next_number(DocumentType.SALES_ORDER)
        second = DocumentSequenceService.next_number(DocumentType.SALES_ORDER)
        self.assertTrue(first.startswith("SO-"))
        self.assertTrue(second.startswith("SO-"))
        self.assertNotEqual(first, second)
        self.assertRegex(first, r"SO-\d{4}-\d{6}")

    def test_party_service_links_customer_and_supplier(self):
        org = Organization.objects.create(
            legal_name="Test Org Pty Ltd",
            trading_name="Test Org",
            email="org@example.com",
            customer_segment=Organization.CustomerSegment.BUSINESS,
        )
        user = User.objects.create_user(email="party-customer@example.com", password="SecurePass123!")
        customer = Customer.objects.create(user=user, organization=org, customer_type="business")
        supplier = Supplier.objects.create(code="SUP-001", name="Test Supplier")

        customer_party = PartyService.ensure_for_customer(customer)
        supplier_party = PartyService.ensure_for_supplier(supplier)

        self.assertEqual(Party.objects.filter(customer=customer).count(), 1)
        self.assertEqual(Party.objects.filter(supplier=supplier).count(), 1)
        self.assertIn("customer", customer_party.roles)
        self.assertIn("supplier", supplier_party.roles)

    def test_domain_event_outbox_publishes(self):
        event = DomainEventPublisher.publish(
            event_type=DomainEventType.ORDER_CREATED,
            aggregate_type="order",
            aggregate_id="test-order-001",
            payload={"order_number": "SO-2026-000001"},
            idempotency_key="test-order-created-001",
        )
        self.assertEqual(event.status, "published")
        self.assertTrue(AuditEvent.objects.filter(resource_id="test-order-001").exists())

    def test_workflow_engine_trade_approval_flow(self):
        instance = WorkflowEngine.start(
            definition_code=WorkflowCode.PO_APPROVAL,
            resource_type="purchase_order",
            resource_id="po-test-001",
            actor=self.admin,
        )
        self.assertEqual(instance.current_state, "draft")

        reviewer = User.objects.create_user(
            email="erp-manager@example.com",
            password="SecurePass123!",
            is_staff=True,
        )
        RoleService.assign_role(reviewer, RoleSlug.MANAGER)

        instance = WorkflowEngine.transition(
            instance=instance,
            action="submit",
            actor=reviewer,
        )
        self.assertEqual(instance.current_state, "submitted")
        self.assertEqual(
            WorkflowInstance.objects.filter(resource_id="po-test-001").count(),
            1,
        )

    def test_platform_company_api(self):
        self.client.force_authenticate(self.admin)
        response = self.client.get("/api/v1/platform/company/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["code"], "A2Z")

    def test_platform_audit_api(self):
        DomainEventPublisher.publish(
            event_type=DomainEventType.TRADE_APPROVED,
            aggregate_type="trade_application",
            aggregate_id="app-001",
            payload={},
            idempotency_key="audit-api-test-001",
        )
        self.client.force_authenticate(self.admin)
        response = self.client.get("/api/v1/platform/audit/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data["data"]), 1)

    def test_default_company_exists_after_seed(self):
        self.assertTrue(Company.objects.filter(is_default=True).exists())
