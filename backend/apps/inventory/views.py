"""Inventory API views."""
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.catalog.models import ProductVariant
from apps.accounts.permissions import CanManageInventory, CanViewInventory
from apps.core.pagination import A2ZCursorPagination
from apps.inventory.filters import InventoryFilter, StockMovementFilter
from apps.inventory.serializers import (
    InventoryAlertSerializer,
    InventoryLevelSerializer,
    InventorySerializer,
    LowStockAlertSerializer,
    ReorderLevelSerializer,
    StockAdjustmentSerializer,
    StockInSerializer,
    StockMovementSerializer,
    StockOperationResponseSerializer,
    StockOutSerializer,
    StockTransferSerializer,
    TransferGroupSerializer,
    WarehouseSerializer,
)
from apps.inventory.alerts import InventoryAlertService
from apps.inventory.models import InventoryAlert, InventoryLevel, InventoryTransaction
from apps.inventory.valuation import InventoryValuationService
from apps.inventory.services import InventoryService


class InventoryPagination(A2ZCursorPagination):
    ordering = "-updated_at"


class WarehouseListView(generics.ListAPIView):
    """GET /inventory/warehouses/"""

    serializer_class = WarehouseSerializer
    permission_classes = [CanViewInventory]
    pagination_class = InventoryPagination

    def get_queryset(self):
        return InventoryService.get_warehouses()


class InventoryListView(generics.ListAPIView):
    """GET /inventory/levels/ — stock positions by warehouse and SKU."""

    serializer_class = InventorySerializer
    permission_classes = [CanViewInventory]
    pagination_class = InventoryPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = InventoryFilter
    ordering_fields = (
        "variant__sku",
        "warehouse__code",
        "quantity_on_hand",
        "average_cost_cents",
        "updated_at",
    )
    ordering = ("warehouse__code", "variant__sku")

    def get_queryset(self):
        return InventoryService.get_inventory_queryset()


class StockMovementListView(generics.ListAPIView):
    """GET /inventory/movements/ — append-only stock ledger."""

    serializer_class = StockMovementSerializer
    permission_classes = [CanViewInventory]
    pagination_class = InventoryPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = StockMovementFilter
    ordering_fields = ("created_at", "movement_number", "variant__sku")
    ordering = ("-created_at",)

    def get_queryset(self):
        return InventoryService.get_movements_queryset()


class StockInView(generics.CreateAPIView):
    """POST /inventory/stock-in/"""

    serializer_class = StockInSerializer
    permission_classes = [CanManageInventory]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        payload = StockOperationResponseSerializer(
            {
                "movement": result.movement,
                "inventory": result.inventory,
                "paired_movement": result.paired_movement,
            }
        ).data
        return Response(payload, status=status.HTTP_201_CREATED)


class StockOutView(generics.CreateAPIView):
    """POST /inventory/stock-out/"""

    serializer_class = StockOutSerializer
    permission_classes = [CanManageInventory]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        payload = StockOperationResponseSerializer(
            {
                "movement": result.movement,
                "inventory": result.inventory,
                "paired_movement": result.paired_movement,
            }
        ).data
        return Response(payload, status=status.HTTP_201_CREATED)


class StockTransferView(generics.CreateAPIView):
    """POST /inventory/stock-transfer/"""

    serializer_class = StockTransferSerializer
    permission_classes = [CanManageInventory]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        payload = StockOperationResponseSerializer(
            {
                "movement": result.movement,
                "inventory": result.inventory,
                "paired_movement": result.paired_movement,
            }
        ).data
        return Response(payload, status=status.HTTP_201_CREATED)


class VariantInventoryView(APIView):
    """GET /inventory/variants/{variant_id}/ — legacy per-variant stock lookup."""

    permission_classes = [CanViewInventory]

    def get(self, request, variant_id):
        variant = ProductVariant.objects.get(public_id=variant_id)
        levels = InventoryService.get_stock(variant.id)
        return Response(
            {
                "variant_id": str(variant.public_id),
                "sku": variant.sku,
                "levels": InventoryLevelSerializer(levels, many=True).data,
            }
        )


class StockAdjustmentView(generics.CreateAPIView):
    """POST /inventory/adjustments/ — cycle count / correction."""

    serializer_class = StockAdjustmentSerializer
    permission_classes = [CanManageInventory]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        payload = StockOperationResponseSerializer(
            {
                "movement": result.movement,
                "inventory": result.inventory,
                "paired_movement": result.paired_movement,
            }
        ).data
        return Response(payload, status=status.HTTP_201_CREATED)


class LowStockAlertListView(generics.ListAPIView):
    """GET /inventory/alerts/low-stock/ — SKUs at or below reorder point."""

    serializer_class = LowStockAlertSerializer
    permission_classes = [CanViewInventory]
    pagination_class = InventoryPagination

    def get_queryset(self):
        return InventoryService.get_low_stock_queryset()


class InventoryLevelDetailView(generics.RetrieveUpdateAPIView):
    """GET/PATCH /inventory/levels/{id}/ — reorder level management."""

    serializer_class = InventorySerializer
    permission_classes = [CanViewInventory]
    lookup_field = "public_id"
    lookup_url_kwarg = "level_id"

    def get_queryset(self):
        return InventoryService.get_inventory_queryset()

    def get_permissions(self):
        if self.request.method in ("PATCH", "PUT"):
            return [CanManageInventory()]
        return [CanViewInventory()]

    def get_serializer_class(self):
        if self.request.method in ("PATCH", "PUT"):
            return ReorderLevelSerializer
        return InventorySerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = ReorderLevelSerializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        level = serializer.save()
        return Response(InventorySerializer(level).data)


class StockMovementDetailView(generics.RetrieveAPIView):
    """GET /inventory/movements/{id}/ — single ledger entry."""

    serializer_class = StockMovementSerializer
    permission_classes = [CanViewInventory]
    lookup_field = "public_id"
    lookup_url_kwarg = "movement_id"

    def get_queryset(self):
        return InventoryService.get_movements_queryset()


class TransferListView(generics.ListAPIView):
    """GET /inventory/transfers/ — warehouse transfer history."""

    serializer_class = TransferGroupSerializer
    permission_classes = [CanViewInventory]
    pagination_class = InventoryPagination

    def list(self, request, *args, **kwargs):
        warehouse_code = request.query_params.get("warehouse_code")
        sku = request.query_params.get("sku")
        out_movements = InventoryService.get_transfers_queryset(
            warehouse_code=warehouse_code,
            sku=sku,
        )

        page = self.paginate_queryset(out_movements)
        items = page if page is not None else out_movements
        results = []

        for out_mv in items:
            in_mv = (
                InventoryTransaction.objects.filter(
                    transfer_group_id=out_mv.transfer_group_id,
                    transaction_type=InventoryTransaction.TransactionType.TRANSFER_IN,
                )
                .select_related("warehouse")
                .first()
            )
            results.append(
                {
                    "transfer_group_id": out_mv.transfer_group_id,
                    "sku": out_mv.variant.sku,
                    "product_name": out_mv.variant.product.name,
                    "from_warehouse_code": out_mv.warehouse.code,
                    "to_warehouse_code": in_mv.warehouse.code if in_mv else None,
                    "quantity": abs(out_mv.quantity_change),
                    "notes": out_mv.notes,
                    "created_at": out_mv.created_at,
                    "created_by_email": out_mv.created_by.email if out_mv.created_by else None,
                }
            )

        serializer = TransferGroupSerializer(results, many=True)
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response({"data": serializer.data})


class LedgerSummaryView(APIView):
    """GET /inventory/ledger/summary/ — movement totals for a period (ex-GST AUD)."""

    permission_classes = [CanViewInventory]

    def get(self, request):
        from datetime import datetime

        date_from = request.query_params.get("date_from")
        date_to = request.query_params.get("date_to")
        warehouse_code = request.query_params.get("warehouse_code")

        parsed_from = datetime.strptime(date_from, "%Y-%m-%d").date() if date_from else None
        parsed_to = datetime.strptime(date_to, "%Y-%m-%d").date() if date_to else None

        summary = InventoryService.get_ledger_summary(
            date_from=parsed_from,
            date_to=parsed_to,
            warehouse_code=warehouse_code,
        )
        return Response(summary)


class ValuationSummaryView(APIView):
    """GET /inventory/valuation/ — weighted average inventory valuation (ex-GST)."""

    permission_classes = [CanViewInventory]

    def get(self, request):
        warehouse_code = request.query_params.get("warehouse_code")
        summary = InventoryValuationService.get_summary(warehouse_code=warehouse_code)
        top_skus = InventoryValuationService.get_top_skus_by_value(
            warehouse_code=warehouse_code,
            limit=int(request.query_params.get("limit", 20)),
        )
        return Response({**summary, "top_skus_by_value": top_skus})


class InventoryNotificationListView(generics.ListAPIView):
    """GET /inventory/notifications/ — active low-stock alerts."""

    serializer_class = InventoryAlertSerializer
    permission_classes = [CanViewInventory]
    pagination_class = InventoryPagination

    def get_queryset(self):
        status_filter = self.request.query_params.get("status", "active")
        qs = InventoryAlertService.get_active_queryset()
        if status_filter == "active":
            return qs.filter(status=InventoryAlert.Status.ACTIVE)
        if status_filter == "acknowledged":
            return qs.filter(status=InventoryAlert.Status.ACKNOWLEDGED)
        return qs


class InventoryNotificationAcknowledgeView(APIView):
    """POST /inventory/notifications/{id}/acknowledge/"""

    permission_classes = [CanManageInventory]

    def post(self, request, alert_id):
        alert = InventoryAlertService.get_active_queryset().get(public_id=alert_id)
        alert = InventoryAlertService.acknowledge(alert=alert, user=request.user)
        return Response(InventoryAlertSerializer(alert).data)


class InventoryNotificationCountView(APIView):
    """GET /inventory/notifications/unread-count/"""

    permission_classes = [CanViewInventory]

    def get(self, request):
        return Response({"count": InventoryAlertService.unread_count()})
