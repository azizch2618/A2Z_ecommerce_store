"""Order list filters."""
import django_filters

from apps.orders.models import Order


class OrderFilter(django_filters.FilterSet):
    status = django_filters.ChoiceFilter(choices=Order.Status.choices)
    from_date = django_filters.DateFilter(field_name="placed_at", lookup_expr="date__gte")
    to_date = django_filters.DateFilter(field_name="placed_at", lookup_expr="date__lte")

    class Meta:
        model = Order
        fields = ["status", "from_date", "to_date"]
