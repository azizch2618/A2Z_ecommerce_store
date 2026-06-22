# Local Validation Guide — A2Z Tools ERP

Step-by-step guide from a **fresh clone** to a running local stack. Commands are taken from the actual repo layout (`docker-compose.yml`, management commands, URL routes).

**Important repo facts:**

| Topic | Actual configuration |
|-------|----------------------|
| Docker services | `postgres`, `redis`, `backend`, `frontend` (not `api`/`web`/`db`) |
| Host Postgres port | **5433** (`POSTGRES_HOST_PORT`) |
| Host Redis port | **6380** (`REDIS_HOST_PORT`) |
| Admin UI | Same Next.js app — **http://localhost:3000/admin-dashboard** (no separate admin app) |
| Celery | Optional — `--profile workers` |
| Makefile | **Stale** — use `docker compose` commands below, not `make migrate` |
| Accounting / AR / AP | **API-only** (no admin UI pages yet) — verify via API |
| Dev payments | `DEMO_AUTO_COMPLETE_PAYMENTS=True` in `config/settings/dev.py` (Stripe optional) |

---

## 0. Prerequisites

- Docker Desktop 24+ with Compose v2
- Git
- (Optional hybrid dev) Node.js 20+, Python 3.12+

---

## 1. Fresh clone → environment files

```powershell
cd E:\
git clone <repository-url> a2z-tools
cd a2z-tools

# Root env (used by Docker Compose)
copy .env.example .env

# Frontend env (Next.js)
copy frontend\.env.local.example frontend\.env.local

# Backend env (only needed for hybrid non-Docker backend)
copy backend\.env.example backend\.env
```

Verify these values in **`.env`** (defaults from `.env.example`):

```env
POSTGRES_HOST_PORT=5433
REDIS_HOST_PORT=6380
BACKEND_HOST_PORT=8000
FRONTEND_HOST_PORT=3000
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000/api/v1
NEXT_PUBLIC_SITE_URL=http://localhost:3000
DJANGO_SETTINGS_MODULE=config.settings.dev
DJANGO_DEBUG=True
```

For **hybrid mode** (backend on host), set in `backend/.env`:

```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5433
REDIS_URL=redis://localhost:6380/0
CSRF_TRUSTED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

> **Windows note:** Use `127.0.0.1` for the API URL, not `localhost`. Windows resolves `localhost` to IPv6 (`::1`) while Django `runserver` binds IPv4 (`127.0.0.1`), which breaks browser requests from the Next.js app.

---

## 2. Start services (exact order)

### Option A — Full Docker stack (recommended)

```powershell
# Build images
docker compose build

# Start Postgres, Redis, backend, frontend
docker compose up -d

# Optional: Celery worker + beat
docker compose --profile workers up -d
```

Wait until healthy:

```powershell
docker compose ps
```

Expected: `postgres`, `redis`, `backend`, `frontend` → **healthy**.  
With workers: `a2z-celery`, `a2z-celery-beat` → **running**.

**Migrations** run automatically on backend start (`RUN_MIGRATIONS=true` in entrypoint).

### Option B — Infrastructure only + native apps

```powershell
docker compose up -d postgres redis pgadmin
```

Then start backend and frontend manually (see section 8).

---

## 3. Environment validation

### Docker / Django

```powershell
docker compose exec backend python manage.py check
docker compose exec backend python manage.py showmigrations --plan | Select-String "\[ \]"
```

No `[ ]` (unapplied) migrations should remain after backend is healthy.

### Production-style env (optional)

```powershell
# Bash/WSL only — validates .env.production.example pattern
bash infrastructure/scripts/validate-production-env.sh .env
```

### Frontend

```powershell
cd frontend
npm run typecheck
npm run lint
```

---

## 4. Migrations (manual, if needed)

Auto-applied on `backend` container start. To run manually:

```powershell
docker compose exec backend python manage.py migrate
```

Create new migrations (development only):

```powershell
docker compose exec backend python manage.py makemigrations
docker compose exec backend python manage.py migrate
```

---

## 5. Seed commands (required order)

Run **after** migrations complete.

```powershell
# 1. ERP foundation — company, workflows, notification templates, sequences
docker compose exec backend python manage.py seed_erp_foundation

# 2. Accounting — COA, fiscal year, GL event mappings (requires default company)
docker compose exec backend python manage.py seed_accounting_foundation

# 3. Demo catalog, users, orders (recommended for local validation)
docker compose exec backend python manage.py seed_demo
```

`seed_demo` also calls `RoleService.ensure_system_roles()` and creates demo users.

**Skip orders** (faster seed):

```powershell
docker compose exec backend python manage.py seed_demo --skip-orders
```

---

## 6. Default admin / demo accounts

### Demo manager (from `seed_demo`)

| Field | Value |
|-------|-------|
| Email | `admin@demo.a2ztools.com` |
| Password | `Demo@2026!` |
| Role | `manager` (admin portal access) |

Other demo accounts (same password): `customer@demo.a2ztools.com`, `trade@demo.a2ztools.com`, `business@demo.a2ztools.com`.

### Create Django super-admin (full RBAC)

```powershell
docker compose exec backend python manage.py shell -c "from apps.accounts.services import RoleService; RoleService.ensure_system_roles()"

docker compose exec backend python manage.py createsuperuser
```

Superusers automatically receive the `super-admin` RBAC role on save.

---

## 7. Health check URLs

| Service | URL | Expected |
|---------|-----|----------|
| API liveness | http://127.0.0.1:8000/api/v1/health/ | `{"status":"ok"}` |
| API readiness | http://127.0.0.1:8000/api/v1/ready/ | `{"status":"ok","checks":{...}}` |
| Frontend | http://localhost:3000/api/health | `{"status":"ok"}` |
| OpenAPI schema | http://127.0.0.1:8000/api/schema/ | Staff auth required |
| Django admin | http://127.0.0.1:8000/admin/ | Login page |
| pgAdmin | http://localhost:5050 | `admin@a2ztools.local` / `changeme` |

**PowerShell:**

```powershell
curl.exe -fsS http://127.0.0.1:8000/api/v1/health/
curl.exe -fsS http://127.0.0.1:8000/api/v1/ready/
curl.exe -fsS http://localhost:3000/api/health
```

---

## 8. Login URLs

| Portal | URL |
|--------|-----|
| Storefront login | http://localhost:3000/login |
| Register | http://localhost:3000/register |
| Admin dashboard | http://localhost:3000/admin-dashboard |
| Account area | http://localhost:3000/account |
| Supplier portal | http://localhost:3000/supplier-portal |
| Warehouse mobile | http://localhost:3000/warehouse-mobile |

**API login** (JWT):

```powershell
curl.exe -X POST http://127.0.0.1:8000/api/v1/auth/login/ `
  -H "Content-Type: application/json" `
  -d "{\"email\":\"admin@demo.a2ztools.com\",\"password\":\"Demo@2026!\"}"
```

Also available: `POST /api/v1/auth/register/`, `POST /api/auth/login/` (legacy path in `config/urls.py`).

---

## 9. Connection & service verification

### PostgreSQL

```powershell
docker exec a2z-postgres pg_isready -U a2z -d a2z_tools
docker compose exec backend python manage.py dbshell -c "SELECT 1;"
```

From host (port 5433):

```powershell
# If psql installed locally
psql -h localhost -p 5433 -U a2z -d a2z_tools -c "SELECT version();"
```

### Redis

```powershell
docker exec a2z-redis redis-cli ping
```

Expected: `PONG`

Readiness endpoint also checks Redis via Django cache.

### Celery

```powershell
docker compose --profile workers ps
docker compose logs celery --tail=50
docker compose exec celery celery -A config inspect ping
docker compose exec celery-beat celery -A config inspect scheduled
```

### Stripe

Dev mode auto-completes payments without Stripe keys (`DEMO_AUTO_COMPLETE_PAYMENTS=True`).

Verify configuration:

```powershell
docker compose exec backend python manage.py shell -c "from django.conf import settings; print('STRIPE_SECRET_KEY set:', bool(settings.STRIPE_SECRET_KEY)); print('DEMO_AUTO_COMPLETE:', settings.DEMO_AUTO_COMPLETE_PAYMENTS)"
```

Optional: set in `.env`:

```env
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
NEXT_PUBLIC_STRIPE_PUBLIC_KEY=pk_test_...
```

### Sentry

Not enabled in dev unless you set `SENTRY_DSN`. Production wiring: `config/sentry.py` + `config/settings/prod.py`.

```powershell
docker compose exec backend python manage.py shell -c "import os; print('SENTRY_DSN:', os.environ.get('SENTRY_DSN','(not set)'))"
```

---

## 10. Hybrid native startup (optional)

If you prefer running Django/Next.js on the host:

```powershell
# 1. Start infra only
docker compose up -d postgres redis

# 2. Backend
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements\dev.txt
$env:DJANGO_SETTINGS_MODULE="config.settings.dev"
$env:POSTGRES_HOST="localhost"
$env:POSTGRES_PORT="5433"
$env:REDIS_URL="redis://localhost:6380/0"
python manage.py migrate
python manage.py seed_erp_foundation
python manage.py seed_accounting_foundation
python manage.py seed_demo
python manage.py runserver 0.0.0.0:8000

# 3. Frontend (new terminal)
cd frontend
npm install
npm run dev

# 4. Celery (new terminals, from backend/)
celery -A config worker -l info
celery -A config beat -l info
```

---

## 11. Smoke test checklist

### Storefront (browser — http://localhost:3000)

- [ ] **Homepage** — `/`
- [ ] **Products** — `/products`
- [ ] **Product detail** — `/products/cisco-catalyst-9200` (after `seed_demo`)
- [ ] **Category** — `/networking` (route: `(categories)/[slug]`)
- [ ] **Cart** — `/cart`
- [ ] **Checkout** — `/checkout` (login as `customer@demo.a2ztools.com`)
- [ ] **Orders** — `/account/orders` (after checkout)

### Admin (login as `admin@demo.a2ztools.com`)

- [ ] **Dashboard** — `/admin-dashboard`
- [ ] **CRM** — `/admin-dashboard/crm`
- [ ] **Quotes** — `/admin-dashboard/quotes`
- [ ] **Procurement** — `/admin-dashboard/procurement`
- [ ] **WMS** — `/admin-dashboard/wms`
- [ ] **HRM** — `/admin-dashboard/hrm`
- [ ] **Payroll** — `/admin-dashboard/payroll`
- [ ] **Executive BI** — `/admin-dashboard/executive-bi`
- [ ] **Reports** — `/admin-dashboard/reports`
- [ ] **Analytics** — `/admin-dashboard/analytics`

### Supplier portal

Requires a user with `supplier-user` role (create manually or via procurement tests).  
- [ ] **Portal home** — `/supplier-portal`

### Accounting / AR / AP (API — no admin UI yet)

Login first, copy `access` token from login response, then:

```powershell
$TOKEN = "<access-token-from-login>"

curl.exe -fsS http://127.0.0.1:8000/api/v1/accounting/admin/reports/trial-balance/ `
  -H "Authorization: Bearer $TOKEN"

curl.exe -fsS http://127.0.0.1:8000/api/v1/receivables/admin/summary/ `
  -H "Authorization: Bearer $TOKEN"

curl.exe -fsS http://127.0.0.1:8000/api/v1/payables/admin/summary/ `
  -H "Authorization: Bearer $TOKEN"
```

Finance manager role or super-admin required for some endpoints.

---

## 12. Automated test commands

```powershell
# Backend (SQLite — fast)
cd backend
$env:USE_SQLITE_FOR_TESTS="1"
$env:DJANGO_SETTINGS_MODULE="config.settings.test"
python manage.py test apps.analytics.tests.test_bi_api --verbosity=2

# Full backend suite (from repo root, Git Bash/WSL)
bash scripts/run-tests.sh smoke

# Frontend
cd frontend
npm run typecheck
npm run lint
npm run build
```

---

## 13. Complete command sequence (copy-paste)

From a **fresh clone** on Windows (PowerShell, repo root):

```powershell
copy .env.example .env
copy frontend\.env.local.example frontend\.env.local
docker compose build
docker compose up -d
docker compose --profile workers up -d

# Wait ~60s for backend health, then seed
docker compose exec backend python manage.py seed_erp_foundation
docker compose exec backend python manage.py seed_accounting_foundation
docker compose exec backend python manage.py seed_demo

# Verify
curl.exe -fsS http://127.0.0.1:8000/api/v1/ready/
curl.exe -fsS http://localhost:3000/api/health
docker exec a2z-redis redis-cli ping
docker compose exec celery celery -A config inspect ping

# Open in browser
start http://localhost:3000
start http://localhost:3000/login
start http://localhost:3000/admin-dashboard
```

**Demo login:** `admin@demo.a2ztools.com` / `Demo@2026!`

---

## 14. Troubleshooting

| Symptom | Fix |
|---------|-----|
| Backend not healthy | `docker compose logs backend --tail=100` |
| Migration errors | `docker compose exec backend python manage.py migrate` |
| Frontend can't reach API | Confirm `NEXT_PUBLIC_API_URL=http://127.0.0.1:8000/api/v1` |
| Redis readiness 503 | Check `a2z-redis`; set `REDIS_URL=redis://redis:6379/0` in Docker |
| Celery not running | `docker compose --profile workers up -d` |
| Admin 403 | Run `seed_demo` or assign RBAC role via Django admin |
| `make migrate` fails | Makefile uses old service names — use `docker compose exec backend` |

---

## 15. Service reference

| Container | Host URL / Port |
|-----------|-----------------|
| `a2z-postgres` | `localhost:5433` |
| `a2z-redis` | `localhost:6380` |
| `a2z-backend` | http://127.0.0.1:8000 |
| `a2z-frontend` | http://localhost:3000 |
| `a2z-celery` | (internal) |
| `a2z-celery-beat` | (internal) |
| `a2z-pgadmin` | http://localhost:5050 |

Stop everything:

```powershell
docker compose --profile workers down
```
