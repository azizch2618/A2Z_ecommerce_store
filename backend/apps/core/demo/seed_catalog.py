"""Seed catalog, pricing, warehouses, and inventory for demo."""

from __future__ import annotations

from django.utils import timezone

from apps.catalog.models import Brand, Category, Product, ProductImage, ProductReview, ProductVariant
from apps.core.demo.catalog import DEMO_BRANDS, DEMO_CATEGORIES, DEMO_PRODUCTS
from apps.inventory.models import InventoryLevel, Warehouse
from apps.pricing.models import PriceList, PriceListItem, TaxRate


def seed_tax_and_pricing() -> PriceList:
    TaxRate.objects.update_or_create(
        code="GST",
        defaults={
            "rate": "0.1000",
            "country": "AU",
            "valid_from": timezone.now(),
            "is_active": True,
        },
    )
    price_list, _ = PriceList.objects.update_or_create(
        slug="retail",
        defaults={
            "name": "Retail AUD",
            "currency_code": "AUD",
            "is_active": True,
        },
    )
    return price_list


def seed_warehouses() -> Warehouse:
    warehouse, _ = Warehouse.objects.update_or_create(
        code="SYD1",
        defaults={
            "name": "Sydney Distribution Centre",
            "warehouse_type": Warehouse.WarehouseType.DISTRIBUTION,
            "suburb": "Wetherill Park",
            "state": "NSW",
            "postcode": "2164",
            "is_active": True,
            "allows_pickup": True,
        },
    )
    Warehouse.objects.update_or_create(
        code="MEL1",
        defaults={
            "name": "Melbourne Distribution Centre",
            "warehouse_type": Warehouse.WarehouseType.DISTRIBUTION,
            "suburb": "Dandenong South",
            "state": "VIC",
            "postcode": "3175",
            "is_active": True,
        },
    )
    return warehouse


def seed_catalog(price_list: PriceList, warehouse: Warehouse) -> list[ProductVariant]:
    brands: dict[str, Brand] = {}
    for brand_data in DEMO_BRANDS:
        brand, _ = Brand.objects.update_or_create(
            slug=brand_data["slug"],
            defaults={
                "name": brand_data["name"],
                "description": brand_data.get("description", ""),
                "is_active": True,
                "is_authorized_reseller": True,
            },
        )
        brands[brand.slug] = brand

    categories: dict[str, Category] = {}
    for cat_data in DEMO_CATEGORIES:
        category, _ = Category.objects.update_or_create(
            slug=cat_data["slug"],
            defaults={
                "name": cat_data["name"],
                "description": cat_data.get("description", ""),
                "is_active": True,
                "sort_order": len(categories),
            },
        )
        categories[category.slug] = category

    variants: list[ProductVariant] = []
    for item in DEMO_PRODUCTS:
        brand = brands[item["brand_slug"]]
        category = categories[item["category_slug"]]
        product, _ = Product.objects.update_or_create(
            slug=item["slug"],
            defaults={
                "brand": brand,
                "name": item["name"],
                "short_description": item["short_description"],
                "description": item["description"],
                "is_active": True,
                "visibility": Product.Visibility.PUBLIC,
                "average_rating": item["average_rating"],
                "review_count": item["review_count"],
                "highlights": item.get("highlights", []),
                "specifications": item.get("specifications", []),
            },
        )
        product.categories.set([category])

        ProductImage.objects.filter(product=product).delete()
        ProductImage.objects.create(
            product=product,
            url=item["image_url"],
            alt_text=item["name"],
            is_primary=True,
            sort_order=0,
        )

        variant, _ = ProductVariant.objects.update_or_create(
            product=product,
            sku=item["sku"],
            defaults={
                "name": "Standard",
                "is_default": True,
                "is_active": True,
            },
        )
        variants.append(variant)

        PriceListItem.objects.update_or_create(
            price_list=price_list,
            variant=variant,
            min_quantity=1,
            defaults={"unit_price_ex_gst_cents": item["price_ex_gst_cents"]},
        )

        InventoryLevel.objects.update_or_create(
            warehouse=warehouse,
            variant=variant,
            defaults={
                "quantity_on_hand": item["stock"],
                "quantity_reserved": 0,
                "reorder_point": item["reorder_point"],
                "reorder_quantity": item["reorder_point"] * 2,
                "average_cost_cents": int(item["price_ex_gst_cents"] * 0.65),
                "last_cost_cents": int(item["price_ex_gst_cents"] * 0.65),
            },
        )

        ProductReview.objects.filter(product=product).delete()
        for review in item.get("reviews", []):
            ProductReview.objects.create(
                product=product,
                author_name=review["author"],
                author_company=review.get("company", ""),
                author_role=review.get("role", ""),
                rating=review["rating"],
                title=review["title"],
                body=review["body"],
                is_verified_purchase=review.get("verified", False),
            )

    return variants
