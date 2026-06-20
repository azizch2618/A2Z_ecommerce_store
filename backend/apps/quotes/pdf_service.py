"""Professional quote PDF generation."""
from __future__ import annotations

import io
from datetime import datetime

from django.utils import timezone

from apps.erp.models import Company
from apps.trade_accounts.models import Quote


def generate_quote_pdf(quote: Quote) -> bytes:
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

    story.append(Paragraph(f"<b>QUOTATION {quote.quote_number}</b>", styles["Heading2"]))
    story.append(Paragraph(f"Status: {quote.get_status_display()}", styles["Normal"]))
    valid = quote.valid_until.strftime("%d %b %Y") if quote.valid_until else "—"
    story.append(Paragraph(f"Valid until: {valid}", styles["Normal"]))
    story.append(Spacer(1, 12))

    party_name = quote.party.display_name if quote.party else "Customer"
    story.append(Paragraph(f"<b>Prepared for:</b> {party_name}", styles["Normal"]))
    story.append(Spacer(1, 12))

    line_data = [["SKU", "Product", "Qty", "Unit (ex GST)", "GST", "Total (inc GST)"]]
    for line in quote.lines.all():
        line_data.append(
            [
                line.sku,
                line.product_name[:40],
                str(line.quantity),
                f"${line.unit_price_ex_gst_cents / 100:.2f}",
                f"${line.line_gst_cents / 100:.2f}",
                f"${line.line_total_inc_gst_cents / 100:.2f}",
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

    totals = [
        ["Subtotal (ex GST)", f"${quote.subtotal_ex_gst_cents / 100:.2f}"],
        ["GST", f"${quote.gst_total_cents / 100:.2f}"],
    ]
    if quote.discount_cents:
        totals.append(["Discount", f"-${quote.discount_cents / 100:.2f}"])
    totals.append(["Total (inc GST)", f"${quote.total_inc_gst_cents / 100:.2f}"])

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
    story.append(Spacer(1, 20))

    terms = quote.terms_and_conditions or ""
    story.append(Paragraph("<b>Terms & Conditions</b>", styles["Heading3"]))
    for para in terms.split("\n"):
        if para.strip():
            story.append(Paragraph(para.strip(), styles["Normal"]))

    if quote.notes:
        story.append(Spacer(1, 12))
        story.append(Paragraph("<b>Notes</b>", styles["Heading3"]))
        story.append(Paragraph(quote.notes, styles["Normal"]))

    story.append(Spacer(1, 24))
    story.append(
        Paragraph(
            f"Generated {timezone.now().strftime('%d %b %Y %H:%M')} · {company_name}",
            styles["Normal"],
        )
    )

    doc.build(story)
    return buffer.getvalue()
