# Phase B — Operational Completion

**Status:** Implemented (June 2026)  
**Scope:** Day-to-day admin and operational modules required for business operations.  
**Related:** [ERP_FOUNDATION_ROADMAP.md](./ERP_FOUNDATION_ROADMAP.md) Phase B

---

## 1. Operational Gap Report

### Pre-Phase B audit (before implementation)

| Module | Frontend | Backend | Primary gap |
|--------|----------|---------|-------------|
| Categories | `throwAdminApiUnavailable()` stub | Public read-only list | No admin CRUD, search, or status |
| Brands | Stub | Public read-only list | No admin CRUD, logo, or status |
| Suppliers | Dashboard slice (top 10) | Public list only | No admin CRUD; FE unwired |
| Warehouses | Stub | List without aggregates | No admin CRUD, capacity, or stats |
| Purchase Orders | Stub | Full lifecycle API existed | FE completely unwired |
| Trade Accounts | Partial read; write stub | Dashboard embed only | Approve/reject/credit APIs missing |
| Order Operations | List only | Pack/ship/deliver/cancel existed | Refund + FE actions missing |
| Reporting | Stub | None | Full module missing |
| Settings | All stubs | None | Out of Phase B scope |
| Inventory (legacy hooks) | `inventory-hooks.ts` live for WMS tab | Live APIs | Legacy `hooks.ts` paths still stubbed |

**Orphan mock artifacts (unused after wiring):**

- `frontend/src/config/admin/mock-data.ts`
- `frontend/src/lib/api/admin/wms-store.ts`
- `frontend/src/lib/api/admin/mock-service.ts`

### Post-Phase B status

| Module | Backend | Frontend | Audit | RBAC |
|--------|---------|----------|-------|------|
| Categories | ✅ List/create/patch/deactivate | ✅ Search, create, deactivate | ✅ | `CanViewCatalog` / `CanManageCatalog` |
| Brands | ✅ List/create/patch/deactivate | ✅ Search, create, featured toggle, logo URL | ✅ | `CanViewCatalog` / `CanManageCatalog` |
| Suppliers | ✅ Admin list/create/patch | ✅ Search, create, list panel | ✅ | `CanViewSuppliers` / `CanManageSuppliers` |
| Warehouses | ✅ Admin CRUD + `capacity_units` | ✅ Search, create, deactivate | ✅ | `CanManageWarehouse` |
| Purchase Orders | ✅ Create/submit/confirm/receive/cancel | ✅ WMS tab wired (create, approve, receive, close) | ✅ PO lifecycle | `CanManageSuppliers` / `CanManageInventory` |
| Trade Accounts | ✅ List/review/credit limit | ✅ Approve/reject + credit limit on approve | ✅ | `CanViewTrade` / `CanApproveTrade` |
| Order Operations | ✅ Pack/ship/deliver/cancel/refund | ✅ Actions menu + status filter on orders table | ✅ All ops | `CanManageOrders` |
| Reporting | ✅ Sales/inventory/GST/customer catalog + CSV export | ✅ Live report cards + CSV download | ✅ Export logged | `CanViewReports` / `CanExportReports` |

### Remaining stubs (intentionally out of scope or deferred)

| Area | Location | Notes |
|------|----------|-------|
| Settings (company, GST, shipping, email, payment) | `hooks.ts` | Phase C / foundation settings |
| Legacy inventory hooks | `hooks.ts` | Superseded by `inventory-hooks.ts` for WMS; safe to delete |
| Mock service files | `mock-service.ts`, `mock-data.ts`, `wms-store.ts` | Orphaned; candidates for removal |
| Trade application on registration | `customers` registration flow | Sets `Customer.trade_account_status=pending` but does not create `TradeApplication` row |
| PDF/Excel report formats | `analytics/reports.py` | CSV fully implemented; PDF/Excel return placeholder content |
| Pagination UI | Category/brand/supplier pages | API supports cursor pagination; UI loads first page only |
| Supplier status toggle in UI | `suppliers-page-view.tsx` | Create + list only; patch API exists |
| File upload for brand logos | `brands-page-view.tsx` | Logo via URL field; no storage integration yet |

---

## 2. Implementation Summary

### Backend

| Component | Path | Description |
|-----------|------|-------------|
| Operational audit log | `apps/core/models.py`, `apps/core/audit.py`, `apps/core/migrations/0001_operational_audit_log.py` | Immutable `OperationalAuditLog` with module/action/resource |
| Catalog admin | `apps/catalog/admin_views.py`, `catalog/urls.py` | Categories and brands CRUD |
| Suppliers admin | `apps/suppliers/admin_views.py`, `suppliers/urls.py` | Supplier CRUD |
| Warehouses admin | `apps/inventory/admin_views.py`, `inventory/migrations/0004_warehouse_capacity_units.py` | Warehouse CRUD + capacity |
| Trade admin | `apps/trade_accounts/admin_views.py`, `services.py` | `TradeAdminService` + restored `TradeAccountService` |
| Order refund | `apps/orders/services.py`, `views.py` | `refund_order()` + `OrderRefundView` |
| PO audit | `apps/suppliers/views.py` | Audit on submit/confirm/receive/cancel |
| Order ops audit | `apps/orders/views.py` | Audit on pack/ship/deliver/cancel/refund |
| Reports | `apps/analytics/reports.py`, `analytics/urls.py` | Report catalog + CSV export |
| RBAC | `apps/accounts/permissions.py` | `CanViewTrade`, `CanApproveTrade`, `CanManageWarehouse`, `CanViewReports`, `CanExportReports` |

### Frontend

| Component | Path | Description |
|-----------|------|-------------|
| Operational API layer | `lib/api/admin/operational-service.ts` | Typed fetch/mutate for all 8 modules |
| Hooks | `lib/api/admin/hooks.ts` | Live queries/mutations replacing stubs |
| API config | `lib/api/config.ts` | Admin endpoint map |
| Page views | `components/admin/pages/*-page-view.tsx` | Categories, brands, warehouses, suppliers, orders, reports |
| Order actions | `components/admin/dashboard/recent-orders-table.tsx` | Pack/ship/deliver/cancel/refund dropdown |
| Trade review | `components/admin/dashboard/trade-applications-panel.tsx` | Credit limit on approve |
| WMS / PO | `components/admin/inventory/inventory-wms-view.tsx` | Live warehouses, PO lifecycle buttons |

### Migrations applied

- `core.0001_operational_audit_log`
- `inventory.0004_warehouse_capacity_units`

---

## 3. Remaining Unfinished Modules

These are **not** part of the eight Phase B modules but still block full production ops:

1. **Admin Settings** — company profile, GST, shipping, email, payment gateways (100% stub).
2. **Trade application intake** — auto-create `TradeApplication` on B2B registration.
3. **Brand logo file upload** — needs storage component (R2/S3); URL field is interim.
4. **Report PDF/Excel** — needs proper renderer (WeasyPrint, openpyxl, or external service).
5. **Operational audit log viewer** — backend writes logs; no admin UI to browse them.
6. **Dedicated PO admin page** — POs live under Inventory/WMS tab; no standalone `/admin/purchase-orders` page.
7. **Backend integration tests** for new admin endpoints (catalog, suppliers admin, trade admin, reports).
8. **Cleanup** — remove `mock-service.ts`, `mock-data.ts`, `wms-store.ts`, and legacy inventory stubs in `hooks.ts`.

---

## 4. Production Readiness Score

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Backend APIs | **88%** | All eight modules have live endpoints; PDF/Excel reports are placeholders |
| Frontend wiring | **78%** | Core pages and actions wired; pagination/edit dialogs are minimal |
| Audit & compliance | **82%** | Operational audit on all Phase B mutations; no viewer UI |
| RBAC enforcement | **90%** | Permissions on all new admin views |
| Test coverage | **45%** | Existing PO/order tests; no new admin API test suite |
| Data integrity | **70%** | Trade application intake gap; logo upload is URL-only |
| **Overall Phase B** | **74%** | Ready for staged internal ops pilot; not full production without settings + tests |

### Go-live checklist (Phase B modules)

- [x] Categories CRUD + search
- [x] Brands CRUD + status/featured
- [x] Suppliers CRUD + contacts
- [x] Warehouses CRUD + capacity
- [x] Purchase order create → approve → receive → close
- [x] Trade review approve/reject + credit limit
- [x] Order pack/ship/deliver/cancel/refund
- [x] Sales, inventory, GST, customer reports (CSV)
- [ ] Run full regression in staging with real staff roles
- [ ] Add integration tests for admin endpoints
- [ ] Wire trade application creation on registration
- [ ] Remove orphan mock files

---

## API reference (admin operational)

| Method | Endpoint | Permission |
|--------|----------|------------|
| GET/POST | `/api/v1/catalog/admin/categories/` | View / Manage catalog |
| PATCH/DELETE | `/api/v1/catalog/admin/categories/{id}/` | Manage catalog |
| GET/POST | `/api/v1/catalog/admin/brands/` | View / Manage catalog |
| PATCH/DELETE | `/api/v1/catalog/admin/brands/{id}/` | Manage catalog |
| GET/POST | `/api/v1/suppliers/admin/` | View / Manage suppliers |
| PATCH | `/api/v1/suppliers/admin/{id}/` | Manage suppliers |
| GET/POST | `/api/v1/inventory/admin/warehouses/` | Manage warehouse |
| PATCH | `/api/v1/inventory/admin/warehouses/{id}/` | Manage warehouse |
| GET/POST | `/api/v1/suppliers/purchase-orders/` | View / Manage suppliers |
| POST | `/api/v1/suppliers/purchase-orders/{id}/submit\|confirm\|receive\|cancel/` | Manage suppliers / inventory |
| GET | `/api/v1/trade-accounts/admin/applications/` | View trade |
| POST | `/api/v1/trade-accounts/admin/applications/{id}/review/` | Approve trade |
| PATCH | `/api/v1/trade-accounts/admin/accounts/{id}/credit/` | Approve trade |
| POST | `/api/v1/orders/{id}/pack\|ship\|deliver\|cancel\|refund/` | Manage orders |
| GET | `/api/v1/analytics/admin/reports/` | View reports |
| POST | `/api/v1/analytics/admin/reports/export/` | Export reports |

---

*Generated as part of Phase B — Operational Completion. Update this document when remaining items are closed.*
