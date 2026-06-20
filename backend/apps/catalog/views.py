"""Catalog API views."""
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.catalog.filters import BrandFilter, CategoryFilter, ProductFilter
from apps.catalog.models import Brand, Category, Product, ProductReview
from apps.catalog.permissions import IsCatalogReadOnly
from apps.catalog.serializers import (
    BrandSerializer,
    CategorySerializer,
    ProductDetailSerializer,
    ProductListSerializer,
    ProductReviewSerializer,
)
from apps.catalog.services import CatalogService
from apps.core.cache_utils import (
    CACHE_TTL_CATALOG_LIST,
    build_cache_key,
    cache_get_or_set,
)
from apps.core.pagination import A2ZCursorPagination


class ProductPagination(A2ZCursorPagination):
    ordering = "-created_at"


class ProductListView(generics.ListAPIView):
    """GET /products — list, filter, search, sort, paginate."""

    serializer_class = ProductListSerializer
    permission_classes = [IsCatalogReadOnly]
    pagination_class = ProductPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = ProductFilter
    ordering_fields = ("created_at", "name", "min_price", "average_rating")
    ordering = ("-created_at",)

    def get_queryset(self):
        user = self.request.user if self.request.user.is_authenticated else None
        return CatalogService.product_list_queryset(user=user)

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        sort = getattr(self.request, "_catalog_sort", None) or self.request.query_params.get(
            "sort"
        )
        return CatalogService.apply_sort(queryset, sort)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        facets = CatalogService.build_facets(queryset)
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        response = self.get_paginated_response(serializer.data)
        response.data["facets"] = facets
        return response


class ProductDetailView(generics.RetrieveAPIView):
    """GET /products/{slug} — full product detail."""

    serializer_class = ProductDetailSerializer
    permission_classes = [IsCatalogReadOnly]
    lookup_field = "slug"

    def get_queryset(self):
        user = self.request.user if self.request.user.is_authenticated else None
        return CatalogService.product_detail_queryset(user=user)


class CategoryListView(generics.ListAPIView):
    """GET /categories — category tree with optional filters."""

    serializer_class = CategorySerializer
    permission_classes = [IsCatalogReadOnly]
    pagination_class = ProductPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = CategoryFilter
    ordering_fields = ("sort_order", "name")
    ordering = ("sort_order", "name")

    def get_queryset(self):
        flat = getattr(self.request, "_category_flat", False) or (
            self.request.query_params.get("flat", "").lower() == "true"
        )
        parent = self.request.query_params.get("parent")
        return CatalogService.list_categories(parent=parent, flat=flat)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["flat"] = getattr(self.request, "_category_flat", False) or (
            self.request.query_params.get("flat", "").lower() == "true"
        )
        return context

    def list(self, request, *args, **kwargs):
        flat = getattr(request, "_category_flat", False) or (
            request.query_params.get("flat", "").lower() == "true"
        )
        parent = request.query_params.get("parent", "")
        search = request.query_params.get("search", "")
        cursor = request.query_params.get("cursor", "")
        limit = request.query_params.get("limit", "")
        cache_key = build_cache_key(
            "categories",
            parent=parent,
            flat=flat,
            search=search,
            cursor=cursor,
            limit=limit,
        )

        def build_response() -> dict:
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data).data

        return Response(
            cache_get_or_set(cache_key, build_response, timeout=CACHE_TTL_CATALOG_LIST)
        )


class BrandListView(generics.ListAPIView):
    """GET /brands — list brands with search and pagination."""

    serializer_class = BrandSerializer
    permission_classes = [IsCatalogReadOnly]
    pagination_class = ProductPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = BrandFilter
    ordering_fields = ("name", "product_count")
    ordering = ("name",)

    def get_queryset(self):
        return CatalogService.list_brands()

    def list(self, request, *args, **kwargs):
        search = request.query_params.get("search", "")
        featured = request.query_params.get("featured", "")
        cursor = request.query_params.get("cursor", "")
        limit = request.query_params.get("limit", "")
        cache_key = build_cache_key(
            "brands",
            search=search,
            featured=featured,
            cursor=cursor,
            limit=limit,
        )

        def build_response() -> dict:
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data).data

        return Response(
            cache_get_or_set(cache_key, build_response, timeout=CACHE_TTL_CATALOG_LIST)
        )


class ProductSearchView(APIView):
    """GET /products/search — predictive search for storefront."""

    permission_classes = [IsCatalogReadOnly]

    def get(self, request):
        query = request.query_params.get("q", "").strip()
        limit = min(int(request.query_params.get("limit", 8)), 20)
        if len(query) < 2:
            return Response({"query": query, "products": [], "categories": [], "brands": []})

        user = request.user if request.user.is_authenticated else None
        products_qs = CatalogService.product_list_queryset(user=user)
        product_filter = ProductFilter(
            data={"search": query},
            queryset=products_qs,
            request=request,
        )
        products = list(product_filter.qs.distinct()[:limit])

        categories = (
            Category.objects.filter(is_active=True, name__icontains=query)
            .order_by("name")[:5]
        )
        brands = (
            Brand.objects.filter(is_active=True, name__icontains=query)
            .order_by("name")[:5]
        )

        list_serializer = ProductListSerializer()
        product_rows = []
        for product in products:
            variant = list_serializer._get_default_variant(product)
            primary_images = getattr(product, "_primary_images", None)
            image = primary_images[0] if primary_images else None
            from apps.catalog.pricing_helpers import build_price_block, get_variant_unit_price_cents

            cents = get_variant_unit_price_cents(variant) if variant else 0
            product_rows.append(
                {
                    "id": str(product.public_id),
                    "name": product.name,
                    "slug": product.slug,
                    "sku": variant.sku if variant else "",
                    "image_url": image.url if image else None,
                    "price": build_price_block(cents),
                }
            )

        return Response(
            {
                "query": query,
                "products": product_rows,
                "categories": [
                    {
                        "id": str(category.public_id),
                        "name": category.name,
                        "slug": category.slug,
                    }
                    for category in categories
                ],
                "brands": [
                    {
                        "id": str(brand.public_id),
                        "name": brand.name,
                        "slug": brand.slug,
                    }
                    for brand in brands
                ],
            }
        )


class ProductCompareView(APIView):
    """POST /products/compare — side-by-side product comparison."""

    permission_classes = [IsCatalogReadOnly]

    def post(self, request):
        product_ids = request.data.get("product_ids", [])
        slugs = request.data.get("slugs", [])
        if not product_ids and not slugs:
            return Response(
                {"error": "product_ids or slugs required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = request.user if request.user.is_authenticated else None
        qs = CatalogService.product_detail_queryset(user=user)
        if product_ids:
            qs = qs.filter(public_id__in=product_ids)
        elif slugs:
            qs = qs.filter(slug__in=slugs)

        products = list(qs[:4])
        serializer = ProductDetailSerializer(products, many=True, context={"request": request})

        comparison_attributes: list[dict[str, str]] = []
        seen_keys: set[str] = set()
        for product in products:
            for group in product.specifications or []:
                for item in group.get("items", []):
                    label = item.get("label") or item.get("name", "")
                    if not label or label in seen_keys:
                        continue
                    seen_keys.add(label)
                    comparison_attributes.append({"key": label, "label": label})

        return Response(
            {
                "products": serializer.data,
                "comparison_attributes": comparison_attributes,
            }
        )


class ProductReviewsView(generics.ListAPIView):
    """GET /products/{slug}/reviews — paginated product reviews."""

    serializer_class = ProductReviewSerializer
    permission_classes = [IsCatalogReadOnly]
    pagination_class = ProductPagination

    def get_queryset(self):
        user = self.request.user if self.request.user.is_authenticated else None
        product = (
            CatalogService.visible_products_queryset(user)
            .filter(slug=self.kwargs["slug"])
            .first()
        )
        if not product:
            return ProductReview.objects.none()
        return product.reviews.all()
