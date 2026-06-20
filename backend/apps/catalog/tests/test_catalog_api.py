"""Catalog API tests."""
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.catalog.models import Brand, Category, Product, ProductImage, ProductVariant
from apps.inventory.models import InventoryLevel, Warehouse
from apps.pricing.models import PriceList, PriceListItem


class CatalogAPITestCase(APITestCase):
    def setUp(self):
        self.brand = Brand.objects.create(
            name="Makita",
            slug="makita",
            is_active=True,
        )
        self.category = Category.objects.create(
            name="Power Tools",
            slug="power-tools",
            is_active=True,
        )
        self.product = Product.objects.create(
            brand=self.brand,
            name="Cordless Drill",
            slug="cordless-drill",
            short_description="18V brushless drill",
            is_active=True,
            visibility=Product.Visibility.PUBLIC,
        )
        self.product.categories.add(self.category)
        self.variant = ProductVariant.objects.create(
            product=self.product,
            sku="DRILL-001",
            name="Kit",
            is_default=True,
            is_active=True,
        )
        ProductImage.objects.create(
            product=self.product,
            url="https://cdn.example.com/drill.jpg",
            alt_text="Drill",
            is_primary=True,
        )
        self.price_list = PriceList.objects.create(
            name="Retail",
            slug="retail",
            is_active=True,
        )
        PriceListItem.objects.create(
            price_list=self.price_list,
            variant=self.variant,
            unit_price_ex_gst_cents=19900,
        )
        self.warehouse = Warehouse.objects.create(
            code="SYD1",
            name="Sydney DC",
            warehouse_type=Warehouse.WarehouseType.DISTRIBUTION,
        )
        InventoryLevel.objects.create(
            warehouse=self.warehouse,
            variant=self.variant,
            quantity_on_hand=25,
            quantity_reserved=0,
        )

    def test_list_products_with_filters(self):
        response = self.client.get(
            reverse("catalog:product-list"),
            {
                "brand": str(self.brand.public_id),
                "category": str(self.category.public_id),
                "search": "drill",
                "sort": "name",
                "limit": 10,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]), 1)
        self.assertEqual(response.data["data"][0]["slug"], "cordless-drill")
        self.assertIn("facets", response.data)
        self.assertEqual(response.data["data"][0]["price"]["amount_ex_gst_cents"], 19900)

    def test_product_detail_by_slug(self):
        response = self.client.get(
            reverse("catalog:product-detail", kwargs={"slug": "cordless-drill"})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Cordless Drill")
        self.assertEqual(len(response.data["variants"]), 1)
        self.assertEqual(len(response.data["images"]), 1)

    def test_list_categories(self):
        response = self.client.get(reverse("catalog:category-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data["data"]), 1)

    def test_list_brands(self):
        response = self.client.get(
            reverse("catalog:brand-list"),
            {"search": "mak"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"][0]["slug"], "makita")
