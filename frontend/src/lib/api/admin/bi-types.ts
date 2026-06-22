export interface ExecutiveKpis {
  revenueCents: number;
  grossMarginCents: number;
  grossMarginPct: number;
  inventoryValueCents: number;
  openOrders: number;
  openQuotes: number;
  cashPositionCents: number;
  payrollCostYtdCents: number;
  arOutstandingCents: number;
  procurementSpendCents: number;
  headcount: number;
  quoteConversionPct: number;
  wmsInventoryValueCents: number;
}

export interface ExecutiveSnapshot {
  generatedAt: string;
  executiveKpis: ExecutiveKpis;
}

export interface RevenueByMonthRow {
  month: string;
  label: string;
  revenueCents: number;
  orderCount: number;
}

export interface SalesAnalytics {
  revenueByMonth: RevenueByMonthRow[];
  revenueByCustomer: Array<{
    customerId: string | null;
    customerName: string;
    revenueCents: number;
    orderCount: number;
  }>;
  revenueByProduct: Array<{
    sku: string;
    productName: string;
    revenueCents: number;
    units: number;
  }>;
  quoteConversion: {
    draftQuotes: number;
    pendingApproval: number;
    accepted: number;
    converted: number;
    conversionRatePct: number;
  };
}

export interface InventoryAnalytics {
  inventoryValueCents: number;
  inventoryTurns: number;
  deadStock: Array<{
    sku: string;
    productName: string;
    warehouse: string;
    quantity: number;
    valueCents: number;
  }>;
  fastMovingProducts: Array<{
    sku: string;
    productName: string;
    unitsSold: number;
  }>;
  warehouseUtilization: {
    totalBins: number;
    usedBins: number;
    utilizationPct: number;
  };
}

export interface ProcurementAnalytics {
  totalSpendCents: number;
  openRequisitions: number;
  openPurchaseOrders: number;
  spendBySupplier: Array<{
    supplierId: string;
    supplierName: string;
    spendCents: number;
    orderCount: number;
  }>;
  spendByCategory: Array<{ category: string; spendCents: number }>;
}

export interface FinanceAnalytics {
  arAging: Record<string, number>;
  apAging: Record<string, number>;
  cashFlow: {
    cashPositionCents: number;
    arOutstandingCents: number;
    apOutstandingCents: number;
    netWorkingCapitalCents: number;
  };
  profitability: {
    revenueCents: number;
    expenseCents: number;
    netPositionCents: number;
  };
}

export interface HrAnalytics {
  headcount: number;
  onLeaveToday: number;
  pendingLeaveRequests: number;
  leaveTrends: Array<{
    month: string;
    label: string;
    byType: Record<string, { totalDays: number; requestCount: number }>;
  }>;
  payrollCostByDepartment: Array<{
    departmentName: string;
    headcount: number;
    totalCents: number;
  }>;
  payrollYtdCents: number;
}

export interface KpiEvaluation {
  id: string;
  code: string;
  name: string;
  category: string;
  unit: string;
  metricKey: string;
  value: number | null;
  targetValue: number | null;
  onTarget: boolean | null;
}

export interface BiSnapshot {
  executive: ExecutiveSnapshot;
  sales: SalesAnalytics;
  inventory: InventoryAnalytics;
  procurement: ProcurementAnalytics;
  finance: FinanceAnalytics;
  hr: HrAnalytics;
  kpis: KpiEvaluation[];
}

export interface ScheduledReport {
  id: string;
  name: string;
  reportId: string;
  format: string;
  frequency: string;
  recipientEmails: string[];
  isActive: boolean;
  lastRunAt: string | null;
  nextRunAt: string | null;
}
