"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { createAdminLiveQueryOptions } from "./admin-query-options";
import { hasAuthTokens } from "../auth/token-storage";
import { withAdminApiLog } from "./log-admin-api-error";
import {
  convertCrmLead,
  createCrmActivity,
  createCrmLead,
  createCrmNote,
  createCrmOpportunity,
  fetchCrmDashboard,
  fetchCrmLeadDetail,
  fetchCrmLeads,
  fetchCrmMeta,
  fetchCrmOpportunities,
  fetchCrmOpportunityDetail,
  fetchCrmPipeline,
  fetchCrmTimeline,
  moveCrmPipelineLead,
  updateCrmLead,
  updateCrmOpportunity,
} from "./crm-service";

export const crmQueryKeys = {
  all: ["crm"] as const,
  dashboard: () => [...crmQueryKeys.all, "dashboard"] as const,
  leads: (params?: object) => [...crmQueryKeys.all, "leads", params ?? {}] as const,
  leadDetail: (id: string) => [...crmQueryKeys.all, "lead", id] as const,
  opportunities: (params?: object) => [...crmQueryKeys.all, "opportunities", params ?? {}] as const,
  opportunityDetail: (id: string) => [...crmQueryKeys.all, "opportunity", id] as const,
  pipeline: () => [...crmQueryKeys.all, "pipeline"] as const,
  timeline: (params: object) => [...crmQueryKeys.all, "timeline", params] as const,
  meta: () => [...crmQueryKeys.all, "meta"] as const,
};

export function useCrmDashboard() {
  return useQuery(
    createAdminLiveQueryOptions("crm-dashboard", crmQueryKeys.dashboard(), fetchCrmDashboard)
  );
}

export function useCrmLeads(params?: { status?: string; search?: string }) {
  return useQuery(
    createAdminLiveQueryOptions("crm-leads", crmQueryKeys.leads(params), () => fetchCrmLeads(params))
  );
}

export function useCrmLeadDetail(id: string) {
  return useQuery({
    queryKey: crmQueryKeys.leadDetail(id),
    queryFn: () => withAdminApiLog("crm-lead-detail", () => fetchCrmLeadDetail(id)),
    enabled: hasAuthTokens() && Boolean(id),
    retry: false as const,
    staleTime: 30_000,
  });
}

export function useCrmOpportunities(params?: { status?: string; search?: string }) {
  return useQuery(
    createAdminLiveQueryOptions(
      "crm-opportunities",
      crmQueryKeys.opportunities(params),
      () => fetchCrmOpportunities(params)
    )
  );
}

export function useCrmOpportunityDetail(id: string) {
  return useQuery({
    queryKey: crmQueryKeys.opportunityDetail(id),
    queryFn: () => withAdminApiLog("crm-opportunity-detail", () => fetchCrmOpportunityDetail(id)),
    enabled: hasAuthTokens() && Boolean(id),
    retry: false as const,
    staleTime: 30_000,
  });
}

export function useCrmPipeline() {
  return useQuery(
    createAdminLiveQueryOptions("crm-pipeline", crmQueryKeys.pipeline(), fetchCrmPipeline)
  );
}

export function useCrmTimeline(params: { leadId?: string; opportunityId?: string }) {
  const enabled = hasAuthTokens() && Boolean(params.leadId || params.opportunityId);
  return useQuery({
    queryKey: crmQueryKeys.timeline(params),
    queryFn: () => withAdminApiLog("crm-timeline", () => fetchCrmTimeline(params)),
    enabled,
    retry: false as const,
    staleTime: 30_000,
  });
}

export function useCrmMeta() {
  return useQuery(
    createAdminLiveQueryOptions("crm-meta", crmQueryKeys.meta(), fetchCrmMeta)
  );
}

export function useMoveCrmPipelineLead() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: moveCrmPipelineLead,
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: crmQueryKeys.all });
    },
  });
}

export function useCreateCrmLead() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: createCrmLead,
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: crmQueryKeys.all });
    },
  });
}

export function useUpdateCrmLead() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, ...payload }: { id: string; status?: string; assignedToId?: string }) =>
      updateCrmLead(id, payload),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: crmQueryKeys.all });
    },
  });
}

export function useConvertCrmLead() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, ...payload }: { id: string; name?: string; expectedRevenueCents?: number }) =>
      convertCrmLead(id, payload),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: crmQueryKeys.all });
    },
  });
}

export function useCreateCrmOpportunity() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: createCrmOpportunity,
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: crmQueryKeys.all });
    },
  });
}

export function useUpdateCrmOpportunity() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({
      id,
      ...payload
    }: {
      id: string;
      status?: string;
      stage?: string;
      probability?: number;
      expectedRevenueCents?: number;
    }) => updateCrmOpportunity(id, payload),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: crmQueryKeys.all });
    },
  });
}

export function useCreateCrmNote() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: createCrmNote,
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: crmQueryKeys.all });
    },
  });
}

export function useCreateCrmActivity() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: createCrmActivity,
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: crmQueryKeys.all });
    },
  });
}
