"""Authentication and user management business logic."""

from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework_simplejwt.tokens import RefreshToken

from apps.core.exceptions import ValidationError

from apps.accounts.constants import (
    ADMIN_PORTAL_ROLES,
    SYSTEM_ROLES,
    TRADE_CUSTOMER_TYPES,
    RoleSlug,
)
from apps.accounts.rbac import ROLE_PERMISSIONS, SYSTEM_PERMISSIONS
from apps.accounts.models import Permission, RolePermission
from apps.accounts.emails import (
    send_password_changed_email,
    send_password_reset_email,
    send_verification_email,
)
from apps.accounts.models import Role, User, UserProfile, UserRole
from apps.accounts.tokens import email_verification_token, password_reset_token
from apps.customers.models import Customer, Organization, OrganizationMember
from apps.customers.services import CustomerService


class RoleService:
    @staticmethod
    def ensure_system_roles() -> None:
        for role_data in SYSTEM_ROLES:
            Role.objects.update_or_create(
                slug=role_data["slug"],
                defaults={
                    "name": role_data["name"],
                    "description": role_data["description"],
                    "is_system": role_data["is_system"],
                },
            )
        PermissionService.ensure_permissions()
        PermissionService.seed_role_permissions()

    @staticmethod
    def get_role(slug: RoleSlug | str) -> Role:
        return Role.objects.get(slug=str(slug))

    @staticmethod
    def assign_role(
        user: User,
        slug: RoleSlug | str,
        *,
        organization=None,
    ) -> UserRole:
        role = RoleService.get_role(slug)
        user_role, _ = UserRole.objects.get_or_create(
            user=user,
            role=role,
            organization=organization,
        )
        return user_role

    @staticmethod
    def remove_role(user: User, slug: RoleSlug | str, *, organization=None) -> None:
        RoleService.get_role(slug)
        UserRole.objects.filter(
            user=user,
            role__slug=str(slug),
            organization=organization,
        ).delete()

    @staticmethod
    def get_role_slugs(user: User) -> list[str]:
        return list(user.user_roles.values_list("role__slug", flat=True))

    @staticmethod
    def sync_superuser_role(user: User) -> None:
        """Assign super-admin RBAC role when Django superuser flag is set.

        ``is_staff`` alone does not grant business permissions — assign operational
        roles explicitly via ``UserRole`` or admin in-app role management.
        """
        if user.is_superuser:
            RoleService.assign_role(user, RoleSlug.SUPER_ADMIN)

    @staticmethod
    def sync_platform_roles(user: User) -> None:
        """Deprecated alias — use ``sync_superuser_role``."""
        RoleService.sync_superuser_role(user)

    @staticmethod
    def assign_customer_role(
        user: User,
        customer_type: str,
        *,
        organization=None,
    ) -> None:
        if customer_type in TRADE_CUSTOMER_TYPES:
            RoleService.assign_role(
                user, RoleSlug.TRADE_CUSTOMER, organization=organization
            )
        else:
            RoleService.assign_role(user, RoleSlug.CUSTOMER, organization=organization)

    @staticmethod
    def get_user_organization_ids(user: User) -> set[int]:
        """Organizations the user belongs to (customer profile or membership)."""
        org_ids: set[int] = set()
        customer_org = (
            Customer.objects.filter(user=user)
            .values_list("organization_id", flat=True)
            .first()
        )
        if customer_org:
            org_ids.add(customer_org)
        org_ids.update(
            user.organization_memberships.values_list("organization_id", flat=True)
        )
        org_ids.discard(None)
        return org_ids

    @staticmethod
    def get_applicable_role_ids(user: User) -> list[int]:
        """Role IDs whose organization scope matches the user (global or member org)."""
        org_ids = RoleService.get_user_organization_ids(user)
        role_filter = Q(organization__isnull=True)
        if org_ids:
            role_filter |= Q(organization_id__in=org_ids)
        return list(
            UserRole.objects.filter(user=user)
            .filter(role_filter)
            .values_list("role_id", flat=True)
            .distinct()
        )

    @staticmethod
    def has_role(user: User, slug: RoleSlug | str) -> bool:
        if not user.is_authenticated:
            return False
        return user.user_roles.filter(role__slug=str(slug)).exists()

    @staticmethod
    def has_any_role(user: User, slugs: tuple[RoleSlug | str, ...]) -> bool:
        if not user.is_authenticated:
            return False
        slug_values = [str(s) for s in slugs]
        return user.user_roles.filter(role__slug__in=slug_values).exists()

    @staticmethod
    def is_internal_staff(user: User) -> bool:
        return RoleService.has_any_role(user, tuple(ADMIN_PORTAL_ROLES))


class PermissionService:
    @staticmethod
    def ensure_permissions() -> None:
        for perm_data in SYSTEM_PERMISSIONS:
            Permission.objects.update_or_create(
                codename=perm_data["codename"],
                defaults={
                    "module": perm_data["module"],
                    "description": perm_data["description"],
                },
            )

    @staticmethod
    def seed_role_permissions() -> None:
        """Sync ROLE_PERMISSIONS matrix into role_permissions table."""
        for role_slug, codenames in ROLE_PERMISSIONS.items():
            try:
                role = Role.objects.get(slug=str(role_slug))
            except Role.DoesNotExist:
                continue
            for codename in codenames:
                permission = Permission.objects.filter(codename=codename).first()
                if permission:
                    RolePermission.objects.get_or_create(role=role, permission=permission)
            RolePermission.objects.filter(role=role).exclude(
                permission__codename__in=codenames,
            ).delete()

    @staticmethod
    def get_user_permissions(user: User) -> list[str]:
        if not user.is_authenticated:
            return []
        if user.is_superuser:
            return list(
                Permission.objects.order_by("codename").values_list("codename", flat=True)
            )

        codenames = (
            Permission.objects.filter(
                role_permissions__role_id__in=RoleService.get_applicable_role_ids(user),
            )
            .values_list("codename", flat=True)
            .distinct()
        )
        return sorted(codenames)

    @staticmethod
    def has_permission(user: User, codename: str) -> bool:
        if not user.is_authenticated:
            return False
        if user.is_superuser:
            return True
        return codename in PermissionService.get_user_permissions(user)

    @staticmethod
    def has_any_permission(user: User, codenames: tuple[str, ...]) -> bool:
        user_perms = set(PermissionService.get_user_permissions(user))
        return any(c in user_perms for c in codenames)


class AuthService:
    @staticmethod
    @transaction.atomic
    def register(
        *,
        email: str,
        password: str,
        first_name: str,
        last_name: str,
        phone: str = "",
        customer_type: str = "retail",
        company_name: str = "",
        abn: str = "",
        marketing_opt_in: bool = False,
    ) -> dict:
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError({"email": "An account with this email already exists."})

        try:
            validate_password(password)
        except DjangoValidationError as exc:
            raise ValidationError({"password": list(exc.messages)}) from exc

        user = User.objects.create_user(email=email, password=password)
        UserProfile.objects.create(
            user=user,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            preferences={"marketing_opt_in": marketing_opt_in},
        )

        organization = None
        if customer_type == "trade":
            organization = Organization.objects.create(
                legal_name=company_name,
                trading_name=company_name,
                abn=abn,
                email=email,
                phone=phone,
                customer_segment=Organization.CustomerSegment.TRADE,
            )
            customer = Customer.objects.create(
                user=user,
                organization=organization,
                customer_type=customer_type,
                trade_account_status=Customer.TradeStatus.PENDING,
            )
            OrganizationMember.objects.create(
                organization=organization,
                user=user,
                role=OrganizationMember.OrgRole.ADMIN,
                is_primary_contact=True,
                accepted_at=timezone.now(),
            )
        else:
            customer = CustomerService.create_for_user(user, customer_type=customer_type)

        RoleService.ensure_system_roles()
        RoleService.assign_customer_role(
            user, customer_type, organization=organization or customer.organization
        )
        AuthService.send_verification_email(user)
        tokens = AuthService.issue_tokens(user)
        return {
            "user": user,
            "customer": customer,
            "tokens": tokens,
            "message": "Registration successful. Please verify your email to activate your account.",
        }

    @staticmethod
    def login(*, email: str, password: str) -> dict:
        user = authenticate(username=email, password=password)
        if not user or not user.is_active:
            raise ValidationError("Invalid email or password.")
        user.last_login_at = timezone.now()
        user.save(update_fields=["last_login_at"])
        customer = Customer.objects.filter(user=user).select_related("organization").first()
        return {
            "user": user,
            "customer": customer,
            "tokens": AuthService.issue_tokens(user),
        }

    @staticmethod
    def issue_tokens(user: User) -> dict:
        refresh = RefreshToken.for_user(user)
        return {"access": str(refresh.access_token), "refresh": str(refresh)}

    @staticmethod
    def logout(*, refresh_token: str) -> None:
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception as exc:
            raise ValidationError({"refresh": "Invalid or expired refresh token."}) from exc

    @staticmethod
    def update_profile(user: User, **fields) -> User:
        profile = user.profile
        profile_fields = {}
        for key in ("first_name", "last_name", "phone", "preferences"):
            if key in fields:
                profile_fields[key] = fields[key]
        if profile_fields:
            for attr, value in profile_fields.items():
                setattr(profile, attr, value)
            profile.save()
        return user

    @staticmethod
    def get_profile_payload(user: User) -> dict:
        customer = CustomerService.get_for_user(user)
        data = {
            "user": user,
            "customer": customer,
            "roles": RoleService.get_role_slugs(user),
            "permissions": PermissionService.get_user_permissions(user),
        }
        if customer and customer.organization_id:
            data["organization"] = customer.organization
        else:
            data["organization"] = None
        return data

    @staticmethod
    def send_verification_email(user: User) -> None:
        if user.email_verified_at:
            return
        send_verification_email(user)

    @staticmethod
    def verify_email(*, uid: str, token: str) -> User:
        user = AuthService._get_user_from_uid(uid)
        if user.email_verified_at:
            return user
        if not email_verification_token.check_token(user, token):
            raise ValidationError({"token": "Invalid or expired verification link."})
        user.email_verified_at = timezone.now()
        user.save(update_fields=["email_verified_at", "updated_at"])
        return user

    @staticmethod
    def resend_verification_email(user: User) -> None:
        if user.email_verified_at:
            raise ValidationError("Email is already verified.")
        AuthService.send_verification_email(user)

    @staticmethod
    def request_password_reset(*, email: str) -> None:
        user = User.objects.filter(email__iexact=email, is_active=True).first()
        if user:
            send_password_reset_email(user)

    @staticmethod
    def reset_password(*, uid: str, token: str, password: str) -> User:
        user = AuthService._get_user_from_uid(uid)
        if not password_reset_token.check_token(user, token):
            raise ValidationError({"token": "Invalid or expired reset link."})
        try:
            validate_password(password, user=user)
        except DjangoValidationError as exc:
            raise ValidationError({"password": list(exc.messages)}) from exc
        user.set_password(password)
        user.save(update_fields=["password", "updated_at"])
        send_password_changed_email(user)
        return user

    @staticmethod
    def change_password(*, user: User, current_password: str, new_password: str) -> None:
        if not user.check_password(current_password):
            raise ValidationError({"current_password": "Current password is incorrect."})
        try:
            validate_password(new_password, user=user)
        except DjangoValidationError as exc:
            raise ValidationError({"new_password": list(exc.messages)}) from exc
        user.set_password(new_password)
        user.save(update_fields=["password", "updated_at"])
        send_password_changed_email(user)

    @staticmethod
    def _get_user_from_uid(uid: str) -> User:
        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=user_id, is_active=True)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist) as exc:
            raise ValidationError({"uid": "Invalid user identifier."}) from exc
        return user
