import type { Quote } from "./quotes-types";

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

export interface AdminCustomerOrganization {
  id: string;
  legalName: string;
  tradingName: string;
  abn: string;
  email: string;
  phone: string;
  segment: string;
}

export interface AdminCustomerProfile {
  id: string;
  name: string;
  email: string;
  phone: string;
  customerType: string;
  tradeStatus: TradeStatus | null;
  joinedAt: string;
  organization: AdminCustomerOrganization | null;
}

export interface AdminCustomerLifetimeValue {
  totalSpentCents: number;
  orderCount: number;
  averageOrderCents: number;
  quoteCount: number;
  acceptedQuoteValueCents: number;
}

export interface AdminCustomerTradeAccount {
  id: string | null;
  accountNumber: string | null;
  status: string | null;
  tier: string | null;
  creditLimitCents: number;
  creditUsedCents: number;
  creditAvailableCents: number;
  paymentTermsDays: number | null;
}

export interface AdminCustomerOrderSummary {
  id: string;
  orderNumber: string;
  status: string;
  paymentStatus: string;
  itemCount: number;
  totalIncGstCents: number;
  currencyCode: string;
  placedAt: string | null;
  customerName: string;
  customerEmail: string;
}

export interface AdminCustomerDetail {
  profile: AdminCustomerProfile;
  partyId: string | null;
  lifetimeValue: AdminCustomerLifetimeValue;
  tradeAccount: AdminCustomerTradeAccount | null;
  orders: AdminCustomerOrderSummary[];
  quotes: Quote[];
  crmActivities: CrmTimelineEntry[];
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

export interface AdminProductImage {
  url: string;
  altText: string;
  sortOrder: number;
  isPrimary: boolean;
}

export interface AdminProduct {
  id: string;
  name: string;
  slug: string;
  sku: string;
  brandId: string | null;
  brand: string;
  categoryId: string | null;
  category: string;
  sellPriceExGstCents: number;
  costPriceCents: number;
  gstRate: string;
  gstCents: number;
  sellPriceIncGstCents: number;
  priceCents: number;
  stock: number;
  isActive: boolean;
  status: "active" | "inactive" | "draft" | "archived";
  shortDescription: string;
  description: string;
  images: AdminProductImage[];
}

export interface AdminProductWritePayload {
  name: string;
  slug?: string;
  sku: string;
  brand_id?: string | null;
  category_id?: string | null;
  sell_price_ex_gst_cents: number;
  cost_price_cents?: number;
  stock?: number;
  is_active?: boolean;
  short_description?: string;
  description?: string;
  images?: Array<{
    url: string;
    alt_text?: string;
    sort_order?: number;
    is_primary?: boolean;
  }>;
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

export type CrmLeadStatus =
  | "new"
  | "contacted"
  | "qualified"
  | "proposal_sent"
  | "won"
  | "lost";

export type CrmActivityType = "call" | "meeting" | "email" | "follow_up" | "note";

export interface CrmUserRef {
  id: string;
  email: string;
  name: string;
}

export interface CrmLead {
  id: string;
  title: string;
  companyName: string;
  contactName: string;
  contactEmail: string;
  contactPhone: string;
  source: string;
  status: CrmLeadStatus;
  assignedTo: CrmUserRef | null;
  partyId: string | null;
  customerId: string | null;
  notesSummary: string;
  createdAt: string;
  updatedAt: string;
}

export interface CrmOpportunity {
  id: string;
  name: string;
  status: "open" | "won" | "lost";
  stage: CrmLeadStatus;
  expectedRevenueCents: number;
  probability: number;
  weightedRevenueCents: number;
  expectedCloseDate: string | null;
  assignedTo: CrmUserRef | null;
  partyId: string;
  partyName: string;
  leadId: string | null;
  customerId: string | null;
  tradeAccountId: string | null;
  wonAt: string | null;
  lostAt: string | null;
  lostReason: string;
  createdAt: string;
  updatedAt: string;
}

export interface CrmTimelineEntry {
  id: string;
  entryType: "activity" | "note" | "status_change";
  activityType?: CrmActivityType;
  title: string;
  body: string;
  occurredAt: string;
  actorEmail: string | null;
}

export interface CrmDashboardKpis {
  totalLeads: number;
  openOpportunities: number;
  conversionRate: number;
  revenueForecastCents: number;
  leadsByStatus: Record<string, number>;
  wonOpportunities: number;
  lostOpportunities: number;
  charts?: CrmDashboardCharts;
}

export interface CrmPipelineStageValue {
  stage: string;
  label: string;
  valueCents: number;
  count: number;
}

export interface CrmForecastStageValue {
  stage: string;
  label: string;
  weightedCents: number;
}

export interface CrmDashboardCharts {
  pipelineValue: CrmPipelineStageValue[];
  forecastRevenue: CrmForecastStageValue[];
  winRate: number;
  conversionRate: number;
}

export interface CrmPartyRef {
  id: string;
  displayName: string;
  legalName: string;
  email: string;
  phone: string;
  partyType: string;
}

export interface CrmCustomerRef {
  id: string;
  email: string;
  organizationName: string | null;
  customerType: string;
}

export interface CrmTradeAccountRef {
  id: string;
  accountNumber: string;
  status: string;
  organizationName: string;
  tier: string;
}

export interface CrmQuoteDraft {
  id: string;
  quoteNumber: string;
  status: string;
  totalIncGstCents: number;
  validUntil: string;
  createdAt: string;
}

export interface CrmActivity {
  id: string;
  activityType: CrmActivityType;
  subject: string;
  description: string;
  scheduledAt: string | null;
  completedAt: string | null;
  assignedTo: CrmUserRef | null;
  createdAt: string;
}

export interface CrmNote {
  id: string;
  body: string;
  createdBy: CrmUserRef | null;
  createdAt: string;
}

export interface CrmLeadDetail extends CrmLead {
  party: CrmPartyRef | null;
  customer: CrmCustomerRef | null;
  opportunities: CrmOpportunity[];
  activities: CrmActivity[];
  notes: CrmNote[];
}

export interface CrmOpportunityDetail extends CrmOpportunity {
  party: CrmPartyRef;
  customer: CrmCustomerRef | null;
  tradeAccount: CrmTradeAccountRef | null;
  quoteDraft: CrmQuoteDraft | null;
}

export type CrmPipelineColumns = Record<CrmLeadStatus, CrmLead[]>;
