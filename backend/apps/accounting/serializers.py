"""Accounting API serializers — camelCase output."""
from __future__ import annotations

from apps.accounting.models import (
    AccountingAuditLog,
    AccountingEventMapping,
    AccountingPeriod,
    ChartOfAccount,
    FiscalYear,
    JournalEntry,
    JournalLine,
)


def _user_ref(user) -> dict | None:
    if not user:
        return None
    return {"id": str(user.public_id), "email": user.email}


def serialize_account(account: ChartOfAccount) -> dict:
    return {
        "id": str(account.public_id),
        "code": account.code,
        "name": account.name,
        "accountType": account.account_type,
        "parentCode": account.parent.code if account.parent else None,
        "description": account.description,
        "isActive": account.is_active,
        "isPosting": account.is_posting,
        "taxTreatment": account.tax_treatment,
    }


def serialize_period(period: AccountingPeriod) -> dict:
    return {
        "id": str(period.public_id),
        "fiscalYearLabel": period.fiscal_year.label,
        "periodNumber": period.period_number,
        "name": period.name,
        "startDate": period.start_date.isoformat(),
        "endDate": period.end_date.isoformat(),
        "status": period.status,
    }


def serialize_fiscal_year(fy: FiscalYear, *, include_periods: bool = True) -> dict:
    data = {
        "id": str(fy.public_id),
        "label": fy.label,
        "startDate": fy.start_date.isoformat(),
        "endDate": fy.end_date.isoformat(),
        "isClosed": fy.is_closed,
    }
    if include_periods:
        data["periods"] = [serialize_period(p) for p in fy.periods.all()]
    return data


def serialize_journal_line(line: JournalLine) -> dict:
    return {
        "id": str(line.public_id),
        "accountCode": line.account.code,
        "accountName": line.account.name,
        "side": line.side,
        "amountCents": line.amount_cents,
        "gstCents": line.gst_cents,
        "taxTreatment": line.tax_treatment,
        "description": line.description,
        "departmentId": str(line.department.public_id) if line.department else None,
        "costCenterId": str(line.cost_center.public_id) if line.cost_center else None,
        "debitCents": line.debit_cents,
        "creditCents": line.credit_cents,
    }


def serialize_journal_entry(entry: JournalEntry, *, include_lines: bool = True) -> dict:
    debits = sum(line.debit_cents for line in entry.lines.all())
    credits = sum(line.credit_cents for line in entry.lines.all())
    data = {
        "id": str(entry.public_id),
        "entryNumber": entry.entry_number,
        "entryDate": entry.entry_date.isoformat(),
        "description": entry.description,
        "status": entry.status,
        "sourceType": entry.source_type,
        "sourceId": entry.source_id,
        "sourceEvent": entry.source_event,
        "periodId": str(entry.period.public_id),
        "periodName": entry.period.name,
        "departmentId": str(entry.department.public_id) if entry.department else None,
        "costCenterId": str(entry.cost_center.public_id) if entry.cost_center else None,
        "postedAt": entry.posted_at.isoformat() if entry.posted_at else None,
        "postedBy": _user_ref(entry.posted_by),
        "createdBy": _user_ref(entry.created_by),
        "totalDebitsCents": debits,
        "totalCreditsCents": credits,
        "isBalanced": debits == credits,
        "createdAt": entry.created_at.isoformat(),
    }
    if include_lines:
        data["lines"] = [serialize_journal_line(line) for line in entry.lines.all()]
    return data


def serialize_event_mapping(mapping: AccountingEventMapping) -> dict:
    return {
        "id": str(mapping.public_id),
        "eventType": mapping.event_type,
        "name": mapping.name,
        "description": mapping.description,
        "isActive": mapping.is_active,
        "autoPost": mapping.auto_post,
        "lines": [
            {
                "accountCode": line.account_code,
                "side": line.side,
                "amountSource": line.amount_source,
                "descriptionTemplate": line.description_template,
                "lineOrder": line.line_order,
            }
            for line in mapping.lines.all()
        ],
    }


def serialize_audit_log(log: AccountingAuditLog) -> dict:
    return {
        "id": str(log.public_id),
        "action": log.action,
        "resourceType": log.resource_type,
        "resourceId": log.resource_id,
        "summary": log.summary,
        "metadata": log.metadata,
        "user": _user_ref(log.user),
        "createdAt": log.created_at.isoformat(),
    }
