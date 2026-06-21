"""Report export — CSV, Excel, PDF."""
from __future__ import annotations

import base64
import csv
import io
from typing import Any

from apps.analytics.reports import REPORT_CATALOG, export_report_csv
from apps.core.audit import log_operation
from apps.core.models import OperationalAuditLog


def export_report(
    *,
    report_id: str,
    export_format: str,
    user,
) -> dict[str, Any]:
    """Return export payload with filename, content (str or base64), mime_type."""
    export_format = export_format.lower()
    if export_format not in {"csv", "excel", "pdf"}:
        raise ValueError(f"Unsupported format: {export_format}")

    if export_format == "csv":
        filename, content = export_report_csv(report_id=report_id, user=user)
        return {
            "filename": filename,
            "content": content,
            "mimeType": "text/csv",
            "encoding": "utf-8",
        }

    filename_csv, csv_content = export_report_csv(report_id=report_id, user=user)
    rows = list(csv.reader(io.StringIO(csv_content)))
    report_name = next((r["name"] for r in REPORT_CATALOG if r["id"] == report_id), report_id)

    if export_format == "excel":
        content_b64 = _to_excel_base64(rows, sheet_name=report_name[:31])
        filename = filename_csv.replace(".csv", ".xlsx")
        mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    else:
        content_b64 = _to_pdf_base64(rows, title=report_name)
        filename = filename_csv.replace(".csv", ".pdf")
        mime = "application/pdf"

    log_operation(
        user=user,
        module=OperationalAuditLog.Module.REPORTS,
        action="export",
        resource_type="report",
        resource_id=report_id,
        details={"format": export_format},
    )

    return {
        "filename": filename,
        "content": content_b64,
        "mimeType": mime,
        "encoding": "base64",
    }


def _to_excel_base64(rows: list[list[str]], *, sheet_name: str) -> str:
    from openpyxl import Workbook

    wb = Workbook()
    ws = wb.active
    ws.title = sheet_name
    for row in rows:
        ws.append(row)
    buffer = io.BytesIO()
    wb.save(buffer)
    return base64.b64encode(buffer.getvalue()).decode("ascii")


def _to_pdf_base64(rows: list[list[str]], *, title: str) -> str:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4))
    styles = getSampleStyleSheet()
    story = [Paragraph(f"<b>{title}</b>", styles["Title"]), Spacer(1, 12)]

    if rows:
        table = Table(rows, repeatRows=1)
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e40af")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                ]
            )
        )
        story.append(table)

    doc.build(story)
    return base64.b64encode(buffer.getvalue()).decode("ascii")
