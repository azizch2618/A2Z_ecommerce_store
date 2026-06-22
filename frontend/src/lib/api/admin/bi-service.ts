import { apiGet, apiPost } from "../client";
import { API_ENDPOINTS } from "../config";
import type {
  BiSnapshot,
  ExecutiveSnapshot,
  FinanceAnalytics,
  HrAnalytics,
  InventoryAnalytics,
  KpiEvaluation,
  ProcurementAnalytics,
  SalesAnalytics,
  ScheduledReport,
} from "./bi-types";

function unwrapList<T>(payload: { data?: T[] } | T[]): T[] {
  if (Array.isArray(payload)) return payload;
  return payload.data ?? [];
}

export async function fetchExecutiveSnapshot(): Promise<ExecutiveSnapshot> {
  return apiGet<ExecutiveSnapshot>(API_ENDPOINTS.admin.bi.executive);
}

export async function fetchSalesAnalytics(): Promise<SalesAnalytics> {
  return apiGet<SalesAnalytics>(API_ENDPOINTS.admin.bi.sales);
}

export async function fetchInventoryAnalytics(): Promise<InventoryAnalytics> {
  return apiGet<InventoryAnalytics>(API_ENDPOINTS.admin.bi.inventory);
}

export async function fetchProcurementAnalytics(): Promise<ProcurementAnalytics> {
  return apiGet<ProcurementAnalytics>(API_ENDPOINTS.admin.bi.procurement);
}

export async function fetchFinanceAnalytics(): Promise<FinanceAnalytics> {
  return apiGet<FinanceAnalytics>(API_ENDPOINTS.admin.bi.finance);
}

export async function fetchHrAnalytics(): Promise<HrAnalytics> {
  return apiGet<HrAnalytics>(API_ENDPOINTS.admin.bi.hr);
}

export async function fetchBiSnapshot(): Promise<BiSnapshot> {
  return apiGet<BiSnapshot>(API_ENDPOINTS.admin.bi.snapshot);
}

export async function fetchKpiEvaluations(): Promise<KpiEvaluation[]> {
  const payload = await apiGet<{ data: KpiEvaluation[] }>(API_ENDPOINTS.admin.bi.kpisEvaluate);
  return unwrapList(payload);
}

export async function fetchScheduledReports(): Promise<ScheduledReport[]> {
  const payload = await apiGet<{ data: ScheduledReport[] }>(API_ENDPOINTS.admin.bi.schedules);
  return unwrapList(payload);
}

export async function createScheduledReport(payload: {
  name: string;
  reportId: string;
  format?: string;
  frequency?: string;
  recipientEmails: string[];
}): Promise<{ id: string; name: string; nextRunAt: string | null }> {
  return apiPost(API_ENDPOINTS.admin.bi.schedules, payload);
}

export async function exportBiReport(payload: {
  reportId: string;
  format: "csv" | "excel" | "pdf";
}): Promise<{
  filename: string;
  content: string;
  mimeType: string;
  encoding?: string;
}> {
  return apiPost(API_ENDPOINTS.admin.bi.reportsExport, payload);
}
