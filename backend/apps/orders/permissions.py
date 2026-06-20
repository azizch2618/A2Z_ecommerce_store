"""Order access permissions."""
from rest_framework.permissions import BasePermission

from apps.accounts.rbac import PermissionCodename
from apps.accounts.services import PermissionService
from apps.customers.services import CustomerService


class IsOrderOwner(BasePermission):
    def has_object_permission(self, request, view, obj) -> bool:
        customer = CustomerService.get_for_user(request.user)
        return customer is not None and obj.customer_id == customer.id


class IsOrderOwnerOrCanViewOrders(BasePermission):
    """Customer owns the order, or staff has orders.view."""

    def has_object_permission(self, request, view, obj) -> bool:
        if PermissionService.has_permission(request.user, PermissionCodename.ORDERS_VIEW):
            return True
        customer = CustomerService.get_for_user(request.user)
        return customer is not None and obj.customer_id == customer.id
