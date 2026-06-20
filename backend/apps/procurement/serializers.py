"""Procurement API serializers — camelCase output."""
from __future__ import annotations

from apps.procurement.models import GoodsReceipt, PurchaseRequest, SupplierDocument
from apps.suppliers.models import PurchaseOrder


def _user_ref(user) -> dict | None:
    if not user:
        return None
    return {"id": str(user.public_id), "email": user.email}


def serialize_pr_line(line) -> dict:
    return {
        "id": str(line.public_id),
        "sku": line.sku,
        "productName": line.product_name,
        "quantity": line.quantity,
        "unitCostCents": line.unit_cost_cents,
        "notes": line.notes,
    }


def serialize_purchase_request(pr: PurchaseRequest, *, include_lines: bool = True) -> dict:
    data = {
        "id": str(pr.public_id),
        "requestNumber": pr.request_number,
        "status": pr.status,
        "priority": pr.priority,
        "justification": pr.justification,
        "requestedBy": _user_ref(pr.requested_by),
        "departmentId": str(pr.department.public_id) if pr.department else None,
        "departmentName": pr.department.name if pr.department else None,
        "costCenterId": str(pr.cost_center.public_id) if pr.cost_center else None,
        "costCenterName": pr.cost_center.name if pr.cost_center else None,
        "warehouseCode": pr.warehouse.code if pr.warehouse else None,
        "supplierId": str(pr.supplier.public_id) if pr.supplier else None,
        "supplierName": pr.supplier.name if pr.supplier else None,
        "convertedPoId": str(pr.converted_po.public_id) if pr.converted_po else None,
        "convertedPoNumber": pr.converted_po.po_number if pr.converted_po else None,
        "createdAt": pr.created_at.isoformat(),
        "updatedAt": pr.updated_at.isoformat(),
    }
    if include_lines:
        data["lines"] = [serialize_pr_line(line) for line in pr.lines.all()]
    return data


def serialize_goods_receipt(grn: GoodsReceipt) -> dict:
    return {
        "id": str(grn.public_id),
        "grnNumber": grn.grn_number,
        "status": grn.status,
        "poNumber": grn.purchase_order.po_number,
        "poId": str(grn.purchase_order.public_id),
        "receivedAt": grn.received_at.isoformat(),
        "lines": [
            {
                "id": str(line.public_id),
                "sku": line.purchase_order_line.variant.sku,
                "quantityReceived": line.quantity_received,
                "batchNumber": line.batch_number,
                "receivedAt": line.received_at.isoformat(),
            }
            for line in grn.lines.select_related(
                "purchase_order_line__variant"
            ).all()
        ],
    }


def serialize_supplier_po(po: PurchaseOrder) -> dict:
    return {
        "id": str(po.public_id),
        "poNumber": po.po_number,
        "status": po.status,
        "totalExGstCents": po.total_ex_gst_cents,
        "expectedAt": po.expected_at.isoformat() if po.expected_at else None,
        "acknowledgedAt": po.supplier_acknowledged_at.isoformat()
        if po.supplier_acknowledged_at
        else None,
        "paymentStatus": po.payment_status,
        "warehouseCode": po.warehouse.code,
        "lines": [
            {
                "id": str(line.public_id),
                "sku": line.variant.sku,
                "productName": line.variant.product.name,
                "quantityOrdered": line.quantity_ordered,
                "quantityReceived": line.quantity_received,
                "unitCostCents": line.unit_cost_cents,
            }
            for line in po.lines.select_related("variant__product").all()
        ],
        "createdAt": po.created_at.isoformat(),
    }


def serialize_supplier_kpis(kpis: dict) -> dict:
    return {
        "onTimeDeliveryPct": kpis["on_time_delivery_pct"],
        "avgLeadTimeDays": kpis["avg_lead_time_days"],
        "orderAccuracyPct": kpis["order_accuracy_pct"],
        "purchaseSpendCents": kpis["purchase_spend_cents"],
        "totalOrders": kpis.get("total_orders", 0),
        "supplierId": kpis.get("supplier_id"),
        "supplierName": kpis.get("supplier_name"),
    }


def serialize_supplier_document(doc: SupplierDocument) -> dict:
    return {
        "id": str(doc.public_id),
        "documentType": doc.document_type,
        "originalFilename": doc.original_filename,
        "fileUrl": doc.file.url if doc.file else None,
        "poId": str(doc.purchase_order.public_id) if doc.purchase_order else None,
        "notes": doc.notes,
        "createdAt": doc.created_at.isoformat(),
    }
