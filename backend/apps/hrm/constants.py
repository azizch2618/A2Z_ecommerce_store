from django.db import models


class EmploymentType(models.TextChoices):
    FULL_TIME = "full_time", "Full Time"
    PART_TIME = "part_time", "Part Time"
    CASUAL = "casual", "Casual"
    CONTRACTOR = "contractor", "Contractor"


class EmployeeStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    ON_LEAVE = "on_leave", "On Leave"
    SUSPENDED = "suspended", "Suspended"
    TERMINATED = "terminated", "Terminated"


class EmployeeDocumentType(models.TextChoices):
    CONTRACT = "contract", "Contract"
    CERTIFICATION = "certification", "Certification"
    LICENSE = "license", "License"
    OTHER = "other", "Other"


class LeaveType(models.TextChoices):
    ANNUAL = "annual", "Annual Leave"
    SICK = "sick", "Sick Leave"
    UNPAID = "unpaid", "Unpaid Leave"


class LeaveRequestStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    SUBMITTED = "submitted", "Submitted"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"
    CANCELLED = "cancelled", "Cancelled"


class AssetCategory(models.TextChoices):
    LAPTOP = "laptop", "Laptop"
    PHONE = "phone", "Phone"
    TOOL = "tool", "Tool"
    VEHICLE = "vehicle", "Vehicle"
    OTHER = "other", "Other"


class AssetStatus(models.TextChoices):
    AVAILABLE = "available", "Available"
    ASSIGNED = "assigned", "Assigned"
    MAINTENANCE = "maintenance", "Maintenance"
    RETIRED = "retired", "Retired"


class AssignmentStatus(models.TextChoices):
    ASSIGNED = "assigned", "Assigned"
    RETURNED = "returned", "Returned"
