"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { createAdminLiveQueryOptions } from "./admin-query-options";
import {
  addQuoteLine,
  approveQuote,
  convertQuote,
  createQuote,
  fetchQuoteDetail,
  fetchQuotes,
  fetchQuotesDashboard,
  rejectQuote,
  sendQuote,
  submitQuote,
  updateQuote,
} from "./quotes-service";

export const quotesQueryKeys = {
  all: ["quotes"] as const,
  dashboard: () => [...quotesQueryKeys.all, "dashboard"] as const,
  list: (params?: object) => [...quotesQueryKeys.all, "list", params ?? {}] as const,
  detail: (id: string) => [...quotesQueryKeys.all, "detail", id] as const,
};

export function useQuotesDashboard() {
  return useQuery(
    createAdminLiveQueryOptions("quotes-dashboard", quotesQueryKeys.dashboard(), fetchQuotesDashboard)
  );
}

export function useQuotes(params?: { status?: string; search?: string }) {
  return useQuery(
    createAdminLiveQueryOptions("quotes-list", quotesQueryKeys.list(params), () => fetchQuotes(params))
  );
}

export function useQuoteDetail(id: string) {
  return useQuery({
    ...createAdminLiveQueryOptions("quotes-detail", quotesQueryKeys.detail(id), () =>
      fetchQuoteDetail(id)
    ),
    enabled: Boolean(id),
  });
}

export function useCreateQuote() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: createQuote,
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: quotesQueryKeys.all });
    },
  });
}

export function useUpdateQuote() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, ...payload }: { id: string; notes?: string; discountCents?: number }) =>
      updateQuote(id, payload),
    onSuccess: (_data, vars) => {
      void qc.invalidateQueries({ queryKey: quotesQueryKeys.detail(vars.id) });
      void qc.invalidateQueries({ queryKey: quotesQueryKeys.all });
    },
  });
}

export function useAddQuoteLine() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({
      quoteId,
      ...payload
    }: {
      quoteId: string;
      variantId: string;
      quantity: number;
      unitPriceExGstCents?: number;
    }) => addQuoteLine(quoteId, payload),
    onSuccess: (_data, vars) => {
      void qc.invalidateQueries({ queryKey: quotesQueryKeys.detail(vars.quoteId) });
      void qc.invalidateQueries({ queryKey: quotesQueryKeys.all });
    },
  });
}

export function useSubmitQuote() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: submitQuote,
    onSuccess: (_data, id) => {
      void qc.invalidateQueries({ queryKey: quotesQueryKeys.detail(id) });
      void qc.invalidateQueries({ queryKey: quotesQueryKeys.all });
    },
  });
}

export function useApproveQuote() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, comment }: { id: string; comment?: string }) => approveQuote(id, comment),
    onSuccess: (_data, vars) => {
      void qc.invalidateQueries({ queryKey: quotesQueryKeys.detail(vars.id) });
      void qc.invalidateQueries({ queryKey: quotesQueryKeys.all });
    },
  });
}

export function useRejectQuote() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, comment }: { id: string; comment?: string }) => rejectQuote(id, comment),
    onSuccess: (_data, vars) => {
      void qc.invalidateQueries({ queryKey: quotesQueryKeys.detail(vars.id) });
      void qc.invalidateQueries({ queryKey: quotesQueryKeys.all });
    },
  });
}

export function useSendQuote() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: sendQuote,
    onSuccess: (_data, id) => {
      void qc.invalidateQueries({ queryKey: quotesQueryKeys.detail(id) });
      void qc.invalidateQueries({ queryKey: quotesQueryKeys.all });
    },
  });
}

export function useConvertQuote() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: convertQuote,
    onSuccess: (_data, id) => {
      void qc.invalidateQueries({ queryKey: quotesQueryKeys.detail(id) });
      void qc.invalidateQueries({ queryKey: quotesQueryKeys.all });
    },
  });
}
