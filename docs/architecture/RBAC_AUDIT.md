# RBAC Security Audit — A2Z Tools

**Date:** 2026-06-20  
**Auditor role:** Senior Security Architect / RBAC Specialist  
**Status:** Remediated

---

## Executive Summary

A critical RBAC flaw was identified: `User.objects.create_user(..., is_staff=True)` implicitly assigned the **Manager** role via `sync_platform_roles()`, granting broad business permissions (including `trade.approve`) independent of explicit role assignment.

**Root cause:** Conflation of Django `is_staff` (Django admin UI access) with application RBAC roles.

**Remediation:** Permissions now derive **only** from explicitly assigned `UserRole` records. `is_superuser` still maps to `super-admin` role only.

---

## 1. RBAC Matrix

| Role | Dashboard | Catalog | Inventory | Orders | Customers | Trade View | Trade Approve | Suppliers | Reports | Settings | Users |
|------|:---------:|:-------:|:---------:|:------:|:---------:|:----------:|:-------------:|:---------:|:-------:|:--------:|:-----:|
| **Super Admin** | ✓ | ✓ manage | ✓ manage | ✓ manage | ✓ manage | ✓ | ✓ | ✓ manage | ✓ export | ✓ manage | ✓ |
| **Admin** | ✓ | ✓ manage | ✓ manage | ✓ manage | ✓ manage | ✓ | ✓ | ✓ manage | ✓ export | ✓ view | — |
| **Manager** | ✓ | ✓ manage | ✓ view | ✓ manage | ✓ manage | ✓ | — | ✓ manage | ✓ export | ✓ view | — |
| **Warehouse Manager** | ✓ | ✓ view | ✓ manage | ✓ view | — | — | — | ✓ view | — | — | — |
| **Sales Representative** | ✓ | ✓ view | — | ✓ manage | ✓ view | ✓ | — | — | ✓ view | — | — |
| **Customer Service** | ✓ | ✓ view | — | ✓ manage | ✓ manage | ✓ | — | — | — | — | — |
| **Trade Reviewer** | ✓ | — | — | — | ✓ view | ✓ | ✓ | — | — | — | — |
| **Customer** | — | — | — | checkout | — | — | — | — | — | — | — |
| **Trade Customer** | — | — | — | checkout + trade pricing | — | — | — | — | — | — | — |

✓ = granted · — = denied · *manage* = read + write

---

## 2. Permission Matrix

| Permission | Super Admin | Admin | Manager | WH Mgr | Sales | CS | Trade Reviewer |
|------------|:-----------:|:-----:|:-------:|:------:|:-----:|:--:|:--------------:|
| `dashboard.view` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `catalog.view` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — |
| `catalog.manage` | ✓ | ✓ | ✓ | — | — | — | — |
| `inventory.view` | ✓ | ✓ | ✓ | ✓ | — | — | — |
| `inventory.manage` | ✓ | ✓ | — | ✓ | — | — | — |
| `warehouse.manage` | ✓ | ✓ | — | ✓ | — | — | — |
| `orders.view` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — |
| `orders.manage` | ✓ | ✓ | ✓ | — | ✓ | ✓ | — |
| `customers.view` | ✓ | ✓ | ✓ | — | ✓ | ✓ | ✓ |
| `customers.manage` | ✓ | ✓ | ✓ | — | — | ✓ | — |
| `trade.view` | ✓ | ✓ | ✓ | — | ✓ | ✓ | ✓ |
| `trade.approve` | ✓ | ✓ | — | — | — | — | ✓ |
| `suppliers.view` | ✓ | ✓ | ✓ | ✓ | — | — | — |
| `suppliers.manage` | ✓ | ✓ | ✓ | — | — | — | — |
| `reports.view` | ✓ | ✓ | ✓ | — | ✓ | — | — |
| `reports.export` | ✓ | ✓ | ✓ | — | — | — | — |
| `settings.view` | ✓ | ✓ | ✓ | — | — | — | — |
| `users.manage` | ✓ | — | — | — | — | — | — |

Source of truth: `backend/apps/accounts/rbac.py` → `ROLE_PERMISSIONS`

---

## 3. Role Hierarchy

```
Super Admin (all permissions)
    └── Admin (all except users.manage)
            └── Manager (operations — no trade.approve)
                    ├── Warehouse Manager (fulfillment/inventory)
                    ├── Sales Representative (orders + trade view)
                    ├── Customer Service (orders + customers + trade view)
                    └── Trade Reviewer (trade approve only + customers view)

Storefront (external):
    ├── Trade Customer
    └── Customer
```

**Separation of duties:**
- Trade approval restricted to **Trade Reviewer**, **Admin**, and **Super Admin**
- Manager retains `trade.view` for visibility but cannot approve/reject
- `is_staff` enables Django admin UI only — **not** business permissions

---

## 4. Required Code Changes (Implemented)

| File | Change |
|------|--------|
| `apps/accounts/managers.py` | Removed `sync_platform_roles` on `is_staff`; superuser only |
| `apps/accounts/services.py` | `sync_superuser_role()` — no Manager auto-assignment |
| `apps/accounts/admin.py` | Django admin save syncs superuser role only |
| `apps/accounts/rbac.py` | Added `TRADE_REVIEWER` role; removed `trade.approve` from Manager |
| `apps/accounts/constants.py` | Added `TRADE_REVIEWER` slug + portal access |
| `frontend/src/lib/rbac/roles.ts` | Added Trade Reviewer role |
| `frontend/src/lib/rbac/access.ts` | Admin portal role list updated |
| `apps/accounts/tests/test_role_boundaries.py` | **New** — automated boundary tests |
| `apps/accounts/tests/test_rbac.py` | Updated helpers + `is_staff` isolation test |

### Post-deploy action

```bash
cd backend
python manage.py shell -c "from apps.accounts.services import RoleService; RoleService.ensure_system_roles()"
```

This seeds the new Trade Reviewer role and removes stale `trade.approve` from Manager in the database.

---

## 5. Security Risk Assessment

| Risk | Severity | Before | After |
|------|----------|--------|-------|
| `is_staff` auto-grants Manager permissions | **Critical** | Any staff flag → Manager + trade.approve | Fixed — staff flag alone grants nothing |
| Dual role accumulation (WH + Manager) | **High** | `create_user(is_staff=True)` + assign WH still had Manager | Fixed |
| Manager can approve trade (SoD violation) | **Medium** | Manager had trade.approve | Fixed — dedicated Trade Reviewer role |
| Superuser bypass | **Low (accepted)** | Superuser gets all permissions via DB query | Unchanged — by design |
| Django `IsStaffUser` on API schema | **Low** | Swagger/docs gated by is_staff | Unchanged — docs only, not business APIs |
| Frontend route guards vs API | **Low** | Permission-based on both layers | Unchanged — verified |

**Residual risks:**
1. Users with multiple explicit roles accumulate union of permissions — review multi-role assignments in production
2. Org-scoped roles require careful assignment for B2B tenants
3. Assign Trade Reviewer role to users who need approval capability (Managers no longer have it)

---

## Automated Test Coverage

Run boundary tests:

```powershell
cd backend
$env:USE_SQLITE_FOR_TESTS='1'
python manage.py test apps.accounts.tests.test_role_boundaries apps.accounts.tests.test_rbac --settings=config.settings.test
```

Tests verify:
- `is_staff` without role → zero business permissions
- Warehouse / Sales / CS cannot approve trade
- Trade Reviewer can approve trade
- Manager cannot approve trade (post-separation)
- Admin can approve trade
- Role permission matrix matches seed
- Customer cannot access admin endpoints

---

## Related Documents

- [RBAC.md](./RBAC.md) — operational RBAC guide (update `is_staff` section after deploy)
- [PHASE_B_OPERATIONAL.md](./PHASE_B_OPERATIONAL.md) — operational module readiness
- [PHASE_C_PRODUCTION_VALIDATION.md](./PHASE_C_PRODUCTION_VALIDATION.md) — validation suite
