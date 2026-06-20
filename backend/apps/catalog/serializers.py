"""Product catalog serializers."""
from rest_framework import serializers

from apps.catalog.models import Brand, Category, Product, ProductImage, ProductReview, ProductVariant
from apps.catalog.services import CatalogService
from apps.catalog.pricing_helpers import (
    build_price_block,
    build_stock_block,
    get_variant_unit_price_cents,
)


class BrandRefSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="public_id", read_only=True)

    class Meta:
        model = Brand
        fields = ("id", "public_id", "name", "slug", "logo_url")
        read_only_fields = fields


class BrandSerializer(BrandRefSerializer):
    product_count = serializers.IntegerField(read_only=True)

    class Meta(BrandRefSerializer.Meta):
        fields = BrandRefSerializer.Meta.fields + (
            "description",
            "website_url",
            "is_authorized_reseller",
            "product_count",
        )


class CategorySerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="public_id", read_only=True)
    product_count = serializers.IntegerField(read_only=True, default=0)
    children = serializers.SerializerMethodField()

    parent = serializers.SerializerMethodField()
    parent_name = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = (
            "id",
            "public_id",
            "name",
            "slug",
            "description",
            "image_url",
            "sort_order",
            "depth",
            "product_count",
            "children",
            "parent",
            "parent_name",
            "meta_title",
            "meta_description",
        )
        read_only_fields = fields

    def get_parent(self, obj: Category) -> str | None:
        if not obj.parent_id:
            return None
        return str(obj.parent.public_id)

    def get_parent_name(self, obj: Category) -> str | None:
        return obj.parent.name if obj.parent_id else None

    def get_children(self, obj: Category) -> list[dict]:
        if self.context.get("flat"):
            return []
        children = getattr(obj, "_prefetched_objects_cache", {}).get("children")
        if children is None:
            children = obj.children.filter(is_active=True)
        return CategorySerializer(
            children,
            many=True,
            context={**self.context, "flat": False},
        ).data


class ProductImageSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="pk", read_only=True)

    class Meta:
        model = ProductImage
        fields = ("id", "url", "alt_text", "sort_order", "is_primary")
        read_only_fields = fields


class ProductVariantSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="public_id", read_only=True)
    price = serializers.SerializerMethodField()
    stock = serializers.SerializerMethodField()
    dimensions = serializers.SerializerMethodField()
    attributes = serializers.SerializerMethodField()

    class Meta:
        model = ProductVariant
        fields = (
            "id",
            "public_id",
            "sku",
            "barcode",
            "name",
            "price",
            "stock",
            "weight_grams",
            "dimensions",
            "attributes",
            "is_default",
            "is_active",
        )
        read_only_fields = fields

    def get_price(self, obj: ProductVariant) -> dict:
        cents = get_variant_unit_price_cents(obj)
        return build_price_block(cents)

    def get_stock(self, obj: ProductVariant) -> dict:
        return build_stock_block(obj)

    def get_dimensions(self, obj: ProductVariant) -> dict | None:
        return None

    def get_attributes(self, obj: ProductVariant) -> list[dict]:
        return []


class ProductCategorySerializer(serializers.Serializer):
    id = serializers.UUIDField(source="category.public_id")
    name = serializers.CharField(source="category.name")
    slug = serializers.CharField(source="category.slug")
    is_primary = serializers.BooleanField()


class ProductReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductReview
        fields = (
            "id",
            "author_name",
            "author_company",
            "author_role",
            "rating",
            "title",
            "body",
            "is_verified_purchase",
            "created_at",
        )
        read_only_fields = fields


class ProductListSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="public_id", read_only=True)
    brand = BrandRefSerializer(read_only=True)
    primary_image = serializers.SerializerMethodField()
    default_variant = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    stock = serializers.SerializerMethodField()
    badges = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            "id",
            "public_id",
            "name",
            "slug",
            "short_description",
            "brand",
            "primary_image",
            "default_variant",
            "price",
            "stock",
            "badges",
            "average_rating",
            "review_count",
        )
        read_only_fields = fields

    def _get_default_variant(self, obj: Product) -> ProductVariant | None:
        default_variants = getattr(obj, "_default_variants", None)
        if default_variants:
            return default_variants[0]
        variants = list(obj.variants.all())
        if not variants:
            return None
        for variant in variants:
            if variant.is_default:
                return variant
        return variants[0]

    def get_primary_image(self, obj: Product) -> dict | None:
        primary_images = getattr(obj, "_primary_images", None)
        if primary_images:
            image = primary_images[0]
            return {"url": image.url, "alt_text": image.alt_text or None}
        images = list(obj.images.all())
        if not images:
            return None
        image = next((img for img in images if img.is_primary), images[0])
        return {"url": image.url, "alt_text": image.alt_text or None}

    def get_default_variant(self, obj: Product) -> dict | None:
        variant = self._get_default_variant(obj)
        if not variant:
            return None
        return {
            "id": str(variant.public_id),
            "sku": variant.sku,
        }

    def get_price(self, obj: Product) -> dict:
        variant = self._get_default_variant(obj)
        cents = get_variant_unit_price_cents(variant) if variant else 0
        return build_price_block(cents)

    def get_stock(self, obj: Product) -> dict:
        variant = self._get_default_variant(obj)
        return build_stock_block(variant) if variant else {
            "status": "out_of_stock",
            "quantity_available": 0,
            "lead_time_days": None,
        }

    def get_badges(self, obj: Product) -> list[str]:
        badges: list[str] = []
        if obj.visibility == Product.Visibility.TRADE_ONLY:
            badges.append("trade_only")
        variant = self._get_default_variant(obj)
        if variant:
            stock = build_stock_block(variant)
            if stock["status"] == "low_stock":
                badges.append("low_stock")
        return badges


class ProductDetailSerializer(ProductListSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    categories = serializers.SerializerMethodField()
    documents = serializers.SerializerMethodField()
    attributes = serializers.SerializerMethodField()
    highlights = serializers.JSONField(read_only=True)
    reviews = serializers.SerializerMethodField()
    related_products = serializers.SerializerMethodField()

    class Meta(ProductListSerializer.Meta):
        fields = ProductListSerializer.Meta.fields + (
            "description",
            "product_type",
            "visibility",
            "images",
            "variants",
            "categories",
            "documents",
            "attributes",
            "highlights",
            "reviews",
            "related_products",
            "meta_title",
            "meta_description",
        )

    def get_categories(self, obj: Product) -> list[dict]:
        links = list(obj.productcategory_set.all())
        return ProductCategorySerializer(links, many=True).data

    def get_documents(self, obj: Product) -> list[dict]:
        return []

    def get_attributes(self, obj: Product) -> list[dict]:
        specs = obj.specifications or []
        return [
            {
                "group": group.get("group", "Specifications"),
                "items": [
                    {"name": item.get("label", item.get("name", "")), "value": item.get("value", "")}
                    for item in group.get("items", [])
                ],
            }
            for group in specs
        ]

    def get_reviews(self, obj: Product) -> list[dict]:
        reviews = obj.reviews.all()[:20]
        return ProductReviewSerializer(reviews, many=True).data

    def get_related_products(self, obj: Product) -> list[dict]:
        category_ids = obj.categories.values_list("id", flat=True)
        if not category_ids:
            return []
        request = self.context.get("request")
        user = request.user if request and request.user.is_authenticated else None
        related = (
            CatalogService.product_list_queryset(user=user)
            .filter(
                categories__in=category_ids,
                visibility=obj.visibility,
            )
            .exclude(pk=obj.pk)
            .distinct()[:4]
        )
        return ProductListSerializer(related, many=True, context=self.context).data
