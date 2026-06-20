"""CRM API and RBAC tests."""
from django.contrib.auth import get_user_model
from django.core.management import call_command
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.constants import RoleSlug
from apps.accounts.rbac import PermissionCodename
from apps.accounts.services import PermissionService, RoleService
from apps.crm.constants import LeadStatus

User = get_user_model()


class CrmApiTests(APITestCase):
    def setUp(self):
        RoleService.ensure_system_roles()
        call_command("seed_erp_foundation", verbosity=0)

        self.manager = User.objects.create_user(
            email="crm-manager@example.com",
            password="SecurePass123!",
            is_staff=True,
        )
        RoleService.assign_role(self.manager, RoleSlug.MANAGER)

        self.sales_rep = User.objects.create_user(
            email="crm-sales@example.com",
            password="SecurePass123!",
            is_staff=True,
        )
        RoleService.assign_role(self.sales_rep, RoleSlug.SALES_REP)

        self.warehouse = User.objects.create_user(
            email="crm-wh@example.com",
            password="SecurePass123!",
            is_staff=True,
        )
        RoleService.assign_role(self.warehouse, RoleSlug.WAREHOUSE_MANAGER)

    def test_sales_rep_can_view_crm_dashboard(self):
        self.client.force_authenticate(user=self.sales_rep)
        response = self.client.get("/api/v1/crm/admin/dashboard/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("totalLeads", response.data)

    def test_warehouse_manager_cannot_access_crm(self):
        self.client.force_authenticate(user=self.warehouse)
        response = self.client.get("/api/v1/crm/admin/leads/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_manager_creates_lead_and_opportunity(self):
        self.client.force_authenticate(user=self.manager)
        lead_resp = self.client.post(
            "/api/v1/crm/admin/leads/",
            {
                "title": "Acme Hardware",
                "companyName": "Acme Hardware Pty Ltd",
                "contactName": "Jane Doe",
                "contactEmail": "jane@acme.example",
                "source": "referral",
                "assignedToId": str(self.sales_rep.public_id),
            },
            format="json",
        )
        self.assertEqual(lead_resp.status_code, status.HTTP_201_CREATED)
        lead_id = lead_resp.data["id"]
        self.assertEqual(lead_resp.data["status"], LeadStatus.NEW)
        self.assertIsNotNone(lead_resp.data["partyId"])

        convert_resp = self.client.post(
            f"/api/v1/crm/admin/leads/{lead_id}/convert/",
            {
                "name": "Acme Annual Supply",
                "expectedRevenueCents": 2500000,
                "probability": 40,
            },
            format="json",
        )
        self.assertEqual(convert_resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(convert_resp.data["leadId"], lead_id)

        timeline = self.client.get(f"/api/v1/crm/admin/timeline/?leadId={lead_id}")
        self.assertEqual(timeline.status_code, status.HTTP_200_OK)

    def test_rbac_permissions_include_crm(self):
        self.assertTrue(
            PermissionService.has_permission(self.manager, PermissionCodename.CRM_MANAGE)
        )
        self.assertTrue(
            PermissionService.has_permission(self.sales_rep, PermissionCodename.CRM_VIEW)
        )
        self.assertFalse(
            PermissionService.has_permission(self.warehouse, PermissionCodename.CRM_VIEW)
        )

    def test_won_opportunity_creates_quote_draft(self):
        from apps.trade_accounts.models import Quote

        self.client.force_authenticate(user=self.manager)
        lead_resp = self.client.post(
            "/api/v1/crm/admin/leads/",
            {
                "title": "Quote Test Lead",
                "companyName": "Quote Co",
                "contactEmail": "quote@test.example",
            },
            format="json",
        )
        lead_id = lead_resp.data["id"]
        convert_resp = self.client.post(
            f"/api/v1/crm/admin/leads/{lead_id}/convert/",
            {"name": "Big Deal", "expectedRevenueCents": 500000},
            format="json",
        )
        opp_id = convert_resp.data["id"]
        patch_resp = self.client.patch(
            f"/api/v1/crm/admin/opportunities/{opp_id}/",
            {"status": "won"},
            format="json",
        )
        self.assertEqual(patch_resp.status_code, status.HTTP_200_OK)
        detail = self.client.get(f"/api/v1/crm/admin/opportunities/{opp_id}/")
        self.assertIsNotNone(detail.data.get("quoteDraft"))
        quote = Quote.objects.filter(crm_opportunity__public_id=opp_id).first()
        self.assertIsNotNone(quote)
        self.assertEqual(quote.status, Quote.Status.DRAFT)
        self.assertTrue(quote.quote_number.startswith("QT-"))
