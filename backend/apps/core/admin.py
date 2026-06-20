from django.contrib import admin

from apps.analytics.models import AnalyticsEvent, SearchLog
from apps.catalog.models import Brand, Category, Product, ProductVariant
from apps.cms.models import BlogPost, Page
from apps.customers.models import Address, Customer, Organization
from apps.orders.models import Cart, Order
from apps.pricing.models import Coupon, PriceList
from apps.suppliers.models import Supplier
from apps.trade_accounts.models import TradeAccount

# User, UserProfile, Role — registered in apps.accounts.admin

admin.site.register(Organization)
admin.site.register(Customer)
admin.site.register(Address)
admin.site.register(TradeAccount)
admin.site.register(Brand)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(ProductVariant)
# Warehouse, InventoryLevel, StockMovement — apps.inventory.admin
admin.site.register(Supplier)
admin.site.register(PriceList)
admin.site.register(Coupon)
admin.site.register(Cart)
admin.site.register(Order)
admin.site.register(Page)
admin.site.register(BlogPost)
admin.site.register(AnalyticsEvent)
admin.site.register(SearchLog)
