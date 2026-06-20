from django.db import models


class BinType(models.TextChoices):
    PICK = "pick", "Pick Face"
    BULK = "bulk", "Bulk Storage"
    STAGING = "staging", "Staging"
    RECEIVING = "receiving", "Receiving Dock"


class TransferType(models.TextChoices):
    WAREHOUSE = "warehouse", "Warehouse to Warehouse"
    BIN = "bin", "Bin to Bin"


class TransferStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    SUBMITTED = "submitted", "Submitted"
    APPROVED = "approved", "Approved"
    IN_TRANSIT = "in_transit", "In Transit"
    COMPLETED = "completed", "Completed"
    CANCELLED = "cancelled", "Cancelled"


class PickListStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    ASSIGNED = "assigned", "Assigned"
    PICKING = "picking", "Picking"
    PICKED = "picked", "Picked"
    COMPLETED = "completed", "Completed"


class PutawayStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    IN_PROGRESS = "in_progress", "In Progress"
    COMPLETED = "completed", "Completed"


class CycleCountStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    IN_PROGRESS = "in_progress", "In Progress"
    COMPLETED = "completed", "Completed"


class AdjustmentStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    SUBMITTED = "submitted", "Submitted"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"
    APPLIED = "applied", "Applied"
