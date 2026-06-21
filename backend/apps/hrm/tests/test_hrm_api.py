"""HRM API tests."""
from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.core.management import call_command
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.constants import RoleSlug
from apps.accounts.services import RoleService
from apps.erp.models import Department
from apps.hrm.constants import LeaveRequestStatus
from apps.hrm.models import Employee
from apps.hrm.services import AttendanceService, LeaveRequestService

User = get_user_model()


class HrmApiTests(APITestCase):
    def setUp(self):
        RoleService.ensure_system_roles()
        call_command("seed_erp_foundation", verbosity=0)
        call_command("seed_accounting_foundation", verbosity=0)

        self.hr_officer = User.objects.create_user(
            email="hr-officer@example.com", password="SecurePass123!", is_staff=True
        )
        RoleService.assign_role(self.hr_officer, RoleSlug.HR_OFFICER)

        self.hr_manager = User.objects.create_user(
            email="hr-manager@example.com", password="SecurePass123!", is_staff=True
        )
        RoleService.assign_role(self.hr_manager, RoleSlug.HR_MANAGER)

        self.dept = Department.objects.first()

    def test_hrm_dashboard(self):
        self.client.force_authenticate(user=self.hr_officer)
        resp = self.client.get("/api/v1/hrm/admin/dashboard/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("headcount", resp.data)

    def test_employee_lifecycle(self):
        self.client.force_authenticate(user=self.hr_officer)
        create = self.client.post(
            "/api/v1/hrm/admin/employees/",
            {
                "firstName": "Jane",
                "lastName": "Smith",
                "email": "jane.smith@example.com",
                "jobTitle": "Warehouse Operator",
                "employmentType": "full_time",
                "hireDate": date.today().isoformat(),
                "departmentId": str(self.dept.public_id) if self.dept else None,
            },
            format="json",
        )
        self.assertEqual(create.status_code, status.HTTP_201_CREATED)
        self.assertTrue(create.data["employeeNumber"].startswith("EMP-"))
        emp_id = create.data["id"]

        clock_in = self.client.post(f"/api/v1/hrm/admin/employees/{emp_id}/clock-in/", format="json")
        self.assertEqual(clock_in.status_code, status.HTTP_201_CREATED)

        clock_out = self.client.post(f"/api/v1/hrm/admin/employees/{emp_id}/clock-out/", format="json")
        self.assertEqual(clock_out.status_code, status.HTTP_200_OK)

    def test_leave_request_workflow(self):
        self.client.force_authenticate(user=self.hr_officer)
        emp_resp = self.client.post(
            "/api/v1/hrm/admin/employees/",
            {
                "firstName": "Bob",
                "lastName": "Jones",
                "email": "bob.jones@example.com",
                "jobTitle": "Sales Rep",
                "employmentType": "full_time",
                "hireDate": date.today().isoformat(),
            },
            format="json",
        )
        emp_id = emp_resp.data["id"]
        start = date.today() + timedelta(days=14)
        end = start + timedelta(days=2)

        leave = self.client.post(
            "/api/v1/hrm/admin/leave-requests/",
            {
                "employeeId": emp_id,
                "leaveType": "annual",
                "startDate": start.isoformat(),
                "endDate": end.isoformat(),
                "reason": "Family holiday",
            },
            format="json",
        )
        self.assertEqual(leave.status_code, status.HTTP_201_CREATED)
        req_id = leave.data["id"]

        submit = self.client.post(f"/api/v1/hrm/admin/leave-requests/{req_id}/submit/", format="json")
        self.assertEqual(submit.status_code, status.HTTP_200_OK)
        self.assertEqual(submit.data["status"], LeaveRequestStatus.SUBMITTED)

        self.client.force_authenticate(user=self.hr_officer)
        deny = self.client.post(f"/api/v1/hrm/admin/leave-requests/{req_id}/approve/", format="json")
        self.assertEqual(deny.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(user=self.hr_manager)
        approve = self.client.post(f"/api/v1/hrm/admin/leave-requests/{req_id}/approve/", format="json")
        self.assertEqual(approve.status_code, status.HTTP_200_OK)
        self.assertEqual(approve.data["status"], LeaveRequestStatus.APPROVED)

    def test_asset_assignment(self):
        self.client.force_authenticate(user=self.hr_officer)
        emp = self.client.post(
            "/api/v1/hrm/admin/employees/",
            {
                "firstName": "Alex",
                "lastName": "Lee",
                "email": "alex.lee@example.com",
                "jobTitle": "Technician",
                "employmentType": "full_time",
                "hireDate": date.today().isoformat(),
            },
            format="json",
        ).data

        asset = self.client.post(
            "/api/v1/hrm/admin/assets/",
            {"name": "MacBook Pro", "category": "laptop", "serialNumber": "SN-12345"},
            format="json",
        )
        self.assertEqual(asset.status_code, status.HTTP_201_CREATED)

        assign = self.client.post(
            f"/api/v1/hrm/admin/assets/{asset.data['id']}/assign/",
            {"employeeId": emp["id"]},
            format="json",
        )
        self.assertEqual(assign.status_code, status.HTTP_201_CREATED)
        self.assertEqual(assign.data["status"], "assigned")

    def test_org_structure(self):
        self.client.force_authenticate(user=self.hr_officer)
        resp = self.client.get("/api/v1/hrm/admin/org-structure/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("departments", resp.data)
