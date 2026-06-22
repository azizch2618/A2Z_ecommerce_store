import type {
  AdminBrand,
  AdminCategory,
  AdminCustomer,
  AdminDashboardData,
  AdminNotification,
  AdminOrder,
  AdminProduct,
  AdminSupplier,
  AdminWarehouse,
  CompanySettings,
  EmailSettings,
  GstSettings,
  InventoryRow,
  PaymentGatewaySettings,
  ReportType,
  ShippingSettings,
  TradeApplication,
} from "@/lib/api/admin/types";

const delay = (ms = 300) => new Promise((resolve) => setTimeout(resolve, ms));

export const mockDashboardData: AdminDashboardData = {
  kpis: [
    { id: "revenue", label: "Total Revenue", value: "$284,520", rawValue: 28452000, growthPercent: 12.4, trend: "up" },
    { id: "orders", label: "Total Orders", value: "1,248", rawValue: 1248, growthPercent: 8.2, trend: "up" },
    { id: "customers", label: "Active Customers", value: "892", rawValue: 892, growthPercent: 5.1, trend: "up" },
    { id: "in_stock", label: "Products In Stock", value: "3,420", rawValue: 3420, growthPercent: 2.3, trend: "up" },
    { id: "low_stock", label: "Low Stock Products", value: "47", rawValue: 47, growthPercent: -3.8, trend: "down" },
    { id: "pending_orders", label: "Pending Orders", value: "23", rawValue: 23, growthPercent: 15.0, trend: "up" },
    { id: "trade_customers", label: "Trade Customers", value: "156", rawValue: 156, growthPercent: 6.7, trend: "up" },
    { id: "suppliers", label: "Suppliers", value: "38", rawValue: 38, growthPercent: 0, trend: "neutral" },
  ],
  revenue: {
    daily: [
      { label: "Mon", revenue: 12400, orders: 18 },
      { label: "Tue", revenue: 15800, orders: 22 },
      { label: "Wed", revenue: 14200, orders: 19 },
      { label: "Thu", revenue: 18900, orders: 28 },
      { label: "Fri", revenue: 22100, orders: 31 },
      { label: "Sat", revenue: 9800, orders: 14 },
      { label: "Sun", revenue: 7600, orders: 11 },
    ],
    weekly: [
      { label: "W1", revenue: 82000, orders: 112 },
      { label: "W2", revenue: 94500, orders: 128 },
      { label: "W3", revenue: 88700, orders: 119 },
      { label: "W4", revenue: 102300, orders: 141 },
    ],
    monthly: [
      { label: "Jan", revenue: 312000, orders: 420 },
      { label: "Feb", revenue: 298500, orders: 398 },
      { label: "Mar", revenue: 345200, orders: 465 },
      { label: "Apr", revenue: 328900, orders: 441 },
      { label: "May", revenue: 367400, orders: 492 },
      { label: "Jun", revenue: 384520, orders: 512 },
    ],
  },
  orderAnalytics: {
    total: 1248,
    completed: 1089,
    cancelled: 42,
    byStatus: [
      { status: "Delivered", count: 892 },
      { status: "Shipped", count: 156 },
      { status: "Packed", count: 78 },
      { status: "Paid", count: 45 },
      { status: "Pending", count: 23 },
      { status: "Cancelled", count: 42 },
    ],
  },
  productAnalytics: {
    bestSellers: [
      { name: "Cat6 UTP Cable 305m", sku: "NET-CAT6-305", units: 342, revenue: 68400 },
      { name: "24-Port PoE+ Switch", sku: "SW-24POE", units: 128, revenue: 153600 },
      { name: "Impact Driver Kit", sku: "DRL-IMP-01", units: 215, revenue: 53750 },
      { name: "RJ45 Keystone Jack", sku: "NET-RJ45-KJ", units: 1840, revenue: 27600 },
      { name: "UniFi AP WiFi 6", sku: "UAP-6-PRO", units: 96, revenue: 43200 },
    ],
    topCategories: [
      { name: "Networking", revenue: 124500, share: 34 },
      { name: "Power Tools", revenue: 89200, share: 24 },
      { name: "Cabling", revenue: 67800, share: 19 },
      { name: "Electrical", revenue: 45600, share: 12 },
      { name: "Safety", revenue: 28900, share: 8 },
    ],
    topBrands: [
      { name: "Ubiquiti", revenue: 98500, share: 28 },
      { name: "DeWalt", revenue: 76200, share: 22 },
      { name: "Makita", revenue: 54800, share: 16 },
      { name: "Panduit", revenue: 42100, share: 12 },
      { name: "Cisco", revenue: 38900, share: 11 },
    ],
  },
  customerAnalytics: {
    newCustomers: 124,
    returningCustomers: 768,
    trend: [
      { label: "Jan", new: 98, returning: 612 },
      { label: "Feb", new: 87, returning: 645 },
      { label: "Mar", new: 112, returning: 698 },
      { label: "Apr", new: 105, returning: 712 },
      { label: "May", new: 118, returning: 745 },
      { label: "Jun", new: 124, returning: 768 },
    ],
  },
  lowStock: [
    { id: "1", productName: "Cat6 UTP Cable 305m", sku: "NET-CAT6-305", warehouse: "Sydney DC", currentStock: 8, reorderLevel: 20 },
    { id: "2", productName: "RJ45 Keystone Jack", sku: "NET-RJ45-KJ", warehouse: "Melbourne DC", currentStock: 45, reorderLevel: 100 },
    { id: "3", productName: "Impact Driver Kit", sku: "DRL-IMP-01", warehouse: "Sydney DC", currentStock: 3, reorderLevel: 15 },
    { id: "4", productName: "PoE Injector 30W", sku: "POE-30W", warehouse: "Brisbane DC", currentStock: 12, reorderLevel: 25 },
  ],
  outOfStock: [
    { id: "1", productName: "48-Port Managed Switch", sku: "SW-48-MGD", warehouse: "Sydney DC", lastSoldAt: "2026-06-12" },
    { id: "2", productName: "Fiber Patch Lead 10m", sku: "FIB-PL-10", warehouse: "Melbourne DC", lastSoldAt: "2026-06-10" },
    { id: "3", productName: "Cable Tester Pro", sku: "TST-CBL-PRO", warehouse: "Perth DC", lastSoldAt: "2026-06-08" },
  ],
  recentOrders: [
    { id: "1", orderNumber: "A2Z-20260617-0042", customerName: "Metro Electrical", customerEmail: "orders@metroelec.com.au", amountCents: 452300, status: "paid", placedAt: "2026-06-17T09:15:00Z" },
    { id: "2", orderNumber: "A2Z-20260617-0041", customerName: "James Wilson", customerEmail: "j.wilson@gmail.com", amountCents: 18950, status: "packed", placedAt: "2026-06-17T08:42:00Z" },
    { id: "3", orderNumber: "A2Z-20260616-0040", customerName: "Network Pro Solutions", customerEmail: "buy@netpro.com.au", amountCents: 1284000, status: "shipped", placedAt: "2026-06-16T16:20:00Z" },
    { id: "4", orderNumber: "A2Z-20260616-0039", customerName: "Lisa Chen", customerEmail: "lisa.chen@outlook.com", amountCents: 6750, status: "pending", placedAt: "2026-06-16T14:05:00Z" },
    { id: "5", orderNumber: "A2Z-20260616-0038", customerName: "BuildRight Contractors", customerEmail: "procurement@buildright.com.au", amountCents: 89200, status: "delivered", placedAt: "2026-06-16T11:30:00Z" },
  ],
  recentCustomers: [
    { id: "1", name: "Metro Electrical Pty Ltd", email: "orders@metroelec.com.au", orderCount: 48, tradeStatus: "approved", joinedAt: "2024-03-15" },
    { id: "2", name: "James Wilson", email: "j.wilson@gmail.com", orderCount: 3, tradeStatus: null, joinedAt: "2026-05-20" },
    { id: "3", name: "Network Pro Solutions", email: "buy@netpro.com.au", orderCount: 112, tradeStatus: "approved", joinedAt: "2023-08-02" },
    { id: "4", name: "Lisa Chen", email: "lisa.chen@outlook.com", orderCount: 1, tradeStatus: null, joinedAt: "2026-06-16" },
    { id: "5", name: "Apex Data Cabling", email: "accounts@apexcabling.com.au", orderCount: 0, tradeStatus: "pending", joinedAt: "2026-06-17" },
  ],
  tradeApplications: [
    { id: "1", companyName: "Apex Data Cabling", contactName: "Tom Richards", email: "accounts@apexcabling.com.au", abn: "51824753556", status: "pending", submittedAt: "2026-06-17T07:00:00Z" },
    { id: "2", companyName: "Sunrise Electrical", contactName: "Maria Santos", email: "maria@sunriseelec.com.au", abn: "67102457489", status: "pending", submittedAt: "2026-06-16T14:30:00Z" },
    { id: "3", companyName: "Coastal Networks", contactName: "David Park", email: "david@coastalnet.com.au", abn: "29123456789", status: "approved", submittedAt: "2026-06-10T09:00:00Z" },
    { id: "4", companyName: "Quick Fix IT", contactName: "Ryan O'Brien", email: "ryan@quickfixit.com.au", abn: "12345678901", status: "rejected", submittedAt: "2026-06-05T11:00:00Z" },
  ],
  suppliers: [
    { id: "1", name: "Tool Distributors Australia", productsSupplied: 420, contactPerson: "Mark Thompson", status: "active" },
    { id: "2", name: "Network Wholesale Pty Ltd", productsSupplied: 285, contactPerson: "Jenny Wu", status: "active" },
    { id: "3", name: "Pacific Cabling Supplies", productsSupplied: 156, contactPerson: "Steve Harris", status: "active" },
    { id: "4", name: "Euro Tools Import Co", productsSupplied: 92, contactPerson: "Anna Kowalski", status: "onboarding" },
  ],
  notifications: [
    { id: "1", type: "low_stock", title: "Low stock alert", message: "Cat6 UTP Cable 305m is below reorder level at Sydney DC", createdAt: "2026-06-17T08:00:00Z", read: false },
    { id: "2", type: "new_order", title: "New order received", message: "Order A2Z-20260617-0042 from Metro Electrical — $4,523.00", createdAt: "2026-06-17T09:15:00Z", read: false },
    { id: "3", type: "trade_application", title: "Trade application", message: "Apex Data Cabling submitted a trade account application", createdAt: "2026-06-17T07:00:00Z", read: false },
    { id: "4", type: "payment", title: "Payment received", message: "Payment confirmed for order A2Z-20260616-0040", createdAt: "2026-06-16T16:25:00Z", read: true },
    { id: "5", type: "low_stock", title: "Out of stock", message: "48-Port Managed Switch is out of stock at Sydney DC", createdAt: "2026-06-16T10:00:00Z", read: true },
  ],
};

function mockAdminProduct(
  row: Pick<AdminProduct, "id" | "name" | "sku" | "brand" | "category" | "priceCents" | "stock" | "status">
): AdminProduct {
  const gstCents = Math.round(row.priceCents * 0.1);
  return {
    ...row,
    slug: row.sku.toLowerCase(),
    brandId: null,
    categoryId: null,
    sellPriceExGstCents: row.priceCents,
    costPriceCents: Math.round(row.priceCents * 0.7),
    gstRate: "0.1",
    gstCents,
    sellPriceIncGstCents: row.priceCents + gstCents,
    isActive: row.status === "active",
    shortDescription: "",
    description: "",
    images: [],
  };
}

export const mockProducts: AdminProduct[] = [
  mockAdminProduct({ id: "1", name: "Cat6 UTP Cable 305m", sku: "NET-CAT6-305", brand: "Panduit", category: "Cabling", priceCents: 19900, stock: 8, status: "active" }),
  mockAdminProduct({ id: "2", name: "24-Port PoE+ Switch", sku: "SW-24POE", brand: "Ubiquiti", category: "Networking", priceCents: 119900, stock: 42, status: "active" }),
  mockAdminProduct({ id: "3", name: "Impact Driver Kit", sku: "DRL-IMP-01", brand: "DeWalt", category: "Power Tools", priceCents: 24900, stock: 3, status: "active" }),
  mockAdminProduct({ id: "4", name: "UniFi AP WiFi 6", sku: "UAP-6-PRO", brand: "Ubiquiti", category: "Networking", priceCents: 44900, stock: 28, status: "active" }),
  mockAdminProduct({ id: "5", name: "48-Port Managed Switch", sku: "SW-48-MGD", brand: "Cisco", category: "Networking", priceCents: 289900, stock: 0, status: "active" }),
];

export const mockCategories: AdminCategory[] = [
  { id: "1", name: "Networking", slug: "networking", productCount: 342, parent: null },
  { id: "2", name: "Power Tools", slug: "power-tools", productCount: 218, parent: null },
  { id: "3", name: "Cabling", slug: "cabling", productCount: 156, parent: null },
  { id: "4", name: "Switches", slug: "switches", productCount: 89, parent: "Networking" },
  { id: "5", name: "Access Points", slug: "access-points", productCount: 45, parent: "Networking" },
];

export const mockBrands: AdminBrand[] = [
  { id: "1", name: "Ubiquiti", slug: "ubiquiti", productCount: 124, featured: true },
  { id: "2", name: "DeWalt", slug: "dewalt", productCount: 98, featured: true },
  { id: "3", name: "Makita", slug: "makita", productCount: 87, featured: true },
  { id: "4", name: "Cisco", slug: "cisco", productCount: 56, featured: false },
  { id: "5", name: "Panduit", slug: "panduit", productCount: 72, featured: false },
];

export const mockWarehouses: AdminWarehouse[] = [
  { id: "1", code: "SYD1", name: "Sydney Distribution Centre", location: "Sydney, NSW", skuCount: 1240, totalUnits: 45200 },
  { id: "2", code: "MEL1", name: "Melbourne Distribution Centre", location: "Melbourne, VIC", skuCount: 980, totalUnits: 32100 },
  { id: "3", code: "BNE1", name: "Brisbane Distribution Centre", location: "Brisbane, QLD", skuCount: 720, totalUnits: 21800 },
  { id: "4", code: "PER1", name: "Perth Distribution Centre", location: "Perth, WA", skuCount: 480, totalUnits: 12400 },
];

export const mockInventory: InventoryRow[] = [
  { id: "1", sku: "NET-CAT6-305", productName: "Cat6 UTP Cable 305m", warehouse: "SYD1", quantity: 8, reorderLevel: 20, averageCostCents: 12400 },
  { id: "2", sku: "SW-24POE", productName: "24-Port PoE+ Switch", warehouse: "SYD1", quantity: 42, reorderLevel: 10, averageCostCents: 89900 },
  { id: "3", sku: "DRL-IMP-01", productName: "Impact Driver Kit", warehouse: "MEL1", quantity: 3, reorderLevel: 15, averageCostCents: 18200 },
  { id: "4", sku: "SW-48-MGD", productName: "48-Port Managed Switch", warehouse: "SYD1", quantity: 0, reorderLevel: 5, averageCostCents: 215000 },
];

export const mockPurchaseOrders = [
  {
    id: "po1",
    poNumber: "PO-20250610-A1B2C3",
    supplierName: "Cable & Data Supplies",
    warehouseCode: "SYD1",
    status: "confirmed" as const,
    totalExGstCents: 248000,
    expectedAt: "2025-06-20T00:00:00.000Z",
    lines: [
      {
        id: "pol1",
        sku: "NET-CAT6-305",
        productName: "Cat6 UTP Cable 305m",
        quantityOrdered: 20,
        quantityReceived: 0,
        unitCostCents: 12400,
      },
    ],
    createdAt: "2025-06-10T08:00:00.000Z",
  },
  {
    id: "po2",
    poNumber: "PO-20250612-D4E5F6",
    supplierName: "PowerTool Wholesale",
    warehouseCode: "MEL1",
    status: "partial_received" as const,
    totalExGstCents: 91000,
    expectedAt: null,
    lines: [
      {
        id: "pol2",
        sku: "DRL-IMP-01",
        productName: "Impact Driver Kit",
        quantityOrdered: 5,
        quantityReceived: 2,
        unitCostCents: 18200,
      },
    ],
    createdAt: "2025-06-12T10:30:00.000Z",
  },
];

export const mockStockMovements = [
  {
    id: "mv1",
    movementNumber: "IN-20250615-X1Y2Z3",
    sku: "SW-24POE",
    productName: "24-Port PoE+ Switch",
    warehouseCode: "SYD1",
    type: "receipt" as const,
    quantity: 10,
    quantityAfter: 42,
    notes: "Supplier delivery",
    createdAt: "2025-06-15T09:00:00.000Z",
  },
];

export const mockOrders: AdminOrder[] = mockDashboardData.recentOrders;

export const mockCustomers: AdminCustomer[] = mockDashboardData.recentCustomers;

export const mockTradeApplications: TradeApplication[] = mockDashboardData.tradeApplications;

export const mockSuppliers: AdminSupplier[] = mockDashboardData.suppliers;

export const mockNotifications: AdminNotification[] = mockDashboardData.notifications;

export const mockReports: ReportType[] = [
  { id: "sales", name: "Sales Report", description: "Revenue, orders, and average order value by period" },
  { id: "inventory", name: "Inventory Report", description: "Stock levels, valuations, and movement summary" },
  { id: "customer", name: "Customer Report", description: "Customer acquisition, retention, and trade accounts" },
  { id: "gst", name: "GST Report", description: "Australian GST collected and payable summary" },
];

export const mockCompanySettings: CompanySettings = {
  legalName: "A2Z Tools Pty Ltd",
  tradingName: "A2Z Tools",
  abn: "12 345 678 901",
  address: "100 Industrial Drive, Alexandria NSW 2015",
  phone: "1300 229 868",
  email: "hello@a2ztools.com.au",
};

export const mockGstSettings: GstSettings = {
  rate: 0.1,
  displayPricesIncGst: true,
  taxInvoicePrefix: "INV",
};

export const mockShippingSettings: ShippingSettings = {
  freeShippingThresholdCents: 15000,
  defaultCarrier: "Australia Post",
  standardRateCents: 1500,
};

export const mockEmailSettings: EmailSettings = {
  fromName: "A2Z Tools",
  fromEmail: "noreply@a2ztools.com.au",
  orderConfirmation: true,
  shippingNotification: true,
};

export const mockPaymentSettings: PaymentGatewaySettings = {
  provider: "Stripe",
  mode: "test",
  enabledMethods: ["card", "bank_transfer", "trade_credit"],
};

export async function simulateApi<T>(data: T, ms = 300): Promise<T> {
  await delay(ms);
  return data;
}
