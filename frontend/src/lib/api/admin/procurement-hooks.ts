"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { createAdminLiveQueryOptions } from "./admin-query-options";
import {
  acknowledgeSupplierPo,
  addPurchaseRequestLine,
  approvePurchaseRequest,
  convertPurchaseRequest,
  createPurchaseRequest,
  fetchGoodsReceipts,
  fetchProcurementDashboard,
  fetchPurchaseRequestDetail,
  fetchPurchaseRequests,
  fetchSupplierDocuments,
  fetchSupplierPerformance,
  fetchSupplierPortalDashboard,
  fetchSupplierPortalPoDetail,
  fetchSupplierPortalPos,
  fetchSupplierPoPaymentStatus,
  rejectPurchaseRequest,
  submitPurchaseRequest,
  updateSupplierPoExpectedDelivery,
  uploadSupplierDocument,
} from "./procurement-service";

export const procurementQueryKeys = {
  all: ["procurement"] as const,
  dashboard: () => [...procurementQueryKeys.all, "dashboard"] as const,
  requests: (params?: object) =>
    [...procurementQueryKeys.all, "requests", params ?? {}] as const,
  request: (id: string) => [...procurementQueryKeys.all, "request", id] as const,
  goodsReceipts: () => [...procurementQueryKeys.all, "goods-receipts"] as const,
  supplierPerformance: (id: string) =>
    [...procurementQueryKeys.all, "supplier-performance", id] as const,
  portal: {
    all: ["supplier-portal"] as const,
    dashboard: () => [...procurementQueryKeys.portal.all, "dashboard"] as const,
    pos: (params?: object) =>
      [...procurementQueryKeys.portal.all, "pos", params ?? {}] as const,
    po: (id: string) => [...procurementQueryKeys.portal.all, "po", id] as const,
    documents: () => [...procurementQueryKeys.portal.all, "documents"] as const,
  },
};

export function useProcurementDashboard() {
  return useQuery(
    createAdminLiveQueryOptions(
      "procurement-dashboard",
      procurementQueryKeys.dashboard(),
      fetchProcurementDashboard
    )
  );
}

export function usePurchaseRequests(params?: { status?: string; search?: string }) {
  return useQuery(
    createAdminLiveQueryOptions(
      "procurement-requests",
      procurementQueryKeys.requests(params),
      () => fetchPurchaseRequests(params)
    )
  );
}

export function usePurchaseRequestDetail(id: string) {
  return useQuery({
    ...createAdminLiveQueryOptions(
      "procurement-request-detail",
      procurementQueryKeys.request(id),
      () => fetchPurchaseRequestDetail(id)
    ),
    enabled: Boolean(id),
  });
}

export function useCreatePurchaseRequest() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: createPurchaseRequest,
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: procurementQueryKeys.all });
    },
  });
}

export function useAddPurchaseRequestLine() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({
      requestId,
      ...payload
    }: {
      requestId: string;
      sku: string;
      quantity: number;
      unitCostCents?: number;
    }) => addPurchaseRequestLine(requestId, payload),
    onSuccess: (_data, vars) => {
      void qc.invalidateQueries({ queryKey: procurementQueryKeys.request(vars.requestId) });
      void qc.invalidateQueries({ queryKey: procurementQueryKeys.all });
    },
  });
}

export function useSubmitPurchaseRequest() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: submitPurchaseRequest,
    onSuccess: (_data, id) => {
      void qc.invalidateQueries({ queryKey: procurementQueryKeys.request(id) });
      void qc.invalidateQueries({ queryKey: procurementQueryKeys.all });
    },
  });
}

export function useApprovePurchaseRequest() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, comment }: { id: string; comment?: string }) =>
      approvePurchaseRequest(id, comment),
    onSuccess: (_data, vars) => {
      void qc.invalidateQueries({ queryKey: procurementQueryKeys.request(vars.id) });
      void qc.invalidateQueries({ queryKey: procurementQueryKeys.all });
    },
  });
}

export function useRejectPurchaseRequest() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, comment }: { id: string; comment?: string }) =>
      rejectPurchaseRequest(id, comment),
    onSuccess: (_data, vars) => {
      void qc.invalidateQueries({ queryKey: procurementQueryKeys.request(vars.id) });
      void qc.invalidateQueries({ queryKey: procurementQueryKeys.all });
    },
  });
}

export function useConvertPurchaseRequest() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: convertPurchaseRequest,
    onSuccess: (_data, id) => {
      void qc.invalidateQueries({ queryKey: procurementQueryKeys.request(id) });
      void qc.invalidateQueries({ queryKey: procurementQueryKeys.all });
    },
  });
}

export function useGoodsReceipts() {
  return useQuery(
    createAdminLiveQueryOptions(
      "goods-receipts",
      procurementQueryKeys.goodsReceipts(),
      fetchGoodsReceipts
    )
  );
}

export function useSupplierPerformance(supplierId: string) {
  return useQuery({
    ...createAdminLiveQueryOptions(
      "supplier-performance",
      procurementQueryKeys.supplierPerformance(supplierId),
      () => fetchSupplierPerformance(supplierId)
    ),
    enabled: Boolean(supplierId),
  });
}

export function useSupplierPortalDashboard() {
  return useQuery({
    queryKey: procurementQueryKeys.portal.dashboard(),
    queryFn: fetchSupplierPortalDashboard,
  });
}

export function useSupplierPortalPos(params?: { status?: string }) {
  return useQuery({
    queryKey: procurementQueryKeys.portal.pos(params),
    queryFn: () => fetchSupplierPortalPos(params),
  });
}

export function useSupplierPortalPoDetail(id: string) {
  return useQuery({
    queryKey: procurementQueryKeys.portal.po(id),
    queryFn: () => fetchSupplierPortalPoDetail(id),
    enabled: Boolean(id),
  });
}

export function useAcknowledgeSupplierPo() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: acknowledgeSupplierPo,
    onSuccess: (_data, id) => {
      void qc.invalidateQueries({ queryKey: procurementQueryKeys.portal.po(id) });
      void qc.invalidateQueries({ queryKey: procurementQueryKeys.portal.all });
    },
  });
}

export function useUpdateSupplierPoExpectedDelivery() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, expectedAt }: { id: string; expectedAt: string }) =>
      updateSupplierPoExpectedDelivery(id, expectedAt),
    onSuccess: (_data, vars) => {
      void qc.invalidateQueries({ queryKey: procurementQueryKeys.portal.po(vars.id) });
      void qc.invalidateQueries({ queryKey: procurementQueryKeys.portal.all });
    },
  });
}

export function useSupplierPoPaymentStatus(poId: string) {
  return useQuery({
    queryKey: [...procurementQueryKeys.portal.all, "payment", poId],
    queryFn: () => fetchSupplierPoPaymentStatus(poId),
    enabled: Boolean(poId),
  });
}

export function useSupplierDocuments() {
  return useQuery({
    queryKey: procurementQueryKeys.portal.documents(),
    queryFn: fetchSupplierDocuments,
  });
}

export function useUploadSupplierDocument() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: uploadSupplierDocument,
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: procurementQueryKeys.portal.documents() });
    },
  });
}
