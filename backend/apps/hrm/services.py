"""HRM business logic."""
from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal
from typing import Any
from uuid import UUID

from django.db import transaction
from django.db.models import Count, Q, QuerySet, Sum
from django.utils import timezone

from apps.core.exceptions import BusinessRuleError, ConflictError, NotFoundError
from apps.erp.constants import DocumentType, WorkflowCode
from apps.erp.models import Company, CostCenter, Department
from apps.erp.services.document_sequence import DocumentSequenceService
from apps.erp.services.notifications import NotificationService
from apps.erp.services.party import PartyService
from apps.erp.services.workflow import WorkflowEngine
from apps.hrm.audit import HrmAuditService
from apps.hrm.constants import (
    AssetStatus,
    AssignmentStatus,
    EmployeeStatus,
    LeaveRequestStatus,
    LeaveType,
)
from apps.hrm.models import (
    AssetAssignment,
    AttendanceRecord,
    Employee,
    EmployeeDocument,
    HrmAsset,
    LeaveBalance,
    LeaveRequest,
)


def _default_company() -> Company:
    company = Company.objects.filter(is_default=True, is_active=True).first()
    if not company:
        company = Company.objects.filter(is_active=True).first()
    if not company:
        raise NotFoundError("No active company configured.")
    return company


def _next_employee_number() -> str:
    return DocumentSequenceService.next_number(DocumentType.EMPLOYEE)


def _next_leave_number() -> str:
    return DocumentSequenceService.next_number(DocumentType.LEAVE_REQUEST)


def _next_asset_number() -> str:
    return DocumentSequenceService.next_number(DocumentType.HRM_ASSET)


class EmployeeService:
    @staticmethod
    def list_employees(
        *,
        status: str | None = None,
        department_id: UUID | None = None,
        search: str | None = None,
    ) -> QuerySet[Employee]:
        qs = Employee.objects.select_related(
            "company", "department", "cost_center", "manager", "user"
        )
        if status:
            qs = qs.filter(status=status)
        if department_id:
            qs = qs.filter(department__public_id=department_id)
        if search:
            qs = qs.filter(
                Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
                | Q(email__icontains=search)
                | Q(employee_number__icontains=search)
            )
        return qs.order_by("last_name", "first_name")

    @staticmethod
    def get_employee(public_id: UUID) -> Employee:
        emp = EmployeeService.list_employees().filter(public_id=public_id).first()
        if not emp:
            raise NotFoundError("Employee not found.")
        return emp

    @classmethod
    @transaction.atomic
    def create(cls, *, actor, data: dict[str, Any]) -> Employee:
        company = _default_company()
        department = None
        cost_center = None
        manager = None
        if data.get("department_id"):
            department = Department.objects.filter(public_id=data["department_id"]).first()
        if data.get("cost_center_id"):
            cost_center = CostCenter.objects.filter(public_id=data["cost_center_id"]).first()
        if data.get("manager_id"):
            manager = Employee.objects.filter(public_id=data["manager_id"]).first()

        employee = Employee.objects.create(
            employee_number=_next_employee_number(),
            company=company,
            department=department,
            cost_center=cost_center,
            manager=manager,
            job_title=data["job_title"],
            employment_type=data["employment_type"],
            hire_date=data["hire_date"],
            first_name=data["first_name"],
            last_name=data["last_name"],
            email=data["email"],
            phone=data.get("phone", ""),
            date_of_birth=data.get("date_of_birth"),
            emergency_contact=data.get("emergency_contact", {}),
            status=EmployeeStatus.ACTIVE,
        )

        party = PartyService.create_party(
            party_type="person",
            display_name=employee.full_name,
            email=employee.email,
            phone=employee.phone,
            company=company,
        )
        employee.party = party
        employee.save(update_fields=["party", "updated_at"])

        for leave_type in (LeaveType.ANNUAL, LeaveType.SICK, LeaveType.UNPAID):
            default_balance = Decimal("20") if leave_type == LeaveType.ANNUAL else Decimal("10")
            if leave_type == LeaveType.UNPAID:
                default_balance = Decimal("0")
            LeaveBalance.objects.create(
                employee=employee,
                leave_type=leave_type,
                balance_days=default_balance,
            )

        HrmAuditService.log(
            user=actor,
            action="employee_create",
            resource_type="employee",
            resource_id=str(employee.public_id),
            summary=f"Employee {employee.employee_number} created",
        )
        return employee


class EmployeeDocumentService:
    @classmethod
    @transaction.atomic
    def upload(
        cls,
        *,
        employee: Employee,
        actor,
        file,
        document_type: str,
        title: str,
        expiry_date: date | None = None,
        notes: str = "",
    ) -> EmployeeDocument:
        doc = EmployeeDocument.objects.create(
            employee=employee,
            document_type=document_type,
            title=title,
            file=file,
            original_filename=getattr(file, "name", ""),
            expiry_date=expiry_date,
            notes=notes,
            uploaded_by=actor if getattr(actor, "is_authenticated", False) else None,
        )
        HrmAuditService.log(
            user=actor,
            action="document_upload",
            resource_type="employee_document",
            resource_id=str(doc.public_id),
            summary=f"Document uploaded for {employee.employee_number}: {title}",
        )
        return doc


class AttendanceService:
    @classmethod
    @transaction.atomic
    def clock_in(cls, *, employee: Employee, actor) -> AttendanceRecord:
        today = timezone.localdate()
        open_record = AttendanceRecord.objects.filter(
            employee=employee, work_date=today, clock_out__isnull=True
        ).first()
        if open_record:
            raise ConflictError("Already clocked in for today.")

        record = AttendanceRecord.objects.create(
            employee=employee,
            work_date=today,
            clock_in=timezone.now(),
        )
        HrmAuditService.log(
            user=actor,
            action="clock_in",
            resource_type="attendance",
            resource_id=str(record.public_id),
            summary=f"{employee.employee_number} clocked in",
        )
        return record

    @classmethod
    @transaction.atomic
    def clock_out(cls, *, employee: Employee, actor) -> AttendanceRecord:
        today = timezone.localdate()
        record = AttendanceRecord.objects.filter(
            employee=employee, work_date=today, clock_out__isnull=True
        ).first()
        if not record:
            raise NotFoundError("No open attendance record for today.")
        record.clock_out = timezone.now()
        record.save(update_fields=["clock_out", "updated_at"])
        HrmAuditService.log(
            user=actor,
            action="clock_out",
            resource_type="attendance",
            resource_id=str(record.public_id),
            summary=f"{employee.employee_number} clocked out",
        )
        return record

    @staticmethod
    def list_for_employee(*, employee: Employee, limit: int = 30) -> QuerySet[AttendanceRecord]:
        return employee.attendance_records.order_by("-work_date")[:limit]


class LeaveRequestService:
    @staticmethod
    def list_requests(
        *,
        status: str | None = None,
        employee_id: UUID | None = None,
    ) -> QuerySet[LeaveRequest]:
        qs = LeaveRequest.objects.select_related(
            "employee", "submitted_by", "approved_by"
        )
        if status:
            qs = qs.filter(status=status)
        if employee_id:
            qs = qs.filter(employee__public_id=employee_id)
        return qs.order_by("-created_at")

    @staticmethod
    def get_request(public_id: UUID) -> LeaveRequest:
        req = LeaveRequestService.list_requests().filter(public_id=public_id).first()
        if not req:
            raise NotFoundError("Leave request not found.")
        return req

    @classmethod
    @transaction.atomic
    def create(
        cls,
        *,
        employee: Employee,
        actor,
        leave_type: str,
        start_date: date,
        end_date: date,
        reason: str = "",
    ) -> LeaveRequest:
        if end_date < start_date:
            raise BusinessRuleError("End date must be on or after start date.")
        days = Decimal(str((end_date - start_date).days + 1))

        req = LeaveRequest.objects.create(
            request_number=_next_leave_number(),
            employee=employee,
            leave_type=leave_type,
            start_date=start_date,
            end_date=end_date,
            days=days,
            reason=reason,
            status=LeaveRequestStatus.DRAFT,
        )
        HrmAuditService.log(
            user=actor,
            action="leave_create",
            resource_type="leave_request",
            resource_id=str(req.public_id),
            summary=f"Leave request {req.request_number} created",
        )
        return req

    @classmethod
    @transaction.atomic
    def submit(cls, *, request: LeaveRequest, actor) -> LeaveRequest:
        if request.status != LeaveRequestStatus.DRAFT:
            raise BusinessRuleError("Only draft requests can be submitted.")
        request.status = LeaveRequestStatus.SUBMITTED
        request.submitted_by = actor if getattr(actor, "is_authenticated", False) else None
        request.save(update_fields=["status", "submitted_by", "updated_at"])

        WorkflowEngine.start(
            definition_code=WorkflowCode.LEAVE_APPROVAL,
            resource_type="leave_request",
            resource_id=str(request.public_id),
            actor=actor,
        )
        manager = request.employee.manager
        if manager and manager.user_id:
            NotificationService.send_from_template(
                recipient=manager.user,
                template_code="leave_submitted",
                context={
                    "request_number": request.request_number,
                    "employee_name": request.employee.full_name,
                },
                resource_type="leave_request",
                resource_id=str(request.public_id),
            )
        HrmAuditService.log(
            user=actor,
            action="leave_submit",
            resource_type="leave_request",
            resource_id=str(request.public_id),
            summary=f"Leave {request.request_number} submitted",
        )
        return request

    @classmethod
    @transaction.atomic
    def approve(cls, *, request: LeaveRequest, actor, comment: str = "") -> LeaveRequest:
        if request.status != LeaveRequestStatus.SUBMITTED:
            raise BusinessRuleError("Only submitted requests can be approved.")
        instance = WorkflowEngine.get_for_resource(
            resource_type="leave_request", resource_id=str(request.public_id)
        )
        if instance:
            WorkflowEngine.transition(
                instance=instance, action="approve", actor=actor, comment=comment
            )

        balance = LeaveBalance.objects.filter(
            employee=request.employee, leave_type=request.leave_type
        ).first()
        if balance and request.leave_type != LeaveType.UNPAID:
            if balance.balance_days - balance.used_days < request.days:
                raise BusinessRuleError("Insufficient leave balance.")
            balance.used_days += request.days
            balance.save(update_fields=["used_days", "updated_at"])

        request.status = LeaveRequestStatus.APPROVED
        request.approved_by = actor if getattr(actor, "is_authenticated", False) else None
        request.save(update_fields=["status", "approved_by", "updated_at"])

        if request.employee.user_id:
            NotificationService.send_from_template(
                recipient=request.employee.user,
                template_code="leave_approved",
                context={"request_number": request.request_number},
                resource_type="leave_request",
                resource_id=str(request.public_id),
            )
        HrmAuditService.log(
            user=actor,
            action="leave_approve",
            resource_type="leave_request",
            resource_id=str(request.public_id),
            summary=f"Leave {request.request_number} approved",
        )
        return request

    @classmethod
    @transaction.atomic
    def reject(cls, *, request: LeaveRequest, actor, comment: str = "") -> LeaveRequest:
        if request.status != LeaveRequestStatus.SUBMITTED:
            raise BusinessRuleError("Only submitted requests can be rejected.")
        instance = WorkflowEngine.get_for_resource(
            resource_type="leave_request", resource_id=str(request.public_id)
        )
        if instance:
            WorkflowEngine.transition(
                instance=instance, action="reject", actor=actor, comment=comment
            )
        request.status = LeaveRequestStatus.REJECTED
        request.save(update_fields=["status", "updated_at"])

        if request.employee.user_id:
            NotificationService.send_from_template(
                recipient=request.employee.user,
                template_code="leave_rejected",
                context={"request_number": request.request_number},
                resource_type="leave_request",
                resource_id=str(request.public_id),
            )
        HrmAuditService.log(
            user=actor,
            action="leave_reject",
            resource_type="leave_request",
            resource_id=str(request.public_id),
            summary=f"Leave {request.request_number} rejected",
        )
        return request


class AssetService:
    @staticmethod
    def list_assets(*, status: str | None = None, category: str | None = None) -> QuerySet[HrmAsset]:
        qs = HrmAsset.objects.all()
        if status:
            qs = qs.filter(status=status)
        if category:
            qs = qs.filter(category=category)
        return qs.order_by("asset_number")

    @classmethod
    @transaction.atomic
    def create(cls, *, actor, data: dict[str, Any]) -> HrmAsset:
        asset = HrmAsset.objects.create(
            asset_number=_next_asset_number(),
            name=data["name"],
            category=data["category"],
            serial_number=data.get("serial_number", ""),
            notes=data.get("notes", ""),
            status=AssetStatus.AVAILABLE,
        )
        HrmAuditService.log(
            user=actor,
            action="asset_create",
            resource_type="hrm_asset",
            resource_id=str(asset.public_id),
            summary=f"Asset {asset.asset_number} created",
        )
        return asset

    @classmethod
    @transaction.atomic
    def assign(
        cls,
        *,
        asset: HrmAsset,
        employee: Employee,
        actor,
        condition_on_issue: str = "",
        notes: str = "",
    ) -> AssetAssignment:
        if asset.status == AssetStatus.ASSIGNED:
            raise ConflictError("Asset is already assigned.")
        assignment = AssetAssignment.objects.create(
            asset=asset,
            employee=employee,
            issued_at=timezone.now(),
            condition_on_issue=condition_on_issue,
            notes=notes,
            issued_by=actor if getattr(actor, "is_authenticated", False) else None,
            status=AssignmentStatus.ASSIGNED,
        )
        asset.status = AssetStatus.ASSIGNED
        asset.save(update_fields=["status", "updated_at"])

        if employee.user_id:
            NotificationService.send_from_template(
                recipient=employee.user,
                template_code="asset_assigned",
                context={
                    "asset_number": asset.asset_number,
                    "asset_name": asset.name,
                },
                resource_type="asset_assignment",
                resource_id=str(assignment.public_id),
            )
        HrmAuditService.log(
            user=actor,
            action="asset_assign",
            resource_type="asset_assignment",
            resource_id=str(assignment.public_id),
            summary=f"Asset {asset.asset_number} assigned to {employee.employee_number}",
        )
        return assignment

    @classmethod
    @transaction.atomic
    def return_asset(
        cls,
        *,
        assignment: AssetAssignment,
        actor,
        condition_on_return: str = "",
    ) -> AssetAssignment:
        if assignment.status == AssignmentStatus.RETURNED:
            raise BusinessRuleError("Asset already returned.")
        assignment.status = AssignmentStatus.RETURNED
        assignment.returned_at = timezone.now()
        assignment.condition_on_return = condition_on_return
        assignment.save(update_fields=["status", "returned_at", "condition_on_return", "updated_at"])

        asset = assignment.asset
        asset.status = AssetStatus.AVAILABLE
        asset.save(update_fields=["status", "updated_at"])

        HrmAuditService.log(
            user=actor,
            action="asset_return",
            resource_type="asset_assignment",
            resource_id=str(assignment.public_id),
            summary=f"Asset {asset.asset_number} returned",
        )
        return assignment


class OrgStructureService:
    @staticmethod
    def get_tree(*, company: Company | None = None) -> dict:
        company = company or _default_company()
        departments = Department.objects.filter(
            business_unit__company=company, is_active=True
        ).select_related("business_unit").prefetch_related("employees")

        nodes = []
        for dept in departments:
            employees = [
                {
                    "id": str(emp.public_id),
                    "employeeNumber": emp.employee_number,
                    "fullName": emp.full_name,
                    "jobTitle": emp.job_title,
                    "managerId": str(emp.manager.public_id) if emp.manager_id else None,
                    "status": emp.status,
                }
                for emp in dept.employees.filter(status=EmployeeStatus.ACTIVE)
            ]
            nodes.append(
                {
                    "id": str(dept.public_id),
                    "code": dept.code,
                    "name": dept.name,
                    "businessUnit": dept.business_unit.name,
                    "employees": employees,
                    "headcount": len(employees),
                }
            )
        return {
            "companyId": str(company.public_id),
            "companyName": company.trading_name or company.legal_name,
            "departments": nodes,
            "totalHeadcount": Employee.objects.filter(
                company=company, status=EmployeeStatus.ACTIVE
            ).count(),
        }


class HrmDashboardService:
    @staticmethod
    def get_kpis() -> dict:
        today = timezone.localdate()
        active = Employee.objects.filter(status=EmployeeStatus.ACTIVE).count()
        on_leave = LeaveRequest.objects.filter(
            status=LeaveRequestStatus.APPROVED,
            start_date__lte=today,
            end_date__gte=today,
        ).count()
        clocked_in = AttendanceRecord.objects.filter(
            work_date=today, clock_out__isnull=True
        ).count()
        pending_leave = LeaveRequest.objects.filter(
            status=LeaveRequestStatus.SUBMITTED
        ).count()
        assigned_assets = AssetAssignment.objects.filter(
            status=AssignmentStatus.ASSIGNED
        ).count()

        balances = LeaveBalance.objects.filter(leave_type=LeaveType.ANNUAL).aggregate(
            total=Sum("balance_days"), used=Sum("used_days")
        )
        annual_remaining = float(balances["total"] or 0) - float(balances["used"] or 0)

        return {
            "headcount": active,
            "onLeaveToday": on_leave,
            "clockedInToday": clocked_in,
            "pendingLeaveRequests": pending_leave,
            "activeAssetAssignments": assigned_assets,
            "annualLeaveRemainingDays": round(annual_remaining, 1),
        }
