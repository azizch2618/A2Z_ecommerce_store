"""Purchase order business logic."""

from __future__ import annotations

import uuid
from uuid import UUID

from django.db import transaction
from django.db.models import QuerySet
from django.utils import timezone

from apps.core.exceptions import BusinessRuleError, ConflictError, NotFoundError
from apps.core.resolvers import resolve_supplier, resolve_variant, resolve_warehouse
from apps.inventory.services import InventoryService
from apps.suppliers.models import PurchaseOrder, PurchaseOrderLine, Supplier


class SupplierService:
    @staticmethod
    def list_active():
        return Supplier.objects.filter(is_active=True).order_by("name")


def generate_po_number() -> str:
    from apps.erp.constants import DocumentType
    from apps.erp.services.document_sequence import DocumentSequenceService

    try:
        return DocumentSequenceService.next_number(DocumentType.PURCHASE_ORDER)
    except Exception:
        stamp = timezone.now().strftime("%Y%m%d")
        token = uuid.uuid4().hex[:6].upper()
        return f"PO-{stamp}-{token}"


class PurchaseOrderService:
    @staticmethod
    def get_queryset(*, status: str | None = None) -> QuerySet[PurchaseOrder]:
        qs = PurchaseOrder.objects.select_related(
            "supplier", "warehouse", "created_by"
        ).prefetch_related("lines__variant__product")
        if status:
            qs = qs.filter(status=status)
        return qs.order_by("-created_at")

    @staticmethod
    def get_by_public_id(public_id: UUID) -> PurchaseOrder:
        try:
            return PurchaseOrderService.get_queryset().get(public_id=public_id)
        except PurchaseOrder.DoesNotExist as exc:
            raise NotFoundError("Purchase order not found.") from exc

    @staticmethod
    @transaction.atomic
    def create(
        *,
        supplier_id: UUID,
        warehouse_code: str,
        lines: list[dict],
        expected_at=None,
        user=None,
    ) -> PurchaseOrder:
        if not lines:
            raise BusinessRuleError("At least one line item is required.")

        supplier = resolve_supplier(supplier_id)
        warehouse = resolve_warehouse(warehouse_code)

        po = PurchaseOrder.objects.create(
            po_number=generate_po_number(),
            supplier=supplier,
            warehouse=warehouse,
            status=PurchaseOrder.Status.DRAFT,
            expected_at=expected_at,
            created_by=user,
        )

        total = 0
        for line in lines:
            variant = resolve_variant(line["sku"])
            qty = line["quantity"]
            unit_cost = line["unit_cost_cents"]
            if qty <= 0:
                raise BusinessRuleError("Line quantity must be positive.")
            PurchaseOrderLine.objects.create(
                purchase_order=po,
                variant=variant,
                quantity_ordered=qty,
                unit_cost_cents=unit_cost,
            )
            total += qty * unit_cost

        po.total_ex_gst_cents = total
        po.save(update_fields=["total_ex_gst_cents", "updated_at"])

        from apps.erp.constants import DomainEventType, WorkflowCode
        from apps.erp.services.events import DomainEventPublisher
        from apps.erp.services.workflow import WorkflowEngine

        WorkflowEngine.start(
            definition_code=WorkflowCode.PO_APPROVAL,
            resource_type="purchase_order",
            resource_id=str(po.public_id),
            actor=user,
        )
        DomainEventPublisher.publish(
            event_type=DomainEventType.PO_CREATED,
            aggregate_type="purchase_order",
            aggregate_id=str(po.public_id),
            payload={"po_number": po.po_number},
            idempotency_key=f"po.created:{po.public_id}",
        )
        return po

    @staticmethod
    @transaction.atomic
    def submit(*, po: PurchaseOrder, user=None) -> PurchaseOrder:
        if po.status != PurchaseOrder.Status.DRAFT:
            raise ConflictError("Only draft purchase orders can be submitted.")
        po.status = PurchaseOrder.Status.SUBMITTED
        po.save(update_fields=["status", "updated_at"])

        from apps.erp.constants import DomainEventType, WorkflowCode
        from apps.erp.services.events import DomainEventPublisher
        from apps.erp.services.workflow import WorkflowEngine

        instance = WorkflowEngine.get_for_resource(
            resource_type="purchase_order",
            resource_id=str(po.public_id),
        )
        if instance:
            WorkflowEngine.transition(
                instance=instance,
                action="submit",
                actor=user,
            )
        DomainEventPublisher.publish(
            event_type=DomainEventType.PO_SUBMITTED,
            aggregate_type="purchase_order",
            aggregate_id=str(po.public_id),
            payload={"po_number": po.po_number},
            idempotency_key=f"po.submitted:{po.public_id}",
        )
        return po

    @staticmethod
    @transaction.atomic
    def confirm(*, po: PurchaseOrder) -> PurchaseOrder:
        if po.status not in (
            PurchaseOrder.Status.SUBMITTED,
            PurchaseOrder.Status.DRAFT,
        ):
            raise ConflictError("Purchase order cannot be confirmed in its current status.")
        po.status = PurchaseOrder.Status.CONFIRMED
        po.save(update_fields=["status", "updated_at"])
        return po

    @staticmethod
    @transaction.atomic
    def receive(
        *,
        po: PurchaseOrder,
        receipts: list[dict],
        user=None,
    ) -> PurchaseOrder:
        if po.status in (
            PurchaseOrder.Status.RECEIVED,
            PurchaseOrder.Status.CANCELLED,
        ):
            raise ConflictError("Purchase order cannot receive stock in its current status.")

        lines_by_id = {line.public_id: line for line in po.lines.all()}
        lines_by_sku = {line.variant.sku.lower(): line for line in po.lines.all()}

        for receipt in receipts:
            line = None
            if receipt.get("line_id"):
                line = lines_by_id.get(receipt["line_id"])
            elif receipt.get("sku"):
                line = lines_by_sku.get(receipt["sku"].lower())
            if not line:
                raise NotFoundError("Purchase order line not found.")

            qty = receipt["quantity"]
            if qty <= 0:
                raise BusinessRuleError("Receive quantity must be positive.")

            remaining = line.quantity_ordered - line.quantity_received
            if qty > remaining:
                raise ConflictError(
                    f"Cannot receive {qty} units for {line.variant.sku}; "
                    f"only {remaining} remaining."
                )

            InventoryService.stock_in(
                sku=line.variant.sku,
                warehouse_code=po.warehouse.code,
                quantity=qty,
                unit_cost_cents=line.unit_cost_cents,
                supplier_id=po.supplier.public_id,
                reference_type="purchase_order",
                reference_id=po.id,
                notes=f"PO receipt {po.po_number}",
                user=user,
            )

            line.quantity_received += qty
            line.save(update_fields=["quantity_received", "updated_at"])

        all_received = all(
            line.quantity_received >= line.quantity_ordered for line in po.lines.all()
        )
        any_received = any(line.quantity_received > 0 for line in po.lines.all())

        if all_received:
            po.status = PurchaseOrder.Status.RECEIVED
        elif any_received:
            po.status = PurchaseOrder.Status.PARTIAL_RECEIVED
        po.save(update_fields=["status", "updated_at"])

        from apps.erp.constants import DomainEventType
        from apps.erp.services.events import DomainEventPublisher

        DomainEventPublisher.publish(
            event_type=DomainEventType.PO_RECEIVED,
            aggregate_type="purchase_order",
            aggregate_id=str(po.public_id),
            payload={"po_number": po.po_number, "status": po.status},
            idempotency_key=f"po.received:{po.public_id}:{po.status}",
        )
        DomainEventPublisher.publish(
            event_type=DomainEventType.INVENTORY_RECEIVED,
            aggregate_type="purchase_order",
            aggregate_id=str(po.public_id),
            payload={"po_number": po.po_number, "warehouse_code": po.warehouse.code},
            idempotency_key=f"inventory.received:{po.public_id}",
        )
        return po
        if po.status == PurchaseOrder.Status.RECEIVED:
            raise ConflictError("Received purchase orders cannot be cancelled.")
        po.status = PurchaseOrder.Status.CANCELLED
        po.save(update_fields=["status", "updated_at"])
        return po
