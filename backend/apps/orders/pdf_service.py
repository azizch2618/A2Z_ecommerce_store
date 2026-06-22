"""Tax invoice PDF generation for sales orders."""
from __future__ import annotations

import io

from django.utils import timezone

from apps.erp.models import Company
from apps.orders.models import Order


def generate_order_invoice_pdf(order: Order) -> bytes:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=20 * mm, leftMargin=20 * mm)
    styles = getSampleStyleSheet()
    story = []

    company = Company.objects.filter(is_default=True).first()
    company_name = company.trading_name if company else "A2Z Tools"
    company_abn = company.abn if company and company.abn else ""
    company_email = company.email if company else "sales@a2ztools.com.au"

    story.append(Paragraph(f"<b>{company_name}</b>", styles["Title"]))
    if company_abn:
        story.append(Paragraph(f"ABN: {company_abn}", styles["Normal"]))
    story.append(Paragraph(company_email, styles["Normal"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph(f"<b>TAX INVOICE {order.order_number}</b>", styles["Heading2"]))
    placed = order.placed_at.strftime("%d %b %Y") if order.placed_at else "—"
    story.append(Paragraph(f"Date: {placed}", styles["Normal"]))
    story.append(Paragraph(f"Status: {order.get_status_display()}", styles["Normal"]))
    story.append(Spacer(1, 12))

    billing = order.billing_address or {}
    bill_to = billing.get("line1", "")
    if billing.get("suburb"):
        bill_to += f", {billing.get('suburb', '')} {billing.get('state', '')} {billing.get('postcode', '')}"
    story.append(Paragraph(f"<b>Bill to:</b> {bill_to or order.guest_email or 'Customer'}", styles["Normal"]))
    story.append(Spacer(1, 12))

    line_data = [["SKU", "Product", "Qty", "Unit (ex GST)", "GST", "Total (inc GST)"]]
    for item in order.items.all():
        line_data.append(
            [
                item.sku,
                item.product_name[:40],
                str(item.quantity),
                f"${item.unit_price_ex_gst_cents / 100:.2f}",
                f"${item.line_gst_cents / 100:.2f}",
                f"${item.line_total_inc_gst_cents / 100:.2f}",
            ]
        )

    if len(line_data) > 1:
        table = Table(line_data, colWidths=[60, 160, 40, 70, 50, 70])
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e40af")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
                ]
            )
        )
        story.append(table)
    story.append(Spacer(1, 16))

    shipping_inc = order.shipping_ex_gst_cents + order.shipping_gst_cents
    totals = [
        ["Subtotal (ex GST)", f"${order.subtotal_ex_gst_cents / 100:.2f}"],
        ["GST", f"${order.gst_total_cents / 100:.2f}"],
        ["Shipping (inc GST)", f"${shipping_inc / 100:.2f}"],
    ]
    if order.discount_cents:
        totals.append(["Discount", f"-${order.discount_cents / 100:.2f}"])
    totals.append(["Total (inc GST)", f"${order.total_inc_gst_cents / 100:.2f}"])

    totals_table = Table(totals, colWidths=[300, 100])
    totals_table.setStyle(
        TableStyle(
            [
                ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
                ("LINEABOVE", (0, -1), (-1, -1), 1, colors.black),
            ]
        )
    )
    story.append(totals_table)
    story.append(Spacer(1, 24))
    story.append(
        Paragraph(
            f"Generated {timezone.now().strftime('%d %b %Y %H:%M')} · {company_name}",
            styles["Normal"],
        )
    )

    doc.build(story)
    return buffer.getvalue()
