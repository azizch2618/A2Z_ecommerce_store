# A2Z Tools — Client Demo Checklist

Use this runbook before a client presentation.

## 1. Environment setup

```bash
# Terminal 1 — API
cd backend
python manage.py migrate
python manage.py seed_demo

# Terminal 2 — Storefront + dashboard
cd frontend
cp .env.local.example .env.local   # if needed
# Set NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
npm run dev
```

## 2. Demo accounts

| Role | Email | Password |
|------|-------|----------|
| Retail customer | `customer@demo.a2ztools.com` | `Demo@2026!` |
| Trade customer | `trade@demo.a2ztools.com` | `Demo@2026!` |
| Business customer | `business@demo.a2ztools.com` | `Demo@2026!` |
| Admin / dashboard | `admin@demo.a2ztools.com` | `Demo@2026!` |

## 3. Recommended demo flow (15–20 min)

### Storefront (5 min)

1. Open **http://localhost:3000**
2. Search **“Cisco”** or **“UniFi”** in the header search
3. Open **Cisco Catalyst 9200** — show specs, GST-inclusive price, reviews
4. **Add to cart** → view cart badge update
5. **Sign in** as `customer@demo.a2ztools.com`
6. **Checkout** — place order with test card details
7. Confirm redirect to **account orders**

### Admin dashboard (8 min)

1. Sign in as **admin@demo.a2ztools.com**
2. Open **http://localhost:3000/admin-dashboard**
3. **Dashboard** — revenue KPIs, sales charts, low stock
4. **Orders** — find the order just placed; show status **Paid**
5. **Inventory** — show stock reduced for ordered SKU
6. **Products** — 12 demo SKUs across networking, security, tools, electrical
7. **Customers** — retail + trade + business profiles

### Trade / B2B (optional, 3 min)

1. Sign in as `trade@demo.a2ztools.com`
2. Show order history and saved Sydney address
3. Mention trade pricing and credit terms on account

## 4. Talking points

- Australian **GST-inclusive** pricing on storefront
- **Real API** — not static mock data for catalog, cart, checkout, dashboard
- **Inventory ledger** updates when orders are paid (dev auto-pay enabled)
- **RBAC** — admin vs customer permissions
- Production path: Docker Compose + Nginx (see `docs/architecture/deployment.md`)

## 5. If something fails

| Issue | Fix |
|-------|-----|
| Empty product list | Run `python manage.py seed_demo` |
| Checkout redirect to login | Sign in with verified demo customer |
| Dashboard shows mock data | Sign in as admin (JWT required for live metrics) |
| API connection error | Confirm `NEXT_PUBLIC_API_URL` and backend on :8000 |

## 6. Reset demo data

```bash
cd backend
python manage.py seed_demo
```

Re-running is idempotent — products and users are updated in place.
