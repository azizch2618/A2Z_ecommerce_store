"""Accounting foundation models — COA, periods, journals, event mappings."""
from django.db import models

from apps.core.models import PublicIdModel
from apps.accounting.constants import (
    AccountType,
    JournalLineSide,
    JournalStatus,
    PeriodStatus,
    TaxTreatment,
)


class ChartOfAccount(PublicIdModel):
    """General ledger account."""

    company = models.ForeignKey(
        "erp.Company",
        on_delete=models.CASCADE,
        related_name="chart_of_accounts",
    )
    code = models.CharField(max_length=20)
    name = models.CharField(max_length=255)
    account_type = models.CharField(max_length=20, choices=AccountType.choices)
    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="children",
    )
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    is_posting = models.BooleanField(default=True)
    tax_treatment = models.CharField(
        max_length=20,
        choices=TaxTreatment.choices,
        default=TaxTreatment.GST_EXCLUSIVE,
    )

    class Meta:
        db_table = "accounting_chart_of_accounts"
        unique_together = [("company", "code")]
        ordering = ["code"]

    def __str__(self) -> str:
        return f"{self.code} — {self.name}"


class FiscalYear(PublicIdModel):
    company = models.ForeignKey(
        "erp.Company",
        on_delete=models.CASCADE,
        related_name="fiscal_years",
    )
    label = models.CharField(max_length=20)
    start_date = models.DateField()
    end_date = models.DateField()
    is_closed = models.BooleanField(default=False)

    class Meta:
        db_table = "accounting_fiscal_years"
        unique_together = [("company", "label")]
        ordering = ["-start_date"]

    def __str__(self) -> str:
        return self.label


class AccountingPeriod(PublicIdModel):
    fiscal_year = models.ForeignKey(
        FiscalYear,
        on_delete=models.CASCADE,
        related_name="periods",
    )
    period_number = models.PositiveSmallIntegerField()
    name = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(
        max_length=10,
        choices=PeriodStatus.choices,
        default=PeriodStatus.OPEN,
    )

    class Meta:
        db_table = "accounting_periods"
        unique_together = [("fiscal_year", "period_number")]
        ordering = ["fiscal_year", "period_number"]

    @property
    def company(self):
        return self.fiscal_year.company

    def __str__(self) -> str:
        return f"{self.fiscal_year.label} / {self.name}"


class JournalEntry(PublicIdModel):
    entry_number = models.CharField(max_length=30, unique=True)
    company = models.ForeignKey(
        "erp.Company",
        on_delete=models.RESTRICT,
        related_name="journal_entries",
    )
    period = models.ForeignKey(
        AccountingPeriod,
        on_delete=models.RESTRICT,
        related_name="journal_entries",
    )
    entry_date = models.DateField()
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=JournalStatus.choices,
        default=JournalStatus.DRAFT,
    )
    source_type = models.CharField(max_length=50, blank=True)
    source_id = models.CharField(max_length=64, blank=True)
    source_event = models.CharField(max_length=50, blank=True)
    department = models.ForeignKey(
        "erp.Department",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="journal_entries",
    )
    cost_center = models.ForeignKey(
        "erp.CostCenter",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="journal_entries",
    )
    posted_at = models.DateTimeField(null=True, blank=True)
    posted_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="posted_journal_entries",
    )
    created_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_journal_entries",
    )

    class Meta:
        db_table = "accounting_journal_entries"
        ordering = ["-entry_date", "-created_at"]
        indexes = [
            models.Index(fields=["source_type", "source_id"], name="idx_je_source"),
            models.Index(fields=["status", "entry_date"], name="idx_je_status_date"),
        ]

    def __str__(self) -> str:
        return self.entry_number


class JournalLine(PublicIdModel):
    journal_entry = models.ForeignKey(
        JournalEntry,
        on_delete=models.CASCADE,
        related_name="lines",
    )
    account = models.ForeignKey(
        ChartOfAccount,
        on_delete=models.RESTRICT,
        related_name="journal_lines",
    )
    side = models.CharField(max_length=10, choices=JournalLineSide.choices)
    amount_cents = models.BigIntegerField()
    gst_cents = models.BigIntegerField(default=0)
    tax_treatment = models.CharField(
        max_length=20,
        choices=TaxTreatment.choices,
        default=TaxTreatment.GST_EXCLUSIVE,
    )
    description = models.CharField(max_length=255, blank=True)
    department = models.ForeignKey(
        "erp.Department",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="journal_lines",
    )
    cost_center = models.ForeignKey(
        "erp.CostCenter",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="journal_lines",
    )

    class Meta:
        db_table = "accounting_journal_lines"
        ordering = ["journal_entry", "id"]

    @property
    def debit_cents(self) -> int:
        return self.amount_cents if self.side == JournalLineSide.DEBIT else 0

    @property
    def credit_cents(self) -> int:
        return self.amount_cents if self.side == JournalLineSide.CREDIT else 0


class AccountingEventMapping(PublicIdModel):
    """Maps domain events to automatic journal entry templates."""

    event_type = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    auto_post = models.BooleanField(default=True)

    class Meta:
        db_table = "accounting_event_mappings"
        ordering = ["event_type"]

    def __str__(self) -> str:
        return self.name


class AccountingEventMappingLine(PublicIdModel):
    mapping = models.ForeignKey(
        AccountingEventMapping,
        on_delete=models.CASCADE,
        related_name="lines",
    )
    account_code = models.CharField(max_length=20)
    side = models.CharField(max_length=10, choices=JournalLineSide.choices)
    amount_source = models.CharField(
        max_length=50,
        help_text="Payload field name, e.g. total_ex_gst_cents",
    )
    description_template = models.CharField(max_length=255, blank=True)
    line_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        db_table = "accounting_event_mapping_lines"
        ordering = ["mapping", "line_order"]


class AccountingAuditLog(PublicIdModel):
    """Immutable accounting-specific audit trail."""

    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="accounting_audit_logs",
    )
    action = models.CharField(max_length=50)
    resource_type = models.CharField(max_length=50)
    resource_id = models.CharField(max_length=64)
    summary = models.TextField()
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "accounting_audit_logs"
        ordering = ["-created_at"]
