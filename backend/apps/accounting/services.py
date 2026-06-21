"""Accounting foundation business logic."""
from __future__ import annotations

import calendar
from datetime import date
from typing import Any
from uuid import UUID

from django.db import transaction
from django.db.models import Q, QuerySet, Sum
from django.utils import timezone

from apps.accounting.audit import AccountingAuditService
from apps.accounting.constants import (
    AccountType,
    JournalLineSide,
    JournalStatus,
    PeriodStatus,
    StandardAccountCode,
)
from apps.accounting.models import (
    AccountingEventMapping,
    AccountingPeriod,
    ChartOfAccount,
    FiscalYear,
    JournalEntry,
    JournalLine,
)
from apps.accounting.tax import TaxEngine
from apps.core.exceptions import BusinessRuleError, ConflictError, NotFoundError
from apps.erp.constants import AuditModule, DocumentType, DomainEventType
from apps.erp.models import Company, CostCenter, Department
from apps.erp.services.document_sequence import DocumentSequenceService


def _default_company() -> Company:
    company = Company.objects.filter(is_default=True, is_active=True).first()
    if not company:
        company = Company.objects.filter(is_active=True).first()
    if not company:
        raise NotFoundError("No active company configured.")
    return company


class ChartOfAccountService:
    @staticmethod
    def list_accounts(*, company: Company | None = None, account_type: str | None = None) -> QuerySet[ChartOfAccount]:
        company = company or _default_company()
        qs = ChartOfAccount.objects.filter(company=company, is_active=True).select_related("parent")
        if account_type:
            qs = qs.filter(account_type=account_type)
        return qs.order_by("code")

    @staticmethod
    def get_account(public_id: UUID) -> ChartOfAccount:
        account = ChartOfAccount.objects.filter(public_id=public_id).select_related("company").first()
        if not account:
            raise NotFoundError("Account not found.")
        return account

    @staticmethod
    def get_by_code(*, company: Company, code: str) -> ChartOfAccount:
        account = ChartOfAccount.objects.filter(company=company, code=code, is_active=True).first()
        if not account:
            raise NotFoundError(f"Account {code} not found.")
        return account

    @classmethod
    @transaction.atomic
    def create(
        cls,
        *,
        company: Company | None,
        code: str,
        name: str,
        account_type: str,
        parent_code: str | None = None,
        actor=None,
    ) -> ChartOfAccount:
        company = company or _default_company()
        parent = None
        if parent_code:
            parent = cls.get_by_code(company=company, code=parent_code)
        account = ChartOfAccount.objects.create(
            company=company,
            code=code,
            name=name,
            account_type=account_type,
            parent=parent,
        )
        AccountingAuditService.log(
            user=actor,
            action="coa_create",
            resource_type="chart_of_account",
            resource_id=str(account.public_id),
            summary=f"Account created: {account.code} {account.name}",
        )
        return account


class FiscalPeriodService:
    @staticmethod
    def list_fiscal_years(*, company: Company | None = None) -> QuerySet[FiscalYear]:
        company = company or _default_company()
        return FiscalYear.objects.filter(company=company).prefetch_related("periods").order_by("-start_date")

    @staticmethod
    def get_open_period(*, company: Company | None = None, as_of: date | None = None) -> AccountingPeriod:
        company = company or _default_company()
        as_of = as_of or timezone.now().date()
        period = (
            AccountingPeriod.objects.filter(
                fiscal_year__company=company,
                status=PeriodStatus.OPEN,
                start_date__lte=as_of,
                end_date__gte=as_of,
            )
            .select_related("fiscal_year")
            .first()
        )
        if not period:
            raise BusinessRuleError(f"No open accounting period for {as_of.isoformat()}.")
        return period

    @classmethod
    @transaction.atomic
    def create_fiscal_year(
        cls,
        *,
        company: Company | None = None,
        year_label: str,
        start_date: date,
        actor=None,
    ) -> FiscalYear:
        company = company or _default_company()
        end_year = start_date.year + 1 if start_date.month > 1 else start_date.year
        end_month = start_date.month - 1 if start_date.month > 1 else 12
        end_day = calendar.monthrange(
            end_year if start_date.month > 1 else start_date.year, end_month
        )[1]
        end_date = date(
            start_date.year if start_date.month == 1 else start_date.year + 1,
            end_month,
            end_day,
        )
        if start_date.month != 1:
            end_date = date(start_date.year + 1, end_month, end_day)

        # AU FY: e.g. start 2025-07-01 end 2026-06-30
        if company.fiscal_year_start_month != 1:
            fy_end_month = company.fiscal_year_start_month - 1
            fy_end_year = start_date.year + 1
            end_day = calendar.monthrange(fy_end_year, fy_end_month)[1]
            end_date = date(fy_end_year, fy_end_month, end_day)

        fy = FiscalYear.objects.create(
            company=company,
            label=year_label,
            start_date=start_date,
            end_date=end_date,
        )
        cls._generate_monthly_periods(fy)
        AccountingAuditService.log(
            user=actor,
            action="fiscal_year_create",
            resource_type="fiscal_year",
            resource_id=str(fy.public_id),
            summary=f"Fiscal year {year_label} created",
        )
        return fy

    @staticmethod
    def _generate_monthly_periods(fy: FiscalYear) -> None:
        current = fy.start_date
        period_num = 1
        while current <= fy.end_date:
            month_end_day = calendar.monthrange(current.year, current.month)[1]
            period_end = date(current.year, current.month, month_end_day)
            if period_end > fy.end_date:
                period_end = fy.end_date
            AccountingPeriod.objects.create(
                fiscal_year=fy,
                period_number=period_num,
                name=current.strftime("%B %Y"),
                start_date=current,
                end_date=period_end,
                status=PeriodStatus.OPEN,
            )
            period_num += 1
            if period_end >= fy.end_date:
                break
            if current.month == 12:
                current = date(current.year + 1, 1, 1)
            else:
                current = date(current.year, current.month + 1, 1)

    @classmethod
    @transaction.atomic
    def close_period(cls, *, period: AccountingPeriod, actor) -> AccountingPeriod:
        if period.status == PeriodStatus.CLOSED:
            raise BusinessRuleError("Period is already closed.")
        period.status = PeriodStatus.CLOSED
        period.save(update_fields=["status", "updated_at"])
        AccountingAuditService.log(
            user=actor,
            action="period_close",
            resource_type="accounting_period",
            resource_id=str(period.public_id),
            summary=f"Period closed: {period.name}",
        )
        return period

    @classmethod
    @transaction.atomic
    def reopen_period(cls, *, period: AccountingPeriod, actor) -> AccountingPeriod:
        if period.status == PeriodStatus.OPEN:
            raise BusinessRuleError("Period is already open.")
        period.status = PeriodStatus.OPEN
        period.save(update_fields=["status", "updated_at"])
        AccountingAuditService.log(
            user=actor,
            action="period_reopen",
            resource_type="accounting_period",
            resource_id=str(period.public_id),
            summary=f"Period reopened: {period.name}",
        )
        return period


class JournalEngine:
    @staticmethod
    def list_entries(*, status: str | None = None, company: Company | None = None) -> QuerySet[JournalEntry]:
        company = company or _default_company()
        qs = JournalEntry.objects.filter(company=company).select_related(
            "period", "department", "cost_center", "posted_by", "created_by"
        ).prefetch_related("lines__account")
        if status:
            qs = qs.filter(status=status)
        return qs.order_by("-entry_date", "-created_at")

    @staticmethod
    def get_entry(public_id: UUID) -> JournalEntry:
        entry = JournalEngine.list_entries().filter(public_id=public_id).first()
        if not entry:
            raise NotFoundError("Journal entry not found.")
        return entry

    @classmethod
    @transaction.atomic
    def create_draft(
        cls,
        *,
        entry_date: date | None = None,
        description: str = "",
        company: Company | None = None,
        period: AccountingPeriod | None = None,
        department: Department | None = None,
        cost_center: CostCenter | None = None,
        source_type: str = "",
        source_id: str = "",
        source_event: str = "",
        actor=None,
    ) -> JournalEntry:
        company = company or _default_company()
        entry_date = entry_date or timezone.now().date()
        period = period or FiscalPeriodService.get_open_period(company=company, as_of=entry_date)
        if period.status != PeriodStatus.OPEN:
            raise BusinessRuleError("Cannot post to a closed period.")

        entry = JournalEntry.objects.create(
            entry_number=DocumentSequenceService.next_number(DocumentType.JOURNAL_ENTRY),
            company=company,
            period=period,
            entry_date=entry_date,
            description=description,
            status=JournalStatus.DRAFT,
            source_type=source_type,
            source_id=source_id,
            source_event=source_event,
            department=department,
            cost_center=cost_center,
            created_by=actor if getattr(actor, "is_authenticated", False) else None,
        )
        AccountingAuditService.log(
            user=actor,
            action="journal_create",
            resource_type="journal_entry",
            resource_id=str(entry.public_id),
            summary=f"Draft journal {entry.entry_number} created",
        )
        return entry

    @classmethod
    @transaction.atomic
    def add_line(
        cls,
        *,
        entry: JournalEntry,
        account: ChartOfAccount,
        side: str,
        amount_cents: int,
        gst_cents: int = 0,
        description: str = "",
        department: Department | None = None,
        cost_center: CostCenter | None = None,
    ) -> JournalLine:
        if entry.status != JournalStatus.DRAFT:
            raise BusinessRuleError("Cannot modify a posted journal entry.")
        if amount_cents <= 0:
            raise BusinessRuleError("Line amount must be positive.")
        if not account.is_posting:
            raise BusinessRuleError(f"Account {account.code} is not a posting account.")

        return JournalLine.objects.create(
            journal_entry=entry,
            account=account,
            side=side,
            amount_cents=amount_cents,
            gst_cents=gst_cents,
            tax_treatment=account.tax_treatment,
            description=description,
            department=department or entry.department,
            cost_center=cost_center or entry.cost_center,
        )

    @staticmethod
    def validate_balanced(entry: JournalEntry) -> tuple[int, int]:
        lines = entry.lines.all()
        debits = sum(line.amount_cents for line in lines if line.side == JournalLineSide.DEBIT)
        credits = sum(line.amount_cents for line in lines if line.side == JournalLineSide.CREDIT)
        return debits, credits

    @classmethod
    @transaction.atomic
    def post(cls, *, entry: JournalEntry, actor) -> JournalEntry:
        if entry.status != JournalStatus.DRAFT:
            raise BusinessRuleError("Only draft entries can be posted.")
        if not entry.lines.exists():
            raise BusinessRuleError("Journal entry must have at least one line.")
        debits, credits = cls.validate_balanced(entry)
        if debits != credits:
            raise ConflictError(
                f"Journal entry is not balanced: debits={debits} credits={credits}"
            )
        if entry.period.status != PeriodStatus.OPEN:
            raise BusinessRuleError("Accounting period is closed.")

        entry.status = JournalStatus.POSTED
        entry.posted_at = timezone.now()
        entry.posted_by = actor if getattr(actor, "is_authenticated", False) else None
        entry.save(update_fields=["status", "posted_at", "posted_by", "updated_at"])

        from apps.erp.services.events import DomainEventPublisher

        DomainEventPublisher.publish(
            event_type=DomainEventType.JOURNAL_POSTED,
            aggregate_type="journal_entry",
            aggregate_id=str(entry.public_id),
            payload={"entry_number": entry.entry_number, "debits": debits, "credits": credits},
            idempotency_key=f"journal.posted:{entry.public_id}",
        )
        AccountingAuditService.log(
            user=actor,
            action="journal_post",
            resource_type="journal_entry",
            resource_id=str(entry.public_id),
            summary=f"Journal {entry.entry_number} posted",
            metadata={"debits": debits, "credits": credits},
        )
        return entry


class AccountingEventProcessor:
    """Creates journal entries from domain event mappings."""

    @classmethod
    @transaction.atomic
    def process_event(cls, *, event_type: str, payload: dict[str, Any], aggregate_id: str, actor=None) -> JournalEntry | None:
        mapping = (
            AccountingEventMapping.objects.filter(event_type=event_type, is_active=True)
            .prefetch_related("lines")
            .first()
        )
        if not mapping:
            return None

        existing = JournalEntry.objects.filter(
            source_event=event_type, source_id=str(aggregate_id)
        ).first()
        if existing:
            return existing

        company = _default_company()
        entry = JournalEngine.create_draft(
            description=mapping.description or mapping.name,
            source_type="domain_event",
            source_id=str(aggregate_id),
            source_event=event_type,
            actor=actor,
        )

        for line_def in mapping.lines.all():
            raw_amount = payload.get(line_def.amount_source, 0)
            try:
                amount = int(raw_amount)
            except (TypeError, ValueError):
                amount = 0
            if amount <= 0:
                continue
            account = ChartOfAccountService.get_by_code(company=company, code=line_def.account_code)
            gst = TaxEngine.gst_from_exclusive(amount) if account.tax_treatment != "gst_free" else 0
            JournalEngine.add_line(
                entry=entry,
                account=account,
                side=line_def.side,
                amount_cents=amount,
                gst_cents=gst if line_def.side == JournalLineSide.CREDIT else 0,
                description=line_def.description_template.format(**payload) if line_def.description_template else "",
            )

        if not entry.lines.exists():
            entry.delete()
            return None

        debits, credits = JournalEngine.validate_balanced(entry)
        if debits != credits:
            # Attempt GST balancing line if mapping expects it
            entry.delete()
            return None

        if mapping.auto_post:
            JournalEngine.post(entry=entry, actor=actor)

        AccountingAuditService.log(
            user=actor,
            action="event_journal",
            resource_type="journal_entry",
            resource_id=str(entry.public_id),
            summary=f"Journal from {event_type}: {entry.entry_number}",
            metadata={"event_type": event_type, "aggregate_id": aggregate_id},
        )
        return entry


class ReportingService:
    @staticmethod
    def trial_balance(*, company: Company | None = None, period_id: UUID | None = None) -> list[dict]:
        company = company or _default_company()
        qs = JournalLine.objects.filter(
            journal_entry__company=company,
            journal_entry__status=JournalStatus.POSTED,
        ).select_related("account")
        if period_id:
            qs = qs.filter(journal_entry__period__public_id=period_id)

        accounts: dict[str, dict] = {}
        for line in qs:
            code = line.account.code
            if code not in accounts:
                accounts[code] = {
                    "accountCode": code,
                    "accountName": line.account.name,
                    "accountType": line.account.account_type,
                    "debitCents": 0,
                    "creditCents": 0,
                }
            if line.side == JournalLineSide.DEBIT:
                accounts[code]["debitCents"] += line.amount_cents
            else:
                accounts[code]["creditCents"] += line.amount_cents

        rows = []
        for row in sorted(accounts.values(), key=lambda r: r["accountCode"]):
            row["balanceCents"] = row["debitCents"] - row["creditCents"]
            rows.append(row)
        return rows

    @staticmethod
    def general_ledger(
        *,
        company: Company | None = None,
        account_code: str | None = None,
    ) -> list[dict]:
        company = company or _default_company()
        qs = JournalLine.objects.filter(
            journal_entry__company=company,
            journal_entry__status=JournalStatus.POSTED,
        ).select_related("account", "journal_entry", "journal_entry__period")
        if account_code:
            qs = qs.filter(account__code=account_code)
        qs = qs.order_by("journal_entry__entry_date", "journal_entry__entry_number")

        running = 0
        rows = []
        for line in qs:
            delta = line.amount_cents if line.side == JournalLineSide.DEBIT else -line.amount_cents
            if line.account.account_type in (AccountType.LIABILITY, AccountType.EQUITY, AccountType.REVENUE):
                delta = -delta if line.side == JournalLineSide.DEBIT else line.amount_cents
            running += delta
            rows.append(
                {
                    "entryNumber": line.journal_entry.entry_number,
                    "entryDate": line.journal_entry.entry_date.isoformat(),
                    "accountCode": line.account.code,
                    "accountName": line.account.name,
                    "description": line.description or line.journal_entry.description,
                    "debitCents": line.debit_cents,
                    "creditCents": line.credit_cents,
                    "runningBalanceCents": running,
                }
            )
        return rows

    @staticmethod
    def gst_summary(*, company: Company | None = None, period_id: UUID | None = None) -> dict:
        company = company or _default_company()
        qs = JournalLine.objects.filter(
            journal_entry__company=company,
            journal_entry__status=JournalStatus.POSTED,
        )
        if period_id:
            qs = qs.filter(journal_entry__period__public_id=period_id)

        output_gst = (
            qs.filter(account__code=StandardAccountCode.GST_PAYABLE, side=JournalLineSide.CREDIT).aggregate(
                total=Sum("amount_cents")
            )["total"]
            or 0
        )
        input_gst = (
            qs.filter(account__code=StandardAccountCode.GST_RECEIVABLE, side=JournalLineSide.DEBIT).aggregate(
                total=Sum("amount_cents")
            )["total"]
            or 0
        )
        sales = (
            qs.filter(account__code=StandardAccountCode.SALES_REVENUE, side=JournalLineSide.CREDIT).aggregate(
                total=Sum("amount_cents")
            )["total"]
            or 0
        )
        return {
            "gstRate": TaxEngine.gst_rate_display(),
            "currencyCode": TaxEngine.currency_code(),
            "salesExGstCents": int(sales),
            "outputGstCents": int(output_gst),
            "inputGstCents": int(input_gst),
            "netGstPayableCents": int(output_gst) - int(input_gst),
        }


class AccountingFoundationSeed:
    """Default COA and event mappings for a company."""

    DEFAULT_COA: tuple[tuple[str, str, str], ...] = (
        (StandardAccountCode.BANK, "Bank Account", AccountType.ASSET),
        (StandardAccountCode.ACCOUNTS_RECEIVABLE, "Accounts Receivable", AccountType.ASSET),
        (StandardAccountCode.INVENTORY, "Inventory", AccountType.ASSET),
        (StandardAccountCode.GST_RECEIVABLE, "GST Receivable (Input Tax Credits)", AccountType.ASSET),
        (StandardAccountCode.ACCOUNTS_PAYABLE, "Accounts Payable", AccountType.LIABILITY),
        (StandardAccountCode.GRN_ACCRUAL, "GRN Accrual", AccountType.LIABILITY),
        (StandardAccountCode.GST_PAYABLE, "GST Payable", AccountType.LIABILITY),
        (StandardAccountCode.TRADE_CREDIT_RESERVE, "Trade Credit Reserve", AccountType.LIABILITY),
        (StandardAccountCode.WAGES_PAYABLE, "Wages Payable", AccountType.LIABILITY),
        (StandardAccountCode.PAYG_WITHHOLDING, "PAYG Withholding Payable", AccountType.LIABILITY),
        (StandardAccountCode.SUPER_PAYABLE, "Superannuation Payable", AccountType.LIABILITY),
        (StandardAccountCode.RETAINED_EARNINGS, "Retained Earnings", AccountType.EQUITY),
        (StandardAccountCode.SALES_REVENUE, "Sales Revenue", AccountType.REVENUE),
        (StandardAccountCode.COGS, "Cost of Goods Sold", AccountType.EXPENSE),
        (StandardAccountCode.INVENTORY_ADJUSTMENT, "Inventory Adjustments", AccountType.EXPENSE),
        (StandardAccountCode.WAGES_EXPENSE, "Wages & Salaries Expense", AccountType.EXPENSE),
    )

    @classmethod
    @transaction.atomic
    def seed_company(cls, *, company: Company | None = None) -> None:
        company = company or _default_company()
        for code, name, acct_type in cls.DEFAULT_COA:
            ChartOfAccount.objects.get_or_create(
                company=company,
                code=code,
                defaults={"name": name, "account_type": acct_type, "is_posting": True},
            )

    @classmethod
    @transaction.atomic
    def seed_event_mappings(cls) -> None:
        from apps.accounting.models import AccountingEventMappingLine

        mappings = [
            {
                "event_type": DomainEventType.ORDER_PAID,
                "name": "Order Paid",
                "description": "Revenue recognition on order payment",
                "lines": [
                    (StandardAccountCode.BANK, JournalLineSide.DEBIT, "total_inc_gst_cents", "Cash receipt {order_number}"),
                    (StandardAccountCode.SALES_REVENUE, JournalLineSide.CREDIT, "total_ex_gst_cents", "Sales {order_number}"),
                    (StandardAccountCode.GST_PAYABLE, JournalLineSide.CREDIT, "gst_cents", "GST on {order_number}"),
                ],
            },
            {
                "event_type": DomainEventType.GOODS_RECEIVED,
                "name": "Goods Received",
                "description": "Inventory accrual on goods receipt",
                "lines": [
                    (StandardAccountCode.INVENTORY, JournalLineSide.DEBIT, "total_ex_gst_cents", "GRN {grn_number}"),
                    (StandardAccountCode.GRN_ACCRUAL, JournalLineSide.CREDIT, "total_ex_gst_cents", "GRN accrual {grn_number}"),
                ],
            },
            {
                "event_type": DomainEventType.INVENTORY_ADJUSTED,
                "name": "Inventory Adjustment",
                "description": "Inventory adjustment posting",
                "lines": [
                    (StandardAccountCode.INVENTORY_ADJUSTMENT, JournalLineSide.DEBIT, "adjustment_ex_gst_cents", "Adjustment {adjustment_number}"),
                    (StandardAccountCode.INVENTORY, JournalLineSide.CREDIT, "adjustment_ex_gst_cents", "Inventory adj {adjustment_number}"),
                ],
            },
            {
                "event_type": DomainEventType.TRADE_APPROVED,
                "name": "Trade Credit Approved",
                "description": "Trade credit limit established (memo)",
                "auto_post": False,
                "lines": [],
            },
            {
                "event_type": DomainEventType.AR_INVOICE_ISSUED,
                "name": "AR Invoice Issued",
                "description": "Recognise revenue on customer invoice",
                "lines": [
                    (StandardAccountCode.ACCOUNTS_RECEIVABLE, JournalLineSide.DEBIT, "total_inc_gst_cents", "AR {invoice_number}"),
                    (StandardAccountCode.SALES_REVENUE, JournalLineSide.CREDIT, "total_ex_gst_cents", "Sales {invoice_number}"),
                    (StandardAccountCode.GST_PAYABLE, JournalLineSide.CREDIT, "gst_cents", "GST {invoice_number}"),
                ],
            },
            {
                "event_type": DomainEventType.AR_PAYMENT_RECEIVED,
                "name": "AR Payment Received",
                "description": "Customer payment against AR",
                "lines": [
                    (StandardAccountCode.BANK, JournalLineSide.DEBIT, "amount_cents", "Receipt {payment_number}"),
                    (StandardAccountCode.ACCOUNTS_RECEIVABLE, JournalLineSide.CREDIT, "amount_cents", "Payment {payment_number}"),
                ],
            },
            {
                "event_type": DomainEventType.AR_CREDIT_NOTE_ISSUED,
                "name": "AR Credit Note",
                "description": "Reverse revenue and reduce AR",
                "lines": [
                    (StandardAccountCode.SALES_REVENUE, JournalLineSide.DEBIT, "total_ex_gst_cents", "CN {credit_note_number}"),
                    (StandardAccountCode.GST_PAYABLE, JournalLineSide.DEBIT, "gst_cents", "GST CN {credit_note_number}"),
                    (StandardAccountCode.ACCOUNTS_RECEIVABLE, JournalLineSide.CREDIT, "total_inc_gst_cents", "CN {credit_note_number}"),
                ],
            },
            {
                "event_type": DomainEventType.AP_INVOICE_APPROVED,
                "name": "AP Invoice Approved",
                "description": "Clear GRN accrual and recognise AP liability",
                "lines": [
                    (StandardAccountCode.GRN_ACCRUAL, JournalLineSide.DEBIT, "total_ex_gst_cents", "Clear accrual {invoice_number}"),
                    (StandardAccountCode.GST_RECEIVABLE, JournalLineSide.DEBIT, "gst_cents", "Input GST {invoice_number}"),
                    (StandardAccountCode.ACCOUNTS_PAYABLE, JournalLineSide.CREDIT, "total_inc_gst_cents", "AP {invoice_number}"),
                ],
            },
            {
                "event_type": DomainEventType.AP_PAYMENT_MADE,
                "name": "AP Payment Made",
                "description": "Pay supplier invoice",
                "lines": [
                    (StandardAccountCode.ACCOUNTS_PAYABLE, JournalLineSide.DEBIT, "amount_cents", "Pay {payment_number}"),
                    (StandardAccountCode.BANK, JournalLineSide.CREDIT, "amount_cents", "Payment {payment_number}"),
                ],
            },
            {
                "event_type": DomainEventType.AP_DEBIT_NOTE_ISSUED,
                "name": "AP Debit Note",
                "description": "Reduce supplier liability",
                "lines": [
                    (StandardAccountCode.ACCOUNTS_PAYABLE, JournalLineSide.DEBIT, "total_inc_gst_cents", "DN {debit_note_number}"),
                    (StandardAccountCode.GRN_ACCRUAL, JournalLineSide.CREDIT, "total_ex_gst_cents", "DN {debit_note_number}"),
                    (StandardAccountCode.GST_RECEIVABLE, JournalLineSide.CREDIT, "gst_cents", "GST DN {debit_note_number}"),
                ],
            },
            {
                "event_type": DomainEventType.PAYROLL_RUN_POSTED,
                "name": "Payroll Run Posted",
                "description": "Accrue wages expense and payroll liabilities",
                "lines": [
                    (StandardAccountCode.WAGES_EXPENSE, JournalLineSide.DEBIT, "wages_expense_cents", "Payroll {period_number}"),
                    (StandardAccountCode.WAGES_PAYABLE, JournalLineSide.CREDIT, "net_pay_cents", "Net pay {period_number}"),
                    (StandardAccountCode.PAYG_WITHHOLDING, JournalLineSide.CREDIT, "payg_cents", "PAYG {period_number}"),
                    (StandardAccountCode.SUPER_PAYABLE, JournalLineSide.CREDIT, "super_cents", "Super {period_number}"),
                ],
            },
        ]

        for spec in mappings:
            mapping, _ = AccountingEventMapping.objects.update_or_create(
                event_type=spec["event_type"],
                defaults={
                    "name": spec["name"],
                    "description": spec["description"],
                    "is_active": True,
                    "auto_post": spec.get("auto_post", True),
                },
            )
            AccountingEventMappingLine.objects.filter(mapping=mapping).delete()
            for idx, (code, side, source, desc) in enumerate(spec.get("lines", [])):
                AccountingEventMappingLine.objects.create(
                    mapping=mapping,
                    account_code=code,
                    side=side,
                    amount_source=source,
                    description_template=desc,
                    line_order=idx,
                )
