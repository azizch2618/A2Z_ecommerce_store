export type PurchaseRequestStatus =
  | "draft"
  | "submitted"
  | "approved"
  | "rejected"
  | "converted";

export type PurchaseRequestPriority = "low" | "medium" | "high" | "urgent";

export interface PurchaseRequestLine {
  id: string;
  sku: string;
  productName: string;
  quantity: number;
  unitCostCents: number;
  notes: string;
}

export interface PurchaseRequest {
  id: string;
  requestNumber: string;
  status: PurchaseRequestStatus;
  priority: PurchaseRequestPriority;
  justification: string;
  requestedBy: { id: string; email: string } | null;
  departmentId: string | null;
  departmentName: string | null;
  costCenterId: string | null;
  costCenterName: string | null;
  warehouseCode: string | null;
  supplierId: string | null;
  supplierName: string | null;
  convertedPoId: string | null;
  convertedPoNumber: string | null;
  createdAt: string;
  updatedAt: string;
  lines: PurchaseRequestLine[];
}

export interface ProcurementDashboardKpis {
  openRequisitions: number;
  openPurchaseOrders: number;
  procurementSpendCents: number;
  onTimeDeliveryPct: number;
  avgLeadTimeDays: number;
  orderAccuracyPct: number;
}

export interface SupplierPerformanceKpis {
  onTimeDeliveryPct: number;
  avgLeadTimeDays: number;
  orderAccuracyPct: number;
  purchaseSpendCents: number;
  totalOrders: number;
  supplierId?: string;
  supplierName?: string;
  openPurchaseOrders?: number;
}

export interface SupplierPortalPo {
  id: string;
  poNumber: string;
  status: string;
  totalExGstCents: number;
  expectedAt: string | null;
  acknowledgedAt: string | null;
  paymentStatus: string;
  warehouseCode: string;
  lines: {
    id: string;
    sku: string;
    productName: string;
    quantityOrdered: number;
    quantityReceived: number;
    unitCostCents: number;
  }[];
  createdAt: string;
}

export interface SupplierDocument {
  id: string;
  documentType: string;
  originalFilename: string;
  fileUrl: string | null;
  poId: string | null;
  notes: string;
  createdAt: string;
}

export interface GoodsReceipt {
  id: string;
  grnNumber: string;
  status: string;
  poNumber: string;
  poId: string;
  receivedAt: string;
  lines: {
    id: string;
    sku: string;
    quantityReceived: number;
    batchNumber: string;
    receivedAt: string;
  }[];
}
