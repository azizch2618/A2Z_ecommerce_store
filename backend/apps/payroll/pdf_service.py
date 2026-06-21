"""Professional payslip PDF generation."""
from __future__ import annotations

import io

from django.utils import timezone

from apps.erp.models import Company
from apps.payroll.models import Payslip


def generate_payslip_pdf(payslip: Payslip) -> bytes:
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

    period = payslip.payroll_period
    employee = payslip.employee

    story.append(Paragraph(f"<b>{company_name}</b>", styles["Title"]))
    if company_abn:
        story.append(Paragraph(f"ABN: {company_abn}", styles["Normal"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph(f"<b>PAYSLIP {payslip.payslip_number}</b>", styles["Heading2"]))
    story.append(Paragraph(f"Pay period: {period.name}", styles["Normal"]))
    story.append(
        Paragraph(
            f"{period.period_start.strftime('%d %b %Y')} — {period.period_end.strftime('%d %b %Y')}",
            styles["Normal"],
        )
    )
    story.append(Paragraph(f"Pay date: {period.pay_date.strftime('%d %b %Y')}", styles["Normal"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph(f"<b>Employee:</b> {employee.full_name}", styles["Normal"]))
    story.append(Paragraph(f"Employee #: {employee.employee_number}", styles["Normal"]))
    story.append(Paragraph(f"Job title: {employee.job_title}", styles["Normal"]))
    if employee.department_id:
        story.append(Paragraph(f"Department: {employee.department.name}", styles["Normal"]))
    story.append(Spacer(1, 16))

    line_data = [["Description", "Type", "Amount"]]
    for line in payslip.lines.all():
        sign = "+" if line.amount_cents >= 0 else ""
        line_data.append(
            [
                line.description,
                line.get_line_type_display(),
                f"{sign}${abs(line.amount_cents) / 100:.2f}",
            ]
        )

    if len(line_data) > 1:
        table = Table(line_data, colWidths=[240, 100, 80])
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e40af")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
                    ("ALIGN", (2, 0), (2, -1), "RIGHT"),
                ]
            )
        )
        story.append(table)
    story.append(Spacer(1, 16))

    totals = [
        ["Gross pay", f"${payslip.gross_cents / 100:.2f}"],
        ["Total deductions", f"-${(payslip.total_deductions_cents + payslip.leave_deduction_cents + payslip.payg_withholding_cents) / 100:.2f}"],
        ["Net pay", f"${payslip.net_cents / 100:.2f}"],
    ]
    if payslip.super_cents:
        totals.insert(2, ["Superannuation (employer)", f"${payslip.super_cents / 100:.2f}"])

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
