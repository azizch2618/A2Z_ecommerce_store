"""HRM API serializers — camelCase output."""
from __future__ import annotations

from apps.hrm.models import (
    AssetAssignment,
    AttendanceRecord,
    Employee,
    EmployeeDocument,
    HrmAsset,
    LeaveBalance,
    LeaveRequest,
)


def _user_ref(user) -> dict | None:
    if not user:
        return None
    return {"id": str(user.public_id), "email": user.email}


def serialize_employee(emp: Employee) -> dict:
    return {
        "id": str(emp.public_id),
        "employeeNumber": emp.employee_number,
        "firstName": emp.first_name,
        "lastName": emp.last_name,
        "fullName": emp.full_name,
        "email": emp.email,
        "phone": emp.phone,
        "jobTitle": emp.job_title,
        "employmentType": emp.employment_type,
        "hireDate": emp.hire_date.isoformat(),
        "status": emp.status,
        "dateOfBirth": emp.date_of_birth.isoformat() if emp.date_of_birth else None,
        "emergencyContact": emp.emergency_contact,
        "departmentId": str(emp.department.public_id) if emp.department_id else None,
        "departmentName": emp.department.name if emp.department_id else None,
        "costCenterId": str(emp.cost_center.public_id) if emp.cost_center_id else None,
        "costCenterName": emp.cost_center.name if emp.cost_center_id else None,
        "managerId": str(emp.manager.public_id) if emp.manager_id else None,
        "managerName": emp.manager.full_name if emp.manager_id else None,
        "userId": str(emp.user.public_id) if emp.user_id else None,
    }


def serialize_document(doc: EmployeeDocument) -> dict:
    return {
        "id": str(doc.public_id),
        "documentType": doc.document_type,
        "title": doc.title,
        "fileUrl": doc.file.url if doc.file else None,
        "originalFilename": doc.original_filename,
        "expiryDate": doc.expiry_date.isoformat() if doc.expiry_date else None,
        "notes": doc.notes,
        "uploadedBy": _user_ref(doc.uploaded_by),
        "createdAt": doc.created_at.isoformat(),
    }


def serialize_attendance(record: AttendanceRecord) -> dict:
    return {
        "id": str(record.public_id),
        "employeeId": str(record.employee.public_id),
        "workDate": record.work_date.isoformat(),
        "clockIn": record.clock_in.isoformat(),
        "clockOut": record.clock_out.isoformat() if record.clock_out else None,
        "notes": record.notes,
    }


def serialize_leave_balance(bal: LeaveBalance) -> dict:
    remaining = float(bal.balance_days) - float(bal.used_days)
    return {
        "leaveType": bal.leave_type,
        "balanceDays": float(bal.balance_days),
        "usedDays": float(bal.used_days),
        "remainingDays": round(remaining, 2),
    }


def serialize_leave_request(req: LeaveRequest) -> dict:
    return {
        "id": str(req.public_id),
        "requestNumber": req.request_number,
        "employeeId": str(req.employee.public_id),
        "employeeName": req.employee.full_name,
        "leaveType": req.leave_type,
        "startDate": req.start_date.isoformat(),
        "endDate": req.end_date.isoformat(),
        "days": float(req.days),
        "reason": req.reason,
        "status": req.status,
        "submittedBy": _user_ref(req.submitted_by),
        "approvedBy": _user_ref(req.approved_by),
        "createdAt": req.created_at.isoformat(),
    }


def serialize_asset(asset: HrmAsset) -> dict:
    return {
        "id": str(asset.public_id),
        "assetNumber": asset.asset_number,
        "name": asset.name,
        "category": asset.category,
        "serialNumber": asset.serial_number,
        "status": asset.status,
        "notes": asset.notes,
    }


def serialize_assignment(assignment: AssetAssignment) -> dict:
    return {
        "id": str(assignment.public_id),
        "assetId": str(assignment.asset.public_id),
        "assetNumber": assignment.asset.asset_number,
        "assetName": assignment.asset.name,
        "employeeId": str(assignment.employee.public_id),
        "employeeName": assignment.employee.full_name,
        "status": assignment.status,
        "issuedAt": assignment.issued_at.isoformat(),
        "returnedAt": assignment.returned_at.isoformat() if assignment.returned_at else None,
        "conditionOnIssue": assignment.condition_on_issue,
        "conditionOnReturn": assignment.condition_on_return,
    }
