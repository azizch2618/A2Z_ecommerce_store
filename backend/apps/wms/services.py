"""WMS business logic — bins, transfers, picks, putaway, cycle counts, adjustments."""
from __future__ import annotations

from typing import Any
from uuid import UUID

from django.db import transaction
from django.db.models import Count, F, Q, QuerySet, Sum
from django.utils import timezone

from apps.core.exceptions import BusinessRuleError, ConflictError, NotFoundError
from apps.core.resolvers import resolve_variant, resolve_warehouse
from apps.erp.constants import AuditModule, DocumentType, DomainEventType, WorkflowCode
from apps.erp.services.audit import AuditService
from apps.erp.services.document_sequence import DocumentSequenceService
from apps.erp.services.events import DomainEventPublisher
from apps.erp.services.workflow import WorkflowEngine
from apps.inventory.models import InventoryLevel, InventoryTransaction
from apps.inventory.services import InventoryService
from apps.orders.models import Order
from apps.wms.constants import (
    AdjustmentStatus,
    CycleCountStatus,
    PickListStatus,
    PutawayStatus,
    TransferStatus,
    TransferType,
)
from apps.wms.models import (
    BinInventory,
    CycleCount,
    CycleCountLine,
    InventoryAdjustmentLine,
    InventoryAdjustmentRequest,
    PickList,
    PickListLine,
    PutawayTask,
    PutawayTaskLine,
    StockTransfer,
    StockTransferLine,
    WarehouseAisle,
    WarehouseBin,
    WarehouseZone,
)


def _next_doc(code: str, fallback_prefix: str) -> str:
    try:
        return DocumentSequenceService.next_number(code)
    except Exception:
        return f"{fallback_prefix}-{timezone.now():%Y%m%d}-0001"


class BinLocationService:
    @staticmethod
    def list_zones(*, warehouse_code: str | None = None) -> QuerySet[WarehouseZone]:
        qs = WarehouseZone.objects.select_related("warehouse").filter(is_active=True)
        if warehouse_code:
            qs = qs.filter(warehouse__code=warehouse_code)
        return qs.order_by("warehouse__code", "code")

    @staticmethod
    def get_zone(public_id: UUID) -> WarehouseZone:
        zone = WarehouseZone.objects.filter(public_id=public_id).select_related("warehouse").first()
        if not zone:
            raise NotFoundError("Zone not found.")
        return zone

    @classmethod
    @transaction.atomic
    def create_zone(cls, *, warehouse_code: str, code: str, name: str) -> WarehouseZone:
        warehouse = resolve_warehouse(warehouse_code)
        zone, _ = WarehouseZone.objects.get_or_create(
            warehouse=warehouse,
            code=code.upper(),
            defaults={"name": name},
        )
        return zone

    @staticmethod
    def list_bins(*, warehouse_code: str | None = None, search: str | None = None) -> QuerySet[WarehouseBin]:
        qs = WarehouseBin.objects.select_related(
            "aisle__zone__warehouse", "aisle__zone"
        ).filter(is_active=True)
        if warehouse_code:
            qs = qs.filter(aisle__zone__warehouse__code=warehouse_code)
        if search:
            qs = qs.filter(
                Q(code__icontains=search)
                | Q(aisle__code__icontains=search)
                | Q(aisle__zone__code__icontains=search)
            )
        return qs.order_by("aisle__zone__code", "aisle__code", "code")

    @staticmethod
    def get_bin(public_id: UUID) -> WarehouseBin:
        bin_obj = (
            WarehouseBin.objects.filter(public_id=public_id)
            .select_related("aisle__zone__warehouse")
            .first()
        )
        if not bin_obj:
            raise NotFoundError("Bin not found.")
        return bin_obj

    @classmethod
    @transaction.atomic
    def create_bin_hierarchy(
        cls,
        *,
        warehouse_code: str,
        zone_code: str,
        zone_name: str,
        aisle_code: str,
        aisle_name: str,
        bin_code: str,
        bin_name: str = "",
        bin_type: str = "pick",
    ) -> WarehouseBin:
        zone = cls.create_zone(warehouse_code=warehouse_code, code=zone_code, name=zone_name)
        aisle, _ = WarehouseAisle.objects.get_or_create(
            zone=zone,
            code=aisle_code.upper(),
            defaults={"name": aisle_name},
        )
        bin_obj, _ = WarehouseBin.objects.get_or_create(
            aisle=aisle,
            code=bin_code.upper(),
            defaults={"name": bin_name or bin_code, "bin_type": bin_type},
        )
        return bin_obj


class BinInventoryService:
    @staticmethod
    def get_bin_qty(*, bin: WarehouseBin, variant_id: int) -> int:
        row = BinInventory.objects.filter(bin=bin, variant_id=variant_id).first()
        return row.quantity_on_hand if row else 0

    @staticmethod
    def get_unlocated_qty(*, warehouse_code: str, variant_id: int) -> int:
        warehouse = resolve_warehouse(warehouse_code)
        level = InventoryLevel.objects.filter(warehouse=warehouse, variant_id=variant_id).first()
        if not level:
            return 0
        located = (
            BinInventory.objects.filter(
                bin__aisle__zone__warehouse=warehouse,
                variant_id=variant_id,
            ).aggregate(total=Sum("quantity_on_hand"))["total"]
            or 0
        )
        return max(level.quantity_on_hand - located, 0)

    @classmethod
    @transaction.atomic
    def move_bin_qty(
        cls,
        *,
        from_bin: WarehouseBin | None,
        to_bin: WarehouseBin | None,
        variant_id: int,
        quantity: int,
    ) -> None:
        if quantity <= 0:
            raise BusinessRuleError("Quantity must be positive.")
        if from_bin:
            cls._adjust_bin(bin=from_bin, variant_id=variant_id, delta=-quantity)
        if to_bin:
            cls._adjust_bin(bin=to_bin, variant_id=variant_id, delta=quantity)

    @staticmethod
    @transaction.atomic
    def _adjust_bin(*, bin: WarehouseBin, variant_id: int, delta: int) -> BinInventory:
        row, _ = BinInventory.objects.select_for_update().get_or_create(
            bin=bin,
            variant_id=variant_id,
            defaults={"quantity_on_hand": 0},
        )
        new_qty = row.quantity_on_hand + delta
        if new_qty < 0:
            raise ConflictError(f"Insufficient stock in bin {bin.location_code}.")
        row.quantity_on_hand = new_qty
        row.save(update_fields=["quantity_on_hand", "updated_at"])
        return row

    @staticmethod
    def list_bin_inventory(*, warehouse_code: str | None = None, sku: str | None = None) -> QuerySet[BinInventory]:
        qs = BinInventory.objects.select_related(
            "bin__aisle__zone__warehouse", "variant__product"
        ).filter(quantity_on_hand__gt=0)
        if warehouse_code:
            qs = qs.filter(bin__aisle__zone__warehouse__code=warehouse_code)
        if sku:
            qs = qs.filter(variant__sku__iexact=sku)
        return qs.order_by("bin__aisle__zone__code", "bin__aisle__code", "bin__code")


class StockTransferService:
    @staticmethod
    def list_transfers(*, status: str | None = None) -> QuerySet[StockTransfer]:
        qs = StockTransfer.objects.select_related(
            "from_warehouse", "to_warehouse", "from_bin", "to_bin", "created_by"
        ).prefetch_related("lines")
        if status:
            qs = qs.filter(status=status)
        return qs.order_by("-created_at")

    @staticmethod
    def get_transfer(public_id: UUID) -> StockTransfer:
        tr = StockTransferService.list_transfers().filter(public_id=public_id).first()
        if not tr:
            raise NotFoundError("Stock transfer not found.")
        return tr

    @classmethod
    @transaction.atomic
    def create(
        cls,
        *,
        actor,
        transfer_type: str,
        from_warehouse_code: str,
        to_warehouse_code: str,
        from_bin_id: UUID | None = None,
        to_bin_id: UUID | None = None,
        requires_approval: bool = False,
        notes: str = "",
    ) -> StockTransfer:
        from_wh = resolve_warehouse(from_warehouse_code)
        to_wh = resolve_warehouse(to_warehouse_code)
        from_bin = BinLocationService.get_bin(from_bin_id) if from_bin_id else None
        to_bin = BinLocationService.get_bin(to_bin_id) if to_bin_id else None

        if transfer_type == TransferType.BIN:
            if not from_bin or not to_bin:
                raise BusinessRuleError("Bin transfers require source and destination bins.")
            if from_bin.warehouse.id != to_bin.warehouse.id:
                raise BusinessRuleError("Bin transfers must stay within the same warehouse.")
            from_wh = from_bin.warehouse
            to_wh = to_bin.warehouse

        transfer = StockTransfer.objects.create(
            transfer_number=_next_doc(DocumentType.STOCK_TRANSFER, "ST"),
            transfer_type=transfer_type,
            from_warehouse=from_wh,
            to_warehouse=to_wh,
            from_bin=from_bin,
            to_bin=to_bin,
            requires_approval=requires_approval,
            notes=notes,
            created_by=actor if getattr(actor, "is_authenticated", False) else None,
        )
        if requires_approval:
            WorkflowEngine.start(
                definition_code=WorkflowCode.WMS_TRANSFER_APPROVAL,
                resource_type="stock_transfer",
                resource_id=str(transfer.public_id),
                actor=actor,
            )
        cls._audit(actor, transfer, "create", "Stock transfer created")
        return transfer

    @classmethod
    @transaction.atomic
    def add_line(cls, *, transfer: StockTransfer, sku: str, quantity: int) -> StockTransferLine:
        if transfer.status != TransferStatus.DRAFT:
            raise BusinessRuleError("Cannot add lines to this transfer.")
        variant = resolve_variant(sku)
        return StockTransferLine.objects.create(
            transfer=transfer,
            variant=variant,
            sku=variant.sku,
            quantity=quantity,
        )

    @classmethod
    @transaction.atomic
    def submit(cls, *, transfer: StockTransfer, actor) -> StockTransfer:
        if transfer.status != TransferStatus.DRAFT:
            raise BusinessRuleError("Only draft transfers can be submitted.")
        if not transfer.lines.exists():
            raise BusinessRuleError("Transfer must have at least one line.")
        transfer.status = TransferStatus.SUBMITTED
        transfer.save(update_fields=["status", "updated_at"])
        if transfer.requires_approval:
            instance = WorkflowEngine.get_for_resource(
                resource_type="stock_transfer", resource_id=str(transfer.public_id)
            )
            if instance:
                WorkflowEngine.transition(instance=instance, action="submit", actor=actor)
        else:
            return cls.execute(transfer=transfer, actor=actor)
        cls._audit(actor, transfer, "submit", "Transfer submitted")
        return transfer

    @classmethod
    @transaction.atomic
    def approve(cls, *, transfer: StockTransfer, actor, comment: str = "") -> StockTransfer:
        if transfer.status != TransferStatus.SUBMITTED:
            raise BusinessRuleError("Only submitted transfers can be approved.")
        instance = WorkflowEngine.get_for_resource(
            resource_type="stock_transfer", resource_id=str(transfer.public_id)
        )
        if instance:
            WorkflowEngine.transition(instance=instance, action="approve", actor=actor, comment=comment)
        transfer.status = TransferStatus.APPROVED
        transfer.save(update_fields=["status", "updated_at"])
        cls._audit(actor, transfer, "approve", "Transfer approved")
        return cls.execute(transfer=transfer, actor=actor)

    @classmethod
    @transaction.atomic
    def execute(cls, *, transfer: StockTransfer, actor) -> StockTransfer:
        if transfer.status in (TransferStatus.COMPLETED, TransferStatus.CANCELLED):
            raise BusinessRuleError("Transfer already finalized.")
        if transfer.transfer_type == TransferType.WAREHOUSE:
            cls._execute_warehouse_transfer(transfer=transfer, actor=actor)
        else:
            cls._execute_bin_transfer(transfer=transfer, actor=actor)
        transfer.status = TransferStatus.COMPLETED
        transfer.save(update_fields=["status", "updated_at"])
        DomainEventPublisher.publish(
            event_type=DomainEventType.INVENTORY_TRANSFERRED,
            aggregate_type="stock_transfer",
            aggregate_id=str(transfer.public_id),
            payload={"transfer_number": transfer.transfer_number},
            idempotency_key=f"inventory.transferred:{transfer.public_id}",
        )
        cls._audit(actor, transfer, "execute", "Transfer completed")
        return transfer

    @staticmethod
    def _execute_warehouse_transfer(*, transfer: StockTransfer, actor) -> None:
        for line in transfer.lines.select_related("variant"):
            InventoryService.stock_transfer(
                sku=line.sku,
                from_warehouse_code=transfer.from_warehouse.code,
                to_warehouse_code=transfer.to_warehouse.code,
                notes=f"Transfer {transfer.transfer_number}",
                user=actor,
            )
            line.quantity_moved = line.quantity
            line.save(update_fields=["quantity_moved", "updated_at"])

    @staticmethod
    def _execute_bin_transfer(*, transfer: StockTransfer, actor) -> None:
        if not transfer.from_bin or not transfer.to_bin:
            raise BusinessRuleError("Bin transfer missing bin references.")
        for line in transfer.lines.select_related("variant"):
            BinInventoryService.move_bin_qty(
                from_bin=transfer.from_bin,
                to_bin=transfer.to_bin,
                variant_id=line.variant_id,
                quantity=line.quantity,
            )
            line.quantity_moved = line.quantity
            line.save(update_fields=["quantity_moved", "updated_at"])

    @staticmethod
    def _audit(user, transfer: StockTransfer, action: str, summary: str) -> None:
        AuditService.log(
            user=user,
            module=AuditModule.WMS,
            action=action,
            resource_type="stock_transfer",
            resource_id=str(transfer.public_id),
            summary=summary,
            metadata={"transfer_number": transfer.transfer_number, "status": transfer.status},
            mirror_operational=False,
        )


class PickListService:
    @staticmethod
    def list_picks(*, status: str | None = None) -> QuerySet[PickList]:
        qs = PickList.objects.select_related("warehouse", "order", "assigned_to", "created_by").prefetch_related(
            "lines"
        )
        if status:
            qs = qs.filter(status=status)
        return qs.order_by("-created_at")

    @staticmethod
    def get_pick(public_id: UUID) -> PickList:
        pl = PickListService.list_picks().filter(public_id=public_id).first()
        if not pl:
            raise NotFoundError("Pick list not found.")
        return pl

    @classmethod
    @transaction.atomic
    def create_for_order(cls, *, order: Order, warehouse_code: str, actor) -> PickList:
        warehouse = resolve_warehouse(warehouse_code)
        pick = PickList.objects.create(
            pick_number=_next_doc(DocumentType.PICK_LIST, "PK"),
            warehouse=warehouse,
            order=order,
            status=PickListStatus.DRAFT,
            created_by=actor if getattr(actor, "is_authenticated", False) else None,
        )
        for item in order.items.select_related("variant__product"):
            PickListLine.objects.create(
                pick_list=pick,
                variant=item.variant,
                sku=item.sku,
                product_name=item.product_name,
                quantity_required=item.quantity,
            )
        cls._audit(actor, pick, "create", f"Pick list for order {order.order_number}")
        return pick

    @classmethod
    @transaction.atomic
    def assign(cls, *, pick: PickList, user, actor) -> PickList:
        if pick.status not in (PickListStatus.DRAFT, PickListStatus.ASSIGNED):
            raise BusinessRuleError("Pick list cannot be assigned in current status.")
        pick.assigned_to = user
        pick.status = PickListStatus.ASSIGNED
        pick.save(update_fields=["assigned_to", "status", "updated_at"])
        cls._audit(actor, pick, "assign", f"Assigned to {user.email}")
        return pick

    @classmethod
    @transaction.atomic
    def start_picking(cls, *, pick: PickList, actor) -> PickList:
        if pick.status not in (PickListStatus.ASSIGNED, PickListStatus.DRAFT):
            raise BusinessRuleError("Cannot start picking.")
        pick.status = PickListStatus.PICKING
        pick.save(update_fields=["status", "updated_at"])
        return pick

    @classmethod
    @transaction.atomic
    def record_pick(
        cls,
        *,
        pick: PickList,
        line_id: UUID,
        quantity: int,
        from_bin_id: UUID | None,
        actor,
    ) -> PickListLine:
        if pick.status not in (PickListStatus.PICKING, PickListStatus.ASSIGNED):
            raise BusinessRuleError("Pick list is not in picking status.")
        line = pick.lines.filter(public_id=line_id).first()
        if not line:
            raise NotFoundError("Pick line not found.")
        if quantity <= 0:
            raise BusinessRuleError("Pick quantity must be positive.")
        remaining = line.quantity_required - line.quantity_picked
        if quantity > remaining:
            raise ConflictError(f"Cannot pick {quantity}; only {remaining} remaining.")

        from_bin = BinLocationService.get_bin(from_bin_id) if from_bin_id else None
        if from_bin:
            BinInventoryService.move_bin_qty(
                from_bin=from_bin,
                to_bin=None,
                variant_id=line.variant_id,
                quantity=quantity,
            )
            line.from_bin = from_bin

        line.quantity_picked += quantity
        line.save(update_fields=["quantity_picked", "from_bin", "updated_at"])

        if all(l.quantity_picked >= l.quantity_required for l in pick.lines.all()):
            pick.status = PickListStatus.PICKED
            pick.save(update_fields=["status", "updated_at"])
        return line

    @classmethod
    @transaction.atomic
    def complete(cls, *, pick: PickList, actor) -> PickList:
        if pick.status not in (PickListStatus.PICKED, PickListStatus.PICKING):
            raise BusinessRuleError("Pick list must be fully picked before completion.")
        if not all(l.quantity_picked >= l.quantity_required for l in pick.lines.all()):
            raise BusinessRuleError("Not all lines fully picked.")

        for line in pick.lines.all():
            InventoryService.stock_out(
                sku=line.sku,
                warehouse_code=pick.warehouse.code,
                quantity=line.quantity_picked,
                transaction_type=InventoryTransaction.TransactionType.SALE,
                reference_type="pick_list",
                reference_id=pick.id,
                notes=f"Pick {pick.pick_number}",
                user=actor,
            )

        pick.status = PickListStatus.COMPLETED
        pick.save(update_fields=["status", "updated_at"])
        DomainEventPublisher.publish(
            event_type=DomainEventType.PICK_COMPLETED,
            aggregate_type="pick_list",
            aggregate_id=str(pick.public_id),
            payload={"pick_number": pick.pick_number},
            idempotency_key=f"pick.completed:{pick.public_id}",
        )
        cls._audit(actor, pick, "complete", "Pick list completed")
        return pick

    @staticmethod
    def _audit(user, pick: PickList, action: str, summary: str) -> None:
        AuditService.log(
            user=user,
            module=AuditModule.WMS,
            action=action,
            resource_type="pick_list",
            resource_id=str(pick.public_id),
            summary=summary,
            metadata={"pick_number": pick.pick_number, "status": pick.status},
            mirror_operational=False,
        )


class PutawayService:
    @staticmethod
    def list_tasks(*, status: str | None = None) -> QuerySet[PutawayTask]:
        qs = PutawayTask.objects.select_related(
            "goods_receipt", "warehouse", "assigned_to"
        ).prefetch_related("lines")
        if status:
            qs = qs.filter(status=status)
        return qs.order_by("-created_at")

    @staticmethod
    def get_task(public_id: UUID) -> PutawayTask:
        task = PutawayService.list_tasks().filter(public_id=public_id).first()
        if not task:
            raise NotFoundError("Putaway task not found.")
        return task

    @classmethod
    @transaction.atomic
    def create_from_grn(cls, *, grn, actor=None) -> PutawayTask:
        existing = PutawayTask.objects.filter(goods_receipt=grn).first()
        if existing:
            return existing
        task = PutawayTask.objects.create(
            task_number=_next_doc(DocumentType.PUTAWAY, "PT"),
            goods_receipt=grn,
            warehouse=grn.warehouse,
            status=PutawayStatus.PENDING,
        )
        for grn_line in grn.lines.select_related("purchase_order_line__variant"):
            pol = grn_line.purchase_order_line
            PutawayTaskLine.objects.create(
                task=task,
                variant=pol.variant,
                sku=pol.variant.sku,
                quantity=grn_line.quantity_received,
            )
        AuditService.log(
            user=actor,
            module=AuditModule.WMS,
            action="putaway_create",
            resource_type="putaway_task",
            resource_id=str(task.public_id),
            summary=f"Putaway task for GRN {grn.grn_number}",
            metadata={"grn_number": grn.grn_number},
            mirror_operational=False,
        )
        return task

    @classmethod
    @transaction.atomic
    def assign_bin(
        cls,
        *,
        task: PutawayTask,
        line_id: UUID,
        target_bin_id: UUID,
        quantity: int,
        actor,
    ) -> PutawayTaskLine:
        if task.status == PutawayStatus.COMPLETED:
            raise BusinessRuleError("Putaway task already completed.")
        line = task.lines.filter(public_id=line_id).first()
        if not line:
            raise NotFoundError("Putaway line not found.")
        target_bin = BinLocationService.get_bin(target_bin_id)
        if target_bin.warehouse_id != task.warehouse_id:
            raise BusinessRuleError("Target bin must be in the same warehouse.")

        remaining = line.quantity - line.quantity_putaway
        if quantity > remaining:
            raise ConflictError(f"Cannot putaway {quantity}; only {remaining} remaining.")

        unlocated = BinInventoryService.get_unlocated_qty(
            warehouse_code=task.warehouse.code,
            variant_id=line.variant_id,
        )
        if quantity > unlocated:
            raise ConflictError(
                f"Only {unlocated} units unlocated for {line.sku} at {task.warehouse.code}."
            )

        BinInventoryService.move_bin_qty(
            from_bin=None,
            to_bin=target_bin,
            variant_id=line.variant_id,
            quantity=quantity,
        )
        line.quantity_putaway += quantity
        line.target_bin = target_bin
        line.save(update_fields=["quantity_putaway", "target_bin", "updated_at"])

        if task.status == PutawayStatus.PENDING:
            task.status = PutawayStatus.IN_PROGRESS
            task.save(update_fields=["status", "updated_at"])

        if all(l.quantity_putaway >= l.quantity for l in task.lines.all()):
            task.status = PutawayStatus.COMPLETED
            task.save(update_fields=["status", "updated_at"])

        return line


class CycleCountService:
    @staticmethod
    def list_counts(*, status: str | None = None) -> QuerySet[CycleCount]:
        qs = CycleCount.objects.select_related("warehouse", "created_by").prefetch_related("lines")
        if status:
            qs = qs.filter(status=status)
        return qs.order_by("-created_at")

    @staticmethod
    def get_count(public_id: UUID) -> CycleCount:
        cc = CycleCountService.list_counts().filter(public_id=public_id).first()
        if not cc:
            raise NotFoundError("Cycle count not found.")
        return cc

    @classmethod
    @transaction.atomic
    def create(cls, *, warehouse_code: str, actor) -> CycleCount:
        warehouse = resolve_warehouse(warehouse_code)
        cc = CycleCount.objects.create(
            count_number=_next_doc(DocumentType.CYCLE_COUNT, "CC"),
            warehouse=warehouse,
            status=CycleCountStatus.DRAFT,
            created_by=actor if getattr(actor, "is_authenticated", False) else None,
        )
        return cc

    @classmethod
    @transaction.atomic
    def add_line(
        cls,
        *,
        cc: CycleCount,
        sku: str,
        bin_id: UUID | None = None,
    ) -> CycleCountLine:
        if cc.status == CycleCountStatus.COMPLETED:
            raise BusinessRuleError("Cycle count is completed.")
        variant = resolve_variant(sku)
        bin_obj = BinLocationService.get_bin(bin_id) if bin_id else None
        if bin_obj and bin_obj.warehouse_id != cc.warehouse_id:
            raise BusinessRuleError("Bin must belong to count warehouse.")

        if bin_obj:
            expected = BinInventoryService.get_bin_qty(bin=bin_obj, variant_id=variant.id)
        else:
            level = InventoryLevel.objects.filter(
                warehouse=cc.warehouse, variant=variant
            ).first()
            expected = level.quantity_on_hand if level else 0

        return CycleCountLine.objects.create(
            cycle_count=cc,
            variant=variant,
            sku=variant.sku,
            bin=bin_obj,
            expected_qty=expected,
        )

    @classmethod
    @transaction.atomic
    def record_count(cls, *, cc: CycleCount, line_id: UUID, counted_qty: int, actor) -> CycleCountLine:
        if cc.status == CycleCountStatus.COMPLETED:
            raise BusinessRuleError("Cycle count is completed.")
        line = cc.lines.filter(public_id=line_id).first()
        if not line:
            raise NotFoundError("Count line not found.")
        line.counted_qty = counted_qty
        line.save(update_fields=["counted_qty", "updated_at"])
        if cc.status == CycleCountStatus.DRAFT:
            cc.status = CycleCountStatus.IN_PROGRESS
            cc.save(update_fields=["status", "updated_at"])
        return line

    @classmethod
    @transaction.atomic
    def complete(cls, *, cc: CycleCount, actor, apply_variances: bool = True) -> CycleCount:
        if cc.status == CycleCountStatus.COMPLETED:
            raise BusinessRuleError("Already completed.")
        incomplete = cc.lines.filter(counted_qty__isnull=True).exists()
        if incomplete:
            raise BusinessRuleError("All lines must be counted before completion.")

        if apply_variances:
            for line in cc.lines.select_related("variant", "bin"):
                variance = line.variance or 0
                if variance == 0:
                    continue
                if line.bin:
                    BinInventoryService._adjust_bin(
                        bin=line.bin, variant_id=line.variant_id, delta=variance
                    )
                level = InventoryLevel.objects.filter(
                    warehouse=cc.warehouse, variant=line.variant
                ).first()
                unit_cost = level.average_cost_cents if level else 0
                InventoryService.stock_adjustment(
                    sku=line.sku,
                    warehouse_code=cc.warehouse.code,
                    quantity_change=variance,
                    unit_cost_cents=unit_cost if variance > 0 else None,
                    notes=f"Cycle count {cc.count_number}",
                    user=actor,
                )

        cc.status = CycleCountStatus.COMPLETED
        cc.completed_at = timezone.now()
        cc.save(update_fields=["status", "completed_at", "updated_at"])

        InventoryLevel.objects.filter(warehouse=cc.warehouse).update(
            last_counted_at=timezone.now()
        )

        DomainEventPublisher.publish(
            event_type=DomainEventType.CYCLE_COUNT_COMPLETED,
            aggregate_type="cycle_count",
            aggregate_id=str(cc.public_id),
            payload={"count_number": cc.count_number},
            idempotency_key=f"cycle_count.completed:{cc.public_id}",
        )
        AuditService.log(
            user=actor,
            module=AuditModule.WMS,
            action="cycle_count_complete",
            resource_type="cycle_count",
            resource_id=str(cc.public_id),
            summary=f"Cycle count {cc.count_number} completed",
            metadata={"count_number": cc.count_number},
            mirror_operational=False,
        )
        return cc


class AdjustmentService:
    @staticmethod
    def list_requests(*, status: str | None = None) -> QuerySet[InventoryAdjustmentRequest]:
        qs = InventoryAdjustmentRequest.objects.select_related(
            "warehouse", "created_by"
        ).prefetch_related("lines")
        if status:
            qs = qs.filter(status=status)
        return qs.order_by("-created_at")

    @staticmethod
    def get_request(public_id: UUID) -> InventoryAdjustmentRequest:
        req = AdjustmentService.list_requests().filter(public_id=public_id).first()
        if not req:
            raise NotFoundError("Adjustment request not found.")
        return req

    @classmethod
    @transaction.atomic
    def create(cls, *, warehouse_code: str, reason: str, actor) -> InventoryAdjustmentRequest:
        warehouse = resolve_warehouse(warehouse_code)
        req = InventoryAdjustmentRequest.objects.create(
            adjustment_number=_next_doc(DocumentType.ADJUSTMENT, "ADJ"),
            warehouse=warehouse,
            reason=reason,
            created_by=actor if getattr(actor, "is_authenticated", False) else None,
        )
        WorkflowEngine.start(
            definition_code=WorkflowCode.WMS_ADJUSTMENT_APPROVAL,
            resource_type="inventory_adjustment",
            resource_id=str(req.public_id),
            actor=actor,
        )
        return req

    @classmethod
    @transaction.atomic
    def add_line(
        cls,
        *,
        req: InventoryAdjustmentRequest,
        sku: str,
        quantity_change: int,
        unit_cost_cents: int = 0,
        bin_id: UUID | None = None,
    ) -> InventoryAdjustmentLine:
        if req.status != AdjustmentStatus.DRAFT:
            raise BusinessRuleError("Cannot add lines to this adjustment.")
        variant = resolve_variant(sku)
        bin_obj = BinLocationService.get_bin(bin_id) if bin_id else None
        return InventoryAdjustmentLine.objects.create(
            request=req,
            variant=variant,
            sku=variant.sku,
            bin=bin_obj,
            quantity_change=quantity_change,
            unit_cost_cents=unit_cost_cents,
        )

    @classmethod
    @transaction.atomic
    def submit(cls, *, req: InventoryAdjustmentRequest, actor) -> InventoryAdjustmentRequest:
        if req.status != AdjustmentStatus.DRAFT:
            raise BusinessRuleError("Only draft adjustments can be submitted.")
        if not req.lines.exists():
            raise BusinessRuleError("Adjustment must have at least one line.")
        req.status = AdjustmentStatus.SUBMITTED
        req.save(update_fields=["status", "updated_at"])
        instance = WorkflowEngine.get_for_resource(
            resource_type="inventory_adjustment", resource_id=str(req.public_id)
        )
        if instance:
            WorkflowEngine.transition(instance=instance, action="submit", actor=actor)
        return req

    @classmethod
    @transaction.atomic
    def approve(cls, *, req: InventoryAdjustmentRequest, actor, comment: str = "") -> InventoryAdjustmentRequest:
        if req.status != AdjustmentStatus.SUBMITTED:
            raise BusinessRuleError("Only submitted adjustments can be approved.")
        instance = WorkflowEngine.get_for_resource(
            resource_type="inventory_adjustment", resource_id=str(req.public_id)
        )
        if instance:
            WorkflowEngine.transition(
                instance=instance, action="approve", actor=actor, comment=comment
            )
        req.status = AdjustmentStatus.APPROVED
        req.save(update_fields=["status", "updated_at"])
        return cls.apply(req=req, actor=actor)

    @classmethod
    @transaction.atomic
    def reject(cls, *, req: InventoryAdjustmentRequest, actor, comment: str = "") -> InventoryAdjustmentRequest:
        if req.status != AdjustmentStatus.SUBMITTED:
            raise BusinessRuleError("Only submitted adjustments can be rejected.")
        instance = WorkflowEngine.get_for_resource(
            resource_type="inventory_adjustment", resource_id=str(req.public_id)
        )
        if instance:
            WorkflowEngine.transition(
                instance=instance, action="reject", actor=actor, comment=comment
            )
        req.status = AdjustmentStatus.REJECTED
        req.save(update_fields=["status", "updated_at"])
        return req

    @classmethod
    @transaction.atomic
    def apply(cls, *, req: InventoryAdjustmentRequest, actor) -> InventoryAdjustmentRequest:
        if req.status not in (AdjustmentStatus.APPROVED, AdjustmentStatus.SUBMITTED):
            raise BusinessRuleError("Adjustment must be approved before applying.")
        for line in req.lines.select_related("bin", "variant"):
            if line.bin and line.quantity_change != 0:
                BinInventoryService._adjust_bin(
                    bin=line.bin, variant_id=line.variant_id, delta=line.quantity_change
                )
            InventoryService.stock_adjustment(
                sku=line.sku,
                warehouse_code=req.warehouse.code,
                quantity_change=line.quantity_change,
                unit_cost_cents=line.unit_cost_cents or None,
                notes=f"Adjustment {req.adjustment_number}: {req.reason}",
                user=actor,
            )
        req.status = AdjustmentStatus.APPLIED
        req.save(update_fields=["status", "updated_at"])
        DomainEventPublisher.publish(
            event_type=DomainEventType.INVENTORY_ADJUSTED,
            aggregate_type="inventory_adjustment",
            aggregate_id=str(req.public_id),
            payload={"adjustment_number": req.adjustment_number},
            idempotency_key=f"inventory.adjusted:{req.public_id}",
        )
        AuditService.log(
            user=actor,
            module=AuditModule.WMS,
            action="adjustment_applied",
            resource_type="inventory_adjustment",
            resource_id=str(req.public_id),
            summary=f"Adjustment {req.adjustment_number} applied",
            metadata={"adjustment_number": req.adjustment_number},
            mirror_operational=False,
        )
        return req


class WmsDashboardService:
    @staticmethod
    def get_kpis() -> dict[str, Any]:
        from apps.inventory.valuation import InventoryValuationService

        summary = InventoryValuationService.get_summary()
        open_transfers = StockTransfer.objects.filter(
            status__in=[
                TransferStatus.DRAFT,
                TransferStatus.SUBMITTED,
                TransferStatus.APPROVED,
                TransferStatus.IN_TRANSIT,
            ]
        ).count()
        open_picks = PickList.objects.filter(
            status__in=[
                PickListStatus.DRAFT,
                PickListStatus.ASSIGNED,
                PickListStatus.PICKING,
                PickListStatus.PICKED,
            ]
        ).count()

        completed_counts = CycleCount.objects.filter(status=CycleCountStatus.COMPLETED)
        accuracy = 0.0
        if completed_counts.exists():
            lines = CycleCountLine.objects.filter(
                cycle_count__status=CycleCountStatus.COMPLETED,
                counted_qty__isnull=False,
            )
            total = lines.count()
            accurate = lines.filter(counted_qty=F("expected_qty")).count()
            accuracy = round((accurate / max(total, 1)) * 100, 1)

        return {
            "inventory_value_cents": summary.get("amount_ex_gst_cents", 0),
            "open_transfers": open_transfers,
            "open_picks": open_picks,
            "cycle_count_accuracy_pct": accuracy,
        }
