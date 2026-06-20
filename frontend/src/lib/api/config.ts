/**
 * API configuration — single source of truth for base URL and route prefixes.
 * Aligns with Django REST Framework `/api/v1` namespace.
 */

const rawBaseUrl =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

/** Normalised base URL without trailing slash */
export const API_BASE_URL = rawBaseUrl.replace(/\/$/, "");

/** API version segment for future v2 expansion */
export const API_VERSION = "v1" as const;

/**
 * Canonical endpoint paths (relative to API_BASE_URL).
 * Add new ERP modules here — e.g. inventory, suppliers, finance.
 */
export const API_ENDPOINTS = {
  auth: {
    register: "/auth/register/",
    login: "/auth/login/",
    refresh: "/auth/refresh/",
    logout: "/auth/logout/",
    profile: "/auth/profile/",
    me: "/auth/me/",
    forgotPassword: "/auth/forgot-password/",
    resetPassword: "/auth/reset-password/",
    verifyEmail: "/auth/verify-email/",
    resendVerification: "/auth/resend-verification/",
    changePassword: "/auth/change-password/",
  },
  customers: {
    addresses: "/customers/addresses/",
    address: (addressId: string) => `/customers/addresses/${addressId}/`,
  },
  products: {
    list: "/products/",
    search: "/products/search/",
    compare: "/products/compare/",
    bySlug: (slug: string) => `/products/${slug}/`,
    byId: (id: string) => `/products/id/${id}/`,
    variant: (variantId: string) => `/products/variants/${variantId}/`,
  },
  categories: {
    list: "/categories/",
    bySlug: (slug: string) => `/categories/${slug}/`,
    products: (slug: string) => `/categories/${slug}/products/`,
  },
  brands: {
    list: "/brands/",
    bySlug: (slug: string) => `/brands/${slug}/`,
    products: (slug: string) => `/brands/${slug}/products/`,
  },
  cart: {
    root: "/cart/",
    items: "/cart/items/",
    item: (itemId: string) => `/cart/items/${itemId}/`,
    clear: "/cart/clear/",
    coupon: "/cart/coupon/",
    merge: "/cart/merge/",
  },
  wishlist: {
    root: "/wishlist/",
    items: "/wishlist/items/",
    item: (itemId: string) => `/wishlist/items/${itemId}/`,
  },
  orders: {
    list: "/orders/",
    create: "/orders/",
    byId: (orderId: string) => `/orders/${orderId}/`,
    cancel: (orderId: string) => `/orders/${orderId}/cancel/`,
    pack: (orderId: string) => `/orders/${orderId}/pack/`,
    ship: (orderId: string) => `/orders/${orderId}/ship/`,
    deliver: (orderId: string) => `/orders/${orderId}/deliver/`,
    refund: (orderId: string) => `/orders/${orderId}/refund/`,
    reorder: (orderId: string) => `/orders/${orderId}/reorder/`,
    invoice: (orderId: string) => `/orders/${orderId}/invoice/`,
  },
  payments: {
    config: "/payments/config/",
    webhook: "/payments/webhook/",
  },
  tradeAccounts: {
    me: "/trade-accounts/me/",
    apply: "/trade-accounts/apply/",
    quotes: "/trade-accounts/quotes/",
    quote: (quoteId: string) => `/trade-accounts/quotes/${quoteId}/`,
    adminApplications: "/trade-accounts/admin/applications/",
    adminApplicationReview: (id: string) =>
      `/trade-accounts/admin/applications/${id}/review/`,
    adminAccountCredit: (id: string) => `/trade-accounts/admin/accounts/${id}/credit/`,
  },
  admin: {
    dashboard: "/analytics/admin/dashboard/",
    customers: "/analytics/admin/customers/",
    products: "/analytics/admin/products/",
    categories: "/catalog/admin/categories/",
    category: (id: string) => `/catalog/admin/categories/${id}/`,
    brands: "/catalog/admin/brands/",
    brand: (id: string) => `/catalog/admin/brands/${id}/`,
    reports: "/analytics/admin/reports/",
    reportsExport: "/analytics/admin/reports/export/",
  },
  suppliers: {
    list: "/suppliers/",
    admin: "/suppliers/admin/",
    adminDetail: (id: string) => `/suppliers/admin/${id}/`,
    purchaseOrders: "/suppliers/purchase-orders/",
    purchaseOrder: (id: string) => `/suppliers/purchase-orders/${id}/`,
    purchaseOrderSubmit: (id: string) => `/suppliers/purchase-orders/${id}/submit/`,
    purchaseOrderConfirm: (id: string) => `/suppliers/purchase-orders/${id}/confirm/`,
    purchaseOrderReceive: (id: string) => `/suppliers/purchase-orders/${id}/receive/`,
    purchaseOrderCancel: (id: string) => `/suppliers/purchase-orders/${id}/cancel/`,
  },
  inventory: {
    levels: "/inventory/levels/",
    level: (id: string) => `/inventory/levels/${id}/`,
    movements: "/inventory/movements/",
    movement: (id: string) => `/inventory/movements/${id}/`,
    transfers: "/inventory/transfers/",
    valuation: "/inventory/valuation/",
    ledgerSummary: "/inventory/ledger/summary/",
    lowStockAlerts: "/inventory/alerts/low-stock/",
    notifications: "/inventory/notifications/",
    notificationCount: "/inventory/notifications/unread-count/",
    acknowledgeNotification: (id: string) =>
      `/inventory/notifications/${id}/acknowledge/`,
    warehouses: "/inventory/warehouses/",
    adminWarehouses: "/inventory/admin/warehouses/",
    adminWarehouse: (id: string) => `/inventory/admin/warehouses/${id}/`,
    stockIn: "/inventory/stock-in/",
    stockOut: "/inventory/stock-out/",
    stockTransfer: "/inventory/stock-transfer/",
    adjustments: "/inventory/adjustments/",
  },
} as const;

export const API_DEFAULTS = {
  locale: "en-AU",
  currency: "AUD",
  gstRate: 0.1,
  paginationLimit: 20,
  paginationMaxLimit: 100,
  requestTimeoutMs: 30_000,
} as const;

export const STORAGE_KEYS = {
  accessToken: "a2z_access_token",
  refreshToken: "a2z_refresh_token",
  sessionKey: "a2z_session_key",
} as const;
