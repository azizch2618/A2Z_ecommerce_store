# Warehouse Management System (WMS)

Location-aware warehouse operations — bin hierarchy, transfers, pick lists, putaway, cycle counts, and approved adjustments — built on the ERP foundation and Inventory module.

## Architecture

```
Warehouse
   └── Zone → Aisle → Bin
              └── BinInventory (SKU × bin qty)

Goods Receipt (GRN)
        │
        ▼
   Putaway Task ──► Bin assignment (unlocated → bin)

Sales Order
        │
        ▼
   Pick List ──► Bin pick ──► stock_out on complete

Cycle Count ──► variance ──► InventoryService.stock_adjustment
Adjustment Request ──► WorkflowEngine ──► apply
```

| Layer | Location |
|-------|----------|
| Models | `apps/wms/models.py` |
| Business logic | `apps/wms/services.py` |
| Admin API | `/api/v1/wms/admin/` |
| Inventory integration | `InventoryService`, GRN putaway hook |

## Bin locations

Hierarchy: **Warehouse → Zone → Aisle → Bin**

- `BinInventory` tracks quantity per bin
- Warehouse-level `InventoryLevel` remains authoritative for orders/catalog
- Unlocated stock = warehouse on-hand minus sum of bin quantities

## Stock transfers

| Type | Behaviour |
|------|-----------|
| `warehouse` | Uses `InventoryService.stock_transfer` (existing ledger) |
| `bin` | Moves qty between bins within same warehouse |

Optional approval via `WorkflowCode.WMS_TRANSFER_APPROVAL`.

Statuses: `draft` → `submitted` → `approved` → `completed`

## Pick lists

Created from sales orders. Statuses:

`draft` → `assigned` → `picking` → `picked` → `completed`

On complete: `InventoryService.stock_out` with `reference_type="pick_list"`.

## Putaway

Auto-created when a GRN is posted (`GoodsReceiptService.receive_po` → `PutawayService.create_from_grn`).

Operator assigns received qty from unlocated stock to target bins.

## Cycle counting

Structured counts with expected vs counted qty and variance. On complete, variances post as inventory adjustments and update `last_counted_at`.

## Inventory adjustments

Approved workflow (`WMS_ADJUSTMENT_APPROVAL`):

`draft` → `submitted` → `approved` / `rejected` → `applied`

## Dashboard KPIs

- Inventory value (ex GST)
- Open transfers
- Open picks
- Cycle count accuracy %

Admin UI: `/admin-dashboard/wms`  
Mobile floor UI: `/warehouse-mobile`

## Domain events

| Event | When |
|-------|------|
| `inventory.transferred` | Stock transfer completed |
| `inventory.adjusted` | Adjustment applied |
| `pick.completed` | Pick list completed |
| `cycle_count.completed` | Cycle count finalized |

## RBAC

| Role | Access |
|------|--------|
| Warehouse Operator | `wms.view`, `wms.execute` — picks, putaway, counts |
| Warehouse Manager | + `wms.manage`, `wms.approve`, full inventory |
| Admin | Full access |

## API quick reference

```
GET  /api/v1/wms/admin/dashboard/
GET  /api/v1/wms/admin/bins/
GET  /api/v1/wms/admin/bin-inventory/
POST /api/v1/wms/admin/transfers/
POST /api/v1/wms/admin/picks/
POST /api/v1/wms/admin/picks/{id}/start|record|complete/
GET  /api/v1/wms/admin/putaway/
POST /api/v1/wms/admin/putaway/{id}/assign-bin/
POST /api/v1/wms/admin/cycle-counts/
POST /api/v1/wms/admin/adjustments/{id}/submit|approve/
```

## Tests

```bash
python manage.py test apps.wms.tests.test_wms_api
```
