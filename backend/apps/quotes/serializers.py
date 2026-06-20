"""Quote API serializers — camelCase output."""
from __future__ import annotations

from apps.trade_accounts.models import Quote, QuoteLine


def _user_ref(user) -> dict | None:
    if not user:
        return None
    return {"id": str(user.public_id), "email": user.email}


def serialize_line(line: QuoteLine) -> dict:
    return {
        "id": str(line.public_id),
        "variantId": str(line.variant.public_id),
        "sku": line.sku,
        "productName": line.product_name,
        "quantity": line.quantity,
        "unitPriceExGstCents": line.unit_price_ex_gst_cents,
        "discountCents": line.discount_cents,
        "lineGstCents": line.line_gst_cents,
        "lineSubtotalExGstCents": line.line_subtotal_ex_gst_cents,
        "lineTotalIncGstCents": line.line_total_inc_gst_cents,
    }


def serialize_quote(quote: Quote, *, include_lines: bool = True) -> dict:
    data = {
        "id": str(quote.public_id),
        "quoteNumber": quote.quote_number,
        "status": quote.status,
        "validUntil": quote.valid_until.isoformat() if quote.valid_until else None,
        "subtotalExGstCents": quote.subtotal_ex_gst_cents,
        "gstTotalCents": quote.gst_total_cents,
        "discountCents": quote.discount_cents,
        "totalIncGstCents": quote.total_inc_gst_cents,
        "currencyCode": quote.currency_code,
        "notes": quote.notes,
        "termsAndConditions": quote.terms_and_conditions,
        "partyId": str(quote.party.public_id) if quote.party else None,
        "partyName": quote.party.display_name if quote.party else None,
        "customerId": str(quote.customer.public_id) if quote.customer else None,
        "tradeAccountId": str(quote.trade_account.public_id) if quote.trade_account else None,
        "opportunityId": str(quote.crm_opportunity.public_id) if quote.crm_opportunity else None,
        "createdBy": _user_ref(quote.created_by),
        "sentAt": quote.sent_at.isoformat() if quote.sent_at else None,
        "acceptedAt": quote.accepted_at.isoformat() if quote.accepted_at else None,
        "convertedOrderId": str(quote.converted_order.public_id) if quote.converted_order else None,
        "convertedOrderNumber": quote.converted_order.order_number if quote.converted_order else None,
        "createdAt": quote.created_at.isoformat(),
        "updatedAt": quote.updated_at.isoformat(),
    }
    if include_lines:
        data["lines"] = [serialize_line(line) for line in quote.lines.all()]
    return data
