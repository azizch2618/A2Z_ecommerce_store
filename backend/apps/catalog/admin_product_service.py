"""Admin product CRUD — create, update, delete with pricing, stock, and images."""
from __future__ import annotations

from django.core.cache import cache
from django.db import transaction
from django.db.models import Prefetch
from django.utils import timezone
from django.utils.text import slugify

from apps.catalog.models import (
    Brand,
    Category,
    Product,
    ProductCategory,
    ProductImage,
    ProductVariant,
)
from apps.catalog.pricing_helpers import GST_RATE, build_price_block, get_retail_price_list
from apps.core.exceptions import ConflictError, NotFoundError, ValidationError
from apps.inventory.models import InventoryLevel, Warehouse
from apps.pricing.models import PriceList, PriceListItem

_RETAIL_CACHE_KEY = "a2z:price_list:retail"


def admin_product_queryset():
    price_list = get_retail_price_list()
    price_prefetch = Prefetch(
        "variants__price_list_items",
        queryset=PriceListItem.objects.filter(price_list=price_list)
        if price_list
        else PriceListItem.objects.none(),
        to_attr="_prefetched_price_items",
    )
    return (
        Product.objects.filter(deleted_at__isnull=True)
        .select_related("brand")
        .prefetch_related(
            "categories",
            "images",
            Prefetch(
                "variants",
                queryset=ProductVariant.objects.filter(is_active=True).order_by(
                    "-is_default", "created_at"
                ),
            ),
            Prefetch("variants__inventory_levels"),
            price_prefetch,
        )
        .order_by("name")
    )


def get_primary_warehouse() -> Warehouse | None:
    return Warehouse.objects.filter(is_active=True).order_by("code").first()


def ensure_retail_price_list() -> PriceList:
    price_list = get_retail_price_list()
    if price_list:
        return price_list
    price_list = PriceList.objects.create(name="Retail", slug="retail", is_active=True)
    cache.delete(_RETAIL_CACHE_KEY)
    return price_list


def get_default_variant(product: Product) -> ProductVariant | None:
    variants = list(product.variants.all())
    if not variants:
        return None
    for variant in variants:
        if variant.is_default:
            return variant
    return variants[0]


def get_variant_sell_price_cents(variant: ProductVariant, price_list: PriceList | None = None) -> int:
    price_list = price_list or get_retail_price_list()
    if not price_list:
        return 0
    cached_items = getattr(variant, "_prefetched_price_items", None)
    if cached_items:
        for item in cached_items:
            if item.price_list_id == price_list.pk:
                return int(item.unit_price_ex_gst_cents)
    item = (
        PriceListItem.objects.filter(price_list=price_list, variant=variant)
        .order_by("min_quantity")
        .first()
    )
    return int(item.unit_price_ex_gst_cents) if item else 0


def get_variant_stock(variant: ProductVariant) -> int:
    levels = list(variant.inventory_levels.all())
    return sum(max(level.quantity_on_hand - level.quantity_reserved, 0) for level in levels)


def get_variant_cost_cents(variant: ProductVariant) -> int:
    levels = list(variant.inventory_levels.all())
    if not levels:
        return 0
    return int(max(level.average_cost_cents for level in levels))


def serialize_admin_product(product: Product) -> dict:
    variant = get_default_variant(product)
    price_list = get_retail_price_list()
    sell_cents = get_variant_sell_price_cents(variant, price_list) if variant else 0
    price_block = build_price_block(sell_cents)
    primary_category = product.categories.filter(productcategory__is_primary=True).first()
    if not primary_category:
        primary_category = product.categories.first()

    images = [
        {
            "url": image.url,
            "alt_text": image.alt_text,
            "sort_order": image.sort_order,
            "is_primary": image.is_primary,
        }
        for image in product.images.all()
    ]

    return {
        "id": str(product.public_id),
        "name": product.name,
        "slug": product.slug,
        "sku": variant.sku if variant else "",
        "variant_id": str(variant.public_id) if variant else None,
        "brand_id": str(product.brand.public_id) if product.brand_id else None,
        "brand": product.brand.name if product.brand_id else "",
        "category_id": str(primary_category.public_id) if primary_category else None,
        "category": primary_category.name if primary_category else "",
        "sell_price_ex_gst_cents": sell_cents,
        "cost_price_cents": get_variant_cost_cents(variant) if variant else 0,
        "gst_rate": str(GST_RATE),
        "gst_cents": price_block["gst_cents"],
        "sell_price_inc_gst_cents": price_block["amount_inc_gst_cents"],
        "stock": get_variant_stock(variant) if variant else 0,
        "is_active": product.is_active,
        "status": "active" if product.is_active else "inactive",
        "short_description": product.short_description,
        "description": product.description,
        "images": images,
    }


def _unique_slug(base_slug: str, *, exclude_product_id: int | None = None) -> str:
    slug = base_slug
    counter = 1
    while True:
        qs = Product.objects.filter(slug=slug, deleted_at__isnull=True)
        if exclude_product_id:
            qs = qs.exclude(pk=exclude_product_id)
        if not qs.exists():
            return slug
        counter += 1
        slug = f"{base_slug}-{counter}"


def _sync_images(product: Product, images_payload: list[dict]) -> None:
    product.images.all().delete()
    if not images_payload:
        return
    for index, image_data in enumerate(images_payload):
        url = (image_data.get("url") or "").strip()
        if not url:
            continue
        ProductImage.objects.create(
            product=product,
            url=url,
            alt_text=image_data.get("alt_text", ""),
            sort_order=int(image_data.get("sort_order", index)),
            is_primary=bool(image_data.get("is_primary", index == 0)),
        )


def _sync_category(product: Product, category_id: str | None) -> None:
    ProductCategory.objects.filter(product=product).delete()
    if not category_id:
        return
    category = Category.objects.filter(public_id=category_id, is_active=True).first()
    if not category:
        raise NotFoundError("Category not found.")
    ProductCategory.objects.create(product=product, category=category, is_primary=True)


def _sync_pricing(variant: ProductVariant, sell_price_ex_gst_cents: int) -> None:
    price_list = ensure_retail_price_list()
    PriceListItem.objects.update_or_create(
        price_list=price_list,
        variant=variant,
        min_quantity=1,
        defaults={"unit_price_ex_gst_cents": max(int(sell_price_ex_gst_cents), 0)},
    )
    cache.delete(_RETAIL_CACHE_KEY)


def _sync_inventory(
    variant: ProductVariant,
    *,
    stock: int | None = None,
    cost_price_cents: int | None = None,
) -> None:
    warehouse = get_primary_warehouse()
    if not warehouse:
        return

    level, _created = InventoryLevel.objects.get_or_create(
        warehouse=warehouse,
        variant=variant,
        defaults={"quantity_on_hand": 0, "quantity_reserved": 0},
    )
    if stock is not None:
        level.quantity_on_hand = max(int(stock), 0)
    if cost_price_cents is not None:
        cost = max(int(cost_price_cents), 0)
        level.average_cost_cents = cost
        level.last_cost_cents = cost
    level.save()


@transaction.atomic
def create_admin_product(data: dict) -> Product:
    name = (data.get("name") or "").strip()
    sku = (data.get("sku") or "").strip()
    if not name:
        raise ValidationError("Product name is required.")
    if not sku:
        raise ValidationError("SKU is required.")
    if ProductVariant.objects.filter(sku=sku).exists():
        raise ConflictError("SKU already exists.")

    slug = (data.get("slug") or slugify(name)).strip() or slugify(name)
    slug = _unique_slug(slug)

    brand = None
    brand_id = data.get("brand_id")
    if brand_id:
        brand = Brand.objects.filter(public_id=brand_id, is_active=True).first()
        if not brand:
            raise NotFoundError("Brand not found.")

    product = Product.objects.create(
        brand=brand,
        name=name,
        slug=slug,
        short_description=data.get("short_description", ""),
        description=data.get("description", ""),
        is_active=bool(data.get("is_active", True)),
        visibility=Product.Visibility.PUBLIC,
        product_type=Product.ProductType.SIMPLE,
    )

    variant = ProductVariant.objects.create(
        product=product,
        sku=sku,
        name=name,
        is_default=True,
        is_active=True,
    )

    _sync_category(product, data.get("category_id"))
    _sync_pricing(variant, int(data.get("sell_price_ex_gst_cents", 0)))
    _sync_inventory(
        variant,
        stock=data.get("stock"),
        cost_price_cents=data.get("cost_price_cents"),
    )
    if "images" in data:
        _sync_images(product, data.get("images") or [])

    return admin_product_queryset().get(pk=product.pk)


@transaction.atomic
def update_admin_product(product: Product, data: dict) -> Product:
    if "name" in data:
        product.name = data["name"].strip()
    if "slug" in data and data["slug"]:
        new_slug = data["slug"].strip()
        if new_slug != product.slug:
            product.slug = _unique_slug(new_slug, exclude_product_id=product.pk)
    if "short_description" in data:
        product.short_description = data["short_description"]
    if "description" in data:
        product.description = data["description"]
    if "is_active" in data:
        product.is_active = bool(data["is_active"])
    if "brand_id" in data:
        brand_id = data["brand_id"]
        if brand_id:
            brand = Brand.objects.filter(public_id=brand_id, is_active=True).first()
            if not brand:
                raise NotFoundError("Brand not found.")
            product.brand = brand
        else:
            product.brand = None
    product.save()

    variant = get_default_variant(product)
    if not variant:
        sku = (data.get("sku") or "").strip()
        if not sku:
            raise ValidationError("SKU is required for product without a variant.")
        variant = ProductVariant.objects.create(
            product=product,
            sku=sku,
            name=product.name,
            is_default=True,
            is_active=True,
        )

    if "sku" in data:
        new_sku = data["sku"].strip()
        if new_sku and new_sku != variant.sku:
            if ProductVariant.objects.filter(sku=new_sku).exclude(pk=variant.pk).exists():
                raise ConflictError("SKU already exists.")
            variant.sku = new_sku
            variant.save(update_fields=["sku", "updated_at"])

    if "category_id" in data:
        _sync_category(product, data.get("category_id"))

    if "sell_price_ex_gst_cents" in data:
        _sync_pricing(variant, int(data["sell_price_ex_gst_cents"]))

    if "stock" in data or "cost_price_cents" in data:
        _sync_inventory(
            variant,
            stock=data.get("stock") if "stock" in data else None,
            cost_price_cents=data.get("cost_price_cents")
            if "cost_price_cents" in data
            else None,
        )

    if "images" in data:
        _sync_images(product, data.get("images") or [])

    return admin_product_queryset().get(pk=product.pk)


@transaction.atomic
def delete_admin_product(product: Product) -> None:
    product.is_active = False
    product.deleted_at = timezone.now()
    product.save(update_fields=["is_active", "deleted_at", "updated_at"])
