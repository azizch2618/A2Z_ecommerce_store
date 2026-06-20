"""Warehouse admin CRUD views."""
from django.db.models import Count, Sum
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import CanManageWarehouse, CanViewInventory
from apps.core.audit import log_operation
from apps.core.exceptions import NotFoundError
from apps.core.models import OperationalAuditLog
from apps.core.pagination import A2ZCursorPagination
from apps.inventory.models import InventoryLevel, Warehouse
from apps.inventory.serializers import WarehouseAdminSerializer, WarehouseWriteSerializer


class WarehouseAdminPagination(A2ZCursorPagination):
    ordering = "code"


class WarehouseAdminListCreateView(generics.ListCreateAPIView):
    """GET/POST /inventory/admin/warehouses/"""

    pagination_class = WarehouseAdminPagination

    def get_permissions(self):
        if self.request.method == "POST":
            return [CanManageWarehouse()]
        return [CanViewInventory()]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return WarehouseWriteSerializer
        return WarehouseAdminSerializer

    def get_queryset(self):
        search = self.request.query_params.get("search", "").strip()
        qs = (
            Warehouse.objects.annotate(
                sku_count=Count("inventory_levels", distinct=True),
                total_units=Sum("inventory_levels__quantity_on_hand"),
            )
            .order_by("code")
        )
        if search:
            qs = qs.filter(code__icontains=search) | qs.filter(name__icontains=search)
        status_filter = self.request.query_params.get("status")
        if status_filter == "active":
            qs = qs.filter(is_active=True)
        elif status_filter == "inactive":
            qs = qs.filter(is_active=False)
        return qs

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        warehouse = serializer.save()
        log_operation(
            user=request.user,
            module=OperationalAuditLog.Module.INVENTORY,
            action="create",
            resource_type="warehouse",
            resource_id=warehouse.public_id,
            details={"code": warehouse.code},
        )
        warehouse.sku_count = 0
        warehouse.total_units = 0
        return Response(WarehouseAdminSerializer(warehouse).data, status=status.HTTP_201_CREATED)


class WarehouseAdminDetailView(APIView):
    """PATCH /inventory/admin/warehouses/{id}/"""

    permission_classes = [CanManageWarehouse]

    def patch(self, request, warehouse_id):
        warehouse = Warehouse.objects.filter(public_id=warehouse_id).first()
        if not warehouse:
            raise NotFoundError("Warehouse not found.")
        serializer = WarehouseWriteSerializer(warehouse, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        warehouse = serializer.save()
        log_operation(
            user=request.user,
            module=OperationalAuditLog.Module.INVENTORY,
            action="update",
            resource_type="warehouse",
            resource_id=warehouse.public_id,
            details=request.data,
        )
        stats = InventoryLevel.objects.filter(warehouse=warehouse).aggregate(
            sku_count=Count("id"),
            total_units=Sum("quantity_on_hand"),
        )
        warehouse.sku_count = stats["sku_count"] or 0
        warehouse.total_units = stats["total_units"] or 0
        return Response(WarehouseAdminSerializer(warehouse).data)
