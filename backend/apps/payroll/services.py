"""Payroll business logic."""
from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal
from typing import Any
from uuid import UUID

from django.db import transaction
from django.db.models import Count, Q, QuerySet, Sum
from django.utils import timezone

from apps.core.exceptions import BusinessRuleError, NotFoundError
from apps.erp.constants import DocumentType, DomainEventType, WorkflowCode
from apps.erp.models import Company
from apps.erp.services.document_sequence import DocumentSequenceService
from apps.erp.services.events import DomainEventPublisher
from apps.erp.services.notifications import NotificationService
from apps.erp.services.workflow import WorkflowEngine
from apps.hrm.constants import EmployeeStatus, LeaveRequestStatus, LeaveType
from apps.hrm.models import Employee, LeaveRequest
from apps.payroll.audit import PayrollAuditService
from apps.payroll.constants import (
    PayFrequency,
    PayrollPeriodStatus,
    PayslipLineType,
    PayslipStatus,
    SalaryComponentType,
)
from apps.payroll.models import (
    PayrollAdjustment,
    PayrollPeriod,
    Payslip,
    PayslipLine,
    SalaryComponent,
    SalaryStructure,
)

# Standard working days per month for pro-rata leave deductions
_WORKING_DAYS_PER_MONTH = Decimal("22")


def _default_company() -> Company:
    company = Company.objects.filter(is_default=True, is_active=True).first()
    if not company:
        company = Company.objects.filter(is_active=True).first()
    if not company:
        raise NotFoundError("No active company configured.")
    return company


def _next_period_number() -> str:
    return DocumentSequenceService.next_number(DocumentType.PAYROLL_RUN)


def _next_payslip_number() -> str:
    return DocumentSequenceService.next_number(DocumentType.PAYSLIP)


def _period_days(period: PayrollPeriod) -> int:
    return (period.period_end - period.period_start).days + 1


def _unpaid_leave_days(*, employee: Employee, period_start: date, period_end: date) -> Decimal:
    requests = LeaveRequest.objects.filter(
        employee=employee,
        leave_type=LeaveType.UNPAID,
        status=LeaveRequestStatus.APPROVED,
        start_date__lte=period_end,
        end_date__gte=period_start,
    )
    total = Decimal("0")
    for req in requests:
        overlap_start = max(req.start_date, period_start)
        overlap_end = min(req.end_date, period_end)
        if overlap_end >= overlap_start:
            total += Decimal(str((overlap_end - overlap_start).days + 1))
    return total


def _active_structure(*, employee: Employee, as_of: date) -> SalaryStructure | None:
    return (
        SalaryStructure.objects.filter(
            employee=employee,
            is_active=True,
            effective_from__lte=as_of,
        )
        .filter(Q(effective_to__isnull=True) | Q(effective_to__gte=as_of))
        .prefetch_related("components")
        .order_by("-effective_from")
        .first()
    )


class SalaryStructureService:
    @staticmethod
    def list_for_employee(*, employee: Employee) -> QuerySet[SalaryStructure]:
        return SalaryStructure.objects.filter(employee=employee).prefetch_related("components")

    @staticmethod
    def get_structure(public_id: UUID) -> SalaryStructure:
        structure = (
            SalaryStructure.objects.filter(public_id=public_id)
            .select_related("employee")
            .prefetch_related("components")
            .first()
        )
        if not structure:
            raise NotFoundError("Salary structure not found.")
        return structure

    @classmethod
    @transaction.atomic
    def create(
        cls,
        *,
        employee: Employee,
        actor,
        effective_from: date,
        pay_frequency: str = PayFrequency.MONTHLY,
        award_code: str = "",
        components: list[dict[str, Any]] | None = None,
        notes: str = "",
    ) -> SalaryStructure:
        structure = SalaryStructure.objects.create(
            employee=employee,
            effective_from=effective_from,
            pay_frequency=pay_frequency,
            award_code=award_code,
            notes=notes,
        )
        for comp in components or []:
            SalaryComponent.objects.create(
                structure=structure,
                component_type=comp.get("component_type", comp.get("componentType", SalaryComponentType.BASE)),
                code=comp["code"],
                name=comp["name"],
                amount_cents=int(comp.get("amount_cents", comp.get("amountCents", 0))),
                is_taxable=comp.get("is_taxable", comp.get("isTaxable", True)),
                is_superable=comp.get("is_superable", comp.get("isSuperable", True)),
                metadata=comp.get("metadata", {}),
            )
        PayrollAuditService.log(
            user=actor,
            action="salary_structure_create",
            resource_type="salary_structure",
            resource_id=str(structure.public_id),
            summary=f"Salary structure for {employee.full_name}",
        )
        return structure


class PayrollPeriodService:
    @staticmethod
    def list_periods(*, status: str | None = None) -> QuerySet[PayrollPeriod]:
        qs = PayrollPeriod.objects.select_related("company")
        if status:
            qs = qs.filter(status=status)
        return qs.order_by("-period_start")

    @staticmethod
    def get_period(public_id: UUID) -> PayrollPeriod:
        period = PayrollPeriod.objects.filter(public_id=public_id).select_related("company").first()
        if not period:
            raise NotFoundError("Payroll period not found.")
        return period

    @classmethod
    @transaction.atomic
    def create(
        cls,
        *,
        actor,
        name: str,
        period_start: date,
        period_end: date,
        pay_date: date,
        notes: str = "",
    ) -> PayrollPeriod:
        if period_end < period_start:
            raise BusinessRuleError("Period end must be on or after period start.")
        period = PayrollPeriod.objects.create(
            period_number=_next_period_number(),
            company=_default_company(),
            name=name,
            period_start=period_start,
            period_end=period_end,
            pay_date=pay_date,
            notes=notes,
        )
        PayrollAuditService.log(
            user=actor,
            action="period_create",
            resource_type="payroll_period",
            resource_id=str(period.public_id),
            summary=f"Payroll period {period.period_number} created",
        )
        return period

    @classmethod
    @transaction.atomic
    def add_adjustment(
        cls,
        *,
        period: PayrollPeriod,
        employee: Employee,
        actor,
        description: str,
        amount_cents: int,
    ) -> PayrollAdjustment:
        if period.status not in (PayrollPeriodStatus.DRAFT, PayrollPeriodStatus.CALCULATED):
            raise BusinessRuleError("Adjustments only allowed on draft or calculated periods.")
        adj = PayrollAdjustment.objects.create(
            payroll_period=period,
            employee=employee,
            description=description,
            amount_cents=amount_cents,
            created_by=actor if getattr(actor, "is_authenticated", False) else None,
        )
        PayrollAuditService.log(
            user=actor,
            action="adjustment_add",
            resource_type="payroll_adjustment",
            resource_id=str(adj.public_id),
            summary=f"Adjustment {description} for {employee.full_name}",
        )
        return adj

    @classmethod
    @transaction.atomic
    def calculate(cls, *, period: PayrollPeriod, actor) -> PayrollPeriod:
        if period.status not in (PayrollPeriodStatus.DRAFT, PayrollPeriodStatus.CALCULATED):
            raise BusinessRuleError("Only draft or calculated periods can be recalculated.")

        PayslipLine.objects.filter(payslip__payroll_period=period).delete()
        Payslip.objects.filter(payroll_period=period).delete()

        employees = Employee.objects.filter(
            company=period.company,
            status=EmployeeStatus.ACTIVE,
        ).select_related("department", "cost_center")

        total_gross = 0
        total_net = 0
        total_deductions = 0
        total_super = 0
        total_payg = 0

        for emp in employees:
            structure = _active_structure(employee=emp, as_of=period.period_end)
            if not structure:
                continue

            payslip = cls._build_payslip(period=period, employee=emp, structure=structure, actor=actor)
            total_gross += payslip.gross_cents
            total_net += payslip.net_cents
            total_deductions += payslip.total_deductions_cents + payslip.leave_deduction_cents
            total_super += payslip.super_cents
            total_payg += payslip.payg_withholding_cents

        period.total_gross_cents = total_gross
        period.total_net_cents = total_net
        period.total_deductions_cents = total_deductions
        period.total_super_cents = total_super
        period.total_payg_cents = total_payg
        period.status = PayrollPeriodStatus.CALCULATED
        period.calculated_at = timezone.now()
        period.calculated_by = actor if getattr(actor, "is_authenticated", False) else None
        period.save()

        WorkflowEngine.start(
            definition_code=WorkflowCode.PAYROLL_RUN_APPROVAL,
            resource_type="payroll_period",
            resource_id=str(period.public_id),
            actor=actor,
        )

        PayrollAuditService.log(
            user=actor,
            action="period_calculate",
            resource_type="payroll_period",
            resource_id=str(period.public_id),
            summary=f"Payroll {period.period_number} calculated — {Payslip.objects.filter(payroll_period=period).count()} payslips",
        )
        return period

    @classmethod
    def _build_payslip(
        cls,
        *,
        period: PayrollPeriod,
        employee: Employee,
        structure: SalaryStructure,
        actor,
    ) -> Payslip:
        lines: list[tuple[str, str, str, int]] = []
        base_cents = 0
        allowance_cents = 0
        deduction_cents = 0
        super_cents = 0
        payg_cents = 0
        overtime_cents = 0

        for comp in structure.components.all():
            amt = int(comp.amount_cents)
            if comp.component_type == SalaryComponentType.BASE:
                base_cents += amt
                lines.append((PayslipLineType.EARNING, comp.code, comp.name, amt))
            elif comp.component_type == SalaryComponentType.ALLOWANCE:
                allowance_cents += amt
                lines.append((PayslipLineType.ALLOWANCE, comp.code, comp.name, amt))
            elif comp.component_type == SalaryComponentType.DEDUCTION:
                deduction_cents += amt
                lines.append((PayslipLineType.DEDUCTION, comp.code, comp.name, -amt))
            elif comp.component_type == SalaryComponentType.SUPER:
                super_cents += amt
                lines.append((PayslipLineType.SUPER, comp.code, comp.name, amt))
            elif comp.component_type == SalaryComponentType.PAYG:
                payg_cents += amt
                lines.append((PayslipLineType.PAYG, comp.code, comp.name, -amt))
            elif comp.component_type == SalaryComponentType.OVERTIME:
                overtime_cents += amt
                lines.append((PayslipLineType.OVERTIME, comp.code, comp.name, amt))

        unpaid_days = _unpaid_leave_days(
            employee=employee,
            period_start=period.period_start,
            period_end=period.period_end,
        )
        leave_deduction = 0
        if unpaid_days > 0 and base_cents > 0:
            daily_rate = Decimal(base_cents) / _WORKING_DAYS_PER_MONTH
            leave_deduction = int(daily_rate * unpaid_days)
            lines.append(
                (
                    PayslipLineType.LEAVE,
                    "UNPAID_LEAVE",
                    f"Unpaid leave ({unpaid_days} days)",
                    -leave_deduction,
                )
            )

        for adj in PayrollAdjustment.objects.filter(payroll_period=period, employee=employee):
            lines.append(
                (PayslipLineType.ADJUSTMENT, "ADJ", adj.description, int(adj.amount_cents))
            )

        adjustment_total = sum(
            int(a.amount_cents)
            for a in PayrollAdjustment.objects.filter(payroll_period=period, employee=employee)
        )

        gross = base_cents + allowance_cents + overtime_cents + max(adjustment_total, 0)
        total_ded = deduction_cents + leave_deduction + payg_cents + abs(min(adjustment_total, 0))
        net = gross - total_ded

        payslip = Payslip.objects.create(
            payslip_number=_next_payslip_number(),
            payroll_period=period,
            employee=employee,
            gross_cents=gross,
            net_cents=net,
            total_allowances_cents=allowance_cents,
            total_deductions_cents=deduction_cents,
            leave_deduction_cents=leave_deduction,
            overtime_cents=overtime_cents,
            payg_withholding_cents=payg_cents,
            super_cents=super_cents,
            status=PayslipStatus.CALCULATED,
            metadata={"awardCode": structure.award_code, "payFrequency": structure.pay_frequency},
        )

        for line_type, code, desc, amount in lines:
            PayslipLine.objects.create(
                payslip=payslip,
                line_type=line_type,
                code=code,
                description=desc,
                amount_cents=amount,
            )

        if employee.user_id:
            NotificationService.send_from_template(
                recipient=employee.user,
                template_code="payslip_available",
                context={
                    "payslip_number": payslip.payslip_number,
                    "period_name": period.name,
                    "net_pay": f"${net / 100:.2f}",
                },
                resource_type="payslip",
                resource_id=str(payslip.public_id),
            )

        return payslip

    @classmethod
    @transaction.atomic
    def approve(cls, *, period: PayrollPeriod, actor, comment: str = "") -> PayrollPeriod:
        if period.status != PayrollPeriodStatus.CALCULATED:
            raise BusinessRuleError("Only calculated periods can be approved.")
        instance = WorkflowEngine.get_for_resource(
            resource_type="payroll_period", resource_id=str(period.public_id)
        )
        if instance:
            WorkflowEngine.transition(
                instance=instance, action="approve", actor=actor, comment=comment
            )
        period.status = PayrollPeriodStatus.APPROVED
        period.approved_at = timezone.now()
        period.approved_by = actor if getattr(actor, "is_authenticated", False) else None
        period.save()

        Payslip.objects.filter(payroll_period=period).update(status=PayslipStatus.FINALIZED)

        PayrollAuditService.log(
            user=actor,
            action="period_approve",
            resource_type="payroll_period",
            resource_id=str(period.public_id),
            summary=f"Payroll {period.period_number} approved",
        )
        return period

    @classmethod
    @transaction.atomic
    def post(cls, *, period: PayrollPeriod, actor) -> PayrollPeriod:
        if period.status != PayrollPeriodStatus.APPROVED:
            raise BusinessRuleError("Only approved periods can be posted.")
        if period.journal_entry_id:
            raise BusinessRuleError("Payroll period already posted.")

        wages_expense = period.total_gross_cents + period.total_super_cents
        payload = {
            "period_number": period.period_number,
            "wages_expense_cents": wages_expense,
            "net_pay_cents": period.total_net_cents,
            "payg_cents": period.total_payg_cents,
            "super_cents": period.total_super_cents,
        }

        DomainEventPublisher.publish(
            event_type=DomainEventType.PAYROLL_RUN_POSTED,
            aggregate_type="payroll_period",
            aggregate_id=str(period.public_id),
            payload=payload,
            idempotency_key=f"payroll.posted:{period.public_id}",
        )

        period.status = PayrollPeriodStatus.POSTED
        period.posted_at = timezone.now()
        period.posted_by = actor if getattr(actor, "is_authenticated", False) else None
        period.save()

        NotificationService.send_from_template(
            recipient=actor,
            template_code="payroll_processed",
            context={
                "period_number": period.period_number,
                "period_name": period.name,
                "total_net": f"${period.total_net_cents / 100:.2f}",
            },
            resource_type="payroll_period",
            resource_id=str(period.public_id),
        )

        PayrollAuditService.log(
            user=actor,
            action="period_post",
            resource_type="payroll_period",
            resource_id=str(period.public_id),
            summary=f"Payroll {period.period_number} posted to GL",
            metadata=payload,
        )
        return period


class PayslipService:
    @staticmethod
    def list_payslips(
        *,
        period_id: UUID | None = None,
        employee_id: UUID | None = None,
    ) -> QuerySet[Payslip]:
        qs = Payslip.objects.select_related(
            "employee", "employee__department", "payroll_period"
        ).prefetch_related("lines")
        if period_id:
            qs = qs.filter(payroll_period__public_id=period_id)
        if employee_id:
            qs = qs.filter(employee__public_id=employee_id)
        return qs.order_by("-payroll_period__period_start")

    @staticmethod
    def get_payslip(public_id: UUID) -> Payslip:
        payslip = (
            Payslip.objects.filter(public_id=public_id)
            .select_related("employee", "employee__department", "payroll_period")
            .prefetch_related("lines")
            .first()
        )
        if not payslip:
            raise NotFoundError("Payslip not found.")
        return payslip


class PayrollDashboardService:
    @staticmethod
    def get_kpis() -> dict:
        today = timezone.localdate()
        posted_qs = PayrollPeriod.objects.filter(status=PayrollPeriodStatus.POSTED)
        fy_start = date(today.year if today.month >= 7 else today.year - 1, 7, 1)
        ytd = posted_qs.filter(period_start__gte=fy_start).aggregate(
            total=Sum("total_net_cents"), gross=Sum("total_gross_cents")
        )

        upcoming = PayrollPeriod.objects.filter(
            status__in=[PayrollPeriodStatus.DRAFT, PayrollPeriodStatus.CALCULATED]
        ).order_by("pay_date")[:5]

        dept_costs = (
            Payslip.objects.filter(payroll_period__status=PayrollPeriodStatus.POSTED)
            .filter(payroll_period__period_start__gte=fy_start)
            .values("employee__department__name")
            .annotate(total_cents=Sum("net_cents"), headcount=Count("id"))
            .order_by("-total_cents")[:10]
        )

        return {
            "totalPayrollYtdCents": int(ytd["total"] or 0),
            "totalGrossYtdCents": int(ytd["gross"] or 0),
            "postedRunsCount": posted_qs.filter(period_start__gte=fy_start).count(),
            "pendingApprovalCount": PayrollPeriod.objects.filter(
                status=PayrollPeriodStatus.CALCULATED
            ).count(),
            "departmentCosts": [
                {
                    "departmentName": row["employee__department__name"] or "Unassigned",
                    "totalCents": int(row["total_cents"] or 0),
                    "headcount": row["headcount"],
                }
                for row in dept_costs
            ],
            "upcomingRuns": [
                {
                    "id": str(p.public_id),
                    "periodNumber": p.period_number,
                    "name": p.name,
                    "payDate": p.pay_date.isoformat(),
                    "status": p.status,
                }
                for p in upcoming
            ],
        }
