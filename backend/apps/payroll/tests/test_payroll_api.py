"""Payroll API tests."""
from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.core.management import call_command
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.constants import RoleSlug
from apps.accounts.services import RoleService
from apps.hrm.services import EmployeeService
from apps.payroll.constants import PayrollPeriodStatus, SalaryComponentType
from apps.payroll.models import Payslip
from apps.payroll.services import PayrollPeriodService, SalaryStructureService

User = get_user_model()


class PayrollApiTests(APITestCase):
    def setUp(self):
        RoleService.ensure_system_roles()
        call_command("seed_erp_foundation", verbosity=0)
        call_command("seed_accounting_foundation", verbosity=0)

        self.payroll_officer = User.objects.create_user(
            email="payroll-officer@example.com", password="SecurePass123!", is_staff=True
        )
        RoleService.assign_role(self.payroll_officer, RoleSlug.PAYROLL_OFFICER)

        self.payroll_manager = User.objects.create_user(
            email="payroll-manager@example.com", password="SecurePass123!", is_staff=True
        )
        RoleService.assign_role(self.payroll_manager, RoleSlug.PAYROLL_MANAGER)

        self.client.force_authenticate(user=self.payroll_officer)

        self.employee = EmployeeService.create(
            actor=self.payroll_officer,
            data={
                "first_name": "Pat",
                "last_name": "Payroll",
                "email": "pat.payroll@example.com",
                "job_title": "Operator",
                "employment_type": "full_time",
                "hire_date": date.today(),
            },
        )
        self.employee_id = str(self.employee.public_id)

        SalaryStructureService.create(
            employee=self.employee,
            actor=self.payroll_officer,
            effective_from=date.today() - timedelta(days=30),
            components=[
                {
                    "componentType": SalaryComponentType.BASE,
                    "code": "BASE",
                    "name": "Base Salary",
                    "amountCents": 500000,
                },
                {
                    "componentType": SalaryComponentType.ALLOWANCE,
                    "code": "CAR",
                    "name": "Car Allowance",
                    "amountCents": 20000,
                },
                {
                    "componentType": SalaryComponentType.PAYG,
                    "code": "PAYG",
                    "name": "PAYG Withholding",
                    "amountCents": 80000,
                },
                {
                    "componentType": SalaryComponentType.SUPER,
                    "code": "SUPER",
                    "name": "Superannuation",
                    "amountCents": 57500,
                },
            ],
            award_code="MA000004",
        )

    def test_payroll_dashboard(self):
        resp = self.client.get("/api/v1/payroll/admin/dashboard/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("totalPayrollYtdCents", resp.data)

    def test_payroll_run_lifecycle(self):
        start = date.today().replace(day=1)
        end = (start + timedelta(days=27))
        pay = end + timedelta(days=3)

        create = self.client.post(
            "/api/v1/payroll/admin/periods/",
            {
                "name": "Test Pay Run",
                "periodStart": start.isoformat(),
                "periodEnd": end.isoformat(),
                "payDate": pay.isoformat(),
            },
            format="json",
        )
        self.assertEqual(create.status_code, status.HTTP_201_CREATED)
        self.assertTrue(create.data["periodNumber"].startswith("PRUN-"))
        period_id = create.data["id"]

        calc = self.client.post(f"/api/v1/payroll/admin/periods/{period_id}/calculate/", format="json")
        self.assertEqual(calc.status_code, status.HTTP_200_OK)
        self.assertEqual(calc.data["status"], PayrollPeriodStatus.CALCULATED)
        self.assertGreater(calc.data["totalNetCents"], 0)

        self.client.force_authenticate(user=self.payroll_officer)
        deny = self.client.post(f"/api/v1/payroll/admin/periods/{period_id}/approve/", format="json")
        self.assertEqual(deny.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(user=self.payroll_manager)
        approve = self.client.post(f"/api/v1/payroll/admin/periods/{period_id}/approve/", format="json")
        self.assertEqual(approve.status_code, status.HTTP_200_OK)
        self.assertEqual(approve.data["status"], PayrollPeriodStatus.APPROVED)

        post = self.client.post(f"/api/v1/payroll/admin/periods/{period_id}/post/", format="json")
        self.assertEqual(post.status_code, status.HTTP_200_OK)
        self.assertEqual(post.data["status"], PayrollPeriodStatus.POSTED)

    def test_payslip_pdf(self):
        period = PayrollPeriodService.create(
            actor=self.payroll_officer,
            name="PDF Test",
            period_start=date.today().replace(day=1),
            period_end=date.today(),
            pay_date=date.today() + timedelta(days=5),
        )
        PayrollPeriodService.calculate(period=period, actor=self.payroll_officer)
        payslip = Payslip.objects.filter(payroll_period=period).first()
        self.assertIsNotNone(payslip)

        resp = self.client.get(f"/api/v1/payroll/admin/payslips/{payslip.public_id}/pdf/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(resp.content.startswith(b"%PDF"))

    def test_employee_payroll_history(self):
        resp = self.client.get(f"/api/v1/payroll/admin/employees/{self.employee_id}/payroll-history/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("salaryStructures", resp.data)
        self.assertEqual(len(resp.data["salaryStructures"]), 1)
