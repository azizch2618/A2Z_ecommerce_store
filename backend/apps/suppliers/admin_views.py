"""Supplier admin CRUD views."""
from django.db.models import Count
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import CanManageSuppliers, CanViewSuppliers
from apps.core.audit import log_operation
from apps.core.exceptions import ConflictError, NotFoundError
from apps.core.models import OperationalAuditLog
from apps.core.pagination import A2ZCursorPagination
from apps.suppliers.models import Supplier
from apps.suppliers.serializers import SupplierWriteSerializer, SupplierSerializer


class SupplierAdminPagination(A2ZCursorPagination):
    ordering = "name"


class SupplierAdminListCreateView(generics.ListCreateAPIView):
    """GET/POST /suppliers/admin/"""

    pagination_class = SupplierAdminPagination

    def get_permissions(self):
        if self.request.method == "POST":
            return [CanManageSuppliers()]
        return [CanViewSuppliers()]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return SupplierWriteSerializer
        return SupplierSerializer

    def get_queryset(self):
        search = self.request.query_params.get("search", "").strip()
        qs = Supplier.objects.annotate(
            products_supplied=Count("supplier_products", distinct=True),
        ).order_by("name")
        status_filter = self.request.query_params.get("status")
        if status_filter == "active":
            qs = qs.filter(is_active=True)
        elif status_filter == "inactive":
            qs = qs.filter(is_active=False)
        if search:
            qs = qs.filter(name__icontains=search)
        return qs

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        supplier = serializer.save()
        log_operation(
            user=request.user,
            module=OperationalAuditLog.Module.SUPPLIERS,
            action="create",
            resource_type="supplier",
            resource_id=supplier.public_id,
            details={"name": supplier.name},
        )
        return Response(SupplierSerializer(supplier).data, status=status.HTTP_201_CREATED)


class SupplierAdminDetailView(APIView):
    """PATCH /suppliers/admin/{id}/"""

    permission_classes = [CanManageSuppliers]

    def patch(self, request, supplier_id):
        supplier = Supplier.objects.filter(public_id=supplier_id).first()
        if not supplier:
            raise NotFoundError("Supplier not found.")
        serializer = SupplierWriteSerializer(supplier, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        supplier = serializer.save()
        log_operation(
            user=request.user,
            module=OperationalAuditLog.Module.SUPPLIERS,
            action="update",
            resource_type="supplier",
            resource_id=supplier.public_id,
            details=request.data,
        )
        return Response(SupplierSerializer(supplier).data)
