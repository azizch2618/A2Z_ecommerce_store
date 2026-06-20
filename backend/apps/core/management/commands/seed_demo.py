"""Load demo dataset for client presentations."""

from __future__ import annotations

from django.core.management.base import BaseCommand

from apps.core.demo.catalog import DEMO_ACCOUNTS, DEMO_PASSWORD
from apps.core.demo.seed_catalog import seed_catalog, seed_tax_and_pricing, seed_warehouses
from apps.core.demo.seed_helpers import (
    seed_analytics_events,
    seed_orders_and_wishlists,
    seed_users_and_customers,
)


class Command(BaseCommand):
    help = "Seed realistic demo data for A2Z Tools client demonstrations."

    def add_arguments(self, parser):
        parser.add_argument(
            "--skip-orders",
            action="store_true",
            help="Skip orders, wishlists, and analytics events.",
        )

    def handle(self, *args, **options):
        self.stdout.write("Seeding demo environment...")

        price_list = seed_tax_and_pricing()
        warehouse = seed_warehouses()
        variants = seed_catalog(price_list, warehouse)
        users = seed_users_and_customers()

        order_count = 0
        event_count = 0
        if not options["skip_orders"]:
            order_count = seed_orders_and_wishlists(users, variants)
            event_count = seed_analytics_events()

        self.stdout.write(self.style.SUCCESS("Demo seed complete."))
        self.stdout.write(f"  Products: {len(variants)}")
        self.stdout.write(f"  Demo users: {len(DEMO_ACCOUNTS)}")
        if not options["skip_orders"]:
            self.stdout.write(f"  Orders: {order_count}")
            self.stdout.write(f"  Analytics events: {event_count}")

        self.stdout.write("")
        self.stdout.write(self.style.WARNING("Demo accounts (password for all):"))
        self.stdout.write(f"  {DEMO_PASSWORD}")
        for account in DEMO_ACCOUNTS:
            role = account.get("role", "customer")
            self.stdout.write(f"  • {account['email']} ({role})")
