"""Executive BI API tests."""
from django.contrib.auth import get_user_model
from django.core.management import call_command
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.constants import RoleSlug
from apps.accounts.services import RoleService

User = get_user_model()


class ExecutiveBiApiTests(APITestCase):
    def setUp(self):
        RoleService.ensure_system_roles()
        call_command("seed_erp_foundation", verbosity=0)
        call_command("seed_accounting_foundation", verbosity=0)

        self.executive = User.objects.create_user(
            email="executive@example.com", password="SecurePass123!", is_staff=True
        )
        RoleService.assign_role(self.executive, RoleSlug.EXECUTIVE)

        self.employee = User.objects.create_user(
            email="employee@example.com", password="SecurePass123!", is_staff=False
        )
        RoleService.assign_role(self.employee, RoleSlug.EMPLOYEE)

        self.admin = User.objects.create_user(
            email="admin-bi@example.com", password="SecurePass123!", is_staff=True
        )
        RoleService.assign_role(self.admin, RoleSlug.ADMIN)

    def test_executive_dashboard_requires_analytics_permission(self):
        self.client.force_authenticate(user=self.executive)
        response = self.client.get("/api/v1/analytics/admin/bi/executive/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("executiveKpis", response.data)
        self.assertIn("revenueCents", response.data["executiveKpis"])

    def test_employee_denied_bi_access(self):
        self.client.force_authenticate(user=self.employee)
        response = self.client.get("/api/v1/analytics/admin/bi/executive/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_bi_snapshot_returns_all_sections(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get("/api/v1/analytics/admin/bi/snapshot/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for key in ("executive", "sales", "inventory", "procurement", "finance", "hr", "kpis"):
            self.assertIn(key, response.data)

    def test_kpi_evaluate_seeds_defaults(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get("/api/v1/analytics/admin/bi/kpis/evaluate/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data["data"]) >= 7)

    def test_scheduled_report_create(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(
            "/api/v1/analytics/admin/bi/schedules/",
            {
                "name": "Weekly Sales Report",
                "reportId": "sales",
                "format": "csv",
                "frequency": "weekly",
                "recipientEmails": ["finance@example.com"],
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("id", response.data)

    def test_bi_export_csv(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(
            "/api/v1/analytics/admin/bi/reports/export/",
            {"reportId": "sales", "format": "csv"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("filename", response.data)
        self.assertEqual(response.data.get("mimeType"), "text/csv")
