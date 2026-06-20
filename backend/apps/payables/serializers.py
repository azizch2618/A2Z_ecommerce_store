"""Payables API serializers."""
from __future__ import annotations

from apps.payables.models import DebitNote, SupplierInvoice, SupplierPayment


def _user_ref(user) -> dict | None:
    if not user:
        return None
    return {"id": str(user.public_id), "email": user.email}


def serialize_supplier_invoice_line(line) -> dict:
    return {
        "id": str(line.public_id),
        "description": line.description,
        "quantity": line.quantity,
        "unitCostExGstCents": line.unit_cost_ex_gst_cents,
        "lineExGstCents": line.line_ex_gst_cents,
        "lineGstCents": line.line_gst_cents,
        "poLineId": str(line.purchase_order_line.public_id) if line.purchase_order_line_id else None,
    }


def serialize_supplier_invoice(inv: SupplierInvoice, *, include_lines: bool = True) -> dict:
    data = {
        "id": str(inv.public_id),
        "invoiceNumber": inv.invoice_number,
        "supplierInvoiceRef": inv.supplier_invoice_ref,
        "supplierId": str(inv.supplier.public_id),
        "supplierName": inv.supplier.name,
        "poId": str(inv.purchase_order.public_id) if inv.purchase_order_id else None,
        "poNumber": inv.purchase_order.po_number if inv.purchase_order_id else None,
        "grnId": str(inv.goods_receipt.public_id) if inv.goods_receipt_id else None,
        "grnNumber": inv.goods_receipt.grn_number if inv.goods_receipt_id else None,
        "status": inv.status,
        "matchStatus": inv.match_status,
        "invoiceDate": inv.invoice_date.isoformat() if inv.invoice_date else None,
        "dueDate": inv.due_date.isoformat() if inv.due_date else None,
        "subtotalExGstCents": inv.subtotal_ex_gst_cents,
        "gstCents": inv.gst_cents,
        "totalIncGstCents": inv.total_inc_gst_cents,
        "amountPaidCents": inv.amount_paid_cents,
        "balanceDueCents": inv.balance_due_cents,
        "approvedBy": _user_ref(inv.approved_by),
        "createdAt": inv.created_at.isoformat(),
    }
    if include_lines:
        data["lines"] = [serialize_supplier_invoice_line(line) for line in inv.lines.all()]
    return data


def serialize_supplier_payment(payment: SupplierPayment) -> dict:
    return {
        "id": str(payment.public_id),
        "paymentNumber": payment.payment_number,
        "supplierId": str(payment.supplier.public_id),
        "paymentDate": payment.payment_date.isoformat(),
        "amountCents": payment.amount_cents,
        "reference": payment.reference,
        "recordedBy": _user_ref(payment.recorded_by),
    }


def serialize_debit_note(dn: DebitNote) -> dict:
    return {
        "id": str(dn.public_id),
        "debitNoteNumber": dn.debit_note_number,
        "supplierId": str(dn.supplier.public_id),
        "invoiceId": str(dn.invoice.public_id) if dn.invoice_id else None,
        "status": dn.status,
        "issueDate": dn.issue_date.isoformat() if dn.issue_date else None,
        "subtotalExGstCents": dn.subtotal_ex_gst_cents,
        "gstCents": dn.gst_cents,
        "totalIncGstCents": dn.total_inc_gst_cents,
        "reason": dn.reason,
    }
