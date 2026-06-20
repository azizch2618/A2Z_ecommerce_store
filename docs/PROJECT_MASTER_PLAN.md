# A2Z Tools — Project Master Plan

**Australian Hardware & Networking Ecommerce Platform**

| Attribute | Value |
|-----------|-------|
| **Product** | A2Z Tools |
| **Market** | Australia |
| **Currency** | AUD |
| **Tax** | GST 10% (inclusive/exclusive display per ATO conventions) |
| **Audience** | Trade Professionals, Contractors, Businesses, DIY Customers |
| **Design** | Mobile-first, professional UI, SEO-friendly |
| **Status** | Architecture & Planning |

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Architecture Overview](#2-architecture-overview)
3. [Complete Project Structure](#3-complete-project-structure)
4. [Feature List](#4-feature-list)
5. [Module List](#5-module-list)
6. [Development Roadmap](#6-development-roadmap)
7. [Cross-Cutting Concerns](#7-cross-cutting-concerns)
8. [Future Expansion Strategy](#8-future-expansion-strategy)
9. [Appendix](#9-appendix)

---

## 1. Executive Summary

A2Z Tools is a B2B/B2C ecommerce platform specialising in hardware, networking equipment, and trade supplies for the Australian market. The platform serves four customer segments with differentiated experiences: trade accounts with credit terms, contractor bulk ordering, business procurement workflows, and consumer DIY shopping.

The initial build focuses on a **headless commerce architecture**: Next.js 15 (frontend) consuming a Django REST Framework API (backend), with PostgreSQL as the system of record and Docker for local development and deployment consistency.

Design principles:

- **Mobile-first** — Primary UX optimised for on-site trade professionals
- **Australian compliance** — AUD, GST, ABN validation, Australian address formats
- **SEO-native** — Server-rendered product/category pages, structured data, sitemaps
- **API-first** — Backend designed for future mobile apps, CRM, HRM, and ERP integration
- **Modular monolith** — Django apps map to business domains; extract to microservices only when scale demands

---

## 2. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           CLIENTS                                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐ │
│  │  Web (Next)  │  │ Mobile (TBD) │  │  Admin Panel │  │  ERP/CRM    │ │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬──────┘ │
└─────────┼─────────────────┼─────────────────┼─────────────────┼────────┘
          │                 │                 │                 │
          └─────────────────┴────────┬────────┴─────────────────┘
                                     │ HTTPS / REST API (v1)
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    API GATEWAY LAYER (optional, Phase 3+)                │
└─────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│              DJANGO + DRF BACKEND (Modular Monolith)                     │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐         │
│  │ Catalog │ │  Cart   │ │ Orders  │ │ Accounts│ │ Payments│  ...    │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘         │
└─────────────────────────────────────────────────────────────────────────┘
          │                    │                    │
          ▼                    ▼                    ▼
   ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
   │ PostgreSQL  │     │    Redis    │     │  S3 / R2    │
   │  (Primary)  │     │   (Cache)   │     │  (Media)    │
   └─────────────┘     └─────────────┘     └─────────────┘
```

### Technology Decisions

| Layer | Technology | Rationale |
|-------|------------|-----------|
| Frontend | Next.js 15, TypeScript, TailwindCSS, ShadCN | SSR/SSG for SEO, App Router, component library |
| Backend | Django 5.x, DRF | Mature ORM, admin, auth, Australian ecosystem familiarity |
| Database | PostgreSQL 16+ | JSON fields, full-text search, reliability |
| Cache | Redis | Sessions, cart, rate limiting, Celery broker |
| Queue | Celery + Redis | Order processing, emails, inventory sync |
| Storage | S3-compatible (AWS S3 / Cloudflare R2) | Product images, documents, invoices |
| Containers | Docker + Docker Compose | Dev parity, CI/CD, production deploys |
| Search | PostgreSQL FTS → Elasticsearch (Phase 3) | Progressive complexity |

---

## 3. Complete Project Structure

```
a2z-tools/
│
├── README.md
├── PROJECT_MASTER_PLAN.md          # This document
├── .gitignore
├── .env.example
├── docker-compose.yml              # Local dev: web, api, db, redis, celery
├── docker-compose.prod.yml         # Production overrides
├── Makefile                        # Common dev commands
│
├── docs/                           # Living documentation
│   ├── architecture/
│   │   ├── api-conventions.md
│   │   ├── database-schema.md
│   │   ├── auth-flow.md
│   │   └── deployment.md
│   ├── api/                        # OpenAPI / Swagger exports
│   ├── adr/                        # Architecture Decision Records
│   └── runbooks/                   # Operational guides
│
├── frontend/                       # Next.js 15 Application
│   ├── package.json
│   ├── tsconfig.json
│   ├── next.config.ts
│   ├── tailwind.config.ts
│   ├── components.json             # ShadCN config
│   ├── Dockerfile
│   ├── .env.local.example
│   │
│   ├── public/
│   │   ├── favicon.ico
│   │   ├── robots.txt
│   │   ├── manifest.json           # PWA manifest (mobile-first)
│   │   └── images/
│   │       └── brand/
│   │
│   └── src/
│       ├── app/                    # App Router
│       │   ├── layout.tsx          # Root layout, fonts, metadata
│       │   ├── page.tsx            # Homepage
│       │   ├── globals.css
│       │   ├── not-found.tsx
│       │   ├── error.tsx
│       │   ├── loading.tsx
│       │   │
│       │   ├── (marketing)/        # Public marketing pages
│       │   │   ├── about/
│       │   │   ├── contact/
│       │   │   ├── trade-account/
│       │   │   ├── delivery/
│       │   │   ├── returns/
│       │   │   └── privacy/
│       │   │
│       │   ├── (shop)/             # Ecommerce routes
│       │   │   ├── products/
│       │   │   │   ├── page.tsx                    # Product listing
│       │   │   │   └── [slug]/
│       │   │   │       └── page.tsx                # Product detail (SSR)
│       │   │   ├── categories/
│       │   │   │   └── [slug]/
│       │   │   │       └── page.tsx
│       │   │   ├── brands/
│       │   │   │   └── [slug]/
│       │   │   │       └── page.tsx
│       │   │   ├── search/
│       │   │   │   └── page.tsx
│       │   │   ├── cart/
│       │   │   │   └── page.tsx
│       │   │   ├── checkout/
│       │   │   │   ├── page.tsx
│       │   │   │   ├── shipping/
│       │   │   │   ├── payment/
│       │   │   │   └── confirmation/
│       │   │   └── compare/
│       │   │       └── page.tsx
│       │   │
│       │   ├── (account)/          # Authenticated customer area
│       │   │   ├── layout.tsx
│       │   │   ├── login/
│       │   │   ├── register/
│       │   │   ├── forgot-password/
│       │   │   ├── dashboard/
│       │   │   ├── orders/
│       │   │   │   └── [id]/
│       │   │   ├── quotes/
│       │   │   ├── wishlist/
│       │   │   ├── addresses/
│       │   │   ├── payment-methods/
│       │   │   ├── invoices/
│       │   │   └── settings/
│       │   │
│       │   ├── (trade)/            # Trade/B2B specific
│       │   │   ├── bulk-order/
│       │   │   ├── credit-account/
│       │   │   ├── price-lists/
│       │   │   └── project-lists/
│       │   │
│       │   ├── blog/               # Content marketing / SEO
│       │   │   ├── page.tsx
│       │   │   └── [slug]/
│       │   │       └── page.tsx
│       │   │
│       │   ├── sitemap.ts          # Dynamic sitemap generation
│       │   └── api/                # Next.js Route Handlers (BFF layer)
│       │       ├── revalidate/
│       │       └── webhooks/
│       │
│       ├── components/
│       │   ├── ui/                 # ShadCN primitives
│       │   ├── layout/
│       │   │   ├── header/
│       │   │   ├── footer/
│       │   │   ├── mobile-nav/
│       │   │   └── breadcrumbs/
│       │   ├── product/
│       │   │   ├── product-card/
│       │   │   ├── product-gallery/
│       │   │   ├── product-specs/
│       │   │   ├── add-to-cart/
│       │   │   └── stock-badge/
│       │   ├── cart/
│       │   ├── checkout/
│       │   ├── search/
│       │   ├── account/
│       │   └── seo/
│       │       ├── json-ld.tsx
│       │       └── meta-tags.tsx
│       │
│       ├── lib/
│       │   ├── api/                # API client (fetch wrappers)
│       │   │   ├── client.ts
│       │   │   ├── catalog.ts
│       │   │   ├── cart.ts
│       │   │   ├── orders.ts
│       │   │   └── auth.ts
│       │   ├── utils/
│       │   │   ├── currency.ts     # AUD formatting
│       │   │   ├── gst.ts          # GST calculations
│       │   │   └── address.ts      # AU address helpers
│       │   ├── hooks/
│       │   ├── stores/             # Client state (Zustand)
│       │   └── constants/
│       │
│       ├── types/                  # TypeScript interfaces
│       │   ├── product.ts
│       │   ├── cart.ts
│       │   ├── order.ts
│       │   └── user.ts
│       │
│       └── middleware.ts           # Auth guards, redirects
│
├── backend/                        # Django + DRF Application
│   ├── Dockerfile
│   ├── requirements/
│   │   ├── base.txt
│   │   ├── dev.txt
│   │   └── prod.txt
│   ├── manage.py
│   ├── pytest.ini
│   ├── .env.example
│   │
│   ├── config/                     # Django project settings
│   │   ├── __init__.py
│   │   ├── settings/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── dev.py
│   │   │   ├── prod.py
│   │   │   └── test.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   ├── asgi.py
│   │   └── celery.py
│   │
│   ├── apps/                       # Domain-driven Django apps
│   │   ├── core/                   # Shared utilities, base models
│   │   │   ├── models.py           # TimeStampedModel, SoftDelete
│   │   │   ├── permissions.py
│   │   │   ├── pagination.py
│   │   │   ├── exceptions.py
│   │   │   └── middleware.py
│   │   │
│   │   ├── accounts/               # Users, auth, profiles
│   │   │   ├── models.py
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   ├── services.py
│   │   │   └── tests/
│   │   │
│   │   ├── organizations/          # B2B companies, ABN, trade accounts
│   │   │   ├── models.py
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   ├── services.py
│   │   │   └── tests/
│   │   │
│   │   ├── catalog/                # Products, categories, brands, attributes
│   │   │   ├── models.py
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   ├── filters.py
│   │   │   ├── services.py
│   │   │   ├── admin.py
│   │   │   └── tests/
│   │   │
│   │   ├── inventory/              # Stock, warehouses, reservations
│   │   │   ├── models.py
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   ├── services.py
│   │   │   ├── signals.py
│   │   │   └── tests/
│   │   │
│   │   ├── pricing/                # Price lists, tiers, promotions, GST
│   │   │   ├── models.py
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   ├── services/
│   │   │   │   ├── gst.py
│   │   │   │   ├── price_engine.py
│   │   │   │   └── promotions.py
│   │   │   └── tests/
│   │   │
│   │   ├── cart/                   # Shopping cart, wishlist
│   │   │   ├── models.py
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   ├── services.py
│   │   │   └── tests/
│   │   │
│   │   ├── orders/                 # Orders, fulfilment, returns
│   │   │   ├── models.py
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   ├── services/
│   │   │   │   ├── order_creation.py
│   │   │   │   ├── fulfilment.py
│   │   │   │   └── returns.py
│   │   │   ├── signals.py
│   │   │   └── tests/
│   │   │
│   │   ├── payments/               # Stripe, PayPal, trade credit, invoicing
│   │   │   ├── models.py
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   ├── gateways/
│   │   │   │   ├── stripe.py
│   │   │   │   └── trade_credit.py
│   │   │   ├── webhooks/
│   │   │   └── tests/
│   │   │
│   │   ├── shipping/               # AU carriers, zones, rates
│   │   │   ├── models.py
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   ├── carriers/
│   │   │   │   ├── australia_post.py
│   │   │   │   └── star_track.py
│   │   │   ├── services.py
│   │   │   └── tests/
│   │   │
│   │   ├── quotes/                 # B2B quote requests, RFQ
│   │   │   ├── models.py
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   └── tests/
│   │   │
│   │   ├── notifications/          # Email, SMS, push (future)
│   │   │   ├── models.py
│   │   │   ├── services/
│   │   │   │   ├── email.py
│   │   │   │   └── templates/
│   │   │   ├── tasks.py            # Celery tasks
│   │   │   └── tests/
│   │   │
│   │   ├── cms/                    # Pages, blog, banners (headless CMS)
│   │   │   ├── models.py
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   └── tests/
│   │   │
│   │   ├── reviews/                # Product reviews & ratings
│   │   │   ├── models.py
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   └── tests/
│   │   │
│   │   ├── analytics/              # Events, reporting hooks
│   │   │   ├── models.py
│   │   │   ├── services.py
│   │   │   └── tests/
│   │   │
│   │   └── integrations/           # Third-party connectors
│   │       ├── models.py
│   │       ├── xero/               # Accounting (future)
│   │       ├── myob/               # Accounting (future)
│   │       └── webhooks/
│   │
│   ├── api/                        # API routing layer
│   │   ├── v1/
│   │   │   ├── urls.py             # /api/v1/...
│   │   │   └── schema.py           # OpenAPI schema
│   │   └── health/
│   │       └── views.py
│   │
│   ├── templates/                  # Email & PDF templates
│   │   ├── emails/
│   │   └── pdf/
│   │       └── invoice.html
│   │
│   ├── static/
│   ├── media/
│   ├── locale/                     # i18n (en-AU primary)
│   ├── fixtures/                   # Seed data for dev
│   └── scripts/
│       ├── seed_catalog.py
│       └── migrate_media.py
│
├── infrastructure/                 # IaC & deployment
│   ├── nginx/
│   │   └── nginx.conf
│   ├── terraform/                  # Optional cloud provisioning
│   └── kubernetes/                 # Optional K8s manifests (Phase 4+)
│
├── scripts/
│   ├── setup.sh                    # First-time dev setup
│   ├── seed.sh
│   └── backup-db.sh
│
└── .github/
    └── workflows/
        ├── ci-frontend.yml
        ├── ci-backend.yml
        └── deploy.yml
```

---

## 4. Feature List

Features are grouped by domain and tagged with priority and customer segment.

**Priority:** P0 (MVP) · P1 (Launch) · P2 (Post-launch) · P3 (Future)

**Segments:** TR = Trade · CO = Contractor · BU = Business · DIY = DIY Consumer · ALL = All

### 4.1 Platform & Foundation

| ID | Feature | Priority | Segment | Notes |
|----|---------|----------|---------|-------|
| F-001 | Dockerised local development environment | P0 | ALL | docker-compose with hot reload |
| F-002 | CI/CD pipeline (lint, test, build) | P0 | ALL | GitHub Actions |
| F-003 | Environment-based configuration | P0 | ALL | Secrets via env vars |
| F-004 | API versioning (`/api/v1/`) | P0 | ALL | Backward-compatible evolution |
| F-005 | OpenAPI documentation | P1 | ALL | Auto-generated from DRF |
| F-006 | Health check endpoints | P0 | ALL | `/health`, `/ready` |
| F-007 | Structured logging & error tracking | P1 | ALL | Sentry integration |
| F-008 | Rate limiting & DDoS protection | P1 | ALL | Redis-backed throttling |

### 4.2 Authentication & Accounts

| ID | Feature | Priority | Segment | Notes |
|----|---------|----------|---------|-------|
| F-010 | Email/password registration & login | P0 | ALL | JWT or session-based |
| F-011 | Email verification | P0 | ALL | Required before first order |
| F-012 | Password reset flow | P0 | ALL | Secure token-based |
| F-013 | Social login (Google) | P2 | DIY, CO | OAuth2 |
| F-014 | Customer profile management | P0 | ALL | Name, phone, preferences |
| F-015 | Multiple saved addresses | P0 | ALL | AU address format validation |
| F-016 | Account dashboard | P0 | ALL | Orders, quotes, settings |
| F-017 | Role-based access (customer, trade, admin) | P0 | ALL | Django groups/permissions |
| F-018 | Two-factor authentication (2FA) | P2 | TR, BU | TOTP for trade accounts |
| F-019 | Session management & device logout | P2 | ALL | Security for shared devices |

### 4.3 B2B & Trade Accounts

| ID | Feature | Priority | Segment | Notes |
|----|---------|----------|---------|-------|
| F-020 | Trade account application workflow | P1 | TR, CO, BU | Online form + admin approval |
| F-021 | ABN validation & verification | P1 | TR, BU | ABR lookup integration |
| F-022 | Organisation/company profiles | P1 | TR, BU | Multi-user per org |
| F-023 | Custom price lists per account | P1 | TR, BU | Contract pricing |
| F-024 | Credit account & payment terms | P2 | TR, BU | Net 30/60, credit limits |
| F-025 | Purchase order (PO) number on orders | P1 | BU | PO reference field |
| F-026 | Bulk CSV upload ordering | P2 | TR, CO | SKU + qty import |
| F-027 | Project/job lists (saved BOMs) | P2 | TR, CO | Reorder entire project |
| F-028 | Multi-user org with roles | P2 | BU | Buyer, approver, admin |
| F-029 | Quote request (RFQ) workflow | P1 | TR, CO, BU | Request → admin quote → accept |
| F-030 | Tax invoice generation (GST-compliant) | P0 | ALL | ATO-compliant format |

### 4.4 Product Catalog

| ID | Feature | Priority | Segment | Notes |
|----|---------|----------|---------|-------|
| F-040 | Product CRUD (admin) | P0 | ALL | Django admin + API |
| F-041 | Hierarchical categories | P0 | ALL | Networking, tools, electrical, etc. |
| F-042 | Brand management | P0 | ALL | Cisco, Ubiquiti, DeWalt, etc. |
| F-043 | Product variants (size, colour, spec) | P1 | ALL | SKU-level variants |
| F-044 | Product attributes & specifications | P0 | ALL | Technical specs table |
| F-045 | Product images & gallery | P0 | ALL | Multiple images, zoom |
| F-046 | Product documents (datasheets, manuals) | P1 | TR, CO | PDF downloads |
| F-047 | Related / cross-sell products | P1 | ALL | "Customers also bought" |
| F-048 | Product comparison (up to 4) | P2 | TR, DIY | Side-by-side specs |
| F-049 | SKU & barcode (EAN/UPC) support | P0 | ALL | Inventory tracking |
| F-050 | Product visibility rules | P1 | TR, BU | Trade-only products |
| F-051 | Discontinued / replacement product mapping | P2 | ALL | Redirect to successor |
| F-052 | Bundle / kit products | P2 | TR, CO | Multi-SKU bundles |

### 4.5 Search & Discovery

| ID | Feature | Priority | Segment | Notes |
|----|---------|----------|---------|-------|
| F-060 | Full-text product search | P0 | ALL | PostgreSQL FTS initially |
| F-061 | Faceted filtering (brand, price, specs) | P0 | ALL | Category sidebar filters |
| F-062 | Sort (price, popularity, newest) | P0 | ALL | |
| F-063 | Search autocomplete / suggestions | P1 | ALL | Typeahead on mobile |
| F-064 | Category landing pages | P0 | ALL | SEO-optimised |
| F-065 | Brand landing pages | P1 | ALL | Brand story + products |
| F-066 | Breadcrumb navigation | P0 | ALL | Schema.org BreadcrumbList |
| F-067 | Advanced search (Elasticsearch) | P3 | ALL | Scale trigger |
| F-068 | Search analytics (zero-result tracking) | P2 | ALL | Merchandising insights |

### 4.6 Pricing & Promotions

| ID | Feature | Priority | Segment | Notes |
|----|---------|----------|---------|-------|
| F-070 | AUD currency display | P0 | ALL | `$1,234.56` format |
| F-071 | GST calculation (10%) | P0 | ALL | Inclusive/exclusive toggle |
| F-072 | GST display on cart & checkout | P0 | ALL | Line-item GST breakdown |
| F-073 | Tiered/volume pricing | P1 | TR, CO | Buy more, save more |
| F-074 | Coupon / discount codes | P1 | ALL | Percentage & fixed amount |
| F-075 | Promotional campaigns (BOGO, % off category) | P2 | ALL | Time-limited |
| F-076 | Price match request | P3 | TR, DIY | Manual approval workflow |
| F-077 | RRP vs sale price display | P1 | ALL | Strike-through pricing |

### 4.7 Inventory & Stock

| ID | Feature | Priority | Segment | Notes |
|----|---------|----------|---------|-------|
| F-080 | Real-time stock levels | P0 | ALL | Per-SKU quantity |
| F-081 | Low stock / backorder indicators | P0 | ALL | "Only 3 left", "Backorder" |
| F-082 | Multi-warehouse inventory | P2 | ALL | Sydney, Melbourne, Brisbane |
| F-083 | Stock reservation on checkout | P0 | ALL | Prevent overselling |
| F-084 | Notify when back in stock | P1 | ALL | Email alert subscription |
| F-085 | Inventory admin dashboard | P1 | Admin | Stock adjustments, history |
| F-086 | Supplier lead time display | P2 | TR | "Ships in 5-7 days" |

### 4.8 Cart & Checkout

| ID | Feature | Priority | Segment | Notes |
|----|---------|----------|---------|-------|
| F-090 | Persistent shopping cart | P0 | ALL | Guest (cookie) + logged-in |
| F-091 | Cart item quantity update | P0 | ALL | Inline +/- on mobile |
| F-092 | Save for later / wishlist | P1 | ALL | Move between cart & wishlist |
| F-093 | Multi-step checkout | P0 | ALL | Shipping → Payment → Review |
| F-094 | Guest checkout | P0 | DIY | No account required |
| F-095 | Australian address autocomplete | P1 | ALL | Google Places / Loqate |
| F-096 | Shipping method selection | P0 | ALL | Standard, express, pickup |
| F-097 | Click & collect (in-store pickup) | P1 | ALL | Warehouse/store selection |
| F-098 | Order summary with GST breakdown | P0 | ALL | Subtotal, GST, shipping, total |
| F-099 | Checkout field validation | P0 | ALL | Phone, postcode, state |
| F-100 | Abandoned cart recovery emails | P2 | ALL | Celery scheduled task |

### 4.9 Payments

| ID | Feature | Priority | Segment | Notes |
|----|---------|----------|---------|-------|
| F-110 | Credit/debit card (Stripe) | P0 | ALL | Visa, Mastercard, Amex |
| F-111 | Apple Pay / Google Pay | P1 | ALL | Stripe Payment Request |
| F-112 | PayPal | P2 | DIY | Alternative payment |
| F-113 | Trade account / invoice payment | P2 | TR, BU | Charge to account |
| F-114 | Bank transfer (EFT) instructions | P1 | BU | For large orders |
| F-115 | Payment failure handling & retry | P0 | ALL | Clear error messages |
| F-116 | Refund processing | P1 | ALL | Full & partial refunds |
| F-117 | Saved payment methods | P2 | ALL | Stripe Customer |

### 4.10 Orders & Fulfilment

| ID | Feature | Priority | Segment | Notes |
|----|---------|----------|---------|-------|
| F-120 | Order placement & confirmation | P0 | ALL | Email + on-screen |
| F-121 | Order history & status tracking | P0 | ALL | Placed → Shipped → Delivered |
| F-122 | Order detail view with line items | P0 | ALL | GST per line |
| F-123 | Shipping tracking integration | P1 | ALL | Carrier tracking links |
| F-124 | Order cancellation (pre-ship) | P1 | ALL | Customer self-service |
| F-125 | Return merchandise authorisation (RMA) | P2 | ALL | Return request workflow |
| F-126 | Reorder (one-click repeat order) | P1 | TR, CO | From order history |
| F-127 | Order export (PDF invoice) | P0 | ALL | Download from account |
| F-128 | Partial shipment support | P2 | TR, BU | Split fulfilment |
| F-129 | Admin order management | P0 | Admin | Status updates, notes |

### 4.11 Shipping & Delivery

| ID | Feature | Priority | Segment | Notes |
|----|---------|----------|---------|-------|
| F-130 | Australian shipping zones (state/postcode) | P0 | ALL | NSW, VIC, QLD, etc. |
| F-131 | Weight/dimension-based rate calculation | P0 | ALL | Per carrier rules |
| F-132 | Free shipping threshold | P1 | ALL | e.g. Free over $150 |
| F-133 | Express delivery option | P1 | ALL | Premium rate |
| F-134 | Australia Post integration | P2 | ALL | Live rates & labels |
| F-135 | StarTrack / courier integration | P3 | TR, BU | Freight for bulk |
| F-136 | Delivery ETA display | P1 | ALL | Estimated delivery date |
| F-137 | Restricted item shipping rules | P2 | ALL | Dangerous goods, batteries |

### 4.12 Content & SEO

| ID | Feature | Priority | Segment | Notes |
|----|---------|----------|---------|-------|
| F-140 | SSR/SSG product pages | P0 | ALL | Next.js generateMetadata |
| F-141 | Dynamic XML sitemap | P0 | ALL | Products, categories, blog |
| F-142 | robots.txt configuration | P0 | ALL | Crawl directives |
| F-143 | Schema.org structured data | P0 | ALL | Product, Organization, Breadcrumb |
| F-144 | Open Graph & Twitter cards | P0 | ALL | Social sharing |
| F-145 | Canonical URLs | P0 | ALL | Duplicate content prevention |
| F-146 | Custom meta title & description per page | P0 | ALL | CMS-managed |
| F-147 | Blog / guides content hub | P1 | DIY, TR | "How to install..." guides |
| F-148 | FAQ pages with FAQ schema | P1 | ALL | Rich snippets |
| F-149 | 301 redirect management | P1 | Admin | URL changes |
| F-150 | Core Web Vitals optimisation | P0 | ALL | Image optimisation, lazy load |
| F-151 | hreflang (en-AU) | P0 | ALL | Australian locale |

### 4.13 Notifications & Communications

| ID | Feature | Priority | Segment | Notes |
|----|---------|----------|---------|-------|
| F-160 | Transactional emails (order confirm, ship) | P0 | ALL | SendGrid / AWS SES |
| F-161 | Account emails (welcome, reset) | P0 | ALL | Branded templates |
| F-162 | Trade account status notifications | P1 | TR, BU | Approval/rejection |
| F-163 | Quote ready notification | P1 | TR, BU | Email + in-app |
| F-164 | SMS notifications (shipping updates) | P3 | ALL | Twilio |
| F-165 | Newsletter subscription | P2 | ALL | Mailchimp / Klaviyo |
| F-166 | Admin notification alerts | P1 | Admin | New orders, low stock |

### 4.14 Reviews & Trust

| ID | Feature | Priority | Segment | Notes |
|----|---------|----------|---------|-------|
| F-170 | Product reviews & star ratings | P2 | ALL | Post-purchase verified |
| F-171 | Review moderation (admin) | P2 | Admin | Approve/reject |
| F-172 | Aggregate rating on product page | P2 | ALL | Schema.org AggregateRating |
| F-173 | Trust badges (secure checkout, ABN) | P1 | ALL | Footer & checkout |

### 4.15 Admin & Operations

| ID | Feature | Priority | Segment | Notes |
|----|---------|----------|---------|-------|
| F-180 | Django admin panel | P0 | Admin | Product, order, user management |
| F-181 | Custom admin dashboard (KPIs) | P2 | Admin | Revenue, orders, top products |
| F-182 | Bulk product import (CSV) | P1 | Admin | Catalog onboarding |
| F-183 | Bulk price update | P1 | Admin | CSV or percentage |
| F-184 | Customer management & notes | P1 | Admin | Support context |
| F-185 | Sales reporting & export | P2 | Admin | Date range, GST summary |
| F-186 | Audit log (admin actions) | P2 | Admin | Who changed what |

### 4.16 Mobile Experience

| ID | Feature | Priority | Segment | Notes |
|----|---------|----------|---------|-------|
| F-190 | Responsive mobile-first layout | P0 | ALL | Breakpoints: 320px+ |
| F-191 | Touch-optimised navigation | P0 | ALL | Bottom nav, hamburger |
| F-192 | Mobile product image swipe gallery | P0 | ALL | Touch gestures |
| F-193 | Sticky add-to-cart bar (mobile) | P0 | ALL | Fixed bottom CTA |
| F-194 | PWA manifest & install prompt | P2 | TR, CO | Add to home screen |
| F-195 | Offline cart persistence | P3 | ALL | Service worker |

---

## 5. Module List

Modules represent deployable/cohesive units of functionality. Each maps to Django apps (backend) and feature folders (frontend).

### 5.1 Backend Modules (Django Apps)

| Module | Django App | Responsibility | Dependencies |
|--------|-----------|----------------|--------------|
| **M-CORE** | `core` | Base models, middleware, pagination, exceptions, shared utilities | — |
| **M-ACCOUNTS** | `accounts` | User auth, profiles, JWT/session, password management | M-CORE |
| **M-ORGANIZATIONS** | `organizations` | Companies, ABN, trade accounts, org users, roles | M-ACCOUNTS |
| **M-CATALOG** | `catalog` | Products, categories, brands, attributes, variants, media | M-CORE |
| **M-INVENTORY** | `inventory` | Stock levels, warehouses, reservations, adjustments | M-CATALOG |
| **M-PRICING** | `pricing` | Price lists, tiers, promotions, coupons, GST engine | M-CATALOG, M-ORGANIZATIONS |
| **M-CART** | `cart` | Cart, wishlist, cart merge (guest→user) | M-CATALOG, M-PRICING, M-INVENTORY |
| **M-ORDERS** | `orders` | Order lifecycle, fulfilment, returns, invoices | M-CART, M-ACCOUNTS, M-INVENTORY |
| **M-PAYMENTS** | `payments` | Payment processing, refunds, trade credit | M-ORDERS |
| **M-SHIPPING** | `shipping` | AU zones, rate calculation, carrier integration | M-ORDERS |
| **M-QUOTES** | `quotes` | RFQ, quote generation, quote-to-order conversion | M-CATALOG, M-PRICING, M-ORGANIZATIONS |
| **M-NOTIFICATIONS** | `notifications` | Email, SMS, in-app notifications, templates | M-ACCOUNTS, M-ORDERS |
| **M-CMS** | `cms` | Pages, blog posts, banners, navigation, SEO metadata | M-CORE |
| **M-REVIEWS** | `reviews` | Product reviews, ratings, moderation | M-CATALOG, M-ORDERS |
| **M-ANALYTICS** | `analytics` | Event tracking, reporting data collection | M-CORE |
| **M-INTEGRATIONS** | `integrations` | Xero, MYOB, webhooks, third-party APIs | M-ORDERS, M-PAYMENTS |

### 5.2 Frontend Modules (Next.js)

| Module | Location | Responsibility |
|--------|----------|----------------|
| **M-FE-CORE** | `src/lib/`, `src/components/ui/`, `src/components/layout/` | API client, utils (AUD, GST), ShadCN, header/footer |
| **M-FE-CATALOG** | `src/app/(shop)/`, `src/components/product/` | Product listing, detail, categories, brands |
| **M-FE-SEARCH** | `src/app/(shop)/search/`, `src/components/search/` | Search, filters, autocomplete |
| **M-FE-CART** | `src/app/(shop)/cart/`, `src/components/cart/` | Cart management, mini-cart |
| **M-FE-CHECKOUT** | `src/app/(shop)/checkout/`, `src/components/checkout/` | Multi-step checkout flow |
| **M-FE-ACCOUNT** | `src/app/(account)/`, `src/components/account/` | Login, register, dashboard, orders |
| **M-FE-TRADE** | `src/app/(trade)/` | Trade account, bulk order, quotes, price lists |
| **M-FE-MARKETING** | `src/app/(marketing)/`, `src/app/blog/` | Static pages, blog, contact |
| **M-FE-SEO** | `src/components/seo/`, `sitemap.ts` | Metadata, JSON-LD, sitemaps |

### 5.3 Infrastructure Modules

| Module | Location | Responsibility |
|--------|----------|----------------|
| **M-INFRA-DOCKER** | `docker-compose*.yml`, `Dockerfile`s | Container orchestration |
| **M-INFRA-CI** | `.github/workflows/` | Automated testing & deployment |
| **M-INFRA-NGINX** | `infrastructure/nginx/` | Reverse proxy, SSL termination |
| **M-INFRA-IAC** | `infrastructure/terraform/` | Cloud resource provisioning |

### 5.4 Module Interaction Map

```
                    ┌─────────────┐
                    │  M-FE-CORE  │
                    └──────┬──────┘
                           │ API calls
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
   │ M-FE-CATALOG│  │ M-FE-CART   │  │ M-FE-ACCOUNT│
   └──────┬──────┘  └──────┬──────┘  └──────┬──────┘
          │                │                │
          ▼                ▼                ▼
   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
   │ M-CATALOG   │  │ M-CART      │  │ M-ACCOUNTS  │
   │ M-PRICING   │  │ M-ORDERS    │  │ M-ORGANIZ.  │
   │ M-INVENTORY │  │ M-PAYMENTS  │  └─────────────┘
   └─────────────┘  │ M-SHIPPING  │
                    └─────────────┘
```

---

## 6. Development Roadmap

### Overview Timeline

```
Phase 0 ──► Phase 1 ──► Phase 2 ──► Phase 3 ──► Phase 4 ──► Phase 5
Foundation   MVP Core    Launch      Growth      Scale       Enterprise
(4 weeks)    (8 weeks)   (6 weeks)   (8 weeks)   (ongoing)   (future)
```

---

### Phase 0: Foundation (Weeks 1–4)

**Goal:** Development environment, project scaffolding, CI/CD, and core conventions.

| Week | Deliverables |
|------|-------------|
| 1 | Repository setup, monorepo structure, Docker Compose (PostgreSQL, Redis, backend, frontend) |
| 2 | Django project scaffold, DRF config, base settings (dev/prod/test), core app with base models |
| 3 | Next.js 15 scaffold, TailwindCSS + ShadCN setup, layout components (header, footer, mobile nav) |
| 4 | CI pipelines (lint, typecheck, test), API health endpoints, OpenAPI schema stub, dev documentation |

**Exit Criteria:**
- `docker compose up` starts full stack
- Frontend renders homepage with brand layout
- Backend responds to `/api/v1/health/`
- CI passes on push

---

### Phase 1: MVP Core (Weeks 5–12)

**Goal:** Minimum viable ecommerce — browse, cart, checkout, pay, order.

#### Sprint 1 (Weeks 5–6): Catalog & Auth

| Backend | Frontend |
|---------|----------|
| M-ACCOUNTS: registration, login, JWT, profile | Login/register pages |
| M-CATALOG: products, categories, brands, attributes | Product listing & detail pages (SSR) |
| M-INVENTORY: stock levels | Stock badges, category pages |
| M-PRICING: AUD display, GST calculation | Price display with GST |

#### Sprint 2 (Weeks 7–8): Search & Cart

| Backend | Frontend |
|---------|----------|
| M-CATALOG: filters, sorting, pagination | Faceted search UI, sort controls |
| M-CART: guest + authenticated cart | Cart page, mini-cart drawer |
| M-PRICING: coupons (basic) | Coupon code input |

#### Sprint 3 (Weeks 9–10): Checkout & Payments

| Backend | Frontend |
|---------|----------|
| M-SHIPPING: AU zones, flat/weight rates | Shipping method selection |
| M-ORDERS: order creation, confirmation | Multi-step checkout flow |
| M-PAYMENTS: Stripe integration | Card payment form (Stripe Elements) |
| M-NOTIFICATIONS: order confirmation email | Order confirmation page |

#### Sprint 4 (Weeks 11–12): Account & Admin

| Backend | Frontend |
|---------|----------|
| M-ACCOUNTS: addresses, order history | Account dashboard, order detail |
| M-ORDERS: order status, PDF invoice | Order tracking view |
| Django admin: product & order management | — |
| M-CMS: static pages API | About, contact, delivery, returns pages |

**Phase 1 Exit Criteria:**
- Customer can register, browse products, add to cart, checkout with card, receive order confirmation
- Admin can manage products and orders via Django admin
- GST correctly calculated and displayed
- Product pages are SSR with basic SEO metadata

---

### Phase 2: Launch Ready (Weeks 13–18)

**Goal:** B2B features, SEO polish, performance, and production deployment.

#### Sprint 5 (Weeks 13–14): Trade & B2B

| Deliverables |
|-------------|
| M-ORGANIZATIONS: trade account application, ABN field |
| M-PRICING: custom price lists, tiered pricing |
| M-QUOTES: RFQ workflow (request → admin quote → accept) |
| M-FE-TRADE: trade account pages, quote request UI |
| PO number on checkout for business customers |

#### Sprint 6 (Weeks 15–16): SEO & Content

| Deliverables |
|-------------|
| Dynamic XML sitemap, robots.txt |
| Schema.org JSON-LD (Product, Organization, Breadcrumb) |
| Open Graph & Twitter cards on all pages |
| M-CMS: blog/guides content hub |
| FAQ pages with structured data |
| Core Web Vitals audit & optimisation |

#### Sprint 7 (Weeks 17–18): Polish & Deploy

| Deliverables |
|-------------|
| Mobile UX audit & refinements (sticky ATC, touch gallery) |
| Abandoned cart email (basic) |
| Production Docker Compose / cloud deployment |
| SSL, domain, CDN for static assets |
| Load testing & security audit |
| Seed catalog with real product data |
| Soft launch with limited catalogue |

**Phase 2 Exit Criteria:**
- Production environment live at staging/production URL
- Trade account workflow functional
- Lighthouse scores: Performance > 80, SEO > 95
- Payment processing in production mode

---

### Phase 3: Growth (Weeks 19–26)

**Goal:** Enhanced B2B, integrations, and customer retention features.

| Area | Features |
|------|----------|
| **B2B** | Credit accounts, bulk CSV ordering, project lists, multi-user orgs |
| **Shipping** | Australia Post live rates, click & collect, delivery ETA |
| **Payments** | Apple Pay / Google Pay, PayPal, trade account invoicing |
| **Retention** | Wishlist, back-in-stock alerts, reorder, product reviews |
| **Marketing** | Newsletter integration, promotional campaigns |
| **Admin** | Custom dashboard, bulk import/export, sales reporting |
| **Search** | Autocomplete, search analytics |

---

### Phase 4: Scale (Weeks 27+)

**Goal:** Performance at scale, advanced integrations, operational efficiency.

| Area | Features |
|------|----------|
| **Search** | Elasticsearch migration for advanced search |
| **Inventory** | Multi-warehouse, supplier lead times |
| **Shipping** | StarTrack/courier freight integration |
| **Integrations** | Xero/MYOB accounting sync |
| **Analytics** | Custom reporting, conversion funnels |
| **Mobile** | PWA enhancements, evaluate native app (React Native) |
| **Infrastructure** | Kubernetes, auto-scaling, read replicas |

---

### Phase 5: Enterprise Expansion (Future)

**Goal:** CRM, HRM, ERP modules as integrated platform.

| System | Scope | Integration Point |
|--------|-------|-------------------|
| **CRM** | Lead management, customer communication history, sales pipeline | M-ACCOUNTS, M-ORGANIZATIONS, M-ANALYTICS |
| **HRM** | Employee records, payroll hooks, leave management | Standalone module, shared auth |
| **ERP** | Procurement, supplier management, financial reporting | M-INVENTORY, M-ORDERS, M-PAYMENTS, M-INTEGRATIONS |
| **Mobile Apps** | iOS & Android native or React Native | Shared REST API (M-FE-CORE patterns) |

These systems will be built as **separate Django apps** (or eventually separate services) sharing the PostgreSQL database and authentication layer, exposed via the same `/api/v1/` namespace.

---

### Roadmap Summary (Gantt-style)

```
Phase 0: Foundation          ████
Phase 1: MVP Core                 ████████████████
Phase 2: Launch Ready                              ████████████
Phase 3: Growth                                               ████████████████
Phase 4: Scale                                                               ████ →
Phase 5: Enterprise                                                              → ∞

MVP Launch Target: ~Week 18
```

---

## 7. Cross-Cutting Concerns

### 7.1 Australian Compliance

| Concern | Implementation |
|---------|---------------|
| Currency | All prices stored and displayed in AUD (cents internally) |
| GST | 10% GST engine in M-PRICING; tax invoices per ATO requirements |
| ABN | Validation on trade account registration (ABR API) |
| Addresses | Australian states, 4-digit postcodes, suburb validation |
| Privacy | Australian Privacy Act compliance, privacy policy page |
| Consumer Law | ACL-compliant returns policy, clear pricing display |

### 7.2 Security

- HTTPS everywhere (TLS 1.2+)
- JWT with short expiry + refresh tokens
- CSRF protection on state-changing endpoints
- Input validation on all API endpoints (DRF serializers)
- PCI DSS compliance via Stripe (no card data stored)
- Rate limiting on auth and checkout endpoints
- OWASP Top 10 mitigations

### 7.3 Performance Targets

| Metric | Target |
|--------|--------|
| TTFB (product page) | < 200ms |
| LCP | < 2.5s |
| API response (p95) | < 300ms |
| Cart operations | < 150ms |
| Checkout completion | < 5s total |

### 7.4 API Design Conventions

- RESTful endpoints under `/api/v1/`
- JSON request/response bodies
- Consistent error format: `{ "error": { "code": "...", "message": "...", "details": {} } }`
- Cursor-based pagination for lists
- Filtering via query params: `?category=networking&brand=ubiquiti&sort=price_asc`
- Version header support for future mobile clients

---

## 8. Future Expansion Strategy

### 8.1 CRM Module (Future)

**Purpose:** Manage customer relationships beyond transactions.

- Lead capture from quote requests and contact forms
- Customer communication timeline (emails, calls, notes)
- Sales pipeline for trade account acquisition
- Automated follow-ups for abandoned quotes
- Integration: shares `M-ACCOUNTS` and `M-ORGANIZATIONS` data model

### 8.2 HRM Module (Future)

**Purpose:** Internal workforce management.

- Employee records and onboarding
- Leave and attendance tracking
- Payroll data export
- Integration: separate auth realm (staff vs customers), shared infrastructure

### 8.3 ERP Module (Future)

**Purpose:** Back-office operations and financial management.

- Purchase orders to suppliers
- Goods received notes (GRN)
- Stock reconciliation
- General ledger integration (Xero/MYOB)
- Financial reporting (P&L, GST BAS reporting)
- Integration: extends `M-INVENTORY`, `M-ORDERS`, `M-PAYMENTS`

### 8.4 Mobile Apps (Future)

**Purpose:** Native mobile experience for trade professionals on job sites.

- React Native or Flutter consuming existing REST API
- Barcode scanning for quick product lookup
- Offline catalog browsing
- Push notifications for order updates
- Quick reorder from order history

### 8.5 Expansion Principles

1. **API-first** — Every new module exposes REST APIs; frontend is just one consumer
2. **Shared auth** — Single sign-on across ecommerce, CRM, HRM, ERP
3. **Event-driven** — Celery tasks and webhooks connect modules loosely
4. **Modular monolith first** — Extract to microservices only when team size or scale demands
5. **Data ownership** — Each module owns its tables; cross-module access via APIs or read replicas

---

## 9. Appendix

### 9.1 Recommended Hardware & Networking Categories

```
├── Networking
│   ├── Routers & Gateways
│   ├── Switches (Managed, Unmanaged, PoE)
│   ├── Wireless Access Points
│   ├── Firewalls & Security
│   ├── Cables & Connectors (Cat6, Cat6a, Fibre)
│   └── Racks & Cabinets
├── Tools & Equipment
│   ├── Hand Tools
│   ├── Power Tools
│   ├── Test Equipment
│   └── Tool Storage
├── Electrical
│   ├── Cabling & Wiring
│   ├── Switches & Outlets
│   ├── Circuit Protection
│   └── Lighting
├── Security & Surveillance
│   ├── CCTV Cameras
│   ├── NVRs & DVRs
│   ├── Access Control
│   └── Alarms
├── Data & Server
│   ├── Server Hardware
│   ├── Storage (NAS, SAN)
│   ├── UPS & Power
│   └── KVM & Peripherals
└── Consumables
    ├── Cable Ties & Management
    ├── Labels & Markers
    ├── Batteries
    └── Adhesives & Tapes
```

### 9.2 Key Third-Party Services

| Service | Purpose | Phase |
|---------|---------|-------|
| Stripe | Card payments | Phase 1 |
| SendGrid / AWS SES | Transactional email | Phase 1 |
| AWS S3 / Cloudflare R2 | Media storage | Phase 1 |
| Sentry | Error tracking | Phase 2 |
| Google Places / Loqate | AU address autocomplete | Phase 2 |
| Australia Post API | Shipping rates & tracking | Phase 3 |
| Xero / MYOB | Accounting integration | Phase 4 |
| Elasticsearch | Advanced search | Phase 4 |

### 9.3 Team Roles (Recommended)

| Role | Responsibility | Phase Needed |
|------|---------------|--------------|
| Tech Lead / Architect | Architecture, code review, DevOps | Phase 0 |
| Backend Developer (Django) | API, business logic, integrations | Phase 0 |
| Frontend Developer (Next.js) | UI, SEO, mobile UX | Phase 0 |
| UI/UX Designer | Wireframes, design system, mobile flows | Phase 0 |
| DevOps Engineer | CI/CD, deployment, monitoring | Phase 2 |
| QA Engineer | Test plans, automation, UAT | Phase 1 |
| Product Owner | Backlog, priorities, stakeholder communication | Phase 0 |
| Content/SEO Specialist | Product descriptions, blog, metadata | Phase 2 |

### 9.4 Success Metrics (KPIs)

| Metric | MVP Target | 6-Month Target |
|--------|-----------|----------------|
| Product catalogue size | 500 SKUs | 5,000 SKUs |
| Page load (LCP) | < 3s | < 2.5s |
| Checkout conversion | 2% | 3.5% |
| Trade account signups | 10 | 100 |
| Monthly orders | 50 | 500 |
| API uptime | 99.5% | 99.9% |

---

*Document Version: 1.0*
*Last Updated: June 2025*
*Author: Senior Software Architect*
