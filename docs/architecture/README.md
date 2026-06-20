# Architecture documentation

| Document | Status | Description |
|----------|--------|-------------|
| [POSTGRESQL_DATABASE_ARCHITECTURE.md](POSTGRESQL_DATABASE_ARCHITECTURE.md) | **Complete** | 21 core tables — ER diagrams, PK/FK, ERP expansion |
| [BACKEND_ARCHITECTURE.md](BACKEND_ARCHITECTURE.md) | **Complete** | Django ERP backend — apps, DB, API, Docker, auth, scalability |
| [../DATABASE_PLAN.md](../DATABASE_PLAN.md) | Complete | Full column-level table definitions (~50 tables) |
| [api-conventions.md](api-conventions.md) | Planned | Request/response patterns |
| [auth-flow.md](auth-flow.md) | Planned | JWT + trade account flows |
| [FRONTEND_API_INTEGRATION.md](FRONTEND_API_INTEGRATION.md) | **Complete** | Mock audit, integration roadmap, API client, React Query strategy |
| [RBAC.md](RBAC.md) | **Complete** | Enterprise roles, permissions, DRF + frontend guards |
| [INVENTORY_MANAGEMENT.md](INVENTORY_MANAGEMENT.md) | **Complete** | Production WMS — ledger, valuation, notifications (AUD/GST) |
| [DEPLOYMENT_ARCHITECTURE.md](DEPLOYMENT_ARCHITECTURE.md) | **Complete** | Production topology, Docker, domains, security, scaling, backup, DR |
| [PRODUCTION_DEPLOYMENT_PLAN.md](PRODUCTION_DEPLOYMENT_PLAN.md) | **Complete** | Go-live execution plan — Cloudflare, CI/CD, monitoring, DR checklist |
| [ERP_FOUNDATION_ROADMAP.md](ERP_FOUNDATION_ROADMAP.md) | **Complete** | ERP foundation — shared entities, abstractions, phased roadmap (no modules yet) |
| [STRIPE_PAYMENTS.md](STRIPE_PAYMENTS.md) | **Complete** | Stripe Payment Intents, webhooks, inventory-safe order flow |
| [PRODUCTION_SECURITY.md](PRODUCTION_SECURITY.md) | **Complete** | HttpOnly JWT cookies, SECRET_KEY enforcement, trade credit, cart ownership |
| [deployment.md](deployment.md) | **Complete** | Operational deploy runbook |
