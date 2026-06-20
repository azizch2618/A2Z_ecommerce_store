"""Procurement business logic — requisitions, goods receipt, supplier portal, KPIs."""
from __future__ import annotations

from datetime import timedelta
from typing import Any
from uuid import UUID

from django.db import transaction
from django.db.models import Avg, Count, F, Q, QuerySet, Sum
from django.utils import timezone

from apps.core.exceptions import BusinessRuleError, ConflictError, NotFoundError
from apps.core.resolvers import resolve_supplier, resolve_variant, resolve_warehouse
from apps.erp.constants import AuditModule, DocumentType, DomainEventType, WorkflowCode
from apps.erp.models import CostCenter, Department
from apps.erp.services.audit import AuditService
from apps.erp.services.document_sequence import DocumentSequenceService
from apps.erp.services.events import DomainEventPublisher
from apps.erp.services.party import PartyService
from apps.erp.services.workflow import WorkflowEngine
from apps.inventory.services import InventoryService
from apps.procurement.constants import PaymentStatus
from apps.procurement.models import (
    GoodsReceipt,
    GoodsReceiptLine,
    PurchaseRequest,
    PurchaseRequestLine,
    SupplierDocument,
    SupplierMembership,
)
from apps.suppliers.models import PurchaseOrder, PurchaseOrderLine, Supplier
from apps.suppliers.services import PurchaseOrderService, generate_po_number


class PurchaseRequestService:
    @staticmethod
    def list_requests(*, status: str | None = None, search: str | None = None) -> QuerySet[PurchaseRequest]:
        qs = PurchaseRequest.objects.select_related(
            "requested_by", "department", "cost_center", "warehouse", "supplier", "converted_po"
        ).prefetch_related("lines")
        if status:
            qs = qs.filter(status=status)
        if search:
            qs = qs.filter(
                Q(request_number__icontains=search)
                | Q(justification__icontains=search)
            )
        return qs.order_by("-created_at")

    @staticmethod
    def get_request(public_id: UUID) -> PurchaseRequest:
        pr = PurchaseRequestService.list_requests().filter(public_id=public_id).first()
        if not pr:
            raise NotFoundError("Purchase request not found.")
        return pr

    @classmethod
    @transaction.atomic
    def create(cls, *, actor, data: dict[str, Any]) -> PurchaseRequest:
        warehouse = resolve_warehouse(data["warehouse_code"])
        supplier = None
        if data.get("supplier_id"):
            supplier = resolve_supplier(data["supplier_id"])

        department = None
        if data.get("department_id"):
            department = Department.objects.filter(public_id=data["department_id"]).first()
        cost_center = None
        if data.get("cost_center_id"):
            cost_center = CostCenter.objects.filter(public_id=data["cost_center_id"]).first()

        request_number = DocumentSequenceService.next_number(DocumentType.PURCHASE_REQUEST)

        pr = PurchaseRequest.objects.create(
            request_number=request_number,
            requested_by=actor if getattr(actor, "is_authenticated", False) else None,
            department=department,
            cost_center=cost_center,
            warehouse=warehouse,
            supplier=supplier,
            priority=data.get("priority", "medium"),
            justification=data.get("justification", ""),
            status=PurchaseRequest.Status.DRAFT,
        )
        cls._audit(actor, pr, "create", "Purchase request created")
        DomainEventPublisher.publish(
            event_type=DomainEventType.PURCHASE_REQUEST_CREATED,
            aggregate_type="purchase_request",
            aggregate_id=str(pr.public_id),
            payload={"request_number": pr.request_number},
            idempotency_key=f"purchase_request.created:{pr.public_id}",
        )
        return pr

    @classmethod
    @transaction.atomic
    def add_line(cls, *, pr: PurchaseRequest, actor, data: dict[str, Any]) -> PurchaseRequestLine:
        if pr.status not in (PurchaseRequest.Status.DRAFT, PurchaseRequest.Status.REJECTED):
            raise BusinessRuleError("Cannot add lines to this request.")
        variant = resolve_variant(data["sku"])
        line = PurchaseRequestLine.objects.create(
            purchase_request=pr,
            variant=variant,
            sku=variant.sku,
            product_name=variant.product.name,
            quantity=int(data["quantity"]),
            unit_cost_cents=int(data.get("unit_cost_cents", 0)),
            notes=data.get("notes", ""),
        )
        cls._audit(actor, pr, "add_line", f"Line added: {line.sku}")
        return line

    @classmethod
    @transaction.atomic
    def submit(cls, *, pr: PurchaseRequest, actor) -> PurchaseRequest:
        if pr.status != PurchaseRequest.Status.DRAFT:
            raise BusinessRuleError("Only draft requests can be submitted.")
        if not pr.lines.exists():
            raise BusinessRuleError("Purchase request must have at least one line.")
        pr.status = PurchaseRequest.Status.SUBMITTED
        pr.save(update_fields=["status", "updated_at"])
        WorkflowEngine.start(
            definition_code=WorkflowCode.PR_APPROVAL,
            resource_type="purchase_request",
            resource_id=str(pr.public_id),
            actor=actor,
        )
        cls._audit(actor, pr, "submit", "Submitted for approval")
        return pr

    @classmethod
    @transaction.atomic
    def approve(cls, *, pr: PurchaseRequest, actor, comment: str = "") -> PurchaseRequest:
        if pr.status != PurchaseRequest.Status.SUBMITTED:
            raise BusinessRuleError("Request is not pending approval.")
        instance = WorkflowEngine.get_for_resource(
            resource_type="purchase_request", resource_id=str(pr.public_id)
        )
        if instance:
            WorkflowEngine.transition(instance=instance, action="approve", actor=actor, comment=comment)
        pr.status = PurchaseRequest.Status.APPROVED
        pr.save(update_fields=["status", "updated_at"])
        cls._audit(actor, pr, "approve", comment or "Approved")
        DomainEventPublisher.publish(
            event_type=DomainEventType.PURCHASE_REQUEST_APPROVED,
            aggregate_type="purchase_request",
            aggregate_id=str(pr.public_id),
            payload={"request_number": pr.request_number},
            idempotency_key=f"purchase_request.approved:{pr.public_id}",
        )
        return pr

    @classmethod
    @transaction.atomic
    def reject(cls, *, pr: PurchaseRequest, actor, comment: str = "") -> PurchaseRequest:
        if pr.status != PurchaseRequest.Status.SUBMITTED:
            raise BusinessRuleError("Request is not pending approval.")
        instance = WorkflowEngine.get_for_resource(
            resource_type="purchase_request", resource_id=str(pr.public_id)
        )
        if instance:
            WorkflowEngine.transition(instance=instance, action="reject", actor=actor, comment=comment)
        pr.status = PurchaseRequest.Status.REJECTED
        pr.save(update_fields=["status", "updated_at"])
        cls._audit(actor, pr, "reject", comment or "Rejected")
        return pr

    @classmethod
    @transaction.atomic
    def convert_to_po(cls, *, pr: PurchaseRequest, actor) -> PurchaseOrder:
        if pr.status != PurchaseRequest.Status.APPROVED:
            raise BusinessRuleError("Only approved requests can be converted.")
        if pr.converted_po_id:
            return pr.converted_po
        if not pr.supplier:
            raise BusinessRuleError("Supplier must be set before conversion.")
        if not pr.lines.exists():
            raise BusinessRuleError("Request must have line items.")

        po = PurchaseOrder.objects.create(
            po_number=generate_po_number(),
            supplier=pr.supplier,
            warehouse=pr.warehouse,
            status=PurchaseOrder.Status.DRAFT,
            created_by=actor if getattr(actor, "is_authenticated", False) else None,
        )
        total = 0
        for line in pr.lines.select_related("variant"):
            PurchaseOrderLine.objects.create(
                purchase_order=po,
                variant=line.variant,
                quantity_ordered=line.quantity,
                unit_cost_cents=line.unit_cost_cents,
            )
            total += line.quantity * line.unit_cost_cents
        po.total_ex_gst_cents = total
        po.save(update_fields=["total_ex_gst_cents", "updated_at"])

        pr.status = PurchaseRequest.Status.CONVERTED
        pr.converted_po = po
        pr.save(update_fields=["status", "converted_po", "updated_at"])

        from apps.erp.constants import DomainEventType as DET

        WorkflowEngine.start(
            definition_code=WorkflowCode.PO_APPROVAL,
            resource_type="purchase_order",
            resource_id=str(po.public_id),
            actor=actor,
        )
        DomainEventPublisher.publish(
            event_type=DET.PO_CREATED,
            aggregate_type="purchase_order",
            aggregate_id=str(po.public_id),
            payload={"po_number": po.po_number, "from_request": pr.request_number},
            idempotency_key=f"po.created:pr:{pr.public_id}",
        )
        cls._audit(actor, pr, "convert", f"Converted to PO {po.po_number}")
        return po

    @staticmethod
    def _audit(user, pr: PurchaseRequest, action: str, summary: str) -> None:
        AuditService.log(
            user=user,
            module=AuditModule.PROCUREMENT,
            action=action,
            resource_type="purchase_request",
            resource_id=str(pr.public_id),
            summary=summary,
            metadata={"request_number": pr.request_number, "status": pr.status},
            mirror_operational=False,
        )


class GoodsReceiptService:
    @staticmethod
    def _next_grn() -> str:
        try:
            return DocumentSequenceService.next_number(DocumentType.GOODS_RECEIPT)
        except Exception:
            return f"GRN-{timezone.now():%Y%m%d}-{GoodsReceipt.objects.count() + 1:04d}"

    @classmethod
    @transaction.atomic
    def receive_po(
        cls,
        *,
        po: PurchaseOrder,
        receipts: list[dict],
        user=None,
    ) -> tuple[PurchaseOrder, GoodsReceipt]:
        if po.status in (PurchaseOrder.Status.CANCELLED,):
            raise ConflictError("Cannot receive cancelled purchase order.")

        received_at = timezone.now()
        grn = GoodsReceipt.objects.create(
            grn_number=cls._next_grn(),
            purchase_order=po,
            warehouse=po.warehouse,
            status=GoodsReceipt.Status.PARTIAL,
            received_by=user if getattr(user, "is_authenticated", False) else None,
            received_at=received_at,
        )

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

            qty = int(receipt["quantity"])
            if qty <= 0:
                raise BusinessRuleError("Receive quantity must be positive.")

            remaining = line.quantity_ordered - line.quantity_received
            if qty > remaining:
                raise ConflictError(
                    f"Cannot receive {qty} for {line.variant.sku}; only {remaining} remaining."
                )

            batch = receipt.get("batch_number", "")
            line_received_at = receipt.get("received_at") or received_at

            InventoryService.stock_in(
                sku=line.variant.sku,
                warehouse_code=po.warehouse.code,
                quantity=qty,
                unit_cost_cents=line.unit_cost_cents,
                supplier_id=po.supplier.public_id,
                reference_type="goods_receipt",
                reference_id=grn.id,
                notes=f"GRN {grn.grn_number} / PO {po.po_number}",
                user=user,
            )

            GoodsReceiptLine.objects.create(
                goods_receipt=grn,
                purchase_order_line=line,
                quantity_received=qty,
                batch_number=batch,
                received_at=line_received_at,
            )

            line.quantity_received += qty
            line.save(update_fields=["quantity_received", "updated_at"])

        all_received = all(
            line.quantity_received >= line.quantity_ordered for line in po.lines.all()
        )
        any_received = any(line.quantity_received > 0 for line in po.lines.all())

        if all_received:
            po.status = PurchaseOrder.Status.RECEIVED
            grn.status = GoodsReceipt.Status.FULL
        elif any_received:
            po.status = PurchaseOrder.Status.PARTIAL_RECEIVED
            grn.status = GoodsReceipt.Status.PARTIAL
        po.save(update_fields=["status", "updated_at"])
        grn.save(update_fields=["status", "updated_at"])

        cls._check_delivery_delay(po)

        DomainEventPublisher.publish(
            event_type=DomainEventType.GOODS_RECEIVED,
            aggregate_type="goods_receipt",
            aggregate_id=str(grn.public_id),
            payload={
                "grn_number": grn.grn_number,
                "po_number": po.po_number,
                "status": grn.status,
            },
            idempotency_key=f"goods.received:{grn.public_id}",
        )
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
            idempotency_key=f"inventory.received:{grn.public_id}",
        )
        AuditService.log(
            user=user,
            module=AuditModule.PROCUREMENT,
            action="goods_receipt",
            resource_type="goods_receipt",
            resource_id=str(grn.public_id),
            summary=f"Goods receipt {grn.grn_number} for PO {po.po_number}",
            metadata={"status": grn.status},
            mirror_operational=False,
        )
        from apps.wms.services import PutawayService

        PutawayService.create_from_grn(grn=grn, actor=user)
        return po, grn

    @staticmethod
    def _check_delivery_delay(po: PurchaseOrder) -> None:
        if not po.expected_at or po.status != PurchaseOrder.Status.RECEIVED:
            return
        if timezone.now() > po.expected_at:
            DomainEventPublisher.publish(
                event_type=DomainEventType.SUPPLIER_DELIVERY_DELAYED,
                aggregate_type="purchase_order",
                aggregate_id=str(po.public_id),
                payload={
                    "po_number": po.po_number,
                    "expected_at": po.expected_at.isoformat(),
                },
                idempotency_key=f"supplier.delivery_delayed:{po.public_id}",
            )


class SupplierPortalService:
    @staticmethod
    def get_supplier_for_user(user) -> Supplier | None:
        membership = (
            SupplierMembership.objects.filter(user=user)
            .select_related("supplier")
            .order_by("-is_primary", "-created_at")
            .first()
        )
        return membership.supplier if membership else None

    @staticmethod
    def list_pos_for_supplier(supplier: Supplier, *, status: str | None = None) -> QuerySet[PurchaseOrder]:
        qs = PurchaseOrder.objects.filter(supplier=supplier).exclude(
            status=PurchaseOrder.Status.DRAFT
        ).select_related("warehouse", "created_by").prefetch_related("lines__variant__product")
        if status:
            qs = qs.filter(status=status)
        return qs.order_by("-created_at")

    @classmethod
    @transaction.atomic
    def acknowledge_po(cls, *, po: PurchaseOrder, supplier: Supplier, user) -> PurchaseOrder:
        if po.supplier_id != supplier.id:
            raise BusinessRuleError("Purchase order does not belong to this supplier.")
        if po.status not in (
            PurchaseOrder.Status.SUBMITTED,
            PurchaseOrder.Status.CONFIRMED,
        ):
            raise BusinessRuleError("Purchase order cannot be acknowledged.")
        po.supplier_acknowledged_at = timezone.now()
        po.save(update_fields=["supplier_acknowledged_at", "updated_at"])
        AuditService.log(
            user=user,
            module=AuditModule.PROCUREMENT,
            action="po_acknowledge",
            resource_type="purchase_order",
            resource_id=str(po.public_id),
            summary=f"PO {po.po_number} acknowledged by supplier",
            metadata={},
            mirror_operational=False,
        )
        return po

    @classmethod
    @transaction.atomic
    def update_expected_delivery(
        cls, *, po: PurchaseOrder, supplier: Supplier, user, expected_at
    ) -> PurchaseOrder:
        if po.supplier_id != supplier.id:
            raise BusinessRuleError("Purchase order does not belong to this supplier.")
        po.expected_at = expected_at
        po.save(update_fields=["expected_at", "updated_at"])
        AuditService.log(
            user=user,
            module=AuditModule.PROCUREMENT,
            action="update_expected_delivery",
            resource_type="purchase_order",
            resource_id=str(po.public_id),
            summary=f"Expected delivery updated for PO {po.po_number}",
            metadata={"expected_at": expected_at.isoformat() if expected_at else None},
            mirror_operational=False,
        )
        return po

    @classmethod
    @transaction.atomic
    def upload_document(
        cls,
        *,
        supplier: Supplier,
        user,
        file,
        document_type: str,
        purchase_order: PurchaseOrder | None = None,
        notes: str = "",
    ) -> SupplierDocument:
        doc = SupplierDocument.objects.create(
            supplier=supplier,
            purchase_order=purchase_order,
            document_type=document_type,
            file=file,
            original_filename=getattr(file, "name", ""),
            uploaded_by=user if getattr(user, "is_authenticated", False) else None,
            notes=notes,
        )
        AuditService.log(
            user=user,
            module=AuditModule.PROCUREMENT,
            action="document_upload",
            resource_type="supplier_document",
            resource_id=str(doc.public_id),
            summary=f"Document uploaded for supplier {supplier.code}",
            metadata={"document_type": document_type},
            mirror_operational=False,
        )
        return doc

    @staticmethod
    def payment_status_for_po(po: PurchaseOrder) -> dict[str, Any]:
        return {
            "poNumber": po.po_number,
            "paymentStatus": po.payment_status,
            "totalExGstCents": po.total_ex_gst_cents,
            "termsDays": po.supplier.payment_terms_days,
        }


class ProcurementDashboardService:
    @staticmethod
    def get_dashboard_kpis() -> dict[str, Any]:
        open_reqs = PurchaseRequest.objects.filter(
            status__in=[
                PurchaseRequest.Status.DRAFT,
                PurchaseRequest.Status.SUBMITTED,
                PurchaseRequest.Status.APPROVED,
            ]
        ).count()
        open_pos = PurchaseOrder.objects.filter(
            status__in=[
                PurchaseOrder.Status.SUBMITTED,
                PurchaseOrder.Status.CONFIRMED,
                PurchaseOrder.Status.PARTIAL_RECEIVED,
            ]
        ).count()
        spend = PurchaseOrder.objects.filter(
            status__in=[
                PurchaseOrder.Status.CONFIRMED,
                PurchaseOrder.Status.PARTIAL_RECEIVED,
                PurchaseOrder.Status.RECEIVED,
            ]
        ).aggregate(total=Sum("total_ex_gst_cents"))["total"] or 0
        performance = SupplierPerformanceService.get_aggregate_kpis()
        return {
            "open_requisitions": open_reqs,
            "open_purchase_orders": open_pos,
            "procurement_spend_cents": spend,
            "supplier_performance": performance,
        }


class SupplierPerformanceService:
    @staticmethod
    def get_supplier_kpis(supplier: Supplier) -> dict[str, Any]:
        pos = PurchaseOrder.objects.filter(
            supplier=supplier,
            status__in=[
                PurchaseOrder.Status.CONFIRMED,
                PurchaseOrder.Status.PARTIAL_RECEIVED,
                PurchaseOrder.Status.RECEIVED,
            ],
        )
        total = pos.count()
        received = pos.filter(status=PurchaseOrder.Status.RECEIVED)
        on_time = received.filter(
            goods_receipts__received_at__lte=F("expected_at")
        ).distinct().count() if total else 0
        spend = pos.aggregate(s=Sum("total_ex_gst_cents"))["s"] or 0

        lead_times = []
        for po in received.prefetch_related("goods_receipts")[:50]:
            first = po.goods_receipts.order_by("received_at").first()
            if first and po.supplier_acknowledged_at:
                lead_times.append(
                    (first.received_at - po.supplier_acknowledged_at).days
                )
            elif first:
                lead_times.append((first.received_at - po.created_at).days)

        accuracy = 0.0
        if total:
            accurate = sum(
                1
                for po in received.prefetch_related("lines")
                if all(line.quantity_received >= line.quantity_ordered for line in po.lines.all())
            )
            accuracy = round((accurate / max(received.count(), 1)) * 100, 1)

        return {
            "supplier_id": str(supplier.public_id),
            "supplier_name": supplier.name,
            "on_time_delivery_pct": round((on_time / max(received.count(), 1)) * 100, 1),
            "avg_lead_time_days": round(sum(lead_times) / len(lead_times), 1) if lead_times else 0,
            "order_accuracy_pct": accuracy,
            "purchase_spend_cents": spend,
            "total_orders": total,
        }

    @staticmethod
    def get_aggregate_kpis() -> dict[str, Any]:
        suppliers = Supplier.objects.filter(is_active=True)[:20]
        if not suppliers:
            return {
                "on_time_delivery_pct": 0,
                "avg_lead_time_days": 0,
                "order_accuracy_pct": 0,
                "purchase_spend_cents": 0,
            }
        metrics = [SupplierPerformanceService.get_supplier_kpis(s) for s in suppliers]
        count = len(metrics)
        return {
            "on_time_delivery_pct": round(
                sum(m["on_time_delivery_pct"] for m in metrics) / count, 1
            ),
            "avg_lead_time_days": round(
                sum(m["avg_lead_time_days"] for m in metrics) / count, 1
            ),
            "order_accuracy_pct": round(
                sum(m["order_accuracy_pct"] for m in metrics) / count, 1
            ),
            "purchase_spend_cents": sum(m["purchase_spend_cents"] for m in metrics),
        }
