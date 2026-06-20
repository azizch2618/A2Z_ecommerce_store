# A2Z Tools — Launch Readiness & QA Report

**Date:** June 2026  
**Scope:** Mock-to-API remediation + client demo readiness  
**Status:** Priority integrations complete; admin secondary modules remain mock-backed

---

## Remediation summary (mock → Django API)

| Priority | Area | Status | API / integration |
|----------|------|--------|-------------------|
| Critical | Registration | ✅ | `POST /auth/register/` via `useRegister()` |
| Critical | Forgot password | ✅ | `POST /auth/password/reset/` |
| Critical | Account dashboard | ✅ | `useCurrentUser()`, `useOrders()`, `useQuotes()`, `useWishlistQuery()` |
| Critical | Account orders | ✅ | `GET /orders/` + `account-mapper.ts` |
| Critical | Account addresses | ✅ | `GET/POST/PATCH/DELETE /customers/addresses/` |
| Critical | Account settings | ✅ | `useUpdateProfile()` |
| Critical | Account trade | ✅ | Profile + quotes from API (no `mockUser`) |
| Critical | Homepage featured products | ✅ | `useProducts({ sort: "featured", limit: 8 })` |
| Critical | Admin dashboard metrics | ✅ | `/analytics/admin/dashboard/` — **mock fallback removed** |
| Critical | Admin orders / customers / products lists | ✅ | Live API when admin JWT present |
| High | Wishlist | ✅ | `/wishlist/` CRUD; guest prompted to sign in |
| High | Compare products | ✅ | `POST /products/compare/` + dynamic spec rows |
| High | Predictive search | ✅ | `GET /products/search/?q=` via `searchPredictiveFromApi` |
| High | PDP reviews & specs | ✅ | `ProductReview` model + detail serializer fields |

---

## Backend additions for remediation

- `ProductReview` model, `highlights` / `specifications` on `Product`
- `GET /products/search/`, `POST /products/compare/`, `GET /products/{slug}/reviews/`
- `featured` product sort (`-average_rating`, `-review_count`)
- Wishlist service + `/wishlist/` routes
- Address serializer exposes `id` (from `public_id`)
- Demo seeder populates specs, highlights, and reviews

---

## Remaining mock / static usage (out of priority scope)

| Item | Location | Notes |
|------|----------|-------|
| Admin categories, brands, suppliers, settings, reports, WMS | `lib/api/admin/mock-service.ts` | Not in client demo script |
| Category landing pages | `app/(categories)/[slug]/page.tsx` | Static catalog config |
| Homepage brands, categories, testimonials | `config/homepage.ts` | UI unchanged; content static |
| Newsletter forms | Various | No backend endpoint yet |
| Legacy config exports | `config/account.ts` (`mockUser`, `mockOrders`) | Unused by pages; types/helpers only |
| Static predictive search | `lib/predictive-search.ts` | Superseded by `predictive-search-api.ts` |

---

## Pre-launch command checklist

```bash
# Backend (requires Postgres on configured port)
cd backend && python manage.py migrate
cd backend && python manage.py seed_demo
cd backend && python manage.py test apps.orders apps.catalog apps.accounts --verbosity=1

# Frontend
cd frontend && npm run typecheck
```

---

## Demo accounts

| Role | Email | Password |
|------|-------|----------|
| Retail | `customer@demo.a2ztools.com` | `Demo@2026!` |
| Trade | `trade@demo.a2ztools.com` | `Demo@2026!` |
| Business | `business@demo.a2ztools.com` | `Demo@2026!` |
| Admin | `admin@demo.a2ztools.com` | `Demo@2026!` |

---

## Smoke-test matrix

| Flow | Expected |
|------|----------|
| Register new user | Account created, can sign in |
| Sign in → Account orders | Live order history |
| Sign in → Addresses | CRUD against API |
| Homepage featured row | Products from API |
| Admin login → dashboard | KPIs from analytics API (no mock fallback) |
| Search dropdown | Live product/category/brand suggestions |
| PDP | Reviews + specs from API |
| Wishlist (signed in) | Persists via `/wishlist/` |
| Compare (2–4 products) | Fetches comparison payload from API |
| `npm run typecheck` | ✅ Passes |

---

## Files touched (remediation)

**Backend:** `apps/catalog/models.py`, migrations, serializers, views, urls; `apps/orders/` wishlist; `apps/customers/serializers.py`; `apps/core/demo/seed_catalog.py`

**Frontend:** Account page views, `featured-products-section.tsx`, `wishlist-provider.tsx`, `compare-provider.tsx`, `use-predictive-search.ts`, `predictive-search-api.ts`, mappers (`account`, `wishlist`, `compare`, `product`), `lib/api/admin/api-service.ts`

**Docs:** `docs/DEMO_CLIENT_CHECKLIST.md`, this report
