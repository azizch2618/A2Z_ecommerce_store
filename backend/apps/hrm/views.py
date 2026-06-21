"""HRM API views."""
from __future__ import annotations

from uuid import UUID

from django.utils.dateparse import parse_date
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.exceptions import NotFoundError
from apps.hrm.models import AssetAssignment, Employee, EmployeeDocument, LeaveBalance, LeaveRequest
from apps.hrm.permissions import CanApproveHrm, CanManageHrm, CanViewHrm
from apps.hrm.serializers import (
    serialize_assignment,
    serialize_asset,
    serialize_attendance,
    serialize_document,
    serialize_employee,
    serialize_leave_balance,
    serialize_leave_request,
)
from apps.hrm.services import (
    AssetService,
    AttendanceService,
    EmployeeDocumentService,
    EmployeeService,
    HrmDashboardService,
    LeaveRequestService,
    OrgStructureService,
)


class HrmDashboardView(APIView):
    permission_classes = [CanViewHrm]

    def get(self, request):
        return Response(HrmDashboardService.get_kpis())


class OrgStructureView(APIView):
    permission_classes = [CanViewHrm]

    def get(self, request):
        return Response(OrgStructureService.get_tree())


class EmployeeListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == "POST":
            return [CanManageHrm()]
        return [CanViewHrm()]

    def get(self, request):
        dept = request.query_params.get("departmentId")
        qs = EmployeeService.list_employees(
            status=request.query_params.get("status"),
            department_id=UUID(dept) if dept else None,
            search=request.query_params.get("search"),
        )
        return Response({"data": [serialize_employee(e) for e in qs[:200]]})

    def post(self, request):
        data = request.data
        hire = parse_date(data.get("hireDate", ""))
        if not hire:
            return Response({"detail": "hireDate is required."}, status=status.HTTP_400_BAD_REQUEST)
        emp = EmployeeService.create(
            actor=request.user,
            data={
                "first_name": data["firstName"],
                "last_name": data["lastName"],
                "email": data["email"],
                "phone": data.get("phone", ""),
                "job_title": data["jobTitle"],
                "employment_type": data.get("employmentType", "full_time"),
                "hire_date": hire,
                "department_id": data.get("departmentId"),
                "cost_center_id": data.get("costCenterId"),
                "manager_id": data.get("managerId"),
                "date_of_birth": parse_date(data["dateOfBirth"]) if data.get("dateOfBirth") else None,
                "emergency_contact": data.get("emergencyContact", {}),
            },
        )
        return Response(serialize_employee(emp), status=status.HTTP_201_CREATED)


class EmployeeDetailView(APIView):
    permission_classes = [CanViewHrm]

    def get(self, request, employee_id: UUID):
        emp = EmployeeService.get_employee(employee_id)
        data = serialize_employee(emp)
        data["leaveBalances"] = [
            serialize_leave_balance(b) for b in LeaveBalance.objects.filter(employee=emp)
        ]
        data["documents"] = [
            serialize_document(d) for d in EmployeeDocument.objects.filter(employee=emp)
        ]
        return Response(data)


class EmployeeDocumentUploadView(APIView):
    permission_classes = [CanManageHrm]

    def post(self, request, employee_id: UUID):
        emp = EmployeeService.get_employee(employee_id)
        file = request.FILES.get("file")
        if not file:
            return Response({"detail": "file is required."}, status=status.HTTP_400_BAD_REQUEST)
        doc = EmployeeDocumentService.upload(
            employee=emp,
            actor=request.user,
            file=file,
            document_type=request.data.get("documentType", "other"),
            title=request.data.get("title", file.name),
            expiry_date=parse_date(request.data["expiryDate"]) if request.data.get("expiryDate") else None,
            notes=request.data.get("notes", ""),
        )
        return Response(serialize_document(doc), status=status.HTTP_201_CREATED)


class AttendanceClockInView(APIView):
    permission_classes = [CanManageHrm]

    def post(self, request, employee_id: UUID):
        emp = EmployeeService.get_employee(employee_id)
        record = AttendanceService.clock_in(employee=emp, actor=request.user)
        return Response(serialize_attendance(record), status=status.HTTP_201_CREATED)


class AttendanceClockOutView(APIView):
    permission_classes = [CanManageHrm]

    def post(self, request, employee_id: UUID):
        emp = EmployeeService.get_employee(employee_id)
        record = AttendanceService.clock_out(employee=emp, actor=request.user)
        return Response(serialize_attendance(record))


class AttendanceListView(APIView):
    permission_classes = [CanViewHrm]

    def get(self, request, employee_id: UUID):
        emp = EmployeeService.get_employee(employee_id)
        records = AttendanceService.list_for_employee(employee=emp)
        return Response({"data": [serialize_attendance(r) for r in records]})


class LeaveRequestListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == "POST":
            return [CanManageHrm()]
        return [CanViewHrm()]

    def get(self, request):
        emp = request.query_params.get("employeeId")
        qs = LeaveRequestService.list_requests(
            status=request.query_params.get("status"),
            employee_id=UUID(emp) if emp else None,
        )
        return Response({"data": [serialize_leave_request(r) for r in qs[:200]]})

    def post(self, request):
        data = request.data
        emp = EmployeeService.get_employee(UUID(str(data["employeeId"])))
        req = LeaveRequestService.create(
            employee=emp,
            actor=request.user,
            leave_type=data["leaveType"],
            start_date=parse_date(data["startDate"]),
            end_date=parse_date(data["endDate"]),
            reason=data.get("reason", ""),
        )
        return Response(serialize_leave_request(req), status=status.HTTP_201_CREATED)


class LeaveRequestSubmitView(APIView):
    permission_classes = [CanManageHrm]

    def post(self, request, request_id: UUID):
        req = LeaveRequestService.get_request(request_id)
        req = LeaveRequestService.submit(request=req, actor=request.user)
        return Response(serialize_leave_request(req))


class LeaveRequestApproveView(APIView):
    permission_classes = [CanApproveHrm]

    def post(self, request, request_id: UUID):
        req = LeaveRequestService.get_request(request_id)
        req = LeaveRequestService.approve(
            request=req, actor=request.user, comment=request.data.get("comment", "")
        )
        return Response(serialize_leave_request(req))


class LeaveRequestRejectView(APIView):
    permission_classes = [CanApproveHrm]

    def post(self, request, request_id: UUID):
        req = LeaveRequestService.get_request(request_id)
        req = LeaveRequestService.reject(
            request=req, actor=request.user, comment=request.data.get("comment", "")
        )
        return Response(serialize_leave_request(req))


class AssetListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == "POST":
            return [CanManageHrm()]
        return [CanViewHrm()]

    def get(self, request):
        qs = AssetService.list_assets(
            status=request.query_params.get("status"),
            category=request.query_params.get("category"),
        )
        return Response({"data": [serialize_asset(a) for a in qs]})

    def post(self, request):
        data = request.data
        asset = AssetService.create(
            actor=request.user,
            data={
                "name": data["name"],
                "category": data.get("category", "other"),
                "serial_number": data.get("serialNumber", ""),
                "notes": data.get("notes", ""),
            },
        )
        return Response(serialize_asset(asset), status=status.HTTP_201_CREATED)


class AssetAssignView(APIView):
    permission_classes = [CanManageHrm]

    def post(self, request, asset_id: UUID):
        from apps.hrm.models import HrmAsset

        asset = HrmAsset.objects.filter(public_id=asset_id).first()
        if not asset:
            raise NotFoundError("Asset not found.")
        emp = EmployeeService.get_employee(request.data["employeeId"])
        assignment = AssetService.assign(
            asset=asset,
            employee=emp,
            actor=request.user,
            condition_on_issue=request.data.get("conditionOnIssue", ""),
            notes=request.data.get("notes", ""),
        )
        return Response(serialize_assignment(assignment), status=status.HTTP_201_CREATED)


class AssetReturnView(APIView):
    permission_classes = [CanManageHrm]

    def post(self, request, assignment_id: UUID):
        assignment = AssetAssignment.objects.filter(public_id=assignment_id).select_related(
            "asset", "employee"
        ).first()
        if not assignment:
            raise NotFoundError("Assignment not found.")
        assignment = AssetService.return_asset(
            assignment=assignment,
            actor=request.user,
            condition_on_return=request.data.get("conditionOnReturn", ""),
        )
        return Response(serialize_assignment(assignment))


class AssetAssignmentListView(APIView):
    permission_classes = [CanViewHrm]

    def get(self, request):
        qs = AssetAssignment.objects.select_related("asset", "employee").filter(
            status="assigned"
        )[:200]
        return Response({"data": [serialize_assignment(a) for a in qs]})
