"""Purchase order business logic."""

from __future__ import annotations

import uuid
from uuid import UUID

from django.db import transaction
from django.db.models import QuerySet
from django.utils import timezone

from apps.core.exceptions import BusinessRuleError, ConflictError, NotFoundError
from apps.core.resolvers import resolve_supplier, resolve_variant, resolve_warehouse
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
    def approve(*, po: PurchaseOrder, user=None, comment: str = "") -> PurchaseOrder:
        if po.status != PurchaseOrder.Status.SUBMITTED:
            raise ConflictError("Only submitted purchase orders can be approved.")
        from apps.erp.constants import DomainEventType, WorkflowCode
        from apps.erp.services.events import DomainEventPublisher
        from apps.erp.services.workflow import WorkflowEngine

        instance = WorkflowEngine.get_for_resource(
            resource_type="purchase_order", resource_id=str(po.public_id)
        )
        if instance:
            WorkflowEngine.transition(
                instance=instance, action="approve", actor=user, comment=comment
            )
        DomainEventPublisher.publish(
            event_type=DomainEventType.PO_APPROVED,
            aggregate_type="purchase_order",
            aggregate_id=str(po.public_id),
            payload={"po_number": po.po_number},
            idempotency_key=f"po.approved:{po.public_id}",
        )
        return po

    @staticmethod
    @transaction.atomic
    def confirm(*, po: PurchaseOrder, user=None) -> PurchaseOrder:
        if po.status not in (
            PurchaseOrder.Status.SUBMITTED,
            PurchaseOrder.Status.DRAFT,
        ):
            raise ConflictError("Purchase order cannot be confirmed in its current status.")
        from apps.erp.constants import WorkflowCode
        from apps.erp.services.workflow import WorkflowEngine

        instance = WorkflowEngine.get_for_resource(
            resource_type="purchase_order", resource_id=str(po.public_id)
        )
        if instance and instance.current_state == "approved":
            WorkflowEngine.transition(instance=instance, action="confirm", actor=user)
        elif instance and instance.current_state == "submitted":
            try:
                WorkflowEngine.transition(instance=instance, action="approve", actor=user)
                WorkflowEngine.transition(instance=instance, action="confirm", actor=user)
            except Exception:
                pass
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
        from apps.procurement.services import GoodsReceiptService

        po, _grn = GoodsReceiptService.receive_po(po=po, receipts=receipts, user=user)
        return po

    @staticmethod
    @transaction.atomic
    def cancel(*, po: PurchaseOrder, user=None) -> PurchaseOrder:
        if po.status == PurchaseOrder.Status.RECEIVED:
            raise ConflictError("Received purchase orders cannot be cancelled.")
        from apps.erp.constants import WorkflowCode
        from apps.erp.services.workflow import WorkflowEngine

        instance = WorkflowEngine.get_for_resource(
            resource_type="purchase_order", resource_id=str(po.public_id)
        )
        if instance and instance.status == "active":
            try:
                WorkflowEngine.transition(instance=instance, action="cancel", actor=user)
            except Exception:
                pass
        po.status = PurchaseOrder.Status.CANCELLED
        po.save(update_fields=["status", "updated_at"])
        return po
