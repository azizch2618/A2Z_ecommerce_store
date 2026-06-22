# Go-Live Checklist — A2Z Tools ERP

Use with [PRODUCTION_READINESS.md](./PRODUCTION_READINESS.md) and [deployment.md](./deployment.md).

## Pre-flight (T-7 days)

- [ ] Staging environment mirrors production Compose profiles (`proxy`, `workers`)
- [ ] All CI workflows green on release branch
- [ ] Security workflow: pip-audit, npm audit, Gitleaks pass
- [ ] Load tests on staging (k6 scripts) meet thresholds
- [ ] Restore drill: `verify-backup-restore.sh --restore-test`
- [ ] RBAC review: executive, manager, finance, admin roles assigned

## Infrastructure (T-1 day)

- [ ] Cloudflare DNS + WAF for `www`, `dashboard`, `api`
- [ ] Origin `.env` complete — `./infrastructure/scripts/validate-production-env.sh .env`
- [ ] TLS certificates in `infrastructure/nginx/ssl/`
- [ ] Backup cron installed: `/etc/cron.d/a2z-backups`
- [ ] Sentry project created; test error received
- [ ] Uptime monitors on `/api/v1/health/` and storefront

## Deploy day

- [ ] Announce maintenance window (if needed)
- [ ] GitHub Actions: Deploy workflow → **production** → target tag/SHA
- [ ] Pre-deploy backup completes (automatic in `deploy.sh`)
- [ ] Smoke tests pass (health, ready, www, dashboard)
- [ ] Seed foundation commands if fresh DB
- [ ] Create super-admin; disable demo mode
- [ ] Stripe live webhook + test transaction
- [ ] Send test transactional email

## Post go-live (T+24h)

- [ ] Monitor Sentry for new error spikes
- [ ] Review backup log `/var/log/a2z-backup.log`
- [ ] Verify Celery scheduled tasks (reports, payroll)
- [ ] Document deployed SHA and image tags
- [ ] Schedule first weekly restore verification

## Rollback triggers

- `/api/v1/ready/` fails for more than 5 minutes after deploy
- Error rate in Sentry exceeds baseline by 10x
- Payment or checkout completely broken
- Data corruption detected

## Rollback steps

1. Stop traffic via Cloudflare maintenance mode (optional)
2. Set `BACKEND_IMAGE` / `FRONTEND_IMAGE` to previous GHCR tag in `.env`
3. `./infrastructure/scripts/deploy.sh PREVIOUS_SHA`
4. If DB migration issue: `./infrastructure/scripts/restore-postgres.sh s3://.../pre-deploy.dump`
5. Smoke test health endpoints
6. Disable maintenance mode; post-mortem within 48h
