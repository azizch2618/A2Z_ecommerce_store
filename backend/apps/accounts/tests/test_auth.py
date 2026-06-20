"""Authentication API tests."""
from django.core import mail
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.constants import RoleSlug
from apps.accounts.models import User
from apps.accounts.services import RoleService
from apps.accounts.tokens import email_verification_token, password_reset_token
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class AuthAPITestCase(APITestCase):
    def setUp(self):
        RoleService.ensure_system_roles()
        self.register_url = reverse("accounts:register")
        self.login_url = reverse("accounts:login")
        self.profile_url = reverse("accounts:profile")
        self.logout_url = reverse("accounts:logout")

    def _register_payload(self, email="buyer@example.com"):
        return {
            "email": email,
            "password": "SecurePass123!",
            "password_confirm": "SecurePass123!",
            "first_name": "Alex",
            "last_name": "Buyer",
            "phone": "0400000000",
            "customer_type": "retail",
        }

    def test_register_login_profile_logout_flow(self):
        register_response = self.client.post(
            self.register_url, self._register_payload(), format="json"
        )
        self.assertEqual(register_response.status_code, status.HTTP_201_CREATED)
        self.assertIn("user", register_response.data)
        self.assertIn("tokens", register_response.data)
        self.assertEqual(len(mail.outbox), 1)

        user = User.objects.get(email="buyer@example.com")
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = email_verification_token.make_token(user)
        verify_response = self.client.post(
            reverse("accounts:verify-email"),
            {"uid": uid, "token": token},
            format="json",
        )
        self.assertEqual(verify_response.status_code, status.HTTP_200_OK)

        login_response = self.client.post(
            self.login_url,
            {"email": "buyer@example.com", "password": "SecurePass123!"},
            format="json",
        )
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

        access = login_response.data["tokens"]["access"]
        refresh = login_response.data["tokens"]["refresh"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

        profile_response = self.client.get(self.profile_url)
        self.assertEqual(profile_response.status_code, status.HTTP_200_OK)
        self.assertIn(RoleSlug.CUSTOMER, profile_response.data["roles"])

        logout_response = self.client.post(
            self.logout_url, {"refresh": refresh}, format="json"
        )
        self.assertEqual(logout_response.status_code, status.HTTP_204_NO_CONTENT)

    def test_trade_customer_gets_trade_role(self):
        payload = self._register_payload(email="trade@example.com")
        payload["customer_type"] = "trade"
        payload["company_name"] = "Trade Co Pty Ltd"
        payload["abn"] = "53004085616"
        response = self.client.post(self.register_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = User.objects.get(email="trade@example.com")
        self.assertTrue(
            user.user_roles.filter(role__slug=RoleSlug.TRADE_CUSTOMER).exists()
        )
        customer = user.customer
        self.assertEqual(customer.trade_account_status, "pending")
        self.assertIsNotNone(customer.organization)
        self.assertEqual(customer.organization.legal_name, "Trade Co Pty Ltd")

    def test_verify_email(self):
        self.client.post(self.register_url, self._register_payload(), format="json")
        user = User.objects.get(email="buyer@example.com")
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = email_verification_token.make_token(user)

        response = self.client.post(
            reverse("accounts:verify-email"),
            {"uid": uid, "token": token},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertIsNotNone(user.email_verified_at)

    def test_password_reset_flow(self):
        self.client.post(self.register_url, self._register_payload(), format="json")
        user = User.objects.get(email="buyer@example.com")

        forgot_response = self.client.post(
            reverse("accounts:forgot-password"),
            {"email": user.email},
            format="json",
        )
        self.assertEqual(forgot_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 2)

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = password_reset_token.make_token(user)
        reset_response = self.client.post(
            reverse("accounts:reset-password"),
            {
                "uid": uid,
                "token": token,
                "password": "NewSecurePass456!",
                "password_confirm": "NewSecurePass456!",
            },
            format="json",
        )
        self.assertEqual(reset_response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertTrue(user.check_password("NewSecurePass456!"))
