"""WMS API serializers — camelCase output."""
from __future__ import annotations

from apps.wms.models import (
    BinInventory,
    CycleCount,
    InventoryAdjustmentRequest,
    PickList,
    PutawayTask,
    StockTransfer,
    WarehouseBin,
    WarehouseZone,
)


def _user_ref(user) -> dict | None:
    if not user:
        return None
    return {"id": str(user.public_id), "email": user.email}


def serialize_zone(zone: WarehouseZone) -> dict:
    return {
        "id": str(zone.public_id),
        "warehouseCode": zone.warehouse.code,
        "code": zone.code,
        "name": zone.name,
        "isActive": zone.is_active,
    }


def serialize_bin(bin_obj: WarehouseBin) -> dict:
    return {
        "id": str(bin_obj.public_id),
        "locationCode": bin_obj.location_code,
        "code": bin_obj.code,
        "name": bin_obj.name,
        "binType": bin_obj.bin_type,
        "zoneCode": bin_obj.aisle.zone.code,
        "aisleCode": bin_obj.aisle.code,
        "warehouseCode": bin_obj.warehouse.code,
        "isActive": bin_obj.is_active,
    }


def serialize_bin_inventory(row: BinInventory) -> dict:
    return {
        "id": str(row.public_id),
        "locationCode": row.bin.location_code,
        "binId": str(row.bin.public_id),
        "sku": row.sku,
        "productName": row.variant.product.name,
        "quantityOnHand": row.quantity_on_hand,
        "warehouseCode": row.bin.warehouse.code,
    }


def serialize_transfer_line(line) -> dict:
    return {
        "id": str(line.public_id),
        "sku": line.sku,
        "quantity": line.quantity,
        "quantityMoved": line.quantity_moved,
    }


def serialize_transfer(tr: StockTransfer) -> dict:
    return {
        "id": str(tr.public_id),
        "transferNumber": tr.transfer_number,
        "transferType": tr.transfer_type,
        "status": tr.status,
        "fromWarehouseCode": tr.from_warehouse.code,
        "toWarehouseCode": tr.to_warehouse.code,
        "fromBinId": str(tr.from_bin.public_id) if tr.from_bin else None,
        "toBinId": str(tr.to_bin.public_id) if tr.to_bin else None,
        "requiresApproval": tr.requires_approval,
        "notes": tr.notes,
        "createdBy": _user_ref(tr.created_by),
        "lines": [serialize_transfer_line(line) for line in tr.lines.all()],
        "createdAt": tr.created_at.isoformat(),
    }


def serialize_pick_line(line) -> dict:
    return {
        "id": str(line.public_id),
        "sku": line.sku,
        "productName": line.product_name,
        "quantityRequired": line.quantity_required,
        "quantityPicked": line.quantity_picked,
        "fromBinId": str(line.from_bin.public_id) if line.from_bin else None,
        "fromBinLocation": line.from_bin.location_code if line.from_bin else None,
    }


def serialize_pick_list(pick: PickList) -> dict:
    return {
        "id": str(pick.public_id),
        "pickNumber": pick.pick_number,
        "status": pick.status,
        "warehouseCode": pick.warehouse.code,
        "orderId": str(pick.order.public_id) if pick.order else None,
        "orderNumber": pick.order.order_number if pick.order else None,
        "assignedTo": _user_ref(pick.assigned_to),
        "notes": pick.notes,
        "lines": [serialize_pick_line(line) for line in pick.lines.all()],
        "createdAt": pick.created_at.isoformat(),
    }


def serialize_putaway_line(line) -> dict:
    return {
        "id": str(line.public_id),
        "sku": line.sku,
        "quantity": line.quantity,
        "quantityPutaway": line.quantity_putaway,
        "targetBinId": str(line.target_bin.public_id) if line.target_bin else None,
        "targetBinLocation": line.target_bin.location_code if line.target_bin else None,
    }


def serialize_putaway_task(task: PutawayTask) -> dict:
    return {
        "id": str(task.public_id),
        "taskNumber": task.task_number,
        "status": task.status,
        "grnNumber": task.goods_receipt.grn_number,
        "warehouseCode": task.warehouse.code,
        "assignedTo": _user_ref(task.assigned_to),
        "lines": [serialize_putaway_line(line) for line in task.lines.all()],
        "createdAt": task.created_at.isoformat(),
    }


def serialize_cycle_count_line(line) -> dict:
    return {
        "id": str(line.public_id),
        "sku": line.sku,
        "binId": str(line.bin.public_id) if line.bin else None,
        "binLocation": line.bin.location_code if line.bin else None,
        "expectedQty": line.expected_qty,
        "countedQty": line.counted_qty,
        "variance": line.variance,
    }


def serialize_cycle_count(cc: CycleCount) -> dict:
    return {
        "id": str(cc.public_id),
        "countNumber": cc.count_number,
        "status": cc.status,
        "warehouseCode": cc.warehouse.code,
        "scheduledAt": cc.scheduled_at.isoformat() if cc.scheduled_at else None,
        "completedAt": cc.completed_at.isoformat() if cc.completed_at else None,
        "lines": [serialize_cycle_count_line(line) for line in cc.lines.all()],
        "createdAt": cc.created_at.isoformat(),
    }


def serialize_adjustment_line(line) -> dict:
    return {
        "id": str(line.public_id),
        "sku": line.sku,
        "binId": str(line.bin.public_id) if line.bin else None,
        "quantityChange": line.quantity_change,
        "unitCostCents": line.unit_cost_cents,
    }


def serialize_adjustment(req: InventoryAdjustmentRequest) -> dict:
    return {
        "id": str(req.public_id),
        "adjustmentNumber": req.adjustment_number,
        "status": req.status,
        "warehouseCode": req.warehouse.code,
        "reason": req.reason,
        "createdBy": _user_ref(req.created_by),
        "lines": [serialize_adjustment_line(line) for line in req.lines.all()],
        "createdAt": req.created_at.isoformat(),
    }
