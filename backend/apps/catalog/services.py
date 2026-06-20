"""Catalog queryset optimizations — split list vs detail paths."""
from django.db.models import Count, Min, Prefetch, Q, QuerySet

from apps.accounts.constants import RoleSlug
from apps.accounts.services import RoleService
from apps.catalog.models import Brand, Category, Product, ProductImage, ProductVariant
from apps.catalog.pricing_helpers import get_retail_price_list
from apps.inventory.models import InventoryLevel
from apps.pricing.models import PriceListItem


class CatalogService:
    SORT_MAP = {
        "newest": ("-created_at",),
        "name": ("name",),
        "price_asc": ("min_price",),
        "price_desc": ("-min_price",),
        "relevance": ("-rank", "-created_at"),
        "featured": ("-average_rating", "-review_count", "-created_at"),
    }

    @staticmethod
    def visible_products_queryset(user=None) -> QuerySet[Product]:
        qs = Product.objects.filter(is_active=True, deleted_at__isnull=True)
        if user and user.is_authenticated and RoleService.has_role(
            user, RoleSlug.TRADE_CUSTOMER
        ):
            return qs.filter(
                visibility__in=[Product.Visibility.PUBLIC, Product.Visibility.TRADE_ONLY]
            )
        return qs.filter(visibility=Product.Visibility.PUBLIC)

    @staticmethod
    def _variant_prefetch(*, price_list, include_inventory: bool = True):
        prefetches = [
            Prefetch(
                "price_list_items",
                queryset=PriceListItem.objects.filter(price_list=price_list)
                if price_list
                else PriceListItem.objects.none(),
                to_attr="_prefetched_price_items",
            ),
        ]
        if include_inventory:
            prefetches.append(
                Prefetch(
                    "inventory_levels",
                    queryset=InventoryLevel.objects.all(),
                    to_attr="_prefetched_inventory_levels",
                )
            )
        return prefetches

    @staticmethod
    def _annotate_min_price(qs: QuerySet[Product], price_list) -> QuerySet[Product]:
        if price_list:
            return qs.annotate(
                min_price=Min(
                    "variants__price_list_items__unit_price_ex_gst_cents",
                    filter=Q(variants__price_list_items__price_list=price_list),
                )
            )
        return qs.annotate(min_price=Min("variants__id"))

    @staticmethod
    def product_list_queryset(*, user=None) -> QuerySet[Product]:
        """Lightweight queryset for list/search — default variant + primary image only."""
        price_list = get_retail_price_list()
        default_variant_qs = (
            ProductVariant.objects.filter(is_active=True, is_default=True)
            .prefetch_related(*CatalogService._variant_prefetch(price_list=price_list))
        )
        primary_image_qs = ProductImage.objects.filter(is_primary=True).order_by(
            "sort_order"
        )

        qs = (
            CatalogService.visible_products_queryset(user)
            .select_related("brand")
            .prefetch_related(
                Prefetch("variants", queryset=default_variant_qs, to_attr="_default_variants"),
                Prefetch("images", queryset=primary_image_qs, to_attr="_primary_images"),
            )
        )
        qs = CatalogService._annotate_min_price(qs, price_list)
        return qs.distinct()

    @staticmethod
    def product_detail_queryset(*, user=None) -> QuerySet[Product]:
        """Full queryset for PDP, compare, and admin — all variants, reviews, categories."""
        price_list = get_retail_price_list()
        variant_qs = ProductVariant.objects.filter(is_active=True).prefetch_related(
            *CatalogService._variant_prefetch(price_list=price_list)
        )

        qs = (
            CatalogService.visible_products_queryset(user)
            .select_related("brand")
            .prefetch_related(
                Prefetch("variants", queryset=variant_qs),
                "images",
                "categories",
                "productcategory_set__category",
                "reviews",
            )
        )
        qs = CatalogService._annotate_min_price(qs, price_list)
        return qs.distinct()

    @staticmethod
    def product_queryset(*, user=None) -> QuerySet[Product]:
        """Backward-compatible alias for detail queryset."""
        return CatalogService.product_detail_queryset(user=user)

    @staticmethod
    def apply_sort(queryset: QuerySet[Product], sort: str | None) -> QuerySet[Product]:
        sort_key = sort or "newest"
        if sort_key == "relevance" and "rank" not in queryset.query.annotations:
            sort_key = "newest"
        ordering = CatalogService.SORT_MAP.get(sort_key, CatalogService.SORT_MAP["newest"])
        return queryset.order_by(*ordering)

    @staticmethod
    def list_products(*, user=None, **filters) -> QuerySet[Product]:
        return CatalogService.product_list_queryset(user=user)

    @staticmethod
    def get_product_by_slug(slug: str, *, user=None) -> Product:
        return CatalogService.product_detail_queryset(user=user).get(slug=slug)

    @staticmethod
    def list_categories(*, parent=None, flat: bool = False) -> QuerySet[Category]:
        qs = Category.objects.filter(is_active=True).annotate(
            product_count=Count(
                "products",
                filter=Q(products__is_active=True, products__deleted_at__isnull=True),
                distinct=True,
            )
        )
        if parent:
            qs = qs.filter(parent__public_id=parent)
        elif not flat:
            qs = qs.filter(parent__isnull=True)
        return qs.prefetch_related(
            Prefetch(
                "children",
                queryset=Category.objects.filter(is_active=True)
                .annotate(
                    product_count=Count(
                        "products",
                        filter=Q(
                            products__is_active=True,
                            products__deleted_at__isnull=True,
                        ),
                        distinct=True,
                    )
                )
                .order_by("sort_order", "name"),
            )
        ).order_by("sort_order", "name")

    @staticmethod
    def list_brands() -> QuerySet[Brand]:
        return (
            Brand.objects.filter(is_active=True)
            .annotate(
                product_count=Count(
                    "products",
                    filter=Q(products__is_active=True, products__deleted_at__isnull=True),
                    distinct=True,
                )
            )
            .order_by("name")
        )

    @staticmethod
    def build_facets(queryset: QuerySet[Product]) -> dict:
        brand_rows = (
            queryset.values("brand__public_id", "brand__name")
            .annotate(count=Count("id", distinct=True))
            .order_by("-count")[:20]
        )
        category_rows = (
            queryset.values("categories__public_id", "categories__name")
            .annotate(count=Count("id", distinct=True))
            .order_by("-count")[:20]
        )
        return {
            "brands": [
                {
                    "id": str(row["brand__public_id"]),
                    "name": row["brand__name"],
                    "count": row["count"],
                }
                for row in brand_rows
                if row["brand__public_id"]
            ],
            "categories": [
                {
                    "id": str(row["categories__public_id"]),
                    "name": row["categories__name"],
                    "count": row["count"],
                }
                for row in category_rows
                if row["categories__public_id"]
            ],
        }
