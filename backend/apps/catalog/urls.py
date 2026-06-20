from django.urls import path

from apps.catalog.admin_views import (
    AdminBrandDetailView,
    AdminBrandListCreateView,
    AdminCategoryDetailView,
    AdminCategoryListCreateView,
)
from apps.catalog.views import (
    BrandListView,
    CategoryListView,
    ProductCompareView,
    ProductDetailView,
    ProductListView,
    ProductReviewsView,
    ProductSearchView,
)

app_name = "catalog"

urlpatterns = [
    path("products/", ProductListView.as_view(), name="product-list"),
    path("products/search/", ProductSearchView.as_view(), name="product-search"),
    path("products/compare/", ProductCompareView.as_view(), name="product-compare"),
    path("products/<slug:slug>/", ProductDetailView.as_view(), name="product-detail"),
    path("products/<slug:slug>/reviews/", ProductReviewsView.as_view(), name="product-reviews"),
    path("categories/", CategoryListView.as_view(), name="category-list"),
    path("brands/", BrandListView.as_view(), name="brand-list"),
    path("admin/categories/", AdminCategoryListCreateView.as_view(), name="admin-category-list"),
    path(
        "admin/categories/<uuid:category_id>/",
        AdminCategoryDetailView.as_view(),
        name="admin-category-detail",
    ),
    path("admin/brands/", AdminBrandListCreateView.as_view(), name="admin-brand-list"),
    path(
        "admin/brands/<uuid:brand_id>/",
        AdminBrandDetailView.as_view(),
        name="admin-brand-detail",
    ),
]
