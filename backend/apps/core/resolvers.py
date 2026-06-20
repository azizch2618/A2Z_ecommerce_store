"""Shared entity resolvers — single lookup path for cross-app services."""

from __future__ import annotations

from uuid import UUID

from apps.catalog.models import ProductVariant
from apps.core.exceptions import NotFoundError
from apps.inventory.models import Warehouse
from apps.suppliers.models import Supplier


def resolve_variant(sku: str, *, select_product: bool = False) -> ProductVariant:
    qs = ProductVariant.objects
    if select_product:
        qs = qs.select_related("product")
    try:
        return qs.get(sku__iexact=sku, is_active=True)
    except ProductVariant.DoesNotExist as exc:
        raise NotFoundError(f"SKU '{sku}' not found.") from exc


def resolve_warehouse(code: str) -> Warehouse:
    try:
        return Warehouse.objects.get(code__iexact=code, is_active=True)
    except Warehouse.DoesNotExist as exc:
        raise NotFoundError(f"Warehouse '{code}' not found.") from exc


def resolve_supplier(supplier_id: UUID, *, active_only: bool = True) -> Supplier:
    try:
        qs = Supplier.objects.filter(public_id=supplier_id)
        if active_only:
            qs = qs.filter(is_active=True)
        return qs.get()
    except Supplier.DoesNotExist as exc:
        raise NotFoundError("Supplier not found.") from exc


def resolve_supplier_optional(supplier_id: UUID | None) -> Supplier | None:
    if not supplier_id:
        return None
    return resolve_supplier(supplier_id)
