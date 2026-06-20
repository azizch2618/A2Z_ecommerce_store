"""Inventory list filters."""
import django_filters
from django.db.models import F

from apps.inventory.models import InventoryLevel, InventoryTransaction


class InventoryFilter(django_filters.FilterSet):
    warehouse_code = django_filters.CharFilter(field_name="warehouse__code", lookup_expr="iexact")
    sku = django_filters.CharFilter(field_name="variant__sku", lookup_expr="iexact")
    low_stock = django_filters.BooleanFilter(method="filter_low_stock")

    class Meta:
        model = InventoryLevel
        fields: list[str] = []

    def filter_low_stock(self, queryset, name, value):
        if value is None:
            return queryset
        if value:
            return queryset.filter(quantity_on_hand__lte=F("reorder_point"))
        return queryset.exclude(quantity_on_hand__lte=F("reorder_point"))


class StockMovementFilter(django_filters.FilterSet):
    warehouse_code = django_filters.CharFilter(field_name="warehouse__code", lookup_expr="iexact")
    sku = django_filters.CharFilter(field_name="variant__sku", lookup_expr="iexact")
    transaction_type = django_filters.CharFilter(field_name="transaction_type")
    transfer_group_id = django_filters.UUIDFilter(field_name="transfer_group_id")
    supplier_id = django_filters.UUIDFilter(field_name="supplier__public_id")
    date_from = django_filters.DateFilter(field_name="created_at", lookup_expr="date__gte")
    date_to = django_filters.DateFilter(field_name="created_at", lookup_expr="date__lte")

    class Meta:
        model = InventoryTransaction
        fields: list[str] = []
