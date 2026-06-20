"""ERP platform API permissions."""
from apps.core.permissions import IsStaffUser


class IsPlatformStaff(IsStaffUser):
    """Staff access to ERP foundation platform endpoints."""
