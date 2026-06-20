import { apiGet, apiPatch, apiPost } from "../client";
import { API_ENDPOINTS } from "../config";
import type {
  CrmDashboardKpis,
  CrmLead,
  CrmLeadDetail,
  CrmOpportunity,
  CrmOpportunityDetail,
  CrmPipelineColumns,
  CrmTimelineEntry,
} from "./types";

function unwrapList<T>(payload: { data?: T[] } | T[]): T[] {
  if (Array.isArray(payload)) return payload;
  return payload.data ?? [];
}

export async function fetchCrmDashboard(): Promise<CrmDashboardKpis> {
  return apiGet<CrmDashboardKpis>(API_ENDPOINTS.crm.dashboard);
}

export async function fetchCrmLeads(params?: {
  status?: string;
  search?: string;
}): Promise<CrmLead[]> {
  const rows = await apiGet<{ data: CrmLead[] }>(API_ENDPOINTS.crm.leads, { params });
  return unwrapList(rows);
}

export async function fetchCrmLeadDetail(id: string): Promise<CrmLeadDetail> {
  return apiGet<CrmLeadDetail>(API_ENDPOINTS.crm.lead(id));
}

export async function fetchCrmOpportunities(params?: {
  status?: string;
  search?: string;
}): Promise<CrmOpportunity[]> {
  const rows = await apiGet<{ data: CrmOpportunity[] }>(API_ENDPOINTS.crm.opportunities, {
    params,
  });
  return unwrapList(rows);
}

export async function fetchCrmOpportunityDetail(id: string): Promise<CrmOpportunityDetail> {
  return apiGet<CrmOpportunityDetail>(API_ENDPOINTS.crm.opportunity(id));
}

export async function fetchCrmPipeline(): Promise<CrmPipelineColumns> {
  const res = await apiGet<{ columns: CrmPipelineColumns }>(API_ENDPOINTS.crm.pipeline);
  return res.columns;
}

export async function moveCrmPipelineLead(payload: {
  leadId: string;
  status: string;
}): Promise<CrmLead> {
  return apiPatch<CrmLead>(API_ENDPOINTS.crm.pipeline, payload);
}

export async function fetchCrmTimeline(params: {
  leadId?: string;
  opportunityId?: string;
}): Promise<CrmTimelineEntry[]> {
  const rows = await apiGet<{ data: CrmTimelineEntry[] }>(API_ENDPOINTS.crm.timeline, {
    params,
  });
  return unwrapList(rows);
}

export async function createCrmLead(payload: {
  title: string;
  companyName?: string;
  contactName?: string;
  contactEmail?: string;
  contactPhone?: string;
  source?: string;
  status?: string;
  assignedToId?: string;
}): Promise<CrmLead> {
  return apiPost<CrmLead>(API_ENDPOINTS.crm.leads, payload);
}

export async function updateCrmLead(
  id: string,
  payload: Partial<{
    title: string;
    companyName: string;
    status: string;
    assignedToId: string;
  }>
): Promise<CrmLead> {
  return apiPatch<CrmLead>(API_ENDPOINTS.crm.lead(id), payload);
}

export async function createCrmOpportunity(payload: {
  name: string;
  partyId?: string;
  leadId?: string;
  customerId?: string;
  expectedRevenueCents?: number;
  probability?: number;
  expectedCloseDate?: string;
}): Promise<CrmOpportunity> {
  return apiPost<CrmOpportunity>(API_ENDPOINTS.crm.opportunities, payload);
}

export async function updateCrmOpportunity(
  id: string,
  payload: Partial<{
    name: string;
    stage: string;
    status: string;
    expectedRevenueCents: number;
    probability: number;
    expectedCloseDate: string;
  }>
): Promise<CrmOpportunity> {
  return apiPatch<CrmOpportunity>(API_ENDPOINTS.crm.opportunity(id), payload);
}

export async function convertCrmLead(
  id: string,
  payload: {
    name?: string;
    expectedRevenueCents?: number;
    probability?: number;
  }
): Promise<CrmOpportunity> {
  return apiPost<CrmOpportunity>(API_ENDPOINTS.crm.leadConvert(id), payload);
}

export async function createCrmNote(payload: {
  body: string;
  leadId?: string;
  opportunityId?: string;
}): Promise<{ id: string; body: string; createdAt: string }> {
  return apiPost(API_ENDPOINTS.crm.notes, payload);
}

export async function createCrmActivity(payload: {
  activityType: string;
  subject: string;
  description?: string;
  leadId?: string;
  opportunityId?: string;
  scheduledAt?: string;
}): Promise<{ id: string }> {
  return apiPost(API_ENDPOINTS.crm.activities, payload);
}

export async function fetchCrmMeta(): Promise<{
  activityTypes: { value: string; label: string }[];
}> {
  return apiGet(API_ENDPOINTS.crm.meta);
}
