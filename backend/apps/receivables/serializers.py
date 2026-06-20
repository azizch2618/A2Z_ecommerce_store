"""Receivables API serializers."""
from __future__ import annotations

from apps.receivables.models import CreditNote, CustomerInvoice, CustomerPayment


def _user_ref(user) -> dict | None:
    if not user:
        return None
    return {"id": str(user.public_id), "email": user.email}


def serialize_invoice_line(line) -> dict:
    return {
        "id": str(line.public_id),
        "description": line.description,
        "quantity": line.quantity,
        "unitPriceExGstCents": line.unit_price_ex_gst_cents,
        "lineExGstCents": line.line_ex_gst_cents,
        "lineGstCents": line.line_gst_cents,
    }


def serialize_customer_invoice(inv: CustomerInvoice, *, include_lines: bool = True) -> dict:
    data = {
        "id": str(inv.public_id),
        "invoiceNumber": inv.invoice_number,
        "customerId": str(inv.customer.public_id),
        "orderId": str(inv.order.public_id) if inv.order_id else None,
        "orderNumber": inv.order.order_number if inv.order_id else None,
        "status": inv.status,
        "issueDate": inv.issue_date.isoformat() if inv.issue_date else None,
        "dueDate": inv.due_date.isoformat() if inv.due_date else None,
        "paymentTermsDays": inv.payment_terms_days,
        "subtotalExGstCents": inv.subtotal_ex_gst_cents,
        "gstCents": inv.gst_cents,
        "totalIncGstCents": inv.total_inc_gst_cents,
        "amountPaidCents": inv.amount_paid_cents,
        "balanceDueCents": inv.balance_due_cents,
        "notes": inv.notes,
        "issuedBy": _user_ref(inv.issued_by),
        "createdAt": inv.created_at.isoformat(),
    }
    if include_lines:
        data["lines"] = [serialize_invoice_line(line) for line in inv.lines.all()]
    return data


def serialize_customer_payment(payment: CustomerPayment) -> dict:
    return {
        "id": str(payment.public_id),
        "paymentNumber": payment.payment_number,
        "customerId": str(payment.customer.public_id),
        "paymentDate": payment.payment_date.isoformat(),
        "amountCents": payment.amount_cents,
        "paymentMethod": payment.payment_method,
        "reference": payment.reference,
        "recordedBy": _user_ref(payment.recorded_by),
    }


def serialize_credit_note(cn: CreditNote) -> dict:
    return {
        "id": str(cn.public_id),
        "creditNoteNumber": cn.credit_note_number,
        "customerId": str(cn.customer.public_id),
        "invoiceId": str(cn.invoice.public_id) if cn.invoice_id else None,
        "status": cn.status,
        "issueDate": cn.issue_date.isoformat() if cn.issue_date else None,
        "subtotalExGstCents": cn.subtotal_ex_gst_cents,
        "gstCents": cn.gst_cents,
        "totalIncGstCents": cn.total_inc_gst_cents,
        "reason": cn.reason,
    }
