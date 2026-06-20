export type OrderStatus =
  | "pending"
  | "awaiting_payment"
  | "paid"
  | "packed"
  | "shipped"
  | "delivered"
  | "cancelled"
  | "refunded";

export type TradeStatus = "pending" | "approved" | "rejected" | "suspended";

export type RevenuePeriod = "daily" | "weekly" | "monthly";

export interface KpiMetric {
  id: string;
  label: string;
  value: string;
  rawValue: number;
  growthPercent: number;
  trend: "up" | "down" | "neutral";
}

export interface RevenueDataPoint {
  label: string;
  revenue: number;
  orders: number;
}

export interface OrderAnalytics {
  total: number;
  completed: number;
  cancelled: number;
  byStatus: { status: string; count: number }[];
}

export interface ProductAnalytics {
  bestSellers: { name: string; sku: string; units: number; revenue: number }[];
  topCategories: { name: string; revenue: number; share: number }[];
  topBrands: { name: string; revenue: number; share: number }[];
}

export interface CustomerAnalytics {
  newCustomers: number;
  returningCustomers: number;
  trend: { label: string; new: number; returning: number }[];
}

export interface LowStockItem {
  id: string;
  productName: string;
  sku: string;
  warehouse: string;
  currentStock: number;
  reorderLevel: number;
}

export interface OutOfStockItem {
  id: string;
  productName: string;
  sku: string;
  warehouse: string;
  lastSoldAt: string;
}

export interface AdminOrder {
  id: string;
  orderNumber: string;
  customerName: string;
  customerEmail: string;
  amountCents: number;
  status: OrderStatus;
  placedAt: string;
}

export interface AdminCustomer {
  id: string;
  name: string;
  email: string;
  orderCount: number;
  tradeStatus: TradeStatus | null;
  joinedAt: string;
}

export interface TradeApplication {
  id: string;
  companyName: string;
  contactName: string;
  email: string;
  abn: string;
  status: TradeStatus;
  submittedAt: string;
}

export interface AdminSupplier {
  id: string;
  name: string;
  productsSupplied: number;
  contactPerson: string;
  status: "active" | "inactive" | "onboarding";
}

export interface AdminNotification {
  id: string;
  type: "low_stock" | "new_order" | "trade_application" | "payment";
  title: string;
  message: string;
  createdAt: string;
  read: boolean;
}

export interface AdminProduct {
  id: string;
  name: string;
  sku: string;
  brand: string;
  category: string;
  priceCents: number;
  stock: number;
  status: "active" | "draft" | "archived";
}

export interface AdminCategory {
  id: string;
  name: string;
  slug: string;
  productCount: number;
  parent: string | null;
}

export interface AdminBrand {
  id: string;
  name: string;
  slug: string;
  productCount: number;
  featured: boolean;
}

export interface AdminWarehouse {
  id: string;
  code: string;
  name: string;
  location: string;
  skuCount: number;
  totalUnits: number;
}

export interface InventoryRow {
  id: string;
  sku: string;
  productName: string;
  warehouse: string;
  quantity: number;
  reorderLevel: number;
  averageCostCents: number;
}

export type PurchaseOrderStatus =
  | "draft"
  | "submitted"
  | "confirmed"
  | "partial_received"
  | "received"
  | "cancelled";

export interface PurchaseOrderLine {
  id: string;
  sku: string;
  productName: string;
  quantityOrdered: number;
  quantityReceived: number;
  unitCostCents: number;
}

export interface AdminPurchaseOrder {
  id: string;
  poNumber: string;
  supplierName: string;
  warehouseCode: string;
  status: PurchaseOrderStatus;
  totalExGstCents: number;
  expectedAt: string | null;
  lines: PurchaseOrderLine[];
  createdAt: string;
}

export type StockMovementType =
  | "receipt"
  | "sale"
  | "adjustment"
  | "transfer_in"
  | "transfer_out";

export interface StockMovementRecord {
  id: string;
  movementNumber: string;
  sku: string;
  productName: string;
  warehouseCode: string;
  type: StockMovementType;
  quantity: number;
  quantityAfter: number;
  notes: string;
  createdAt: string;
}

export interface LowStockAlert {
  id: string;
  sku: string;
  productName: string;
  warehouseCode: string;
  quantityOnHand: number;
  reorderPoint: number;
  reorderQuantity: number;
  shortfall: number;
  alertLevel: "low_stock" | "out_of_stock";
}

export interface StockInPayload {
  sku: string;
  warehouseCode: string;
  quantity: number;
  costPriceCents: number;
  notes?: string;
}

export interface StockOutPayload {
  sku: string;
  warehouseCode: string;
  quantity: number;
  notes?: string;
}

export interface StockAdjustmentPayload {
  sku: string;
  warehouseCode: string;
  quantityChange: number;
  costPriceCents?: number;
  notes?: string;
}

export interface StockTransferPayload {
  sku: string;
  fromWarehouseCode: string;
  toWarehouseCode: string;
  quantity: number;
  notes?: string;
}

export interface CreatePurchaseOrderPayload {
  supplierId: string;
  warehouseCode: string;
  lines: { sku: string; quantity: number; unitCostCents: number }[];
}

export interface ReportType {
  id: string;
  name: string;
  description: string;
}

export interface CompanySettings {
  legalName: string;
  tradingName: string;
  abn: string;
  address: string;
  phone: string;
  email: string;
}

export interface GstSettings {
  rate: number;
  displayPricesIncGst: boolean;
  taxInvoicePrefix: string;
}

export interface ShippingSettings {
  freeShippingThresholdCents: number;
  defaultCarrier: string;
  standardRateCents: number;
}

export interface EmailSettings {
  fromName: string;
  fromEmail: string;
  orderConfirmation: boolean;
  shippingNotification: boolean;
}

export interface PaymentGatewaySettings {
  provider: string;
  mode: "test" | "live";
  enabledMethods: string[];
}

export interface AdminDashboardData {
  kpis: KpiMetric[];
  revenue: Record<RevenuePeriod, RevenueDataPoint[]>;
  orderAnalytics: OrderAnalytics;
  productAnalytics: ProductAnalytics;
  customerAnalytics: CustomerAnalytics;
  lowStock: LowStockItem[];
  outOfStock: OutOfStockItem[];
  recentOrders: AdminOrder[];
  recentCustomers: AdminCustomer[];
  tradeApplications: TradeApplication[];
  suppliers: AdminSupplier[];
  notifications: AdminNotification[];
}
