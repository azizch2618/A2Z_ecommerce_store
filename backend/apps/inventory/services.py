"""Inventory domain services — stock in, out, transfer."""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from uuid import UUID

from django.db import transaction
from django.db.models import QuerySet

from apps.catalog.models import ProductVariant
from apps.core.exceptions import BusinessRuleError, ConflictError, NotFoundError
from apps.core.resolvers import resolve_supplier_optional, resolve_variant, resolve_warehouse
from apps.inventory.models import (
    InventoryLevel,
    InventoryTransaction,
    Warehouse,
    generate_movement_number,
)
from apps.suppliers.models import Supplier


@dataclass
class StockMovementResult:
    movement: InventoryTransaction
    inventory: InventoryLevel
    paired_movement: InventoryTransaction | None = None


class InventoryService:
    @staticmethod
    def get_warehouses(*, active_only: bool = True) -> QuerySet[Warehouse]:
        qs = Warehouse.objects.all()
        if active_only:
            qs = qs.filter(is_active=True)
        return qs.order_by("code")

    @staticmethod
    def get_inventory_queryset(
        *,
        warehouse_code: str | None = None,
        sku: str | None = None,
    ) -> QuerySet[InventoryLevel]:
        qs = InventoryLevel.objects.select_related(
            "warehouse", "variant", "variant__product"
        )
        if warehouse_code:
            qs = qs.filter(warehouse__code=warehouse_code)
        if sku:
            qs = qs.filter(variant__sku__iexact=sku)
        return qs.order_by("warehouse__code", "variant__sku")

    @staticmethod
    def get_movements_queryset(
        *,
        warehouse_code: str | None = None,
        sku: str | None = None,
        movement_type: str | None = None,
        transfer_group_id: UUID | None = None,
    ) -> QuerySet[InventoryTransaction]:
        qs = InventoryTransaction.objects.select_related(
            "warehouse", "variant", "supplier", "created_by"
        )
        if warehouse_code:
            qs = qs.filter(warehouse__code=warehouse_code)
        if sku:
            qs = qs.filter(variant__sku__iexact=sku)
        if movement_type:
            qs = qs.filter(transaction_type=movement_type)
        if transfer_group_id:
            qs = qs.filter(transfer_group_id=transfer_group_id)
        return qs

    @staticmethod
    def get_stock(variant_id: int, warehouse_code: str | None = None) -> list[InventoryLevel]:
        qs = InventoryLevel.objects.filter(variant_id=variant_id).select_related("warehouse")
        if warehouse_code:
            qs = qs.filter(warehouse__code=warehouse_code)
        return list(qs)

    DEFAULT_FULFILMENT_WAREHOUSE = "SYD1"

    @staticmethod
    def get_available_quantity(*, variant_id: int, warehouse_code: str | None = None) -> int:
        levels = InventoryService.get_stock(variant_id, warehouse_code)
        return sum(max(level.quantity_on_hand - level.quantity_reserved, 0) for level in levels)

    @staticmethod
    def validate_cart_availability(
        cart,
        *,
        warehouse_code: str = DEFAULT_FULFILMENT_WAREHOUSE,
    ) -> None:
        """Raise ConflictError if cart quantities exceed available stock."""
        for item in cart.items.select_related("variant"):
            available = InventoryService.get_available_quantity(
                variant_id=item.variant_id,
                warehouse_code=warehouse_code,
            )
            if available < item.quantity:
                raise ConflictError(
                    f"Insufficient stock for {item.variant.sku}. "
                    f"Requested {item.quantity}, available {available}."
                )

    @staticmethod
    def validate_order_availability(
        order,
        *,
        warehouse_code: str = DEFAULT_FULFILMENT_WAREHOUSE,
    ) -> None:
        """Raise ConflictError if order line quantities exceed available stock."""
        for item in order.items.select_related("variant"):
            available = InventoryService.get_available_quantity(
                variant_id=item.variant_id,
                warehouse_code=warehouse_code,
            )
            if available < item.quantity:
                raise ConflictError(
                    f"Insufficient stock for {item.sku}. "
                    f"Requested {item.quantity}, available {available}."
                )

    @staticmethod
    def _update_weighted_average_cost(
        level: InventoryLevel,
        *,
        quantity_in: int,
        unit_cost_cents: int,
    ) -> None:
        if quantity_in <= 0:
            return
        existing_qty = max(level.quantity_on_hand - quantity_in, 0)
        existing_value = existing_qty * level.average_cost_cents
        incoming_value = quantity_in * unit_cost_cents
        new_qty = level.quantity_on_hand
        if new_qty > 0:
            level.average_cost_cents = (existing_value + incoming_value) // new_qty
        else:
            level.average_cost_cents = unit_cost_cents
        level.last_cost_cents = unit_cost_cents

    @staticmethod
    @transaction.atomic
    def _apply_movement(
        *,
        warehouse: Warehouse,
        variant: ProductVariant,
        quantity_change: int,
        transaction_type: str,
        unit_cost_cents: int | None = None,
        sale_price_cents: int | None = None,
        supplier: Supplier | None = None,
        transfer_group_id: UUID | None = None,
        reference_type: str = "",
        reference_id: int | None = None,
        notes: str = "",
        user=None,
        movement_prefix: str = "SM",
    ) -> StockMovementResult:
        if quantity_change == 0:
            raise BusinessRuleError("Quantity must not be zero.")

        level, _ = InventoryLevel.objects.select_for_update().get_or_create(
            warehouse=warehouse,
            variant=variant,
            defaults={
                "quantity_on_hand": 0,
                "quantity_reserved": 0,
                "average_cost_cents": 0,
                "last_cost_cents": 0,
                "last_sale_price_cents": 0,
            },
        )

        new_qty = level.quantity_on_hand + quantity_change
        if new_qty < 0:
            raise ConflictError(
                f"Insufficient stock for SKU {variant.sku} at {warehouse.code}."
            )

        if quantity_change > 0 and unit_cost_cents is not None:
            InventoryService._update_weighted_average_cost(
                level,
                quantity_in=quantity_change,
                unit_cost_cents=unit_cost_cents,
            )

        if sale_price_cents is not None:
            level.last_sale_price_cents = sale_price_cents

        level.quantity_on_hand = new_qty
        level.save(
            update_fields=[
                "quantity_on_hand",
                "average_cost_cents",
                "last_cost_cents",
                "last_sale_price_cents",
                "updated_at",
            ]
        )

        movement = InventoryTransaction.objects.create(
            movement_number=generate_movement_number(movement_prefix),
            warehouse=warehouse,
            variant=variant,
            supplier=supplier,
            transaction_type=transaction_type,
            quantity_change=quantity_change,
            quantity_after=new_qty,
            unit_cost_cents=unit_cost_cents,
            sale_price_cents=sale_price_cents,
            transfer_group_id=transfer_group_id,
            reference_type=reference_type,
            reference_id=reference_id,
            notes=notes,
            created_by=user,
        )

        from apps.inventory.alerts import InventoryAlertService

        InventoryAlertService.sync_alerts_for_level(level)

        return StockMovementResult(movement=movement, inventory=level)

    @staticmethod
    @transaction.atomic
    def stock_in(
        *,
        sku: str,
        warehouse_code: str,
        quantity: int,
        unit_cost_cents: int,
        sale_price_cents: int | None = None,
        supplier_id: UUID | None = None,
        reference_type: str = "",
        reference_id: int | None = None,
        notes: str = "",
        user=None,
    ) -> StockMovementResult:
        if quantity <= 0:
            raise BusinessRuleError("Stock in quantity must be positive.")

        variant = resolve_variant(sku, select_product=True)
        warehouse = resolve_warehouse(warehouse_code)
        supplier = resolve_supplier_optional(supplier_id)

        return InventoryService._apply_movement(
            warehouse=warehouse,
            variant=variant,
            quantity_change=quantity,
            transaction_type=InventoryTransaction.TransactionType.RECEIPT,
            unit_cost_cents=unit_cost_cents,
            sale_price_cents=sale_price_cents,
            supplier=supplier,
            reference_type=reference_type,
            reference_id=reference_id,
            notes=notes,
            user=user,
            movement_prefix="IN",
        )

    @staticmethod
    @transaction.atomic
    def stock_out(
        *,
        sku: str,
        warehouse_code: str,
        quantity: int,
        sale_price_cents: int | None = None,
        unit_cost_cents: int | None = None,
        transaction_type: str = InventoryTransaction.TransactionType.ADJUSTMENT,
        reference_type: str = "",
        reference_id: int | None = None,
        notes: str = "",
        user=None,
    ) -> StockMovementResult:
        if quantity <= 0:
            raise BusinessRuleError("Stock out quantity must be positive.")

        variant = resolve_variant(sku, select_product=True)
        warehouse = resolve_warehouse(warehouse_code)
        level = (
            InventoryLevel.objects.filter(warehouse=warehouse, variant=variant)
            .select_for_update()
            .first()
        )
        cost = unit_cost_cents
        if cost is None and level:
            cost = level.average_cost_cents or level.last_cost_cents

        return InventoryService._apply_movement(
            warehouse=warehouse,
            variant=variant,
            quantity_change=-quantity,
            transaction_type=transaction_type,
            unit_cost_cents=cost,
            sale_price_cents=sale_price_cents,
            reference_type=reference_type,
            reference_id=reference_id,
            notes=notes,
            user=user,
            movement_prefix="OUT",
        )

    @staticmethod
    @transaction.atomic
    def stock_transfer(
        *,
        sku: str,
        from_warehouse_code: str,
        to_warehouse_code: str,
        quantity: int,
        sale_price_cents: int | None = None,
        notes: str = "",
        user=None,
    ) -> StockMovementResult:
        if quantity <= 0:
            raise BusinessRuleError("Transfer quantity must be positive.")
        if from_warehouse_code.lower() == to_warehouse_code.lower():
            raise BusinessRuleError("Source and destination warehouses must differ.")

        variant = resolve_variant(sku, select_product=True)
        from_warehouse = resolve_warehouse(from_warehouse_code)
        to_warehouse = resolve_warehouse(to_warehouse_code)

        source_level = (
            InventoryLevel.objects.filter(warehouse=from_warehouse, variant=variant)
            .select_for_update()
            .first()
        )
        unit_cost_cents = 0
        if source_level:
            unit_cost_cents = source_level.average_cost_cents or source_level.last_cost_cents

        transfer_group_id = uuid.uuid4()

        out_result = InventoryService._apply_movement(
            warehouse=from_warehouse,
            variant=variant,
            quantity_change=-quantity,
            transaction_type=InventoryTransaction.TransactionType.TRANSFER_OUT,
            unit_cost_cents=unit_cost_cents,
            sale_price_cents=sale_price_cents,
            transfer_group_id=transfer_group_id,
            notes=notes,
            user=user,
            movement_prefix="XFER-OUT",
        )

        in_result = InventoryService._apply_movement(
            warehouse=to_warehouse,
            variant=variant,
            quantity_change=quantity,
            transaction_type=InventoryTransaction.TransactionType.TRANSFER_IN,
            unit_cost_cents=unit_cost_cents,
            sale_price_cents=sale_price_cents,
            transfer_group_id=transfer_group_id,
            notes=notes,
            user=user,
            movement_prefix="XFER-IN",
        )

        out_result.paired_movement = in_result.movement
        return out_result

    @staticmethod
    @transaction.atomic
    def stock_adjustment(
        *,
        sku: str,
        warehouse_code: str,
        quantity_change: int,
        unit_cost_cents: int | None = None,
        notes: str = "",
        user=None,
    ) -> StockMovementResult:
        """Positive or negative stock correction (cycle count, shrinkage, etc.)."""
        if quantity_change == 0:
            raise BusinessRuleError("Adjustment quantity must not be zero.")

        variant = resolve_variant(sku, select_product=True)
        warehouse = resolve_warehouse(warehouse_code)

        if quantity_change > 0 and unit_cost_cents is None:
            raise BusinessRuleError("Cost is required for positive adjustments.")

        prefix = "ADJ-IN" if quantity_change > 0 else "ADJ-OUT"
        return InventoryService._apply_movement(
            warehouse=warehouse,
            variant=variant,
            quantity_change=quantity_change,
            transaction_type=InventoryTransaction.TransactionType.ADJUSTMENT,
            unit_cost_cents=unit_cost_cents,
            reference_type="adjustment",
            notes=notes,
            user=user,
            movement_prefix=prefix,
        )

    @staticmethod
    def get_low_stock_queryset() -> QuerySet[InventoryLevel]:
        from django.db.models import F, Q

        return (
            InventoryLevel.objects.select_related(
                "warehouse", "variant", "variant__product"
            )
            .filter(reorder_point__gt=0)
            .filter(
                Q(quantity_on_hand__lte=F("reorder_point"))
                | Q(quantity_on_hand=0)
            )
            .order_by("quantity_on_hand", "warehouse__code", "variant__sku")
        )

    @staticmethod
    def update_reorder_levels(
        *,
        level: InventoryLevel,
        reorder_point: int,
        reorder_quantity: int,
    ) -> InventoryLevel:
        if reorder_point < 0 or reorder_quantity < 0:
            raise BusinessRuleError("Reorder values must not be negative.")
        if reorder_point > 0 and reorder_quantity <= 0:
            raise BusinessRuleError(
                "Reorder quantity must be positive when a reorder point is set."
            )
        level.reorder_point = reorder_point
        level.reorder_quantity = reorder_quantity
        level.save(update_fields=["reorder_point", "reorder_quantity", "updated_at"])

        from apps.inventory.alerts import InventoryAlertService

        InventoryAlertService.sync_alerts_for_level(level)
        return level

    @staticmethod
    def get_transfers_queryset(
        *,
        warehouse_code: str | None = None,
        sku: str | None = None,
    ) -> QuerySet[InventoryTransaction]:
        qs = (
            InventoryTransaction.objects.filter(
                transaction_type=InventoryTransaction.TransactionType.TRANSFER_OUT,
                transfer_group_id__isnull=False,
            )
            .select_related("warehouse", "variant", "created_by")
            .order_by("-created_at")
        )
        if warehouse_code:
            qs = qs.filter(warehouse__code__iexact=warehouse_code)
        if sku:
            qs = qs.filter(variant__sku__iexact=sku)
        return qs

    @staticmethod
    def get_ledger_summary(
        *,
        date_from=None,
        date_to=None,
        warehouse_code: str | None = None,
    ) -> dict:
        from django.conf import settings
        from django.db.models import Count, Sum

        from apps.inventory.valuation import InventoryValuationService
        from apps.pricing.services import PricingService

        qs = InventoryTransaction.objects.all()
        if warehouse_code:
            qs = qs.filter(warehouse__code__iexact=warehouse_code)
        if date_from:
            qs = qs.filter(created_at__date__gte=date_from)
        if date_to:
            qs = qs.filter(created_at__date__lte=date_to)

        def sum_value(transaction_types: list[str], sign: int = 1) -> dict:
            filtered = qs.filter(transaction_type__in=transaction_types)
            agg = filtered.aggregate(
                count=Count("id"),
                quantity=Sum("quantity_change"),
            )
            total_ex = 0
            for mv in filtered.only("quantity_change", "unit_cost_cents"):
                if mv.unit_cost_cents:
                    total_ex += abs(mv.quantity_change) * mv.unit_cost_cents
            total_ex *= sign
            return {
                "count": agg["count"] or 0,
                "quantity": abs(int(agg["quantity"] or 0)),
                **InventoryValuationService.valuation_block(abs(total_ex)),
            }

        receipts = sum_value(
            [InventoryTransaction.TransactionType.RECEIPT],
        )
        issues = sum_value(
            [
                InventoryTransaction.TransactionType.SALE,
                InventoryTransaction.TransactionType.ADJUSTMENT,
                InventoryTransaction.TransactionType.TRANSFER_OUT,
            ],
        )
        transfers = qs.filter(
            transaction_type=InventoryTransaction.TransactionType.TRANSFER_OUT
        ).aggregate(count=Count("id"))

        by_type = []
        for choice in InventoryTransaction.TransactionType:
            type_qs = qs.filter(transaction_type=choice.value)
            type_ex = 0
            for mv in type_qs.only("quantity_change", "unit_cost_cents"):
                if mv.unit_cost_cents:
                    type_ex += abs(mv.quantity_change) * mv.unit_cost_cents
            by_type.append(
                {
                    "transaction_type": choice.value,
                    "label": choice.label,
                    "count": type_qs.count(),
                    **InventoryValuationService.valuation_block(type_ex),
                }
            )

        return {
            "period": {
                "from": date_from.isoformat() if date_from else None,
                "to": date_to.isoformat() if date_to else None,
            },
            "warehouse_code": warehouse_code,
            "currency_code": settings.A2Z_CURRENCY_CODE,
            "gst_rate": float(PricingService.GST_RATE),
            "total_movements": qs.count(),
            "receipts": receipts,
            "issues": issues,
            "transfers": {"count": transfers["count"] or 0},
            "by_type": by_type,
            "tax_note": "Movement values are recorded ex-GST (AUD) for Australian BAS reporting.",
        }

    @staticmethod
    @transaction.atomic
    def adjust_stock(
        *,
        warehouse: Warehouse,
        variant_id: int,
        quantity_change: int,
        transaction_type: str,
        unit_cost_cents: int | None = None,
        sale_price_cents: int | None = None,
        reference_type: str = "",
        reference_id: int | None = None,
        user=None,
    ) -> InventoryTransaction:
        variant = ProductVariant.objects.get(pk=variant_id)
        prefix = "IN" if quantity_change > 0 else "OUT"
        result = InventoryService._apply_movement(
            warehouse=warehouse,
            variant=variant,
            quantity_change=quantity_change,
            transaction_type=transaction_type,
            unit_cost_cents=unit_cost_cents,
            sale_price_cents=sale_price_cents,
            reference_type=reference_type,
            reference_id=reference_id,
            user=user,
            movement_prefix=prefix,
        )
        return result.movement
