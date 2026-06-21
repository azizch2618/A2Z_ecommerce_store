"""Payroll models — periods, salary structures, payslips."""
from django.db import models

from apps.core.models import PublicIdModel
from apps.payroll.constants import (
    PayFrequency,
    PayrollPeriodStatus,
    PayslipLineType,
    PayslipStatus,
    SalaryComponentType,
)


class PayrollPeriod(PublicIdModel):
    period_number = models.CharField(max_length=30, unique=True)
    company = models.ForeignKey(
        "erp.Company",
        on_delete=models.RESTRICT,
        related_name="payroll_periods",
    )
    name = models.CharField(max_length=100)
    period_start = models.DateField()
    period_end = models.DateField()
    pay_date = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=PayrollPeriodStatus.choices,
        default=PayrollPeriodStatus.DRAFT,
        db_index=True,
    )
    total_gross_cents = models.BigIntegerField(default=0)
    total_net_cents = models.BigIntegerField(default=0)
    total_deductions_cents = models.BigIntegerField(default=0)
    total_super_cents = models.BigIntegerField(default=0)
    total_payg_cents = models.BigIntegerField(default=0)
    journal_entry = models.ForeignKey(
        "accounting.JournalEntry",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payroll_periods",
    )
    calculated_at = models.DateTimeField(null=True, blank=True)
    calculated_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="calculated_payroll_periods",
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_payroll_periods",
    )
    posted_at = models.DateTimeField(null=True, blank=True)
    posted_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="posted_payroll_periods",
    )
    notes = models.TextField(blank=True)

    class Meta:
        db_table = "payroll_periods"
        ordering = ["-period_start", "-created_at"]
        indexes = [
            models.Index(fields=["status", "period_start"], name="idx_pay_period_status"),
        ]


class SalaryStructure(PublicIdModel):
    employee = models.ForeignKey(
        "hrm.Employee",
        on_delete=models.CASCADE,
        related_name="salary_structures",
    )
    effective_from = models.DateField()
    effective_to = models.DateField(null=True, blank=True)
    pay_frequency = models.CharField(
        max_length=20,
        choices=PayFrequency.choices,
        default=PayFrequency.MONTHLY,
    )
    award_code = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = "payroll_salary_structures"
        ordering = ["-effective_from"]


class SalaryComponent(PublicIdModel):
    structure = models.ForeignKey(
        SalaryStructure,
        on_delete=models.CASCADE,
        related_name="components",
    )
    component_type = models.CharField(max_length=20, choices=SalaryComponentType.choices)
    code = models.CharField(max_length=30)
    name = models.CharField(max_length=100)
    amount_cents = models.BigIntegerField(default=0)
    is_taxable = models.BooleanField(default=True)
    is_superable = models.BooleanField(default=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "payroll_salary_components"
        ordering = ["component_type", "code"]
        unique_together = [("structure", "code")]


class PayrollAdjustment(PublicIdModel):
    payroll_period = models.ForeignKey(
        PayrollPeriod,
        on_delete=models.CASCADE,
        related_name="adjustments",
    )
    employee = models.ForeignKey(
        "hrm.Employee",
        on_delete=models.CASCADE,
        related_name="payroll_adjustments",
    )
    description = models.CharField(max_length=255)
    amount_cents = models.BigIntegerField()
    created_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payroll_adjustments",
    )

    class Meta:
        db_table = "payroll_adjustments"
        ordering = ["-created_at"]


class Payslip(PublicIdModel):
    payslip_number = models.CharField(max_length=30, unique=True)
    payroll_period = models.ForeignKey(
        PayrollPeriod,
        on_delete=models.CASCADE,
        related_name="payslips",
    )
    employee = models.ForeignKey(
        "hrm.Employee",
        on_delete=models.RESTRICT,
        related_name="payslips",
    )
    status = models.CharField(
        max_length=20,
        choices=PayslipStatus.choices,
        default=PayslipStatus.CALCULATED,
    )
    gross_cents = models.BigIntegerField(default=0)
    net_cents = models.BigIntegerField(default=0)
    total_allowances_cents = models.BigIntegerField(default=0)
    total_deductions_cents = models.BigIntegerField(default=0)
    leave_deduction_cents = models.BigIntegerField(default=0)
    overtime_cents = models.BigIntegerField(default=0)
    payg_withholding_cents = models.BigIntegerField(default=0)
    super_cents = models.BigIntegerField(default=0)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "payroll_payslips"
        ordering = ["employee__last_name", "employee__first_name"]
        unique_together = [("payroll_period", "employee")]
        indexes = [
            models.Index(fields=["employee", "-created_at"], name="idx_payslip_employee"),
        ]


class PayslipLine(PublicIdModel):
    payslip = models.ForeignKey(
        Payslip,
        on_delete=models.CASCADE,
        related_name="lines",
    )
    line_type = models.CharField(max_length=20, choices=PayslipLineType.choices)
    code = models.CharField(max_length=30, blank=True)
    description = models.CharField(max_length=255)
    amount_cents = models.BigIntegerField()

    class Meta:
        db_table = "payroll_payslip_lines"
        ordering = ["line_type", "id"]
