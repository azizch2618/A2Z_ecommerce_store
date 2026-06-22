# Executive BI & Analytics Module

Cross-module business intelligence orchestration over Ecommerce, CRM, Procurement, WMS, Accounting, HRM, and Payroll — executive KPIs, domain analytics, configurable KPI engine, scheduled reports, and multi-format export.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Executive BI Layer                          │
│              apps/analytics (orchestration only)                │
├─────────────┬─────────────┬─────────────┬─────────────┬─────────┤
│   Orders    │    CRM      │ Procurement │    WMS      │ Finance │
│   Quotes    │             │             │  Inventory  │ AR / AP │
├─────────────┴─────────────┴─────────────┴─────────────┴─────────┤
│              HRM + Payroll domain dashboard services            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    KPI Engine (KpiDefinition)
                    Scheduled Reports + Celery
                    Export (CSV / Excel / PDF)
```

| Layer | App | API Base |
|-------|-----|----------|
| Executive BI | `apps/analytics` | `/api/v1/analytics/admin/bi/` |
| Commerce analytics (legacy) | `apps/analytics` | `/api/v1/analytics/admin/dashboard/` |

## Data Aggregation Strategy

BI does **not** duplicate transactional data. Each domain module exposes dashboard/report services; the analytics app aggregates them:

| Domain | Source service | Cached |
|--------|----------------|--------|
| Executive KPIs | `ExecutiveBiService` | 60s (`cache_get_or_set`) |
| Sales | `SalesAnalyticsService` | Live query |
| Inventory | `InventoryAnalyticsService` + `InventoryValuationService` | Live query |
| Procurement | `ProcurementDashboardService`, `SupplierPerformanceService` | Live query |
| Finance | `ReportingService`, `ReceivablesReportingService`, `PayablesReportingService` | Live query |
| HR | `HrmDashboardService`, `PayrollDashboardService` | Live query |

Money values are returned in **cents** (AUD). Executive snapshot keys use camelCase for API consistency.

## Executive Dashboard KPIs

| KPI | Metric key | Source |
|-----|------------|--------|
| Revenue (30d) | `revenueCents` | Paid orders |
| Gross margin | `grossMarginCents` / `grossMarginPct` | Revenue − COGS |
| Inventory value | `inventoryValueCents` | Inventory valuation |
| Open orders | `openOrders` | Non-terminal order statuses |
| Open quotes | `openQuotes` | Draft through accepted quotes |
| Cash position | `cashPositionCents` | GL bank account (1100) trial balance |
| Payroll cost YTD | `payrollCostYtdCents` | Posted payroll runs |

## Domain Analytics

### Sales
- Revenue by month, customer, product
- Quote conversion (draft → converted)

### Inventory
- Inventory turns (90-day COGS / value, annualized)
- Dead stock (no movement in 90 days)
- Fast moving products (30-day units sold)
- Warehouse bin utilization

### Procurement
- Spend by supplier and category
- Supplier performance KPIs

### Finance
- AR/AP aging buckets
- Cash flow (cash, AR, AP, net working capital)
- Profitability (revenue vs expense from trial balance)

### HR
- Headcount, leave trends
- Payroll cost by department (YTD)

## KPI Engine

`KpiDefinition` stores configurable KPI metadata:

- **code** — stable identifier (e.g. `revenue_30d`)
- **metric_key** — maps to evaluated metric from domain services
- **target_value** — optional threshold for on-target flag
- **category** — executive, sales, inventory, procurement, finance, hr

Default KPIs are seeded on first evaluate via `KpiEngineService.ensure_defaults()`.

## Scheduled Reports

`ScheduledReport` model with frequency (daily / weekly / monthly), export format, and recipient emails.

Delivery:
1. Celery task `analytics.deliver_scheduled_reports` runs due schedules
2. Report generated via unified `export_report()`
3. Email sent + in-app notification (`report_delivered` template)

## Export

| Format | Library | Encoding |
|--------|---------|----------|
| CSV | stdlib | UTF-8 text |
| Excel | openpyxl | Base64 |
| PDF | ReportLab | Base64 |

Uses existing `REPORT_CATALOG` from commerce reports; BI export endpoint supports all three formats.

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/bi/executive/` | Executive KPI snapshot |
| GET | `/bi/sales/` | Sales analytics |
| GET | `/bi/inventory/` | Inventory analytics |
| GET | `/bi/procurement/` | Procurement analytics |
| GET | `/bi/finance/` | Finance analytics |
| GET | `/bi/hr/` | HR analytics |
| GET | `/bi/snapshot/` | Full rollup (all sections + KPIs) |
| GET | `/bi/kpis/` | KPI definitions |
| GET | `/bi/kpis/evaluate/` | Evaluate all active KPIs |
| PATCH | `/bi/kpis/{id}/` | Update target / active flag |
| POST | `/bi/reports/export/` | Export report (csv/excel/pdf) |
| GET/POST | `/bi/schedules/` | List / create scheduled reports |

## RBAC

| Permission | Description |
|------------|-------------|
| `analytics.view` | View BI dashboards and KPIs |
| `analytics.manage` | Configure KPIs and scheduled reports |
| `reports.view` | View report catalog |
| `reports.export` | Export reports |

| Role | BI access |
|------|-----------|
| **Executive** | View + export (read-only cross-module BI) |
| **Manager** | View analytics + reports + export |
| **Department Manager** | View analytics + HR scope |
| **Finance Manager** | View analytics + finance reports |
| **Admin / Super Admin** | Full access including `analytics.manage` |

## Frontend

- **Executive BI**: `/admin-dashboard/executive-bi`
- **Commerce analytics** (legacy charts): `/admin-dashboard/analytics`
- Hooks: `useBiSnapshot`, `useExecutiveSnapshot`, domain-specific hooks in `lib/api/admin/bi-hooks.ts`

## Models

| Model | Table | Purpose |
|-------|-------|---------|
| `AnalyticsEvent` | `analytics_events` | Event tracking (storefront) |
| `SearchLog` | `search_logs` | Search analytics |
| `KpiDefinition` | `analytics_kpi_definitions` | Configurable KPI catalog |
| `ScheduledReport` | `analytics_scheduled_reports` | Email delivery schedules |

## Celery

```python
# config/celery.py beat schedule (optional)
"deliver-scheduled-reports": {
    "task": "analytics.deliver_scheduled_reports",
    "schedule": crontab(minute=0),  # hourly
}
```

## Related modules

- [Accounting](./ACCOUNTING.md)
- [HRM](./HRM.md)
- [Payroll](./PAYROLL.md)
- [AR/AP](./AR_AP.md)
