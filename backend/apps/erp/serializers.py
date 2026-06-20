"""ERP platform API serializers."""
from rest_framework import serializers

from apps.erp.models import (
    AuditEvent,
    BusinessUnit,
    Company,
    Contact,
    CoreAddress,
    CostCenter,
    Department,
    DocumentSequence,
    DomainEvent,
    Notification,
    Party,
    PlatformSetting,
    WorkflowDefinition,
    WorkflowInstance,
)


class CompanySerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="public_id", read_only=True)

    class Meta:
        model = Company
        fields = (
            "id",
            "public_id",
            "code",
            "legal_name",
            "trading_name",
            "abn",
            "acn",
            "gst_registered",
            "base_currency",
            "fiscal_year_start_month",
            "email",
            "phone",
            "website",
            "is_active",
            "is_default",
            "metadata",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("public_id", "created_at", "updated_at")


class BusinessUnitSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="public_id", read_only=True)
    company_id = serializers.UUIDField(source="company.public_id", read_only=True)

    class Meta:
        model = BusinessUnit
        fields = (
            "id",
            "public_id",
            "company_id",
            "code",
            "name",
            "description",
            "is_active",
            "metadata",
        )
        read_only_fields = fields


class DepartmentSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="public_id", read_only=True)

    class Meta:
        model = Department
        fields = ("id", "public_id", "code", "name", "description", "is_active", "metadata")
        read_only_fields = fields


class CostCenterSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="public_id", read_only=True)

    class Meta:
        model = CostCenter
        fields = ("id", "public_id", "code", "name", "description", "is_active", "metadata")
        read_only_fields = fields


class PartySerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="public_id", read_only=True)
    roles = serializers.ListField(read_only=True)

    class Meta:
        model = Party
        fields = (
            "id",
            "public_id",
            "party_type",
            "display_name",
            "legal_name",
            "tax_id",
            "email",
            "phone",
            "is_active",
            "roles",
            "metadata",
            "created_at",
        )
        read_only_fields = ("public_id", "roles", "created_at")


class ContactSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="public_id", read_only=True)

    class Meta:
        model = Contact
        fields = (
            "id",
            "public_id",
            "first_name",
            "last_name",
            "email",
            "phone",
            "position",
            "notes",
            "is_primary",
            "is_active",
        )
        read_only_fields = ("public_id",)


class CoreAddressSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="public_id", read_only=True)

    class Meta:
        model = CoreAddress
        fields = (
            "id",
            "public_id",
            "owner_kind",
            "address_type",
            "label",
            "line1",
            "line2",
            "suburb",
            "state",
            "postcode",
            "country",
            "is_default",
        )
        read_only_fields = ("public_id", "owner_kind")


class DocumentSequenceSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="public_id", read_only=True)
    next_preview = serializers.SerializerMethodField()

    class Meta:
        model = DocumentSequence
        fields = (
            "id",
            "public_id",
            "code",
            "name",
            "prefix",
            "pattern",
            "reset_period",
            "padding",
            "next_value",
            "is_active",
            "next_preview",
        )
        read_only_fields = fields

    def get_next_preview(self, obj: DocumentSequence) -> str:
        from django.utils import timezone

        from apps.erp.services.document_sequence import DocumentSequenceService

        return DocumentSequenceService._format_number(
            obj, obj.next_value, timezone.localdate()
        )


class AuditEventSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="public_id", read_only=True)
    user_email = serializers.EmailField(source="user.email", read_only=True, allow_null=True)

    class Meta:
        model = AuditEvent
        fields = (
            "id",
            "public_id",
            "user_email",
            "module",
            "action",
            "resource_type",
            "resource_id",
            "summary",
            "changes",
            "metadata",
            "created_at",
        )
        read_only_fields = fields


class NotificationSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="public_id", read_only=True)

    class Meta:
        model = Notification
        fields = (
            "id",
            "public_id",
            "channel",
            "subject",
            "body",
            "status",
            "resource_type",
            "resource_id",
            "sent_at",
            "read_at",
            "created_at",
        )
        read_only_fields = fields


class WorkflowDefinitionSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="public_id", read_only=True)

    class Meta:
        model = WorkflowDefinition
        fields = (
            "id",
            "public_id",
            "code",
            "name",
            "document_type",
            "version",
            "initial_state",
            "states",
            "transitions",
            "is_active",
        )
        read_only_fields = fields


class WorkflowInstanceSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="public_id", read_only=True)
    definition_code = serializers.CharField(source="definition.code", read_only=True)
    available_actions = serializers.SerializerMethodField()

    class Meta:
        model = WorkflowInstance
        fields = (
            "id",
            "public_id",
            "definition_code",
            "current_state",
            "resource_type",
            "resource_id",
            "status",
            "history",
            "available_actions",
            "completed_at",
            "created_at",
        )
        read_only_fields = fields

    def get_available_actions(self, obj: WorkflowInstance) -> list:
        from apps.erp.services.workflow import WorkflowEngine

        return WorkflowEngine.available_actions(obj)


class DomainEventSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="public_id", read_only=True)

    class Meta:
        model = DomainEvent
        fields = (
            "id",
            "public_id",
            "event_type",
            "aggregate_type",
            "aggregate_id",
            "payload",
            "status",
            "occurred_at",
            "published_at",
        )
        read_only_fields = fields


class PlatformSettingSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="public_id", read_only=True)

    class Meta:
        model = PlatformSetting
        fields = ("id", "public_id", "key", "value", "description", "is_sensitive")
        read_only_fields = ("public_id",)
