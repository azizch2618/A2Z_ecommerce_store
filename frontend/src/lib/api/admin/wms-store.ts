/**
 * In-memory WMS state for admin demo — updated by mock mutations.
 */

import {
  mockInventory,
  mockPurchaseOrders as initialPurchaseOrders,
  mockStockMovements as initialMovements,
} from "@/config/admin/mock-data";
import type {
  AdminPurchaseOrder,
  CreatePurchaseOrderPayload,
  InventoryRow,
  LowStockAlert,
  StockAdjustmentPayload,
  StockInPayload,
  StockMovementRecord,
  StockOutPayload,
  StockTransferPayload,
} from "./types";

let inventoryRows: InventoryRow[] = structuredClone(mockInventory);
let purchaseOrders: AdminPurchaseOrder[] = structuredClone(initialPurchaseOrders);
let stockMovements: StockMovementRecord[] = structuredClone(initialMovements);
let idCounter = 100;

function nextId() {
  idCounter += 1;
  return String(idCounter);
}

function nowIso() {
  return new Date().toISOString();
}

function movementNumber(prefix: string) {
  const d = new Date().toISOString().slice(0, 10).replace(/-/g, "");
  return `${prefix}-${d}-${idCounter}`;
}

function findRow(sku: string, warehouse: string) {
  return inventoryRows.find(
    (r) => r.sku.toLowerCase() === sku.toLowerCase() && r.warehouse === warehouse
  );
}

function upsertRow(
  sku: string,
  warehouse: string,
  productName: string,
  delta: number,
  costCents?: number
) {
  const row = findRow(sku, warehouse);
  if (row) {
    row.quantity = Math.max(0, row.quantity + delta);
    if (costCents !== undefined && delta > 0) {
      row.averageCostCents = costCents;
    }
    return row;
  }
  const created: InventoryRow = {
    id: nextId(),
    sku,
    productName,
    warehouse,
    quantity: Math.max(0, delta),
    reorderLevel: 10,
    averageCostCents: costCents ?? 0,
  };
  inventoryRows.push(created);
  return created;
}

function addMovement(
  partial: Omit<StockMovementRecord, "id" | "movementNumber" | "createdAt">
) {
  const record: StockMovementRecord = {
    ...partial,
    id: nextId(),
    movementNumber: movementNumber(
      partial.type === "transfer_in"
        ? "XFER-IN"
        : partial.type === "transfer_out"
          ? "XFER-OUT"
          : partial.type === "receipt"
            ? "IN"
            : partial.type === "adjustment"
              ? "ADJ"
              : "OUT"
    ),
    createdAt: nowIso(),
  };
  stockMovements.unshift(record);
  return record;
}

export function getInventoryRows(): InventoryRow[] {
  return inventoryRows;
}

export function getPurchaseOrders(): AdminPurchaseOrder[] {
  return purchaseOrders;
}

export function getStockMovements(): StockMovementRecord[] {
  return stockMovements;
}

export function getLowStockAlerts(): LowStockAlert[] {
  return inventoryRows
    .filter((r) => r.reorderLevel > 0 && r.quantity <= r.reorderLevel)
    .map((r) => ({
      id: r.id,
      sku: r.sku,
      productName: r.productName,
      warehouseCode: r.warehouse,
      quantityOnHand: r.quantity,
      reorderPoint: r.reorderLevel,
      reorderQuantity: r.reorderLevel * 2,
      shortfall: Math.max(r.reorderLevel - r.quantity, 0),
      alertLevel: r.quantity <= 0 ? "out_of_stock" as const : "low_stock" as const,
    }))
    .sort((a, b) => a.quantityOnHand - b.quantityOnHand);
}

export function mockStockIn(payload: StockInPayload): StockMovementRecord {
  const row = upsertRow(
    payload.sku,
    payload.warehouseCode,
    payload.sku,
    payload.quantity,
    payload.costPriceCents
  );
  return addMovement({
    sku: payload.sku,
    productName: row.productName,
    warehouseCode: payload.warehouseCode,
    type: "receipt",
    quantity: payload.quantity,
    quantityAfter: row.quantity,
    notes: payload.notes ?? "Stock in",
  });
}

export function mockStockOut(payload: StockOutPayload): StockMovementRecord {
  const row = findRow(payload.sku, payload.warehouseCode);
  if (!row || row.quantity < payload.quantity) {
    throw new Error("Insufficient stock");
  }
  row.quantity -= payload.quantity;
  return addMovement({
    sku: payload.sku,
    productName: row.productName,
    warehouseCode: payload.warehouseCode,
    type: "sale",
    quantity: payload.quantity,
    quantityAfter: row.quantity,
    notes: payload.notes ?? "Stock out",
  });
}

export function mockStockAdjustment(payload: StockAdjustmentPayload): StockMovementRecord {
  const row = findRow(payload.sku, payload.warehouseCode);
  const productName = row?.productName ?? payload.sku;
  if (payload.quantityChange < 0) {
    const existing = row;
    if (!existing || existing.quantity < Math.abs(payload.quantityChange)) {
      throw new Error("Insufficient stock for adjustment");
    }
    existing.quantity += payload.quantityChange;
    return addMovement({
      sku: payload.sku,
      productName,
      warehouseCode: payload.warehouseCode,
      type: "adjustment",
      quantity: Math.abs(payload.quantityChange),
      quantityAfter: existing.quantity,
      notes: payload.notes ?? "Negative adjustment",
    });
  }
  const updated = upsertRow(
    payload.sku,
    payload.warehouseCode,
    productName,
    payload.quantityChange,
    payload.costPriceCents
  );
  return addMovement({
    sku: payload.sku,
    productName: updated.productName,
    warehouseCode: payload.warehouseCode,
    type: "adjustment",
    quantity: payload.quantityChange,
    quantityAfter: updated.quantity,
    notes: payload.notes ?? "Positive adjustment",
  });
}

export function mockStockTransfer(payload: StockTransferPayload): StockMovementRecord[] {
  const fromRow = findRow(payload.sku, payload.fromWarehouseCode);
  if (!fromRow || fromRow.quantity < payload.quantity) {
    throw new Error("Insufficient stock at source warehouse");
  }
  fromRow.quantity -= payload.quantity;
  const toRow = upsertRow(
    payload.sku,
    payload.toWarehouseCode,
    fromRow.productName,
    payload.quantity,
    fromRow.averageCostCents
  );
  const outMv = addMovement({
    sku: payload.sku,
    productName: fromRow.productName,
    warehouseCode: payload.fromWarehouseCode,
    type: "transfer_out",
    quantity: payload.quantity,
    quantityAfter: fromRow.quantity,
    notes: payload.notes ?? `Transfer to ${payload.toWarehouseCode}`,
  });
  addMovement({
    sku: payload.sku,
    productName: toRow.productName,
    warehouseCode: payload.toWarehouseCode,
    type: "transfer_in",
    quantity: payload.quantity,
    quantityAfter: toRow.quantity,
    notes: payload.notes ?? `Transfer from ${payload.fromWarehouseCode}`,
  });
  return [outMv];
}

export function mockCreatePurchaseOrder(
  payload: CreatePurchaseOrderPayload,
  supplierName: string
): AdminPurchaseOrder {
  const po: AdminPurchaseOrder = {
    id: nextId(),
    poNumber: `PO-${new Date().toISOString().slice(0, 10).replace(/-/g, "")}-${idCounter}`,
    supplierName,
    warehouseCode: payload.warehouseCode,
    status: "draft",
    totalExGstCents: payload.lines.reduce(
      (sum, l) => sum + l.quantity * l.unitCostCents,
      0
    ),
    expectedAt: null,
    lines: payload.lines.map((l) => ({
      id: nextId(),
      sku: l.sku,
      productName: l.sku,
      quantityOrdered: l.quantity,
      quantityReceived: 0,
      unitCostCents: l.unitCostCents,
    })),
    createdAt: nowIso(),
  };
  purchaseOrders.unshift(po);
  return po;
}

export function mockReceivePurchaseOrder(
  poId: string,
  receipts: { lineId: string; quantity: number }[]
): AdminPurchaseOrder {
  const po = purchaseOrders.find((p) => p.id === poId);
  if (!po) throw new Error("Purchase order not found");

  for (const receipt of receipts) {
    const line = po.lines.find((l) => l.id === receipt.lineId);
    if (!line) continue;
    const remaining = line.quantityOrdered - line.quantityReceived;
    const qty = Math.min(receipt.quantity, remaining);
    line.quantityReceived += qty;
    mockStockIn({
      sku: line.sku,
      warehouseCode: po.warehouseCode,
      quantity: qty,
      costPriceCents: line.unitCostCents,
      notes: `PO receipt ${po.poNumber}`,
    });
  }

  const allReceived = po.lines.every((l) => l.quantityReceived >= l.quantityOrdered);
  const anyReceived = po.lines.some((l) => l.quantityReceived > 0);
  po.status = allReceived ? "received" : anyReceived ? "partial_received" : po.status;
  return po;
}

export function mockSubmitPurchaseOrder(poId: string): AdminPurchaseOrder {
  const po = purchaseOrders.find((p) => p.id === poId);
  if (!po) throw new Error("Purchase order not found");
  po.status = "confirmed";
  return po;
}
