"""Catalog query filters."""
import django_filters
from django.contrib.postgres.search import SearchQuery, SearchRank
from django.db.models import F, Q

from apps.catalog.models import Brand, Category, Product
from apps.catalog.pricing_helpers import get_retail_price_list
from apps.inventory.models import InventoryLevel
from apps.pricing.models import PriceListItem


class ProductFilter(django_filters.FilterSet):
    category = django_filters.UUIDFilter(field_name="categories__public_id")
    brand = django_filters.UUIDFilter(field_name="brand__public_id")
    search = django_filters.CharFilter(method="filter_search")
    min_price = django_filters.NumberFilter(method="filter_min_price")
    max_price = django_filters.NumberFilter(method="filter_max_price")
    in_stock = django_filters.BooleanFilter(method="filter_in_stock")
    sort = django_filters.CharFilter(method="filter_sort")

    class Meta:
        model = Product
        fields: list[str] = []

    def filter_search(self, queryset, name, value):
        if not value:
            return queryset

        text_q = (
            Q(name__icontains=value)
            | Q(short_description__icontains=value)
            | Q(variants__sku__icontains=value)
        )

        from django.db import connection

        if connection.vendor != "postgresql":
            return queryset.filter(text_q).distinct()

        query = SearchQuery(value, search_type="websearch", config="english")
        ranked = queryset.annotate(
            rank=SearchRank("search_vector", query),
        ).filter(Q(search_vector=query) | text_q)
        setattr(self.request, "_catalog_sort", "relevance")
        return ranked.distinct()

    def filter_min_price(self, queryset, name, value):
        if value is None:
            return queryset
        price_list = get_retail_price_list()
        if not price_list:
            return queryset.none()
        variant_ids = PriceListItem.objects.filter(
            price_list=price_list,
            unit_price_ex_gst_cents__gte=int(value),
        ).values_list("variant_id", flat=True)
        return queryset.filter(variants__id__in=variant_ids).distinct()

    def filter_max_price(self, queryset, name, value):
        if value is None:
            return queryset
        price_list = get_retail_price_list()
        if not price_list:
            return queryset.none()
        variant_ids = PriceListItem.objects.filter(
            price_list=price_list,
            unit_price_ex_gst_cents__lte=int(value),
        ).values_list("variant_id", flat=True)
        return queryset.filter(variants__id__in=variant_ids).distinct()

    def filter_in_stock(self, queryset, name, value):
        if value is None:
            return queryset

        stocked_variant_ids = InventoryLevel.objects.filter(
            quantity_on_hand__gt=F("quantity_reserved"),
        ).values_list("variant_id", flat=True)

        if value:
            return queryset.filter(variants__id__in=stocked_variant_ids).distinct()
        return queryset.exclude(variants__id__in=stocked_variant_ids).distinct()

    def filter_sort(self, queryset, name, value):
        setattr(self.request, "_catalog_sort", value)
        return queryset


class CategoryFilter(django_filters.FilterSet):
    parent = django_filters.UUIDFilter(field_name="parent__public_id")
    depth = django_filters.NumberFilter(field_name="depth")
    flat = django_filters.BooleanFilter(method="filter_flat")
    search = django_filters.CharFilter(field_name="name", lookup_expr="icontains")

    class Meta:
        model = Category
        fields: list[str] = []

    def filter_flat(self, queryset, name, value):
        setattr(self.request, "_category_flat", bool(value))
        return queryset


class BrandFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method="filter_search")
    featured = django_filters.BooleanFilter(method="filter_featured")

    class Meta:
        model = Brand
        fields: list[str] = []

    def filter_search(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(
            Q(name__icontains=value) | Q(description__icontains=value)
        )

    def filter_featured(self, queryset, name, value):
        if value is None:
            return queryset
        return queryset.filter(is_authorized_reseller=value)
