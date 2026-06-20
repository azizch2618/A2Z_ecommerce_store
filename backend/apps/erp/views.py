"""ERP foundation platform API views."""
from django.db.models import Q
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.pagination import A2ZCursorPagination
from apps.erp.models import (
    AuditEvent,
    Company,
    Contact,
    CoreAddress,
    DocumentSequence,
    DomainEvent,
    Notification,
    Party,
    PlatformSetting,
    WorkflowDefinition,
    WorkflowInstance,
)
from apps.erp.permissions import IsPlatformStaff
from apps.erp.serializers import (
    AuditEventSerializer,
    CompanySerializer,
    ContactSerializer,
    CoreAddressSerializer,
    DocumentSequenceSerializer,
    DomainEventSerializer,
    NotificationSerializer,
    PartySerializer,
    PlatformSettingSerializer,
    WorkflowDefinitionSerializer,
    WorkflowInstanceSerializer,
)
from apps.erp.services.party import PartyService
from apps.erp.services.workflow import WorkflowEngine


class PlatformPagination(A2ZCursorPagination):
    ordering = "-created_at"


class CompanyDetailView(generics.RetrieveUpdateAPIView):
    """GET/PATCH /platform/company/ — default company profile."""

    serializer_class = CompanySerializer
    permission_classes = [IsPlatformStaff]

    def get_object(self):
        company = Company.objects.filter(is_default=True, is_active=True).first()
        if company is None:
            company = Company.objects.filter(is_active=True).first()
        return company


class PlatformSettingListView(generics.ListAPIView):
    serializer_class = PlatformSettingSerializer
    permission_classes = [IsPlatformStaff]
    pagination_class = PlatformPagination

    def get_queryset(self):
        return PlatformSetting.objects.filter(is_sensitive=False).order_by("key")


class AuditEventListView(generics.ListAPIView):
    serializer_class = AuditEventSerializer
    permission_classes = [IsPlatformStaff]
    pagination_class = PlatformPagination

    def get_queryset(self):
        qs = AuditEvent.objects.select_related("user").order_by("-created_at")
        module = self.request.query_params.get("module")
        resource_type = self.request.query_params.get("resource_type")
        if module:
            qs = qs.filter(module=module)
        if resource_type:
            qs = qs.filter(resource_type=resource_type)
        return qs


class DocumentSequenceListView(generics.ListAPIView):
    serializer_class = DocumentSequenceSerializer
    permission_classes = [IsPlatformStaff]

    def get_queryset(self):
        return DocumentSequence.objects.filter(is_active=True).order_by("code")


class PartyListView(generics.ListAPIView):
    serializer_class = PartySerializer
    permission_classes = [IsPlatformStaff]
    pagination_class = PlatformPagination

    def get_queryset(self):
        qs = Party.objects.filter(is_active=True, deleted_at__isnull=True)
        search = self.request.query_params.get("search", "").strip()
        if search:
            qs = qs.filter(
                Q(display_name__icontains=search)
                | Q(legal_name__icontains=search)
                | Q(email__icontains=search)
            )
        role = self.request.query_params.get("role")
        if role == "customer":
            qs = qs.filter(customer__isnull=False)
        elif role == "supplier":
            qs = qs.filter(supplier__isnull=False)
        return qs.order_by("display_name")


class PartyContactListCreateView(generics.ListCreateAPIView):
    serializer_class = ContactSerializer
    permission_classes = [IsPlatformStaff]
    pagination_class = PlatformPagination

    def get_party(self) -> Party:
        return Party.objects.get(public_id=self.kwargs["party_id"])

    def get_queryset(self):
        return Contact.objects.filter(
            party=self.get_party(),
            is_active=True,
            deleted_at__isnull=True,
        )

    def perform_create(self, serializer):
        serializer.save(party=self.get_party())


class PartyAddressListCreateView(generics.ListCreateAPIView):
    serializer_class = CoreAddressSerializer
    permission_classes = [IsPlatformStaff]
    pagination_class = PlatformPagination

    def get_party(self) -> Party:
        return Party.objects.get(public_id=self.kwargs["party_id"])

    def get_queryset(self):
        return CoreAddress.objects.filter(
            party=self.get_party(),
            deleted_at__isnull=True,
        )

    def perform_create(self, serializer):
        serializer.save(
            party=self.get_party(),
            owner_kind=CoreAddress.OwnerKind.PARTY,
        )


class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsPlatformStaff]
    pagination_class = PlatformPagination

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user).order_by("-created_at")


class NotificationMarkReadView(APIView):
    permission_classes = [IsPlatformStaff]

    def post(self, request, notification_id):
        notification = Notification.objects.get(
            public_id=notification_id,
            recipient=request.user,
        )
        from apps.erp.services.notifications import NotificationService

        NotificationService.mark_read(notification)
        return Response(NotificationSerializer(notification).data)


class WorkflowDefinitionListView(generics.ListAPIView):
    serializer_class = WorkflowDefinitionSerializer
    permission_classes = [IsPlatformStaff]

    def get_queryset(self):
        return WorkflowDefinition.objects.filter(is_active=True)


class WorkflowInstanceDetailView(generics.RetrieveAPIView):
    serializer_class = WorkflowInstanceSerializer
    permission_classes = [IsPlatformStaff]
    lookup_field = "public_id"
    lookup_url_kwarg = "instance_id"

    def get_queryset(self):
        return WorkflowInstance.objects.select_related("definition")


class WorkflowTransitionView(APIView):
    permission_classes = [IsPlatformStaff]

    def post(self, request, instance_id):
        instance = WorkflowInstance.objects.select_related("definition").get(
            public_id=instance_id,
        )
        action = request.data.get("action", "")
        comment = request.data.get("comment", "")
        instance = WorkflowEngine.transition(
            instance=instance,
            action=action,
            actor=request.user,
            comment=comment,
        )
        return Response(WorkflowInstanceSerializer(instance).data)


class DomainEventListView(generics.ListAPIView):
    serializer_class = DomainEventSerializer
    permission_classes = [IsPlatformStaff]
    pagination_class = PlatformPagination

    def get_queryset(self):
        qs = DomainEvent.objects.order_by("-occurred_at")
        event_type = self.request.query_params.get("event_type")
        status_filter = self.request.query_params.get("status")
        if event_type:
            qs = qs.filter(event_type=event_type)
        if status_filter:
            qs = qs.filter(status=status_filter)
        return qs


class PartySyncView(APIView):
    """POST /platform/parties/sync/ — backfill parties from customers and suppliers."""

    permission_classes = [IsPlatformStaff]

    def post(self, request):
        from apps.customers.models import Customer
        from apps.suppliers.models import Supplier

        created = 0
        for customer in Customer.objects.filter(party__isnull=True).iterator():
            PartyService.ensure_for_customer(customer)
            created += 1
        for supplier in Supplier.objects.filter(party__isnull=True).iterator():
            PartyService.ensure_for_supplier(supplier)
            created += 1
        return Response({"synced": created}, status=status.HTTP_200_OK)
