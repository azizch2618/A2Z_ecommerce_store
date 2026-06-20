import { apiGet, apiPost } from "../client";
import { API_BASE_URL, API_ENDPOINTS } from "../config";
import type {
  GoodsReceipt,
  ProcurementDashboardKpis,
  PurchaseRequest,
  SupplierDocument,
  SupplierPerformanceKpis,
  SupplierPortalPo,
} from "./procurement-types";

function unwrapList<T>(payload: { data?: T[] } | T[]): T[] {
  if (Array.isArray(payload)) return payload;
  return payload.data ?? [];
}

export async function fetchProcurementDashboard(): Promise<ProcurementDashboardKpis> {
  return apiGet<ProcurementDashboardKpis>(API_ENDPOINTS.procurement.dashboard);
}

export async function fetchPurchaseRequests(params?: {
  status?: string;
  search?: string;
}): Promise<PurchaseRequest[]> {
  const rows = await apiGet<{ data: PurchaseRequest[] }>(
    API_ENDPOINTS.procurement.requests,
    { params }
  );
  return unwrapList(rows);
}

export async function fetchPurchaseRequestDetail(id: string): Promise<PurchaseRequest> {
  return apiGet<PurchaseRequest>(API_ENDPOINTS.procurement.request(id));
}

export async function createPurchaseRequest(payload: {
  warehouseCode?: string;
  supplierId?: string;
  departmentId?: string;
  costCenterId?: string;
  priority?: string;
  justification?: string;
}): Promise<PurchaseRequest> {
  return apiPost<PurchaseRequest>(API_ENDPOINTS.procurement.requests, payload);
}

export async function addPurchaseRequestLine(
  requestId: string,
  payload: { sku: string; quantity: number; unitCostCents?: number; notes?: string }
): Promise<PurchaseRequest> {
  return apiPost<PurchaseRequest>(API_ENDPOINTS.procurement.requestLines(requestId), payload);
}

export async function submitPurchaseRequest(id: string): Promise<PurchaseRequest> {
  return apiPost<PurchaseRequest>(API_ENDPOINTS.procurement.requestSubmit(id), {});
}

export async function approvePurchaseRequest(
  id: string,
  comment?: string
): Promise<PurchaseRequest> {
  return apiPost<PurchaseRequest>(API_ENDPOINTS.procurement.requestApprove(id), {
    comment: comment ?? "",
  });
}

export async function rejectPurchaseRequest(
  id: string,
  comment?: string
): Promise<PurchaseRequest> {
  return apiPost<PurchaseRequest>(API_ENDPOINTS.procurement.requestReject(id), {
    comment: comment ?? "",
  });
}

export async function convertPurchaseRequest(id: string): Promise<{
  poId: string;
  poNumber: string;
  request: PurchaseRequest;
}> {
  return apiPost(API_ENDPOINTS.procurement.requestConvert(id), {});
}

export async function fetchGoodsReceipts(): Promise<GoodsReceipt[]> {
  const rows = await apiGet<{ data: GoodsReceipt[] }>(API_ENDPOINTS.procurement.goodsReceipts);
  return unwrapList(rows);
}

export async function fetchSupplierPerformance(supplierId: string): Promise<SupplierPerformanceKpis> {
  return apiGet<SupplierPerformanceKpis>(
    API_ENDPOINTS.procurement.supplierPerformance(supplierId)
  );
}

export async function fetchSupplierPortalDashboard(): Promise<SupplierPerformanceKpis> {
  return apiGet<SupplierPerformanceKpis>(API_ENDPOINTS.procurement.portalDashboard);
}

export async function fetchSupplierPortalPos(params?: {
  status?: string;
}): Promise<SupplierPortalPo[]> {
  const rows = await apiGet<{ data: SupplierPortalPo[] }>(
    API_ENDPOINTS.procurement.portalPurchaseOrders,
    { params }
  );
  return unwrapList(rows);
}

export async function fetchSupplierPortalPoDetail(id: string): Promise<SupplierPortalPo> {
  return apiGet<SupplierPortalPo>(API_ENDPOINTS.procurement.portalPurchaseOrder(id));
}

export async function acknowledgeSupplierPo(id: string): Promise<SupplierPortalPo> {
  return apiPost<SupplierPortalPo>(API_ENDPOINTS.procurement.portalAcknowledge(id), {});
}

export async function updateSupplierPoExpectedDelivery(
  id: string,
  expectedAt: string
): Promise<SupplierPortalPo> {
  return apiPost<SupplierPortalPo>(API_ENDPOINTS.procurement.portalExpectedDelivery(id), {
    expectedAt,
  });
}

export async function fetchSupplierPoPaymentStatus(id: string): Promise<{
  poNumber: string;
  paymentStatus: string;
  totalExGstCents: number;
  termsDays: number;
}> {
  return apiGet(API_ENDPOINTS.procurement.portalPaymentStatus(id));
}

export async function fetchSupplierDocuments(): Promise<SupplierDocument[]> {
  const rows = await apiGet<{ data: SupplierDocument[] }>(
    API_ENDPOINTS.procurement.portalDocuments
  );
  return unwrapList(rows);
}

export async function uploadSupplierDocument(payload: {
  file: File;
  documentType?: string;
  poId?: string;
  notes?: string;
}): Promise<SupplierDocument> {
  const form = new FormData();
  form.append("file", payload.file);
  if (payload.documentType) form.append("documentType", payload.documentType);
  if (payload.poId) form.append("poId", payload.poId);
  if (payload.notes) form.append("notes", payload.notes);

  const token =
    typeof window !== "undefined"
      ? localStorage.getItem("a2z_access_token")
      : null;

  const response = await fetch(
    `${API_BASE_URL}${API_ENDPOINTS.procurement.portalDocumentUpload}`,
    {
      method: "POST",
      headers: token ? { Authorization: `Bearer ${token}` } : {},
      body: form,
    }
  );
  if (!response.ok) {
    throw new Error("Document upload failed");
  }
  return response.json() as Promise<SupplierDocument>;
}
