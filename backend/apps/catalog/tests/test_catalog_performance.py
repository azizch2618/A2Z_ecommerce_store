"""P0 performance regression tests for catalog list vs detail query paths."""
from django.test import TestCase
from django.test.utils import override_settings
from django.urls import reverse

from apps.catalog.models import Brand, Category, Product, ProductImage, ProductVariant
from apps.catalog.services import CatalogService
from apps.inventory.models import InventoryLevel, Warehouse
from apps.pricing.models import PriceList, PriceListItem


@override_settings(
    CACHES={
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        }
    }
)
class CatalogListPerformanceTestCase(TestCase):
    def setUp(self):
        self.warehouse = Warehouse.objects.create(
            code="SYD",
            name="Sydney DC",
            is_active=True,
        )
        self.brand = Brand.objects.create(name="DeWalt", slug="dewalt")
        self.category = Category.objects.create(name="Power Tools", slug="power-tools")
        self.price_list = PriceList.objects.create(
            name="Retail",
            slug="retail",
            is_active=True,
        )

        for index in range(3):
            product = Product.objects.create(
                brand=self.brand,
                name=f"Product {index}",
                slug=f"product-{index}",
                is_active=True,
            )
            product.categories.add(self.category)
            variant = ProductVariant.objects.create(
                product=product,
                sku=f"SKU-{index}",
                is_default=True,
                is_active=True,
            )
            ProductImage.objects.create(
                product=product,
                url=f"https://example.com/{index}.jpg",
                is_primary=True,
            )
            PriceListItem.objects.create(
                price_list=self.price_list,
                variant=variant,
                unit_price_ex_gst_cents=10_000 + index * 100,
            )
            InventoryLevel.objects.create(
                warehouse=self.warehouse,
                variant=variant,
                quantity_on_hand=25,
            )

    def test_list_queryset_uses_fewer_queries_than_detail(self):
        with self.assertNumQueries(6):
            products = list(CatalogService.product_list_queryset()[:3])
            self.assertEqual(len(products), 3)
            for product in products:
                self.assertTrue(hasattr(product, "_default_variants"))
                self.assertTrue(hasattr(product, "_primary_images"))

        with self.assertNumQueries(9):
            products = list(CatalogService.product_detail_queryset()[:3])
            self.assertEqual(len(products), 3)

    def test_product_list_api_returns_paginated_payload(self):
        url = reverse("catalog:product-list")
        response = self.client.get(url, {"limit": 2})
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertIn("data", body)
        self.assertLessEqual(len(body["data"]), 2)
        self.assertIn("pagination", body)
        first = body["data"][0]
        self.assertIn("price", first)
        self.assertIn("default_variant", first)
        self.assertNotIn("price", first["default_variant"])
        self.assertNotIn("stock", first["default_variant"])
