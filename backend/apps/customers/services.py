"""Customer domain services."""
from apps.accounts.models import User
from apps.customers.models import Customer


class CustomerService:
    @staticmethod
    def create_for_user(user: User, customer_type: str = "retail") -> Customer:
        return Customer.objects.create(user=user, customer_type=customer_type)

    @staticmethod
    def get_for_user(user: User) -> Customer | None:
        return Customer.objects.filter(user=user).select_related("organization").first()
