"""Pytest configuration: test groups, markers, and collection hooks."""

from __future__ import annotations

import pytest

# Path fragments → marker names (first match wins).
_PATH_MARKERS: tuple[tuple[str, str], ...] = (
    ("test_auth.py", "smoke"),
    ("test_catalog_api.py", "smoke"),
    ("test_inventory_api.py", "smoke"),
    ("test_phase_c_integration.py", "integration"),
    ("test_orders_api.py", "integration"),
    ("test_purchase_orders.py", "integration"),
    ("test_stripe_payments.py", "integration"),
    ("test_wms_api.py", "integration"),
    ("test_production_inventory.py", "integration"),
    ("test_phase_c_regression.py", "regression"),
    ("test_security.py", "security"),
    ("test_rbac.py", "security"),
    ("test_role_boundaries.py", "security"),
    ("apps/erp/tests/", "integration"),
    ("apps/crm/tests/", "integration"),
    ("test_catalog_performance.py", "slow"),
)


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "smoke: fast critical-path API tests")
    config.addinivalue_line("markers", "integration: cross-module workflow tests")
    config.addinivalue_line("markers", "regression: route and RBAC integrity checks")
    config.addinivalue_line("markers", "security: auth, RBAC boundary, and hardening tests")
    config.addinivalue_line("markers", "slow: performance or load-sensitive tests")


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    del config
    for item in items:
        path = str(item.fspath)
        for fragment, marker_name in _PATH_MARKERS:
            if fragment in path:
                item.add_marker(getattr(pytest.mark, marker_name))
                break
