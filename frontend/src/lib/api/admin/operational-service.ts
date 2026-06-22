import { apiDelete, apiGet, apiPatch, apiPost } from "../client";
import { API_ENDPOINTS } from "../config";
import type {
  AdminBrand,
  AdminCategory,
  AdminProduct,
  AdminProductWritePayload,
  AdminPurchaseOrder,
  AdminSupplier,
  AdminWarehouse,
  CreatePurchaseOrderPayload,
  ReportType,
  TradeApplication,
  TradeStatus,
} from "./types";

type Paginated<T> = {
  data: T[];
  pagination?: { has_more: boolean; next_cursor: string | null };
};

function mapCategory(row: {
  id: string;
  name: string;
  slug: string;
  product_count?: number;
  parent_name?: string | null;
}): AdminCategory {
  return {
    id: row.id,
    name: row.name,
    slug: row.slug,
    productCount: row.product_count ?? 0,
    parent: row.parent_name ?? null,
  };
}

function mapBrand(row: {
  id: string;
  name: string;
  slug: string;
  product_count?: number;
  is_authorized_reseller?: boolean;
}): AdminBrand {
  return {
    id: row.id,
    name: row.name,
    slug: row.slug,
    productCount: row.product_count ?? 0,
    featured: Boolean(row.is_authorized_reseller),
  };
}

function mapProduct(row: {
  id: string;
  name: string;
  slug?: string;
  sku: string;
  brand_id?: string | null;
  brand?: string;
  category_id?: string | null;
  category?: string;
  sell_price_ex_gst_cents?: number;
  cost_price_cents?: number;
  gst_rate?: string;
  gst_cents?: number;
  sell_price_inc_gst_cents?: number;
  stock?: number;
  is_active?: boolean;
  status?: string;
  short_description?: string;
  description?: string;
  images?: Array<{
    url: string;
    alt_text?: string;
    sort_order?: number;
    is_primary?: boolean;
  }>;
}): AdminProduct {
  const sellPriceExGstCents = row.sell_price_ex_gst_cents ?? 0;
  return {
    id: row.id,
    name: row.name,
    slug: row.slug ?? "",
    sku: row.sku,
    brandId: row.brand_id ?? null,
    brand: row.brand ?? "",
    categoryId: row.category_id ?? null,
    category: row.category ?? "",
    sellPriceExGstCents,
    costPriceCents: row.cost_price_cents ?? 0,
    gstRate: row.gst_rate ?? "0.1",
    gstCents: row.gst_cents ?? 0,
    sellPriceIncGstCents: row.sell_price_inc_gst_cents ?? sellPriceExGstCents,
    priceCents: sellPriceExGstCents,
    stock: row.stock ?? 0,
    isActive: row.is_active ?? row.status === "active",
    status:
      row.status === "inactive"
        ? "inactive"
        : row.status === "active"
          ? "active"
          : row.is_active === false
            ? "inactive"
            : "active",
    shortDescription: row.short_description ?? "",
    description: row.description ?? "",
    images: (row.images ?? []).map((image, index) => ({
      url: image.url,
      altText: image.alt_text ?? "",
      sortOrder: image.sort_order ?? index,
      isPrimary: Boolean(image.is_primary),
    })),
  };
}

function mapSupplier(row: {
  id: string;
  name: string;
  products_supplied?: number;
  contact_person?: string;
  status?: string;
  is_active?: boolean;
}): AdminSupplier {
  return {
    id: row.id,
    name: row.name,
    productsSupplied: row.products_supplied ?? 0,
    contactPerson: row.contact_person ?? "—",
    status: row.status === "inactive" || row.is_active === false ? "inactive" : "active",
  };
}

function mapWarehouse(row: {
  id: string;
  code: string;
  name: string;
  location?: string;
  sku_count?: number;
  total_units?: number;
}): AdminWarehouse {
  return {
    id: row.id,
    code: row.code,
    name: row.name,
    location: row.location ?? "—",
    skuCount: row.sku_count ?? 0,
    totalUnits: row.total_units ?? 0,
  };
}

function mapPurchaseOrder(row: {
  id: string;
  po_number: string;
  supplier_name: string;
  warehouse_code: string;
  status: string;
  total_ex_gst_cents: number;
  expected_at: string | null;
  created_at: string;
  lines?: Array<{
    id: string;
    sku: string;
    product_name: string;
    quantity_ordered: number;
    quantity_received: number;
    unit_cost_cents: number;
  }>;
}): AdminPurchaseOrder {
  return {
    id: row.id,
    poNumber: row.po_number,
    supplierName: row.supplier_name,
    warehouseCode: row.warehouse_code,
    status: row.status as AdminPurchaseOrder["status"],
    totalExGstCents: row.total_ex_gst_cents,
    expectedAt: row.expected_at,
    createdAt: row.created_at,
    lines: (row.lines ?? []).map((line) => ({
      id: line.id,
      sku: line.sku,
      productName: line.product_name,
      quantityOrdered: line.quantity_ordered,
      quantityReceived: line.quantity_received,
      unitCostCents: line.unit_cost_cents,
    })),
  };
}

export async function fetchAdminCategories(params?: {
  search?: string;
  status?: string;
  cursor?: string;
}): Promise<AdminCategory[]> {
  const response = await apiGet<Paginated<Record<string, unknown>>>(
    API_ENDPOINTS.admin.categories,
    { params }
  );
  return response.data.map((row) =>
    mapCategory(row as Parameters<typeof mapCategory>[0])
  );
}

export async function createAdminCategory(payload: {
  name: string;
  slug?: string;
  parent_id?: string;
  is_active?: boolean;
}): Promise<AdminCategory> {
  const row = await apiPost<Record<string, unknown>>(
    API_ENDPOINTS.admin.categories,
    payload
  );
  return mapCategory(row as Parameters<typeof mapCategory>[0]);
}

export async function updateAdminCategory(
  id: string,
  payload: Partial<{ name: string; slug: string; is_active: boolean }>
): Promise<AdminCategory> {
  const row = await apiPatch<Record<string, unknown>>(
    API_ENDPOINTS.admin.category(id),
    payload
  );
  return mapCategory(row as Parameters<typeof mapCategory>[0]);
}

export async function deactivateAdminCategory(id: string): Promise<void> {
  await apiDelete(API_ENDPOINTS.admin.category(id));
}

export async function fetchAdminBrands(params?: {
  search?: string;
  status?: string;
}): Promise<AdminBrand[]> {
  const response = await apiGet<Paginated<Record<string, unknown>>>(
    API_ENDPOINTS.admin.brands,
    { params }
  );
  return response.data.map((row) =>
    mapBrand(row as Parameters<typeof mapBrand>[0])
  );
}

export async function createAdminBrand(payload: {
  name: string;
  slug?: string;
  logo_url?: string;
  is_active?: boolean;
  featured?: boolean;
}): Promise<AdminBrand> {
  const row = await apiPost<Record<string, unknown>>(API_ENDPOINTS.admin.brands, {
    ...payload,
    is_authorized_reseller: payload.featured ?? true,
  });
  return mapBrand(row as Parameters<typeof mapBrand>[0]);
}

export async function updateAdminBrand(
  id: string,
  payload: Partial<{ name: string; logo_url: string; is_active: boolean; featured: boolean }>
): Promise<AdminBrand> {
  const row = await apiPatch<Record<string, unknown>>(API_ENDPOINTS.admin.brand(id), payload);
  return mapBrand(row as Parameters<typeof mapBrand>[0]);
}

export async function fetchAdminProductsList(params?: {
  search?: string;
  status?: string;
}): Promise<AdminProduct[]> {
  const response = await apiGet<Paginated<Record<string, unknown>>>(
    API_ENDPOINTS.admin.products,
    { params: { ...params, limit: 100 } }
  );
  return response.data.map((row) =>
    mapProduct(row as Parameters<typeof mapProduct>[0])
  );
}

export async function fetchAdminProduct(id: string): Promise<AdminProduct> {
  const row = await apiGet<Record<string, unknown>>(API_ENDPOINTS.admin.product(id));
  return mapProduct(row as Parameters<typeof mapProduct>[0]);
}

export async function createAdminProduct(
  payload: AdminProductWritePayload
): Promise<AdminProduct> {
  const row = await apiPost<Record<string, unknown>>(API_ENDPOINTS.admin.products, payload);
  return mapProduct(row as Parameters<typeof mapProduct>[0]);
}

export async function updateAdminProduct(
  id: string,
  payload: Partial<AdminProductWritePayload>
): Promise<AdminProduct> {
  const row = await apiPatch<Record<string, unknown>>(API_ENDPOINTS.admin.product(id), payload);
  return mapProduct(row as Parameters<typeof mapProduct>[0]);
}

export async function deleteAdminProduct(id: string): Promise<void> {
  await apiDelete(API_ENDPOINTS.admin.product(id));
}

export async function fetchAdminSuppliersList(params?: {
  search?: string;
  status?: string;
}): Promise<AdminSupplier[]> {
  const response = await apiGet<Paginated<Record<string, unknown>>>(
    API_ENDPOINTS.suppliers.admin,
    { params }
  );
  return response.data.map((row) =>
    mapSupplier(row as Parameters<typeof mapSupplier>[0])
  );
}

export async function createAdminSupplier(payload: {
  code: string;
  name: string;
  email?: string;
  phone?: string;
  contact_person?: string;
  is_active?: boolean;
}): Promise<AdminSupplier> {
  const row = await apiPost<Record<string, unknown>>(
    API_ENDPOINTS.suppliers.admin,
    payload
  );
  return mapSupplier(row as Parameters<typeof mapSupplier>[0]);
}

export async function updateAdminSupplier(
  id: string,
  payload: Partial<{
    name: string;
    email: string;
    phone: string;
    contact_person: string;
    is_active: boolean;
  }>
): Promise<AdminSupplier> {
  const row = await apiPatch<Record<string, unknown>>(
    API_ENDPOINTS.suppliers.adminDetail(id),
    payload
  );
  return mapSupplier(row as Parameters<typeof mapSupplier>[0]);
}

export async function fetchAdminWarehousesList(params?: {
  search?: string;
  status?: string;
}): Promise<AdminWarehouse[]> {
  const response = await apiGet<Paginated<Record<string, unknown>>>(
    API_ENDPOINTS.inventory.adminWarehouses,
    { params }
  );
  return response.data.map((row) =>
    mapWarehouse(row as Parameters<typeof mapWarehouse>[0])
  );
}

export async function createAdminWarehouse(payload: {
  code: string;
  name: string;
  warehouse_type?: string;
  suburb?: string;
  state?: string;
  postcode?: string;
  capacity_units?: number;
  is_active?: boolean;
}): Promise<AdminWarehouse> {
  const row = await apiPost<Record<string, unknown>>(
    API_ENDPOINTS.inventory.adminWarehouses,
    { warehouse_type: "distribution", ...payload }
  );
  return mapWarehouse(row as Parameters<typeof mapWarehouse>[0]);
}

export async function updateAdminWarehouse(
  id: string,
  payload: Partial<{
    name: string;
    suburb: string;
    state: string;
    postcode: string;
    capacity_units: number;
    is_active: boolean;
  }>
): Promise<AdminWarehouse> {
  const row = await apiPatch<Record<string, unknown>>(
    API_ENDPOINTS.inventory.adminWarehouse(id),
    payload
  );
  return mapWarehouse(row as Parameters<typeof mapWarehouse>[0]);
}

export async function fetchPurchaseOrders(params?: {
  status?: string;
}): Promise<AdminPurchaseOrder[]> {
  const response = await apiGet<Paginated<Record<string, unknown>>>(
    API_ENDPOINTS.suppliers.purchaseOrders,
    { params }
  );
  return response.data.map((row) =>
    mapPurchaseOrder(row as Parameters<typeof mapPurchaseOrder>[0])
  );
}

export async function createPurchaseOrder(
  payload: CreatePurchaseOrderPayload
): Promise<AdminPurchaseOrder> {
  const row = await apiPost<Record<string, unknown>>(
    API_ENDPOINTS.suppliers.purchaseOrders,
    {
      supplier_id: payload.supplierId,
      warehouse_code: payload.warehouseCode,
      lines: payload.lines.map((line) => ({
        sku: line.sku,
        quantity: line.quantity,
        unit_cost_cents: line.unitCostCents,
      })),
    }
  );
  return mapPurchaseOrder(row as Parameters<typeof mapPurchaseOrder>[0]);
}

export async function submitPurchaseOrder(poId: string): Promise<AdminPurchaseOrder> {
  const row = await apiPost<Record<string, unknown>>(
    API_ENDPOINTS.suppliers.purchaseOrderSubmit(poId)
  );
  return mapPurchaseOrder(row as Parameters<typeof mapPurchaseOrder>[0]);
}

export async function confirmPurchaseOrder(poId: string): Promise<AdminPurchaseOrder> {
  const row = await apiPost<Record<string, unknown>>(
    API_ENDPOINTS.suppliers.purchaseOrderConfirm(poId)
  );
  return mapPurchaseOrder(row as Parameters<typeof mapPurchaseOrder>[0]);
}

export async function receivePurchaseOrder(
  poId: string,
  receipts: { lineId: string; quantity: number }[]
): Promise<AdminPurchaseOrder> {
  const row = await apiPost<Record<string, unknown>>(
    API_ENDPOINTS.suppliers.purchaseOrderReceive(poId),
    {
      receipts: receipts.map((r) => ({
        line_id: r.lineId,
        quantity: r.quantity,
      })),
    }
  );
  return mapPurchaseOrder(row as Parameters<typeof mapPurchaseOrder>[0]);
}

export async function cancelPurchaseOrder(poId: string): Promise<AdminPurchaseOrder> {
  const row = await apiPost<Record<string, unknown>>(
    API_ENDPOINTS.suppliers.purchaseOrderCancel(poId)
  );
  return mapPurchaseOrder(row as Parameters<typeof mapPurchaseOrder>[0]);
}

export async function fetchTradeApplicationsList(params?: {
  status?: string;
}): Promise<TradeApplication[]> {
  const response = await apiGet<{ data: TradeApplication[] }>(
    API_ENDPOINTS.tradeAccounts.adminApplications,
    { params }
  );
  return response.data;
}

export async function reviewTradeApplication(
  id: string,
  payload: {
    status: TradeStatus;
    credit_limit_cents?: number;
    payment_terms_days?: number;
    notes?: string;
  }
): Promise<void> {
  await apiPost(API_ENDPOINTS.tradeAccounts.adminApplicationReview(id), payload);
}

export async function updateTradeCreditLimit(
  accountId: string,
  creditLimitCents: number
): Promise<void> {
  await apiPatch(API_ENDPOINTS.tradeAccounts.adminAccountCredit(accountId), {
    credit_limit_cents: creditLimitCents,
  });
}

export async function packOrder(orderId: string): Promise<void> {
  await apiPost(API_ENDPOINTS.orders.pack(orderId));
}

export async function shipOrder(
  orderId: string,
  payload?: { carrier?: string; tracking_number?: string }
): Promise<void> {
  await apiPost(API_ENDPOINTS.orders.ship(orderId), payload ?? {});
}

export async function deliverOrder(orderId: string): Promise<void> {
  await apiPost(API_ENDPOINTS.orders.deliver(orderId));
}

export async function cancelOrder(orderId: string, reason?: string): Promise<void> {
  await apiPost(API_ENDPOINTS.orders.cancel(orderId), { reason: reason ?? "" });
}

export async function refundOrder(orderId: string, reason?: string): Promise<void> {
  await apiPost(API_ENDPOINTS.orders.refund(orderId), { reason: reason ?? "" });
}

export async function fetchAdminReports(): Promise<ReportType[]> {
  const response = await apiGet<{ data: ReportType[] }>(API_ENDPOINTS.admin.reports);
  return response.data;
}

export async function exportAdminReport(
  reportId: string,
  format: "pdf" | "excel" | "csv"
): Promise<{ filename: string; content: string }> {
  return apiPost(API_ENDPOINTS.admin.reportsExport, {
    report_id: reportId,
    format,
  });
}
