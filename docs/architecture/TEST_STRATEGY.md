# Test Execution Strategy — A2Z Tools Backend

**Date:** 2026-06-20  
**Owner:** DevOps / Django Test Architecture

---

## Goals

- Deterministic automated tests on every pull request
- PostgreSQL in CI (production parity)
- SQLite for fast local iteration
- Grouped execution with isolated failure reporting

---

## Test Groups

| Group | Marker | Scope | Typical runtime |
|-------|--------|-------|-----------------|
| **Smoke** | `smoke` | Auth, catalog, inventory API sanity | ~30s |
| **Security** | `security` | RBAC boundaries, hardening, SoD | ~15s |
| **Regression** | `regression` | Route health, RBAC leak checks | ~10s |
| **Integration** | `integration` | Orders, PO, WMS, Stripe, Phase C journeys | ~60s |
| **Slow** | `slow` | Performance benchmarks (optional locally) | varies |

Markers are applied automatically in `backend/conftest.py` from test file paths. No per-test decorators required.

### File → group mapping

| File | Group |
|------|-------|
| `apps/accounts/tests/test_auth.py` | smoke |
| `apps/catalog/tests/test_catalog_api.py` | smoke |
| `apps/inventory/tests/test_inventory_api.py` | smoke |
| `apps/core/tests/test_security.py` | security |
| `apps/accounts/tests/test_rbac.py` | security |
| `apps/accounts/tests/test_role_boundaries.py` | security |
| `apps/integrations/tests/test_phase_c_regression.py` | regression |
| `apps/integrations/tests/test_phase_c_integration.py` | integration |
| `apps/orders/tests/test_orders_api.py` | integration |
| `apps/suppliers/tests/test_purchase_orders.py` | integration |
| `apps/payments/tests/test_stripe_payments.py` | integration |
| `apps/inventory/tests/test_wms_api.py` | integration |
| `apps/inventory/tests/test_production_inventory.py` | integration |
| `apps/catalog/tests/test_catalog_performance.py` | slow |

---

## Database Modes

### SQLite (fast local)

```powershell
# Windows
$env:USE_SQLITE_FOR_TESTS = '1'
.\scripts\run-tests.ps1 smoke
```

```bash
# Linux/macOS
USE_SQLITE_FOR_TESTS=1 ./scripts/run-tests.sh smoke
```

Uses in-memory SQLite. No PostgreSQL required. Ideal for TDD and pre-commit.

### PostgreSQL (CI / parity)

```powershell
$env:TEST_DB = 'postgres'
$env:POSTGRES_DB = 'a2z_tools_test'
$env:POSTGRES_TEST_DB = 'test_a2z_tools'   # MUST differ from POSTGRES_DB
.\scripts\run-tests.ps1 all
```

```bash
TEST_DB=postgres ./scripts/run-tests.sh ci
```

**Bootstrap fix:** `config/settings/test.py` connects to `POSTGRES_DB` and Django creates a **separate** database named `POSTGRES_TEST_DB` (default: `test_<POSTGRES_DB>`). Never set `TEST["NAME"]` equal to the connection database — that caused indefinite hangs on Windows and Linux.

Connection timeout defaults to 10 seconds (`POSTGRES_CONNECT_TIMEOUT`).

---

## Local Commands

| Command | Description |
|---------|-------------|
| `.\scripts\run-tests.ps1 smoke` | Smoke tests (SQLite default) |
| `.\scripts\run-tests.ps1 security` | RBAC + security tests |
| `.\scripts\run-tests.ps1 regression` | Regression suite |
| `.\scripts\run-tests.ps1 integration` | Integration workflows |
| `.\scripts\run-tests.ps1 all` | Full suite minus slow |
| `.\scripts\run-tests.ps1 ci` | CI sequence + JUnit + coverage |
| `pytest -m smoke` | Direct pytest (from `backend/`) |

---

## CI Pipeline (GitHub Actions)

Workflow: `.github/workflows/ci-backend.yml`

```
┌─────────────┐
│    lint     │  Ruff + django check (no DB)
└──────┬──────┘
       │
       ├──────────────────────────┐
       ▼                          ▼
┌──────────────┐          ┌─────────────────┐
│ sqlite-smoke │          │  test (PG 16)   │
│ smoke+security│         │  full CI script │
└──────────────┘          └────────┬────────┘
                                   │
                    smoke → security → regression
                         → integration → coverage
                                   │
                    JUnit reports + coverage artifact
                    PR comment with coverage summary
```

### Jobs

1. **lint** — Ruff, `manage.py check`
2. **sqlite-smoke** — Fast gate without PostgreSQL service
3. **test** — PostgreSQL 16 service, grouped tests, coverage

### Failure reporting

- **JUnit XML** per group under `backend/reports/junit-*.xml`
- **GitHub Checks** via `dorny/test-reporter` (one check per group)
- **Artifacts** — all JUnit files, `coverage.xml`, HTML report (14-day retention)
- **PR comment** — sticky coverage summary via `marocchino/sticky-pull-request-comment`

### Environment variables (CI)

| Variable | Value |
|----------|-------|
| `POSTGRES_DB` | `a2z_tools_test` (service connection DB) |
| `POSTGRES_TEST_DB` | `test_a2z_tools` (Django test clone) |
| `USE_SQLITE_FOR_TESTS` | `0` |
| `TEST_DB` | `postgres` |

---

## Coverage

Configured in `backend/pyproject.toml` `[tool.coverage.*]`.

Sources: `apps`, `api`, `config`  
Omits: migrations, tests, `__init__.py`

```bash
cd backend
pytest -m "not slow" --cov=apps --cov=api --cov=config --cov-report=html:reports/htmlcov
```

Open `backend/reports/htmlcov/index.html` for interactive report.

---

## Troubleshooting

### PostgreSQL bootstrap hangs

1. Confirm `POSTGRES_TEST_DB` ≠ `POSTGRES_DB`
2. Run `python scripts/wait_for_postgres.py` before tests
3. Drop stale test DB: `DROP DATABASE IF EXISTS test_a2z_tools;`
4. Use SQLite while debugging: `USE_SQLITE_FOR_TESTS=1`

### Tests pass locally (SQLite) but fail in CI (PostgreSQL)

- JSON field differences, constraints, or transaction semantics
- Reproduce: `TEST_DB=postgres ./scripts/run-tests.sh all`

### Unknown marker error

Ensure `backend/conftest.py` is present and run pytest from `backend/` directory.

### Tests fail with `KeyError: 'tokens'`

Test settings set `JWT_AUTH_COOKIE_ONLY = False` so APITestCase receives tokens in JSON bodies. Cookie-only behaviour is covered in `apps/core/tests/test_security.py`.

### Catalog search fails on SQLite

`ProductFilter.filter_search` falls back to `icontains` when not on PostgreSQL. Full-text search (`search_vector`) is exercised in CI with PostgreSQL.

---

## Related Documents

- [RBAC_AUDIT.md](./RBAC_AUDIT.md)
- [PHASE_C_PRODUCTION_VALIDATION.md](./PHASE_C_PRODUCTION_VALIDATION.md)
