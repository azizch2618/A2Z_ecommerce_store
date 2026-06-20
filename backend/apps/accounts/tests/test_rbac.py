"""Enterprise RBAC tests."""

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.constants import RoleSlug
from apps.accounts.models import Permission, Role, RolePermission, UserRole
from apps.accounts.rbac import PermissionCodename
from apps.customers.models import Customer, Organization
from apps.accounts.services import PermissionService, RoleService

User = get_user_model()


class RBACTestCase(TestCase):
    def setUp(self):
        RoleService.ensure_system_roles()
        self.client = APIClient()

    def _create_user(self, email: str, *, role: str, is_staff: bool = False) -> User:
        user = User.objects.create_user(
            email=email,
            password="TestPass123!",
            is_staff=is_staff,
        )
        RoleService.assign_role(user, role)
        return user

    def test_warehouse_manager_cannot_manage_catalog(self):
        user = self._create_user("wh@example.com", role=RoleSlug.WAREHOUSE_MANAGER)
        perms = PermissionService.get_user_permissions(user)
        self.assertIn(PermissionCodename.INVENTORY_MANAGE, perms)
        self.assertNotIn(PermissionCodename.CATALOG_MANAGE, perms)

    def test_sales_rep_can_view_orders_not_inventory_manage(self):
        user = self._create_user("sales@example.com", role=RoleSlug.SALES_REP)
        perms = PermissionService.get_user_permissions(user)
        self.assertIn(PermissionCodename.ORDERS_MANAGE, perms)
        self.assertNotIn(PermissionCodename.INVENTORY_MANAGE, perms)

    def test_customer_has_store_checkout_only(self):
        user = self._create_user("cust@example.com", role=RoleSlug.CUSTOMER)
        perms = PermissionService.get_user_permissions(user)
        self.assertEqual(perms, [PermissionCodename.STORE_CHECKOUT])

    def test_superuser_gets_all_permissions(self):
        user = User.objects.create_superuser(
            email="super@example.com", password="TestPass123!"
        )
        perms = PermissionService.get_user_permissions(user)
        self.assertIn(PermissionCodename.USERS_MANAGE, perms)

    def test_is_staff_flag_alone_grants_no_permissions(self):
        user = User.objects.create_user(
            email="staffonly@example.com",
            password="TestPass123!",
            is_staff=True,
        )
        self.assertEqual(PermissionService.get_user_permissions(user), [])

    def test_profile_includes_permissions(self):
        user = self._create_user(
            "mgr@example.com", role=RoleSlug.MANAGER, is_staff=True
        )
        self.client.force_authenticate(user=user)
        response = self.client.get("/api/v1/auth/profile/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("permissions", response.data)
        self.assertIn(PermissionCodename.DASHBOARD_VIEW, response.data["permissions"])

    def test_permissions_endpoint(self):
        user = self._create_user("cs@example.com", role=RoleSlug.CUSTOMER_SERVICE)
        self.client.force_authenticate(user=user)
        response = self.client.get("/api/v1/auth/permissions/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(RoleSlug.CUSTOMER_SERVICE, response.data["roles"])
        self.assertIn(PermissionCodename.ORDERS_MANAGE, response.data["permissions"])

    def test_inventory_api_requires_permission(self):
        wh_user = self._create_user("wh2@example.com", role=RoleSlug.WAREHOUSE_MANAGER)
        sales_user = self._create_user("sales2@example.com", role=RoleSlug.SALES_REP)

        self.client.force_authenticate(user=wh_user)
        wh_response = self.client.get("/api/v1/inventory/levels/")
        self.assertEqual(wh_response.status_code, status.HTTP_200_OK)

        self.client.force_authenticate(user=sales_user)
        sales_response = self.client.get("/api/v1/inventory/levels/")
        self.assertEqual(sales_response.status_code, status.HTTP_403_FORBIDDEN)

    def test_runtime_permissions_read_from_database(self):
        user = self._create_user("db@example.com", role=RoleSlug.MANAGER, is_staff=True)
        perms_before = PermissionService.get_user_permissions(user)
        self.assertIn(PermissionCodename.CATALOG_MANAGE, perms_before)

        role = Role.objects.get(slug=RoleSlug.MANAGER)
        catalog_manage = Permission.objects.get(codename=PermissionCodename.CATALOG_MANAGE)
        RolePermission.objects.filter(role=role, permission=catalog_manage).delete()

        perms_after = PermissionService.get_user_permissions(user)
        self.assertNotIn(PermissionCodename.CATALOG_MANAGE, perms_after)
        self.assertIn(PermissionCodename.DASHBOARD_VIEW, perms_after)

    def test_checkout_requires_store_checkout_permission(self):
        user = User.objects.create_user(email="nostore@example.com", password="TestPass123!")
        RoleService.assign_role(user, RoleSlug.SALES_REP)
        self.client.force_authenticate(user=user)
        response = self.client.post(
            "/api/v1/orders/",
            {
                "cart_id": "00000000-0000-0000-0000-000000000000",
                "billing_address": {"line1": "1 St", "suburb": "Sydney", "state": "NSW", "postcode": "2000", "country": "AU"},
                "shipping_method_id": "00000000-0000-0000-0000-000000000001",
                "payment_method": "card",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_org_scoped_role_only_applies_for_matching_organization(self):
        org_a = Organization.objects.create(
            legal_name="Org A Pty Ltd",
            email="a@example.com",
            customer_segment=Organization.CustomerSegment.BUSINESS,
        )
        org_b = Organization.objects.create(
            legal_name="Org B Pty Ltd",
            email="b@example.com",
            customer_segment=Organization.CustomerSegment.BUSINESS,
        )
        user = User.objects.create_user(email="orguser@example.com", password="TestPass123!")
        Customer.objects.create(user=user, customer_type="business", organization=org_a)

        manager_role = Role.objects.get(slug=RoleSlug.MANAGER)
        UserRole.objects.filter(user=user).delete()
        UserRole.objects.create(user=user, role=manager_role, organization=org_b)

        perms = PermissionService.get_user_permissions(user)
        self.assertNotIn(PermissionCodename.CATALOG_MANAGE, perms)

        UserRole.objects.filter(user=user).delete()
        UserRole.objects.create(user=user, role=manager_role, organization=org_a)
        perms = PermissionService.get_user_permissions(user)
        self.assertIn(PermissionCodename.CATALOG_MANAGE, perms)

    def test_checkout_requires_verified_email(self):
        user = User.objects.create_user(email="unverified@example.com", password="TestPass123!")
        RoleService.assign_role(user, RoleSlug.CUSTOMER)
        self.client.force_authenticate(user=user)
        response = self.client.post(
            "/api/v1/orders/",
            {
                "cart_id": "00000000-0000-0000-0000-000000000000",
                "billing_address": {
                    "line1": "1 St",
                    "suburb": "Sydney",
                    "state": "NSW",
                    "postcode": "2000",
                    "country": "AU",
                },
                "shipping_method_id": "00000000-0000-0000-0000-000000000001",
                "payment_method": "card",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
