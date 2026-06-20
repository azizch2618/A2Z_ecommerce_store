"""Low-stock alert lifecycle — create, acknowledge, resolve."""

from __future__ import annotations

from django.db import transaction
from django.db.models import QuerySet
from django.utils import timezone

from apps.inventory.models import InventoryAlert, InventoryLevel


class InventoryAlertService:
    @staticmethod
    def get_active_queryset() -> QuerySet[InventoryAlert]:
        return (
            InventoryAlert.objects.filter(
                status__in=[
                    InventoryAlert.Status.ACTIVE,
                    InventoryAlert.Status.ACKNOWLEDGED,
                ]
            )
            .select_related(
                "inventory_level",
                "inventory_level__warehouse",
                "inventory_level__variant",
                "inventory_level__variant__product",
                "acknowledged_by",
            )
            .order_by("-created_at")
        )

    @staticmethod
    def _alert_type_for_level(level: InventoryLevel) -> str | None:
        if level.reorder_point <= 0:
            return None
        if level.quantity_on_hand <= 0:
            return InventoryAlert.AlertType.OUT_OF_STOCK
        if level.quantity_on_hand <= level.reorder_point:
            return InventoryAlert.AlertType.LOW_STOCK
        return None

    @staticmethod
    def _build_message(level: InventoryLevel, alert_type: str) -> str:
        sku = level.variant.sku
        wh = level.warehouse.code
        if alert_type == InventoryAlert.AlertType.OUT_OF_STOCK:
            return f"{sku} is out of stock at {wh}. Reorder point: {level.reorder_point}."
        shortfall = max(level.reorder_point - level.quantity_on_hand, 0)
        return (
            f"{sku} is below reorder level at {wh}. "
            f"On hand: {level.quantity_on_hand}, reorder: {level.reorder_point} "
            f"(shortfall: {shortfall})."
        )

    @classmethod
    @transaction.atomic
    def sync_alerts_for_level(cls, level: InventoryLevel) -> InventoryAlert | None:
        """Create, update, or resolve alerts after a stock movement."""
        alert_type = cls._alert_type_for_level(level)

        active = (
            InventoryAlert.objects.select_for_update()
            .filter(
                inventory_level=level,
                status__in=[
                    InventoryAlert.Status.ACTIVE,
                    InventoryAlert.Status.ACKNOWLEDGED,
                ],
            )
            .first()
        )

        if alert_type is None:
            if active:
                active.status = InventoryAlert.Status.RESOLVED
                active.resolved_at = timezone.now()
                active.save(update_fields=["status", "resolved_at", "updated_at"])
            return None

        shortfall = max(level.reorder_point - level.quantity_on_hand, 0)
        message = cls._build_message(level, alert_type)

        if active:
            active.alert_type = alert_type
            active.quantity_on_hand = level.quantity_on_hand
            active.reorder_point = level.reorder_point
            active.shortfall = shortfall
            active.message = message
            if active.status == InventoryAlert.Status.ACKNOWLEDGED and alert_type != active.alert_type:
                active.status = InventoryAlert.Status.ACTIVE
                active.acknowledged_at = None
                active.acknowledged_by = None
            active.save(
                update_fields=[
                    "alert_type",
                    "quantity_on_hand",
                    "reorder_point",
                    "shortfall",
                    "message",
                    "status",
                    "acknowledged_at",
                    "acknowledged_by",
                    "updated_at",
                ]
            )
            return active

        return InventoryAlert.objects.create(
            inventory_level=level,
            alert_type=alert_type,
            status=InventoryAlert.Status.ACTIVE,
            quantity_on_hand=level.quantity_on_hand,
            reorder_point=level.reorder_point,
            shortfall=shortfall,
            message=message,
        )

    @staticmethod
    @transaction.atomic
    def acknowledge(*, alert: InventoryAlert, user) -> InventoryAlert:
        if alert.status == InventoryAlert.Status.RESOLVED:
            return alert
        alert.status = InventoryAlert.Status.ACKNOWLEDGED
        alert.acknowledged_at = timezone.now()
        alert.acknowledged_by = user
        alert.save(
            update_fields=[
                "status",
                "acknowledged_at",
                "acknowledged_by",
                "updated_at",
            ]
        )
        return alert

    @staticmethod
    def unread_count() -> int:
        return InventoryAlert.objects.filter(status=InventoryAlert.Status.ACTIVE).count()
