"""HRM core models — employees, attendance, leave, assets."""
from django.db import models

from apps.core.models import PublicIdModel
from apps.hrm.constants import (
    AssetCategory,
    AssetStatus,
    AssignmentStatus,
    EmployeeDocumentType,
    EmployeeStatus,
    EmploymentType,
    LeaveRequestStatus,
    LeaveType,
)


class Employee(PublicIdModel):
    employee_number = models.CharField(max_length=30, unique=True)
    user = models.OneToOneField(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employee_profile",
    )
    party = models.OneToOneField(
        "erp.Party",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employee",
    )
    company = models.ForeignKey(
        "erp.Company",
        on_delete=models.RESTRICT,
        related_name="employees",
    )
    department = models.ForeignKey(
        "erp.Department",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employees",
    )
    cost_center = models.ForeignKey(
        "erp.CostCenter",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employees",
    )
    manager = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="direct_reports",
    )
    job_title = models.CharField(max_length=100)
    employment_type = models.CharField(max_length=20, choices=EmploymentType.choices)
    hire_date = models.DateField()
    termination_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=EmployeeStatus.choices,
        default=EmployeeStatus.ACTIVE,
        db_index=True,
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    emergency_contact = models.JSONField(default=dict, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "hrm_employees"
        ordering = ["last_name", "first_name"]
        indexes = [
            models.Index(fields=["status", "department"], name="idx_hrm_emp_status_dept"),
        ]

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    def __str__(self) -> str:
        return f"{self.employee_number} — {self.full_name}"


class EmployeeDocument(PublicIdModel):
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="documents",
    )
    document_type = models.CharField(max_length=20, choices=EmployeeDocumentType.choices)
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to="employee_documents/%Y/%m/")
    original_filename = models.CharField(max_length=255, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    uploaded_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="uploaded_employee_documents",
    )

    class Meta:
        db_table = "hrm_employee_documents"
        ordering = ["-created_at"]


class AttendanceRecord(PublicIdModel):
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="attendance_records",
    )
    work_date = models.DateField(db_index=True)
    clock_in = models.DateTimeField()
    clock_out = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = "hrm_attendance_records"
        ordering = ["-work_date", "-clock_in"]
        indexes = [
            models.Index(fields=["employee", "work_date"], name="idx_hrm_att_emp_date"),
        ]


class LeaveBalance(PublicIdModel):
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="leave_balances",
    )
    leave_type = models.CharField(max_length=20, choices=LeaveType.choices)
    balance_days = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    used_days = models.DecimalField(max_digits=6, decimal_places=2, default=0)

    class Meta:
        db_table = "hrm_leave_balances"
        unique_together = [("employee", "leave_type")]


class LeaveRequest(PublicIdModel):
    request_number = models.CharField(max_length=30, unique=True)
    employee = models.ForeignKey(
        Employee,
        on_delete=models.RESTRICT,
        related_name="leave_requests",
    )
    leave_type = models.CharField(max_length=20, choices=LeaveType.choices)
    start_date = models.DateField()
    end_date = models.DateField()
    days = models.DecimalField(max_digits=5, decimal_places=2)
    reason = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=LeaveRequestStatus.choices,
        default=LeaveRequestStatus.DRAFT,
        db_index=True,
    )
    submitted_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="submitted_leave_requests",
    )
    approved_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_leave_requests",
    )

    class Meta:
        db_table = "hrm_leave_requests"
        ordering = ["-start_date", "-created_at"]


class HrmAsset(PublicIdModel):
    asset_number = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=20, choices=AssetCategory.choices)
    serial_number = models.CharField(max_length=100, blank=True)
    status = models.CharField(
        max_length=20,
        choices=AssetStatus.choices,
        default=AssetStatus.AVAILABLE,
    )
    notes = models.TextField(blank=True)

    class Meta:
        db_table = "hrm_assets"
        ordering = ["asset_number"]


class AssetAssignment(PublicIdModel):
    asset = models.ForeignKey(
        HrmAsset,
        on_delete=models.RESTRICT,
        related_name="assignments",
    )
    employee = models.ForeignKey(
        Employee,
        on_delete=models.RESTRICT,
        related_name="asset_assignments",
    )
    status = models.CharField(
        max_length=20,
        choices=AssignmentStatus.choices,
        default=AssignmentStatus.ASSIGNED,
    )
    issued_at = models.DateTimeField()
    returned_at = models.DateTimeField(null=True, blank=True)
    condition_on_issue = models.CharField(max_length=255, blank=True)
    condition_on_return = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)
    issued_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="issued_asset_assignments",
    )

    class Meta:
        db_table = "hrm_asset_assignments"
        ordering = ["-issued_at"]
