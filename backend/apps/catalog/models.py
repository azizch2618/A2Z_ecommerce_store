"""Product catalog models."""
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.db import models

from apps.core.models import PublicIdModel, SoftDeleteModel


class Brand(PublicIdModel):
    name = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(max_length=150, unique=True)
    description = models.TextField(blank=True)
    logo_url = models.URLField(max_length=500, blank=True)
    website_url = models.URLField(max_length=500, blank=True)
    is_authorized_reseller = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "brands"

    def __str__(self) -> str:
        return self.name


class Category(PublicIdModel):
    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="children",
    )
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=150, unique=True)
    description = models.TextField(blank=True)
    image_url = models.URLField(max_length=500, blank=True)
    sort_order = models.IntegerField(default=0)
    depth = models.SmallIntegerField(default=0)
    path = models.CharField(max_length=500, blank=True)
    is_active = models.BooleanField(default=True)
    meta_title = models.CharField(max_length=70, blank=True)
    meta_description = models.CharField(max_length=160, blank=True)

    class Meta:
        db_table = "categories"
        verbose_name_plural = "categories"
        ordering = ["sort_order", "name"]

    def __str__(self) -> str:
        return self.name


class Product(PublicIdModel, SoftDeleteModel):
    class ProductType(models.TextChoices):
        SIMPLE = "simple", "Simple"
        VARIABLE = "variable", "Variable"
        BUNDLE = "bundle", "Bundle"

    class Visibility(models.TextChoices):
        PUBLIC = "public", "Public"
        TRADE_ONLY = "trade_only", "Trade Only"
        HIDDEN = "hidden", "Hidden"

    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, related_name="products")
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    short_description = models.CharField(max_length=500, blank=True)
    product_type = models.CharField(max_length=20, choices=ProductType.choices, default=ProductType.SIMPLE)
    visibility = models.CharField(max_length=20, choices=Visibility.choices, default=Visibility.PUBLIC)
    is_active = models.BooleanField(default=True)
    search_vector = SearchVectorField(null=True, editable=False)
    meta_title = models.CharField(max_length=70, blank=True)
    meta_description = models.CharField(max_length=160, blank=True)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    review_count = models.PositiveIntegerField(default=0)
    highlights = models.JSONField(default=list, blank=True)
    specifications = models.JSONField(default=list, blank=True)
    categories = models.ManyToManyField(Category, through="ProductCategory", related_name="products")

    class Meta:
        db_table = "products"
        indexes = [
            GinIndex(fields=["search_vector"], name="idx_products_fts"),
            models.Index(
                fields=["is_active", "deleted_at", "visibility"],
                name="idx_products_visibility_active",
            ),
        ]

    def __str__(self) -> str:
        return self.name


class ProductCategory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    is_primary = models.BooleanField(default=False)

    class Meta:
        db_table = "product_categories"
        unique_together = [("product", "category")]


class ProductVariant(PublicIdModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="variants")
    sku = models.CharField(max_length=50, unique=True)
    barcode = models.CharField(max_length=50, blank=True)
    name = models.CharField(max_length=255, blank=True)
    weight_grams = models.PositiveIntegerField(null=True, blank=True)
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "product_variants"

    def __str__(self) -> str:
        return self.sku


class ProductReview(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    author_name = models.CharField(max_length=150)
    author_company = models.CharField(max_length=150, blank=True)
    author_role = models.CharField(max_length=100, blank=True)
    rating = models.PositiveSmallIntegerField()
    title = models.CharField(max_length=200)
    body = models.TextField()
    is_verified_purchase = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "product_reviews"
        ordering = ["-created_at"]


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    url = models.URLField(max_length=500)
    alt_text = models.CharField(max_length=255, blank=True)
    sort_order = models.SmallIntegerField(default=0)
    is_primary = models.BooleanField(default=False)

    class Meta:
        db_table = "product_images"
        ordering = ["sort_order"]
