"""Customer permissions."""
from rest_framework.permissions import BasePermission


class IsCustomerOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        customer = getattr(request.user, "customer", None)
        return bool(customer and getattr(obj, "customer_id", None) == customer.id)
