"""Automated RBAC boundary tests — permissions from assigned roles only."""

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.constants import RoleSlug
from apps.accounts.rbac import PermissionCodename, ROLE_PERMISSIONS
from apps.accounts.services import PermissionService, RoleService
from apps.customers.models import Customer, Organization
from apps.trade_accounts.models import TradeApplication

User = get_user_model()


class RoleBoundaryTestCase(APITestCase):
    """Verify least-privilege boundaries for operational roles."""

    def setUp(self):
        RoleService.ensure_system_roles()

    def _staff_user(self, email: str, role: str, *, is_staff: bool = True) -> User:
        user = User.objects.create_user(
            email=email,
            password="TestPass123!",
            is_staff=is_staff,
        )
        RoleService.assign_role(user, role)
        return user

    def test_is_staff_without_role_has_no_business_permissions(self):
        user = User.objects.create_user(
            email="staff-only@example.com",
            password="TestPass123!",
            is_staff=True,
        )
        perms = PermissionService.get_user_permissions(user)
        self.assertEqual(perms, [])

    def test_is_staff_does_not_implicitly_assign_manager_role(self):
        user = User.objects.create_user(
            email="implicit@example.com",
            password="TestPass123!",
            is_staff=True,
        )
        roles = RoleService.get_role_slugs(user)
        self.assertEqual(roles, [])

    def test_matrix_matches_seed_for_each_operational_role(self):
        for role_slug in (
            RoleSlug.WAREHOUSE_MANAGER,
            RoleSlug.SALES_REP,
            RoleSlug.CUSTOMER_SERVICE,
            RoleSlug.TRADE_REVIEWER,
            RoleSlug.ADMIN,
            RoleSlug.SUPER_ADMIN,
        ):
            user = self._staff_user(f"{role_slug}@example.com", role_slug)
            expected = sorted(ROLE_PERMISSIONS[str(role_slug)])
            actual = PermissionService.get_user_permissions(user)
            self.assertEqual(actual, expected, msg=f"Permission drift for {role_slug}")

    def test_warehouse_manager_cannot_approve_trade(self):
        user = self._staff_user("wh-boundary@example.com", RoleSlug.WAREHOUSE_MANAGER)
        org = Organization.objects.create(
            legal_name="WH Boundary Co",
            email="wh-boundary-co@example.com",
            customer_segment=Organization.CustomerSegment.BUSINESS,
        )
        application = TradeApplication.objects.create(organization=org, status="pending")

        self.client.force_authenticate(user)
        response = self.client.post(
            f"/api/v1/trade-accounts/admin/applications/{application.public_id}/review/",
            {"status": "approved", "credit_limit_cents": 100000},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_sales_rep_cannot_approve_trade(self):
        user = self._staff_user("sales-boundary@example.com", RoleSlug.SALES_REP)
        org = Organization.objects.create(
            legal_name="Sales Boundary Co",
            email="sales-boundary-co@example.com",
            customer_segment=Organization.CustomerSegment.BUSINESS,
        )
        application = TradeApplication.objects.create(organization=org, status="pending")

        self.client.force_authenticate(user)
        response = self.client.post(
            f"/api/v1/trade-accounts/admin/applications/{application.public_id}/review/",
            {"status": "approved", "credit_limit_cents": 100000},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_customer_service_cannot_approve_trade(self):
        user = self._staff_user("cs-boundary@example.com", RoleSlug.CUSTOMER_SERVICE)
        org = Organization.objects.create(
            legal_name="CS Boundary Co",
            email="cs-boundary-co@example.com",
            customer_segment=Organization.CustomerSegment.BUSINESS,
        )
        application = TradeApplication.objects.create(organization=org, status="pending")

        self.client.force_authenticate(user)
        response = self.client.post(
            f"/api/v1/trade-accounts/admin/applications/{application.public_id}/review/",
            {"status": "approved", "credit_limit_cents": 100000},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_trade_reviewer_can_approve_trade(self):
        user = self._staff_user("trade-reviewer@example.com", RoleSlug.TRADE_REVIEWER)
        org = Organization.objects.create(
            legal_name="Trade Review Co",
            email="trade-review-co@example.com",
            customer_segment=Organization.CustomerSegment.BUSINESS,
        )
        application = TradeApplication.objects.create(organization=org, status="pending")

        self.client.force_authenticate(user)
        response = self.client.post(
            f"/api/v1/trade-accounts/admin/applications/{application.public_id}/review/",
            {"status": "approved", "credit_limit_cents": 250000},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "approved")

    def test_manager_cannot_approve_trade_after_separation(self):
        user = self._staff_user("mgr-boundary@example.com", RoleSlug.MANAGER)
        org = Organization.objects.create(
            legal_name="Mgr Boundary Co",
            email="mgr-boundary-co@example.com",
            customer_segment=Organization.CustomerSegment.BUSINESS,
        )
        application = TradeApplication.objects.create(organization=org, status="pending")

        self.client.force_authenticate(user)
        response = self.client.post(
            f"/api/v1/trade-accounts/admin/applications/{application.public_id}/review/",
            {"status": "approved", "credit_limit_cents": 100000},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_approve_trade(self):
        user = self._staff_user("admin-boundary@example.com", RoleSlug.ADMIN)
        org = Organization.objects.create(
            legal_name="Admin Boundary Co",
            email="admin-boundary-co@example.com",
            customer_segment=Organization.CustomerSegment.BUSINESS,
        )
        application = TradeApplication.objects.create(organization=org, status="pending")

        self.client.force_authenticate(user)
        response = self.client.post(
            f"/api/v1/trade-accounts/admin/applications/{application.public_id}/review/",
            {"status": "approved", "credit_limit_cents": 500000},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_warehouse_manager_cannot_manage_catalog(self):
        user = self._staff_user("wh-cat@example.com", RoleSlug.WAREHOUSE_MANAGER)
        self.client.force_authenticate(user)
        response = self.client.post(
            "/api/v1/admin/categories/",
            {"name": "Blocked Category"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_sales_rep_cannot_export_reports(self):
        user = self._staff_user("sales-reports@example.com", RoleSlug.SALES_REP)
        self.client.force_authenticate(user)
        response = self.client.post(
            "/api/v1/analytics/admin/reports/export/",
            {"report_id": "sales", "format": "csv"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_customer_cannot_access_admin_endpoints(self):
        user = User.objects.create_user(
            email="retail-boundary@example.com",
            password="TestPass123!",
            email_verified_at=timezone.now(),
        )
        RoleService.assign_role(user, RoleSlug.CUSTOMER)
        Customer.objects.create(user=user, customer_type="retail")

        self.client.force_authenticate(user)
        for endpoint in (
            "/api/v1/admin/categories/",
            "/api/v1/trade-accounts/admin/applications/",
            "/api/v1/analytics/admin/reports/",
        ):
            response = self.client.get(endpoint)
            self.assertIn(
                response.status_code,
                [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN],
                msg=endpoint,
            )
