"""Auth serializers."""
from django.contrib.auth import authenticate
from rest_framework import serializers

from apps.accounts.models import User, UserProfile
from apps.accounts.services import AuthService, PermissionService
from apps.customers.serializers import CustomerSerializer, OrganizationSerializer


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ("first_name", "last_name", "phone", "avatar_url")


class UserSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="public_id", read_only=True)
    first_name = serializers.CharField(source="profile.first_name", read_only=True)
    last_name = serializers.CharField(source="profile.last_name", read_only=True)
    phone = serializers.CharField(source="profile.phone", read_only=True, allow_null=True)
    avatar_url = serializers.CharField(
        source="profile.avatar_url", read_only=True, allow_blank=True
    )
    email_verified = serializers.SerializerMethodField()
    roles = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "public_id",
            "email",
            "first_name",
            "last_name",
            "phone",
            "avatar_url",
            "email_verified",
            "roles",
            "permissions",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields

    def get_email_verified(self, obj: User) -> bool:
        return obj.email_verified_at is not None

    def get_roles(self, obj: User) -> list[str]:
        return list(obj.user_roles.values_list("role__slug", flat=True))

    def get_permissions(self, obj: User) -> list[str]:
        return PermissionService.get_user_permissions(obj)


class ProfileSerializer(serializers.Serializer):
    """Full authenticated profile payload."""

    id = serializers.UUIDField(source="user.public_id", read_only=True)
    public_id = serializers.UUIDField(source="user.public_id", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    first_name = serializers.CharField(source="user.profile.first_name", read_only=True)
    last_name = serializers.CharField(source="user.profile.last_name", read_only=True)
    phone = serializers.CharField(
        source="user.profile.phone", read_only=True, allow_null=True
    )
    avatar_url = serializers.CharField(
        source="user.profile.avatar_url", read_only=True, allow_blank=True
    )
    email_verified = serializers.SerializerMethodField()
    roles = serializers.ListField(child=serializers.CharField(), read_only=True)
    permissions = serializers.ListField(child=serializers.CharField(), read_only=True)
    customer = CustomerSerializer(read_only=True, allow_null=True)
    organization = OrganizationSerializer(read_only=True, allow_null=True)
    created_at = serializers.DateTimeField(source="user.created_at", read_only=True)
    updated_at = serializers.DateTimeField(source="user.updated_at", read_only=True)

    def get_email_verified(self, obj: dict) -> bool:
        return obj["user"].email_verified_at is not None


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    customer_type = serializers.ChoiceField(
        choices=["retail", "trade", "contractor", "business"],
        default="retail",
    )
    company_name = serializers.CharField(
        max_length=255, required=False, allow_blank=True
    )
    abn = serializers.CharField(max_length=11, required=False, allow_blank=True)
    marketing_opt_in = serializers.BooleanField(default=False)

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError(
                {"password_confirm": "Passwords do not match."}
            )

        customer_type = attrs.get("customer_type", "retail")
        if customer_type == "trade":
            company_name = (attrs.get("company_name") or "").strip()
            abn = "".join(ch for ch in (attrs.get("abn") or "") if ch.isdigit())
            if not company_name:
                raise serializers.ValidationError(
                    {"company_name": "Company name is required for trade accounts."}
                )
            if len(abn) != 11:
                raise serializers.ValidationError(
                    {"abn": "Enter a valid 11-digit ABN."}
                )
            attrs["company_name"] = company_name
            attrs["abn"] = abn

        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirm", None)
        return AuthService.register(**validated_data)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(
            request=self.context.get("request"),
            username=attrs["email"],
            password=attrs["password"],
        )
        if not user:
            raise serializers.ValidationError("Invalid email or password.")
        if not user.is_active:
            raise serializers.ValidationError("This account has been deactivated.")
        attrs["user"] = user
        return attrs


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField(required=False, allow_blank=True)


class UpdateProfileSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=100, required=False)
    last_name = serializers.CharField(max_length=100, required=False)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    preferences = serializers.JSONField(required=False)


class VerifyEmailSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ResetPasswordSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError(
                {"password_confirm": "Passwords do not match."}
            )
        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)
    new_password_confirm = serializers.CharField(write_only=True, min_length=8)

    def validate(self, attrs):
        if attrs["new_password"] != attrs["new_password_confirm"]:
            raise serializers.ValidationError(
                {"new_password_confirm": "Passwords do not match."}
            )
        return attrs
