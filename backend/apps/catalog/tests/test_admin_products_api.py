"""Admin product CRUD API tests."""
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.constants import RoleSlug
from apps.accounts.services import RoleService
from apps.catalog.models import Brand, Category, Product, ProductVariant
from apps.inventory.models import InventoryLevel, Warehouse
from apps.pricing.models import PriceList, PriceListItem

User = get_user_model()


class AdminProductAPITestCase(APITestCase):
    def setUp(self):
        from django.core.cache import cache

        cache.delete("a2z:price_list:retail")
        RoleService.ensure_system_roles()
        self.admin = User.objects.create_user(
            email="catalog-admin@example.com",
            password="TestPass123!",
            is_staff=True,
        )
        RoleService.assign_role(self.admin, RoleSlug.ADMIN)

        self.viewer = User.objects.create_user(
            email="catalog-viewer@example.com",
            password="TestPass123!",
            is_staff=True,
        )
        RoleService.assign_role(self.viewer, RoleSlug.SALES_REP)

        self.brand = Brand.objects.create(name="DeWalt", slug="dewalt", is_active=True)
        self.category = Category.objects.create(
            name="Hand Tools",
            slug="hand-tools",
            is_active=True,
        )
        self.warehouse = Warehouse.objects.create(
            code="MEL1",
            name="Melbourne DC",
            warehouse_type=Warehouse.WarehouseType.DISTRIBUTION,
        )
        self.price_list = PriceList.objects.create(
            name="Retail",
            slug="retail",
            is_active=True,
        )

        self.product = Product.objects.create(
            brand=self.brand,
            name="Hammer Drill",
            slug="hammer-drill",
            is_active=True,
        )
        self.product.categories.add(self.category)
        self.variant = ProductVariant.objects.create(
            product=self.product,
            sku="HD-100",
            is_default=True,
            is_active=True,
        )
        PriceListItem.objects.create(
            price_list=self.price_list,
            variant=self.variant,
            unit_price_ex_gst_cents=25000,
        )
        InventoryLevel.objects.create(
            warehouse=self.warehouse,
            variant=self.variant,
            quantity_on_hand=12,
            average_cost_cents=18000,
        )

    def test_list_products_requires_auth(self):
        response = self.client.get("/api/v1/admin/products/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_products_as_viewer(self):
        self.client.force_authenticate(self.viewer)
        response = self.client.get("/api/v1/admin/products/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data["data"]), 1)
        row = next(item for item in response.data["data"] if item["sku"] == "HD-100")
        self.assertEqual(row["sell_price_ex_gst_cents"], 25000)
        self.assertEqual(row["cost_price_cents"], 18000)
        self.assertEqual(row["stock"], 12)

    def test_create_product(self):
        self.client.force_authenticate(self.admin)
        response = self.client.post(
            "/api/v1/admin/products/",
            {
                "name": "Impact Driver",
                "sku": "ID-200",
                "brand_id": str(self.brand.public_id),
                "category_id": str(self.category.public_id),
                "sell_price_ex_gst_cents": 32000,
                "cost_price_cents": 21000,
                "stock": 8,
                "is_active": True,
                "short_description": "Compact impact driver",
                "images": [
                    {"url": "https://cdn.example.com/id.jpg", "alt_text": "Impact driver", "is_primary": True},
                    {"url": "https://cdn.example.com/id-2.jpg", "alt_text": "Side view"},
                ],
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["sku"], "ID-200")
        self.assertEqual(response.data["sell_price_ex_gst_cents"], 32000)
        self.assertEqual(response.data["cost_price_cents"], 21000)
        self.assertEqual(response.data["stock"], 8)
        self.assertEqual(len(response.data["images"]), 2)
        self.assertTrue(response.data["is_active"])

    def test_viewer_cannot_create_product(self):
        self.client.force_authenticate(self.viewer)
        response = self.client.post(
            "/api/v1/admin/products/",
            {"name": "Blocked", "sku": "BLK-1", "sell_price_ex_gst_cents": 1000},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_update_delete_product(self):
        self.client.force_authenticate(self.admin)
        product_id = str(self.product.public_id)

        detail = self.client.get(f"/api/v1/admin/products/{product_id}/")
        self.assertEqual(detail.status_code, status.HTTP_200_OK)
        self.assertEqual(detail.data["name"], "Hammer Drill")

        updated = self.client.patch(
            f"/api/v1/admin/products/{product_id}/",
            {
                "name": "Hammer Drill Pro",
                "sell_price_ex_gst_cents": 27500,
                "stock": 20,
                "is_active": False,
                "images": [{"url": "https://cdn.example.com/hd-new.jpg", "is_primary": True}],
            },
            format="json",
        )
        self.assertEqual(updated.status_code, status.HTTP_200_OK)
        self.assertEqual(updated.data["name"], "Hammer Drill Pro")
        self.assertEqual(updated.data["sell_price_ex_gst_cents"], 27500)
        self.assertEqual(updated.data["stock"], 20)
        self.assertFalse(updated.data["is_active"])
        self.assertEqual(len(updated.data["images"]), 1)

        deleted = self.client.delete(f"/api/v1/admin/products/{product_id}/")
        self.assertEqual(deleted.status_code, status.HTTP_204_NO_CONTENT)
        self.product.refresh_from_db()
        self.assertFalse(self.product.is_active)
        self.assertIsNotNone(self.product.deleted_at)

        list_response = self.client.get("/api/v1/admin/products/")
        skus = [row["sku"] for row in list_response.data["data"]]
        self.assertNotIn("HD-100", skus)
