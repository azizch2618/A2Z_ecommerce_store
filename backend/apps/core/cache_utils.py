"""Redis cache helpers for catalog and analytics."""
from __future__ import annotations

import hashlib
import json
from collections.abc import Callable
from typing import TypeVar

from django.core.cache import cache

T = TypeVar("T")

# TTLs (seconds)
CACHE_TTL_DASHBOARD = 60
CACHE_TTL_CATALOG_LIST = 300
CACHE_TTL_PRICE_LIST = 600


def build_cache_key(prefix: str, **parts: object) -> str:
    """Stable cache key from prefix and sorted parameter parts."""
    payload = json.dumps(parts, sort_keys=True, default=str)
    digest = hashlib.md5(payload.encode()).hexdigest()[:12]
    return f"a2z:{prefix}:{digest}"


def cache_get_or_set(key: str, factory: Callable[[], T], *, timeout: int) -> T:
    cached = cache.get(key)
    if cached is not None:
        return cached
    value = factory()
    cache.set(key, value, timeout)
    return value


def cache_delete_prefix(prefix: str) -> None:
    """Best-effort invalidation when using django-redis; no-op on locmem."""
    try:
        from django_redis import get_redis_connection

        conn = get_redis_connection("default")
        keys = conn.keys(f"a2z:{prefix}:*")
        if keys:
            conn.delete(*keys)
    except Exception:
        pass
