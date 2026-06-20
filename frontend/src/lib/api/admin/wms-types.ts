export interface WmsDashboardKpis {
  inventoryValueCents: number;
  openTransfers: number;
  openPicks: number;
  cycleCountAccuracyPct: number;
}

export interface WarehouseBin {
  id: string;
  locationCode: string;
  code: string;
  name: string;
  binType: string;
  zoneCode: string;
  aisleCode: string;
  warehouseCode: string;
  isActive: boolean;
}

export interface BinInventoryRow {
  id: string;
  locationCode: string;
  binId: string;
  sku: string;
  productName: string;
  quantityOnHand: number;
  warehouseCode: string;
}

export interface StockTransfer {
  id: string;
  transferNumber: string;
  transferType: string;
  status: string;
  fromWarehouseCode: string;
  toWarehouseCode: string;
  requiresApproval: boolean;
  lines: { id: string; sku: string; quantity: number; quantityMoved: number }[];
  createdAt: string;
}

export interface PickList {
  id: string;
  pickNumber: string;
  status: string;
  warehouseCode: string;
  orderNumber: string | null;
  lines: {
    id: string;
    sku: string;
    productName: string;
    quantityRequired: number;
    quantityPicked: number;
    fromBinLocation: string | null;
  }[];
  createdAt: string;
}

export interface PutawayTask {
  id: string;
  taskNumber: string;
  status: string;
  grnNumber: string;
  warehouseCode: string;
  lines: {
    id: string;
    sku: string;
    quantity: number;
    quantityPutaway: number;
    targetBinLocation: string | null;
  }[];
}

export interface CycleCount {
  id: string;
  countNumber: string;
  status: string;
  warehouseCode: string;
  lines: {
    id: string;
    sku: string;
    binLocation: string | null;
    expectedQty: number;
    countedQty: number | null;
    variance: number | null;
  }[];
}
