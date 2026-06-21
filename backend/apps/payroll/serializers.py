"""Payroll API serializers — camelCase output."""
from __future__ import annotations

from apps.payroll.models import (
    PayrollAdjustment,
    PayrollPeriod,
    Payslip,
    PayslipLine,
    SalaryComponent,
    SalaryStructure,
)


def _user_ref(user) -> dict | None:
    if not user:
        return None
    return {"id": str(user.public_id), "email": user.email}


def serialize_salary_component(comp: SalaryComponent) -> dict:
    return {
        "id": str(comp.public_id),
        "componentType": comp.component_type,
        "code": comp.code,
        "name": comp.name,
        "amountCents": comp.amount_cents,
        "isTaxable": comp.is_taxable,
        "isSuperable": comp.is_superable,
        "metadata": comp.metadata,
    }


def serialize_salary_structure(structure: SalaryStructure) -> dict:
    return {
        "id": str(structure.public_id),
        "employeeId": str(structure.employee.public_id),
        "employeeName": structure.employee.full_name,
        "effectiveFrom": structure.effective_from.isoformat(),
        "effectiveTo": structure.effective_to.isoformat() if structure.effective_to else None,
        "payFrequency": structure.pay_frequency,
        "awardCode": structure.award_code,
        "isActive": structure.is_active,
        "notes": structure.notes,
        "components": [serialize_salary_component(c) for c in structure.components.all()],
    }


def serialize_period(period: PayrollPeriod) -> dict:
    return {
        "id": str(period.public_id),
        "periodNumber": period.period_number,
        "name": period.name,
        "periodStart": period.period_start.isoformat(),
        "periodEnd": period.period_end.isoformat(),
        "payDate": period.pay_date.isoformat(),
        "status": period.status,
        "totalGrossCents": period.total_gross_cents,
        "totalNetCents": period.total_net_cents,
        "totalDeductionsCents": period.total_deductions_cents,
        "totalSuperCents": period.total_super_cents,
        "totalPaygCents": period.total_payg_cents,
        "calculatedAt": period.calculated_at.isoformat() if period.calculated_at else None,
        "approvedAt": period.approved_at.isoformat() if period.approved_at else None,
        "postedAt": period.posted_at.isoformat() if period.posted_at else None,
        "calculatedBy": _user_ref(period.calculated_by),
        "approvedBy": _user_ref(period.approved_by),
        "postedBy": _user_ref(period.posted_by),
        "notes": period.notes,
    }


def serialize_payslip_line(line: PayslipLine) -> dict:
    return {
        "id": str(line.public_id),
        "lineType": line.line_type,
        "code": line.code,
        "description": line.description,
        "amountCents": line.amount_cents,
    }


def serialize_payslip(payslip: Payslip) -> dict:
    return {
        "id": str(payslip.public_id),
        "payslipNumber": payslip.payslip_number,
        "payrollPeriodId": str(payslip.payroll_period.public_id),
        "periodName": payslip.payroll_period.name,
        "periodNumber": payslip.payroll_period.period_number,
        "employeeId": str(payslip.employee.public_id),
        "employeeName": payslip.employee.full_name,
        "employeeNumber": payslip.employee.employee_number,
        "departmentName": payslip.employee.department.name if payslip.employee.department_id else None,
        "status": payslip.status,
        "grossCents": payslip.gross_cents,
        "netCents": payslip.net_cents,
        "totalAllowancesCents": payslip.total_allowances_cents,
        "totalDeductionsCents": payslip.total_deductions_cents,
        "leaveDeductionCents": payslip.leave_deduction_cents,
        "overtimeCents": payslip.overtime_cents,
        "paygWithholdingCents": payslip.payg_withholding_cents,
        "superCents": payslip.super_cents,
        "payDate": payslip.payroll_period.pay_date.isoformat(),
        "lines": [serialize_payslip_line(l) for l in payslip.lines.all()],
        "metadata": payslip.metadata,
    }


def serialize_adjustment(adj: PayrollAdjustment) -> dict:
    return {
        "id": str(adj.public_id),
        "employeeId": str(adj.employee.public_id),
        "employeeName": adj.employee.full_name,
        "description": adj.description,
        "amountCents": adj.amount_cents,
        "createdBy": _user_ref(adj.created_by),
        "createdAt": adj.created_at.isoformat(),
    }
