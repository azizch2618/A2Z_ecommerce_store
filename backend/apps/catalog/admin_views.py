"""Admin CRUD for catalog categories and brands."""
from __future__ import annotations

from django.db.models import Count, Q
from django.utils.text import slugify
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import CanManageCatalog, CanViewCatalog
from apps.catalog.admin_product_service import (
    admin_product_queryset,
    create_admin_product,
    delete_admin_product,
    serialize_admin_product,
    update_admin_product,
)
from apps.catalog.models import Brand, Category
from apps.catalog.serializers import BrandSerializer, CategorySerializer
from apps.core.audit import log_operation
from apps.core.exceptions import ConflictError, NotFoundError
from apps.core.models import OperationalAuditLog
from apps.core.pagination import A2ZCursorPagination


class AdminPagination(A2ZCursorPagination):
    ordering = "name"


class AdminCategoryListCreateView(generics.ListCreateAPIView):
    """GET/POST /catalog/admin/categories/"""

    serializer_class = CategorySerializer
    pagination_class = AdminPagination
    filterset_fields: list[str] = []

    def get_permissions(self):
        if self.request.method == "POST":
            return [CanManageCatalog()]
        return [CanViewCatalog()]

    def get_queryset(self):
        search = self.request.query_params.get("search", "").strip()
        qs = (
            Category.objects.filter(is_active=True)
            .annotate(
                product_count=Count(
                    "products",
                    filter=Q(products__is_active=True, products__deleted_at__isnull=True),
                    distinct=True,
                )
            )
            .select_related("parent")
            .order_by("sort_order", "name")
        )
        if search:
            qs = qs.filter(name__icontains=search)
        status_filter = self.request.query_params.get("status")
        if status_filter == "inactive":
            qs = Category.objects.filter(is_active=False).annotate(
                product_count=Count("products", distinct=True)
            )
        return qs

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["flat"] = True
        return context

    def create(self, request, *args, **kwargs):
        name = request.data.get("name", "").strip()
        if not name:
            return Response({"name": ["This field is required."]}, status=status.HTTP_400_BAD_REQUEST)

        slug = request.data.get("slug") or slugify(name)
        parent_id = request.data.get("parent_id")
        parent = None
        if parent_id:
            parent = Category.objects.filter(public_id=parent_id).first()
            if not parent:
                raise NotFoundError("Parent category not found.")

        if Category.objects.filter(slug=slug).exists():
            raise ConflictError("Category slug already exists.")

        category = Category.objects.create(
            name=name,
            slug=slug,
            description=request.data.get("description", ""),
            parent=parent,
            sort_order=int(request.data.get("sort_order", 0)),
            is_active=request.data.get("is_active", True),
        )
        log_operation(
            user=request.user,
            module=OperationalAuditLog.Module.CATALOG,
            action="create",
            resource_type="category",
            resource_id=category.public_id,
            details={"name": category.name},
        )
        category.product_count = 0
        return Response(CategorySerializer(category, context={"flat": True}).data, status=status.HTTP_201_CREATED)


class AdminCategoryDetailView(APIView):
    """PATCH/DELETE /catalog/admin/categories/{id}/"""

    permission_classes = [CanManageCatalog]

    def _get_category(self, category_id):
        category = Category.objects.filter(public_id=category_id).first()
        if not category:
            raise NotFoundError("Category not found.")
        return category

    def patch(self, request, category_id):
        category = self._get_category(category_id)
        if "name" in request.data:
            category.name = request.data["name"]
        if "slug" in request.data:
            category.slug = request.data["slug"]
        if "description" in request.data:
            category.description = request.data["description"]
        if "sort_order" in request.data:
            category.sort_order = int(request.data["sort_order"])
        if "is_active" in request.data:
            category.is_active = bool(request.data["is_active"])
        if "parent_id" in request.data:
            parent_id = request.data["parent_id"]
            if parent_id:
                category.parent = Category.objects.filter(public_id=parent_id).first()
            else:
                category.parent = None
        category.save()
        log_operation(
            user=request.user,
            module=OperationalAuditLog.Module.CATALOG,
            action="update",
            resource_type="category",
            resource_id=category.public_id,
            details=request.data,
        )
        return Response(CategorySerializer(category, context={"flat": True}).data)

    def delete(self, request, category_id):
        category = self._get_category(category_id)
        category.is_active = False
        category.save(update_fields=["is_active", "updated_at"])
        log_operation(
            user=request.user,
            module=OperationalAuditLog.Module.CATALOG,
            action="deactivate",
            resource_type="category",
            resource_id=category.public_id,
        )
        return Response(status=status.HTTP_204_NO_CONTENT)


class AdminBrandListCreateView(generics.ListCreateAPIView):
    """GET/POST /catalog/admin/brands/"""

    serializer_class = BrandSerializer
    pagination_class = AdminPagination

    def get_permissions(self):
        if self.request.method == "POST":
            return [CanManageCatalog()]
        return [CanViewCatalog()]

    def get_queryset(self):
        search = self.request.query_params.get("search", "").strip()
        qs = (
            Brand.objects.annotate(
                product_count=Count(
                    "products",
                    filter=Q(products__is_active=True, products__deleted_at__isnull=True),
                    distinct=True,
                )
            )
            .order_by("name")
        )
        if search:
            qs = qs.filter(name__icontains=search)
        status_filter = self.request.query_params.get("status")
        if status_filter == "active":
            qs = qs.filter(is_active=True)
        elif status_filter == "inactive":
            qs = qs.filter(is_active=False)
        return qs

    def create(self, request, *args, **kwargs):
        name = request.data.get("name", "").strip()
        if not name:
            return Response({"name": ["This field is required."]}, status=status.HTTP_400_BAD_REQUEST)

        slug = request.data.get("slug") or slugify(name)
        if Brand.objects.filter(slug=slug).exists():
            raise ConflictError("Brand slug already exists.")

        brand = Brand.objects.create(
            name=name,
            slug=slug,
            description=request.data.get("description", ""),
            logo_url=request.data.get("logo_url", ""),
            website_url=request.data.get("website_url", ""),
            is_authorized_reseller=request.data.get("is_authorized_reseller", True),
            is_active=request.data.get("is_active", True),
        )
        brand.product_count = 0
        log_operation(
            user=request.user,
            module=OperationalAuditLog.Module.CATALOG,
            action="create",
            resource_type="brand",
            resource_id=brand.public_id,
            details={"name": brand.name},
        )
        return Response(BrandSerializer(brand).data, status=status.HTTP_201_CREATED)


class AdminBrandDetailView(APIView):
    """PATCH/DELETE /catalog/admin/brands/{id}/"""

    permission_classes = [CanManageCatalog]

    def _get_brand(self, brand_id):
        brand = Brand.objects.filter(public_id=brand_id).first()
        if not brand:
            raise NotFoundError("Brand not found.")
        return brand

    def patch(self, request, brand_id):
        brand = self._get_brand(brand_id)
        for field in ("name", "slug", "description", "logo_url", "website_url"):
            if field in request.data:
                setattr(brand, field, request.data[field])
        if "is_active" in request.data:
            brand.is_active = bool(request.data["is_active"])
        if "is_authorized_reseller" in request.data:
            brand.is_authorized_reseller = bool(request.data["is_authorized_reseller"])
        if "featured" in request.data:
            brand.is_authorized_reseller = bool(request.data["featured"])
        brand.save()
        log_operation(
            user=request.user,
            module=OperationalAuditLog.Module.CATALOG,
            action="update",
            resource_type="brand",
            resource_id=brand.public_id,
            details=request.data,
        )
        return Response(BrandSerializer(brand).data)

    def delete(self, request, brand_id):
        brand = self._get_brand(brand_id)
        brand.is_active = False
        brand.save(update_fields=["is_active", "updated_at"])
        log_operation(
            user=request.user,
            module=OperationalAuditLog.Module.CATALOG,
            action="deactivate",
            resource_type="brand",
            resource_id=brand.public_id,
        )
        return Response(status=status.HTTP_204_NO_CONTENT)


class AdminProductListCreateView(generics.ListCreateAPIView):
    """GET/POST /admin/products/"""

    pagination_class = AdminPagination
    filterset_fields: list[str] = []

    def get_permissions(self):
        if self.request.method == "POST":
            return [CanManageCatalog()]
        return [CanViewCatalog()]

    def get_queryset(self):
        qs = admin_product_queryset()
        search = self.request.query_params.get("search", "").strip()
        if search:
            qs = qs.filter(
                Q(name__icontains=search)
                | Q(variants__sku__icontains=search)
                | Q(brand__name__icontains=search)
            ).distinct()
        status_filter = self.request.query_params.get("status")
        if status_filter == "active":
            qs = qs.filter(is_active=True)
        elif status_filter == "inactive":
            qs = qs.filter(is_active=False)
        return qs

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        rows = [serialize_admin_product(product) for product in (page or queryset)]
        if page is not None:
            return self.get_paginated_response(rows)
        return Response({"data": rows})

    def create(self, request, *args, **kwargs):
        product = create_admin_product(request.data)
        log_operation(
            user=request.user,
            module=OperationalAuditLog.Module.CATALOG,
            action="create",
            resource_type="product",
            resource_id=product.public_id,
            details={"name": product.name, "slug": product.slug},
        )
        return Response(serialize_admin_product(product), status=status.HTTP_201_CREATED)


class AdminProductDetailView(APIView):
    """GET/PATCH/DELETE /admin/products/{id}/"""

    def get_permissions(self):
        if self.request.method == "GET":
            return [CanViewCatalog()]
        return [CanManageCatalog()]

    def _get_product(self, product_id):
        product = admin_product_queryset().filter(public_id=product_id).first()
        if not product:
            raise NotFoundError("Product not found.")
        return product

    def get(self, request, product_id):
        product = self._get_product(product_id)
        return Response(serialize_admin_product(product))

    def patch(self, request, product_id):
        product = self._get_product(product_id)
        product = update_admin_product(product, request.data)
        log_operation(
            user=request.user,
            module=OperationalAuditLog.Module.CATALOG,
            action="update",
            resource_type="product",
            resource_id=product.public_id,
            details=request.data,
        )
        return Response(serialize_admin_product(product))

    def delete(self, request, product_id):
        product = self._get_product(product_id)
        delete_admin_product(product)
        log_operation(
            user=request.user,
            module=OperationalAuditLog.Module.CATALOG,
            action="delete",
            resource_type="product",
            resource_id=product.public_id,
        )
        return Response(status=status.HTTP_204_NO_CONTENT)
