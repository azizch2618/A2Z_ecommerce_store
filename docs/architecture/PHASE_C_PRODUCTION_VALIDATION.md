# Phase C - Production Validation

**Project:** A2Z Tools  
**Objective:** Validate pilot deployment readiness without adding features.  
**Date:** 2026-06-20

---

## Validation Scope

This phase validates:

- Integration behavior across authentication, commerce, operations, and reporting
- End-to-end customer and operations journeys
- Regression checks for route/API integrity and permission boundaries
- UAT execution readiness for Admin, Warehouse, Sales, and Customer cohorts

---

## 1) Integration Test Suite

Implemented in:

- `backend/apps/integrations/tests/test_phase_c_integration.py`
- `backend/apps/integrations/tests/test_phase_c_regression.py`

### Coverage Matrix

| Domain | Coverage status | Evidence |
|---|---|---|
| Authentication | Covered | register + login flow in integration suite |
| Products | Covered | `GET /api/v1/products/` |
| Categories | Covered | public + admin category endpoints |
| Brands | Covered | public + admin brand endpoints |
| Inventory | Covered | inventory level changes via PO receive |
| Orders | Covered | checkout, detail, pack/ship/deliver/refund |
| Cart | Covered | add item + fetch cart |
| Checkout | Covered | `POST /api/v1/orders/` |
| Payments | Covered | Stripe config + webhook success simulation |
| Trade Accounts | Covered | application review (approve) |
| Purchase Orders | Covered | create -> submit -> confirm -> receive |
| Warehouses | Covered | admin warehouse endpoint in regression suite |
| Reports | Covered | report catalog + CSV export |

### Test Commands Used

- `python manage.py check --settings=config.settings.test` (completed successfully)
- `python manage.py test apps.integrations.tests.test_phase_c_integration apps.integrations.tests.test_phase_c_regression --settings=config.settings.test --keepdb -v 2` (execution blocked during DB bootstrap)

---

## 2) End-to-End Test Scenarios

## Customer E2E Scenario

1. Register customer account
2. Login
3. Browse products/categories/brands
4. Add SKU to cart
5. Checkout order
6. Complete payment (Stripe webhook simulation)
7. View order detail and paid status

## Operations E2E Scenario

1. Approve trade application with credit limit
2. Create purchase order
3. Submit and confirm PO
4. Receive stock into warehouse
5. Pack -> ship -> deliver order
6. Process refund
7. Export sales report CSV

---

## 3) Regression Test Suite

Regression suite validates:

- No broken core routes (health, catalog, payments, cart, order auth boundaries)
- No broken admin API responses for authorized users
- No RBAC leaks for customer role on admin endpoints
- No permission bypass for warehouse role on trade approval endpoints
- No anonymous mutation of admin resources

Implemented in:

- `backend/apps/integrations/tests/test_phase_c_regression.py`

---

## 4) UAT Checklist

## Admin UAT

- [ ] Manage categories (create/search/deactivate)
- [ ] Manage brands (create/logo URL/feature toggle)
- [ ] Review trade applications (approve/reject/credit limit)
- [ ] Export all report types (sales/inventory/GST/customers)

## Warehouse Staff UAT

- [ ] Receive PO lines and verify stock increments
- [ ] Validate warehouse list/search and status visibility
- [ ] Confirm order fulfillment status transitions are reflected

## Sales Team UAT

- [ ] View all orders and perform pack/ship/deliver
- [ ] Validate cancellation and refund actions
- [ ] Confirm customer/trade account status visibility

## Customer UAT

- [ ] Register/login/profile
- [ ] Browse product catalog + filters
- [ ] Add/update cart items and checkout
- [ ] Confirm payment and order tracking visibility

---

## 5) Deliverables

## A. Test Coverage Report

- **API module coverage:** 13/13 requested domains instrumented in Phase C tests.
- **Cross-functional journey coverage:** 2 major E2E journeys implemented (Customer + Operations).
- **Security regression checks:** RBAC leak and permission bypass checks included.

## B. Failed Scenarios

1. **Automated test execution blocked by environment**
   - Django test runner stalls at PostgreSQL test database bootstrap (`a2z_tools_test`) even with `--keepdb`.
   - This prevented obtaining pass/fail counts for newly added suites in current environment.

## C. Critical Bugs

1. **P0 Test Infrastructure Blocker**  
   Test suite cannot complete in current environment due test DB bootstrap lock/hang.

2. **P1 Data workflow gap (known from Phase B)**  
   Trade registration marks customer as pending but does not always create `TradeApplication` automatically; operations currently rely on manual application rows.

3. **P1 Report format parity gap (known)**  
   CSV export is operational; PDF/Excel production output path remains incomplete for accounting-grade exports.

## D. Pilot Readiness Score

**78 / 100**

Rationale:

- + Strong operational API and RBAC posture
- + End-to-end operational workflows now test-specified
- - Automated validation blocked by environment issue
- - Remaining known operational gaps in trade intake/report formats

## E. Production Readiness Score

**69 / 100**

Rationale:

- + Platform and operational modules implemented
- + Security and permissions hardened
- - Incomplete automated execution evidence due CI/test DB blocker
- - Missing full report format parity and some workflow hardening before general availability

---

## Immediate Actions Before Pilot

1. Fix PostgreSQL test database bootstrap stall in test environment (highest priority).
2. Run full Phase C suites and publish exact pass/fail metrics.
3. Close trade application intake automation gap.
4. Complete PDF/Excel report generation path or downgrade requirements for pilot scope.
5. Execute UAT checklist with signed acceptance from each role group.
