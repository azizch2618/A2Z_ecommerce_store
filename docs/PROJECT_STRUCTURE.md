# Project Folder Structure

Complete directory layout for A2Z Tools. Empty directories contain `.gitkeep`.

```
a2z-tools/
├── .github/workflows/          # CI/CD pipelines
├── docs/                       # Planning & architecture docs
├── frontend/                   # Next.js 15 application
├── backend/                    # Django + DRF API
├── infrastructure/             # Nginx, Terraform, K8s
├── scripts/                    # Dev & ops scripts
├── docker-compose.yml
├── docker-compose.prod.yml
├── Makefile
├── README.md
└── .env.example
```

## Frontend (`frontend/`)

```
frontend/
├── public/
│   ├── images/brand/
│   ├── robots.txt
│   └── manifest.json
├── src/
│   ├── app/
│   │   ├── (marketing)/        # about, contact, trade-account, etc.
│   │   ├── (shop)/             # products, cart, checkout, search
│   │   ├── (account)/          # login, dashboard, orders, wishlist
│   │   ├── (trade)/            # bulk-order, price-lists, quotes
│   │   ├── blog/
│   │   ├── api/                # BFF route handlers
│   │   └── globals.css
│   ├── components/
│   │   ├── ui/                 # ShadCN primitives
│   │   ├── layout/
│   │   ├── product/
│   │   ├── cart/
│   │   ├── checkout/
│   │   ├── search/
│   │   ├── account/
│   │   └── seo/
│   ├── lib/
│   │   ├── api/
│   │   ├── utils/
│   │   ├── hooks/
│   │   ├── stores/
│   │   └── constants/
│   └── types/
├── package.json
├── tsconfig.json
├── next.config.ts
├── tailwind.config.ts
├── components.json
└── Dockerfile
```

## Backend (`backend/`)

```
backend/
├── apps/
│   ├── core/
│   ├── accounts/               # Auth, users, profiles
│   ├── organizations/            # B2B, ABN, trade accounts
│   ├── catalog/                # Products, categories, brands
│   ├── inventory/              # Stock, warehouses, suppliers
│   ├── pricing/                # GST, coupons, price lists
│   ├── cart/                   # Cart & wishlist
│   ├── orders/                 # Orders, fulfilment
│   ├── payments/               # Stripe, invoices
│   ├── shipping/               # AU carriers, rates
│   ├── quotes/                 # B2B RFQ
│   ├── notifications/          # Email, SMS
│   ├── cms/                    # Pages, blog
│   ├── reviews/
│   ├── analytics/
│   └── integrations/           # Xero, MYOB, webhooks
├── api/
│   ├── v1/                     # /api/v1/ routing
│   └── health/                 # Health & readiness probes
├── config/
│   ├── settings/               # base, dev, prod, test
│   ├── urls.py
│   ├── wsgi.py
│   ├── asgi.py
│   └── celery.py
├── requirements/
├── templates/
├── static/
├── media/
├── fixtures/
├── scripts/
├── manage.py
└── Dockerfile
```

## Infrastructure (`infrastructure/`)

```
infrastructure/
├── nginx/nginx.conf            # Reverse proxy (production)
├── terraform/                  # Cloud provisioning (future)
└── kubernetes/                 # K8s manifests (future)
```
