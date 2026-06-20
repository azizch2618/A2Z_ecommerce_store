# A2Z Tools — Production Deployment Runbook

Operational commands and checklists. For architecture decisions, see [DEPLOYMENT_ARCHITECTURE.md](DEPLOYMENT_ARCHITECTURE.md).

---

## Pre-deploy checklist

- [ ] Secrets rotated and stored in secret manager (not `.env` on disk in prod)
- [ ] `DJANGO_DEBUG=False`, `DJANGO_ALLOWED_HOSTS=api.a2ztools.com`
- [ ] `NEXT_PUBLIC_API_URL=https://api.a2ztools.com/api/v1`
- [ ] Database backup completed within last 24 hours
- [ ] Staging smoke tests passed
- [ ] Migration plan reviewed (expand/contract for zero-downtime if needed)

---

## Deploy (Docker Compose)

```bash
# TLS for local prod testing (use Cloudflare Origin cert on real hosts)
# See infrastructure/nginx/ssl/README.md

# On production host
git pull origin main
cp .env.production .env   # or inject via secret manager

docker compose -f docker-compose.yml -f docker-compose.prod.yml build
docker compose -f docker-compose.yml -f docker-compose.prod.yml \
  --profile proxy --profile workers up -d

# Verify
docker compose ps
curl -fsS https://api.a2ztools.com/api/v1/health/
curl -fsS https://www.a2ztools.com/
curl -fsS https://dashboard.a2ztools.com/admin-dashboard
```

---

## Rollback

```bash
export IMAGE_TAG=<previous-sha>
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --no-build
# If migration was destructive, restore DB from backup first
```

---

## Backup (manual)

```bash
./infrastructure/scripts/backup-postgres.sh
```

---

## Smoke tests (post-deploy)

| Check | Command / URL |
|-------|----------------|
| API health | `GET https://api.a2ztools.com/api/v1/health/` |
| API ready | `GET https://api.a2ztools.com/api/v1/ready/` |
| Storefront | `GET https://www.a2ztools.com/` |
| Admin | `GET https://dashboard.a2ztools.com/admin-dashboard` |
| Auth | Login via www; verify JWT on API |
| Orders | Place test order in staging before prod promotion |

---

## Incident contacts

| Role | Responsibility |
|------|----------------|
| On-call engineer | First response, rollback |
| DBA / backend lead | Database restore |
| Frontend lead | CDN / Next.js issues |

---

## Related

- [PRODUCTION_DEPLOYMENT_PLAN.md](PRODUCTION_DEPLOYMENT_PLAN.md) — go-live checklist and Cloudflare/CI/CD
- [DEPLOYMENT_ARCHITECTURE.md](DEPLOYMENT_ARCHITECTURE.md) — full architecture
- [BACKEND_ARCHITECTURE.md](BACKEND_ARCHITECTURE.md) — API and Docker
- `infrastructure/nginx/production.conf.example` — multi-domain Nginx
