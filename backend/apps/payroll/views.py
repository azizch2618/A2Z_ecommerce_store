"""Payroll API views."""
from __future__ import annotations

from uuid import UUID

from django.http import HttpResponse
from django.utils.dateparse import parse_date
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.exceptions import NotFoundError
from apps.hrm.services import EmployeeService
from apps.payroll.models import PayrollAdjustment
from apps.payroll.pdf_service import generate_payslip_pdf
from apps.payroll.permissions import (
    CanApprovePayroll,
    CanManagePayroll,
    CanPostPayroll,
    CanViewPayroll,
)
from apps.payroll.serializers import (
    serialize_adjustment,
    serialize_payslip,
    serialize_period,
    serialize_salary_structure,
)
from apps.payroll.services import (
    PayrollDashboardService,
    PayrollPeriodService,
    PayslipService,
    SalaryStructureService,
)


class PayrollDashboardView(APIView):
    permission_classes = [CanViewPayroll]

    def get(self, request):
        return Response(PayrollDashboardService.get_kpis())


class PayrollPeriodListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == "POST":
            return [CanManagePayroll()]
        return [CanViewPayroll()]

    def get(self, request):
        qs = PayrollPeriodService.list_periods(status=request.query_params.get("status"))
        return Response({"data": [serialize_period(p) for p in qs[:100]]})

    def post(self, request):
        data = request.data
        start = parse_date(data.get("periodStart", ""))
        end = parse_date(data.get("periodEnd", ""))
        pay = parse_date(data.get("payDate", ""))
        if not start or not end or not pay:
            return Response(
                {"detail": "periodStart, periodEnd, and payDate are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        period = PayrollPeriodService.create(
            actor=request.user,
            name=data["name"],
            period_start=start,
            period_end=end,
            pay_date=pay,
            notes=data.get("notes", ""),
        )
        return Response(serialize_period(period), status=status.HTTP_201_CREATED)


class PayrollPeriodDetailView(APIView):
    permission_classes = [CanViewPayroll]

    def get(self, request, period_id: UUID):
        period = PayrollPeriodService.get_period(period_id)
        data = serialize_period(period)
        data["adjustments"] = [
            serialize_adjustment(a)
            for a in PayrollAdjustment.objects.filter(payroll_period=period).select_related(
                "employee", "created_by"
            )
        ]
        return Response(data)


class PayrollPeriodCalculateView(APIView):
    permission_classes = [CanManagePayroll]

    def post(self, request, period_id: UUID):
        period = PayrollPeriodService.get_period(period_id)
        period = PayrollPeriodService.calculate(period=period, actor=request.user)
        return Response(serialize_period(period))


class PayrollPeriodApproveView(APIView):
    permission_classes = [CanApprovePayroll]

    def post(self, request, period_id: UUID):
        period = PayrollPeriodService.get_period(period_id)
        period = PayrollPeriodService.approve(
            period=period, actor=request.user, comment=request.data.get("comment", "")
        )
        return Response(serialize_period(period))


class PayrollPeriodPostView(APIView):
    permission_classes = [CanPostPayroll]

    def post(self, request, period_id: UUID):
        period = PayrollPeriodService.get_period(period_id)
        period = PayrollPeriodService.post(period=period, actor=request.user)
        return Response(serialize_period(period))


class PayrollPeriodAdjustmentView(APIView):
    permission_classes = [CanManagePayroll]

    def post(self, request, period_id: UUID):
        period = PayrollPeriodService.get_period(period_id)
        emp = EmployeeService.get_employee(request.data["employeeId"])
        adj = PayrollPeriodService.add_adjustment(
            period=period,
            employee=emp,
            actor=request.user,
            description=request.data["description"],
            amount_cents=int(request.data["amountCents"]),
        )
        return Response(serialize_adjustment(adj), status=status.HTTP_201_CREATED)


class SalaryStructureListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == "POST":
            return [CanManagePayroll()]
        return [CanViewPayroll()]

    def get(self, request):
        emp_id = request.query_params.get("employeeId")
        if not emp_id:
            return Response({"detail": "employeeId is required."}, status=status.HTTP_400_BAD_REQUEST)
        emp = EmployeeService.get_employee(UUID(emp_id))
        structures = SalaryStructureService.list_for_employee(employee=emp)
        return Response({"data": [serialize_salary_structure(s) for s in structures]})

    def post(self, request):
        data = request.data
        emp = EmployeeService.get_employee(data["employeeId"])
        eff = parse_date(data.get("effectiveFrom", ""))
        if not eff:
            return Response({"detail": "effectiveFrom is required."}, status=status.HTTP_400_BAD_REQUEST)
        structure = SalaryStructureService.create(
            employee=emp,
            actor=request.user,
            effective_from=eff,
            pay_frequency=data.get("payFrequency", "monthly"),
            award_code=data.get("awardCode", ""),
            components=data.get("components", []),
            notes=data.get("notes", ""),
        )
        return Response(serialize_salary_structure(structure), status=status.HTTP_201_CREATED)


class PayslipListView(APIView):
    permission_classes = [CanViewPayroll]

    def get(self, request):
        period = request.query_params.get("periodId")
        employee = request.query_params.get("employeeId")
        qs = PayslipService.list_payslips(
            period_id=UUID(period) if period else None,
            employee_id=UUID(employee) if employee else None,
        )
        return Response({"data": [serialize_payslip(p) for p in qs[:200]]})


class PayslipDetailView(APIView):
    permission_classes = [CanViewPayroll]

    def get(self, request, payslip_id: UUID):
        payslip = PayslipService.get_payslip(payslip_id)
        return Response(serialize_payslip(payslip))


class PayslipPdfView(APIView):
    permission_classes = [CanViewPayroll]

    def get(self, request, payslip_id: UUID):
        payslip = PayslipService.get_payslip(payslip_id)
        pdf_bytes = generate_payslip_pdf(payslip)
        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        response["Content-Disposition"] = f'inline; filename="{payslip.payslip_number}.pdf"'
        return response


class EmployeePayrollHistoryView(APIView):
    permission_classes = [CanViewPayroll]

    def get(self, request, employee_id: UUID):
        emp = EmployeeService.get_employee(employee_id)
        payslips = PayslipService.list_payslips(employee_id=employee_id)
        structures = SalaryStructureService.list_for_employee(employee=emp)
        return Response(
            {
                "employeeId": str(emp.public_id),
                "employeeName": emp.full_name,
                "payslips": [serialize_payslip(p) for p in payslips],
                "salaryStructures": [serialize_salary_structure(s) for s in structures],
            }
        )
