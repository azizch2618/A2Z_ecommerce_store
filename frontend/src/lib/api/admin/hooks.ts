"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { createAdminLiveQueryOptions } from "./admin-query-options";
import {
  fetchAdminCustomers,
  fetchAdminDashboard,
  fetchAdminOrders,
  fetchAdminProducts,
  fetchRevenueByPeriod,
} from "./api-service";
import {
  cancelOrder,
  cancelPurchaseOrder,
  confirmPurchaseOrder,
  createAdminBrand,
  createAdminCategory,
  createAdminSupplier,
  createAdminWarehouse,
  createPurchaseOrder,
  deliverOrder,
  exportAdminReport,
  fetchAdminBrands,
  fetchAdminCategories,
  fetchAdminReports,
  fetchAdminSuppliersList,
  fetchAdminWarehousesList,
  fetchPurchaseOrders,
  fetchTradeApplicationsList,
  packOrder,
  receivePurchaseOrder,
  refundOrder,
  reviewTradeApplication,
  shipOrder,
  submitPurchaseOrder,
  updateAdminBrand,
  updateAdminCategory,
  updateAdminSupplier,
  updateAdminWarehouse,
} from "./operational-service";
import type {
  AdminBrand,
  AdminCategory,
  AdminPurchaseOrder,
  AdminWarehouse,
  CompanySettings,
  CreatePurchaseOrderPayload,
  EmailSettings,
  GstSettings,
  InventoryRow,
  LowStockAlert,
  PaymentGatewaySettings,
  ReportType,
  RevenuePeriod,
  ShippingSettings,
  StockAdjustmentPayload,
  StockInPayload,
  StockMovementRecord,
  StockOutPayload,
  StockTransferPayload,
  TradeStatus,
} from "./types";
import { throwAdminApiUnavailable } from "./admin-api-unavailable";

export const adminQueryKeys = {
  all: ["admin"] as const,
  dashboard: () => [...adminQueryKeys.all, "dashboard"] as const,
  products: () => [...adminQueryKeys.all, "products"] as const,
  categories: (params?: object) => [...adminQueryKeys.all, "categories", params ?? {}] as const,
  brands: (params?: object) => [...adminQueryKeys.all, "brands", params ?? {}] as const,
  inventory: () => [...adminQueryKeys.all, "inventory"] as const,
  lowStockAlerts: () => [...adminQueryKeys.all, "low-stock-alerts"] as const,
  stockMovements: () => [...adminQueryKeys.all, "stock-movements"] as const,
  purchaseOrders: (params?: object) =>
    [...adminQueryKeys.all, "purchase-orders", params ?? {}] as const,
  warehouses: (params?: object) => [...adminQueryKeys.all, "warehouses", params ?? {}] as const,
  orders: () => [...adminQueryKeys.all, "orders"] as const,
  customers: () => [...adminQueryKeys.all, "customers"] as const,
  tradeApplications: (params?: object) =>
    [...adminQueryKeys.all, "trade-applications", params ?? {}] as const,
  suppliers: (params?: object) => [...adminQueryKeys.all, "suppliers", params ?? {}] as const,
  revenue: (period: RevenuePeriod) => [...adminQueryKeys.all, "revenue", period] as const,
  reports: () => [...adminQueryKeys.all, "reports"] as const,
  settings: {
    company: () => [...adminQueryKeys.all, "settings", "company"] as const,
    gst: () => [...adminQueryKeys.all, "settings", "gst"] as const,
    shipping: () => [...adminQueryKeys.all, "settings", "shipping"] as const,
    email: () => [...adminQueryKeys.all, "settings", "email"] as const,
    payment: () => [...adminQueryKeys.all, "settings", "payment"] as const,
  },
};

export function useAdminDashboard() {
  return useQuery(
    createAdminLiveQueryOptions(
      "dashboard",
      adminQueryKeys.dashboard(),
      fetchAdminDashboard
    )
  );
}

export function useAdminProducts() {
  return useQuery(
    createAdminLiveQueryOptions(
      "products",
      adminQueryKeys.products(),
      fetchAdminProducts
    )
  );
}

export function useAdminCategories(params?: { search?: string; status?: string }) {
  return useQuery(
    createAdminLiveQueryOptions<AdminCategory[]>(
      "categories",
      adminQueryKeys.categories(params),
      () => fetchAdminCategories(params)
    )
  );
}

export function useCreateCategory() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: createAdminCategory,
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: [...adminQueryKeys.all, "categories"] });
    },
  });
}

export function useUpdateCategory() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, ...payload }: { id: string; name?: string; is_active?: boolean }) =>
      updateAdminCategory(id, payload),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: [...adminQueryKeys.all, "categories"] });
    },
  });
}

export function useAdminBrands(params?: { search?: string; status?: string }) {
  return useQuery(
    createAdminLiveQueryOptions<AdminBrand[]>(
      "brands",
      adminQueryKeys.brands(params),
      () => fetchAdminBrands(params)
    )
  );
}

export function useCreateBrand() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: createAdminBrand,
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: [...adminQueryKeys.all, "brands"] });
    },
  });
}

export function useUpdateBrand() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({
      id,
      ...payload
    }: {
      id: string;
      name?: string;
      logo_url?: string;
      is_active?: boolean;
      featured?: boolean;
    }) => updateAdminBrand(id, payload),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: [...adminQueryKeys.all, "brands"] });
    },
  });
}

export function useAdminInventory() {
  return useQuery(
    createAdminLiveQueryOptions<InventoryRow[]>(
      "inventory",
      adminQueryKeys.inventory(),
      () => throwAdminApiUnavailable("inventory levels")
    )
  );
}

export function useAdminWarehouses(params?: { search?: string; status?: string }) {
  return useQuery(
    createAdminLiveQueryOptions<AdminWarehouse[]>(
      "warehouses",
      adminQueryKeys.warehouses(params),
      () => fetchAdminWarehousesList(params)
    )
  );
}

export function useCreateWarehouse() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: createAdminWarehouse,
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: [...adminQueryKeys.all, "warehouses"] });
    },
  });
}

export function useUpdateWarehouse() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({
      id,
      ...payload
    }: {
      id: string;
      name?: string;
      capacity_units?: number;
      is_active?: boolean;
    }) => updateAdminWarehouse(id, payload),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: [...adminQueryKeys.all, "warehouses"] });
    },
  });
}

export function useLowStockAlerts() {
  return useQuery(
    createAdminLiveQueryOptions<LowStockAlert[]>(
      "low-stock-alerts",
      adminQueryKeys.lowStockAlerts(),
      () => throwAdminApiUnavailable("low stock alerts")
    )
  );
}

export function useStockMovements() {
  return useQuery(
    createAdminLiveQueryOptions<StockMovementRecord[]>(
      "stock-movements",
      adminQueryKeys.stockMovements(),
      () => throwAdminApiUnavailable("stock movements")
    )
  );
}

export function usePurchaseOrders(params?: { status?: string }) {
  return useQuery(
    createAdminLiveQueryOptions<AdminPurchaseOrder[]>(
      "purchase-orders",
      adminQueryKeys.purchaseOrders(params),
      () => fetchPurchaseOrders(params)
    )
  );
}

function useInvalidateWms() {
  const queryClient = useQueryClient();
  return () => {
    void queryClient.invalidateQueries({ queryKey: adminQueryKeys.inventory() });
    void queryClient.invalidateQueries({ queryKey: adminQueryKeys.lowStockAlerts() });
    void queryClient.invalidateQueries({ queryKey: adminQueryKeys.stockMovements() });
    void queryClient.invalidateQueries({ queryKey: [...adminQueryKeys.all, "purchase-orders"] });
    void queryClient.invalidateQueries({ queryKey: adminQueryKeys.dashboard() });
  };
}

export function useStockIn() {
  const invalidate = useInvalidateWms();
  return useMutation({
    mutationFn: (_payload: StockInPayload) =>
      throwAdminApiUnavailable("stock in"),
    onSuccess: invalidate,
  });
}

export function useStockOut() {
  const invalidate = useInvalidateWms();
  return useMutation({
    mutationFn: (_payload: StockOutPayload) =>
      throwAdminApiUnavailable("stock out"),
    onSuccess: invalidate,
  });
}

export function useStockAdjustment() {
  const invalidate = useInvalidateWms();
  return useMutation({
    mutationFn: (_payload: StockAdjustmentPayload) =>
      throwAdminApiUnavailable("stock adjustment"),
    onSuccess: invalidate,
  });
}

export function useStockTransfer() {
  const invalidate = useInvalidateWms();
  return useMutation({
    mutationFn: (_payload: StockTransferPayload) =>
      throwAdminApiUnavailable("stock transfer"),
    onSuccess: invalidate,
  });
}

export function useCreatePurchaseOrder() {
  const invalidate = useInvalidateWms();
  return useMutation({
    mutationFn: (args: { payload: CreatePurchaseOrderPayload; supplierName: string }) =>
      createPurchaseOrder(args.payload),
    onSuccess: invalidate,
  });
}

export function useReceivePurchaseOrder() {
  const invalidate = useInvalidateWms();
  return useMutation({
    mutationFn: (args: { poId: string; receipts: { lineId: string; quantity: number }[] }) =>
      receivePurchaseOrder(args.poId, args.receipts),
    onSuccess: invalidate,
  });
}

export function useSubmitPurchaseOrder() {
  const invalidate = useInvalidateWms();
  return useMutation({
    mutationFn: (poId: string) => submitPurchaseOrder(poId),
    onSuccess: invalidate,
  });
}

export function useConfirmPurchaseOrder() {
  const invalidate = useInvalidateWms();
  return useMutation({
    mutationFn: (poId: string) => confirmPurchaseOrder(poId),
    onSuccess: invalidate,
  });
}

export function useCancelPurchaseOrder() {
  const invalidate = useInvalidateWms();
  return useMutation({
    mutationFn: (poId: string) => cancelPurchaseOrder(poId),
    onSuccess: invalidate,
  });
}

export function useAdminOrders() {
  return useQuery(
    createAdminLiveQueryOptions(
      "orders",
      adminQueryKeys.orders(),
      fetchAdminOrders
    )
  );
}

export function useOrderPack() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: packOrder,
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: adminQueryKeys.orders() });
      void qc.invalidateQueries({ queryKey: adminQueryKeys.dashboard() });
    },
  });
}

export function useOrderShip() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ orderId, carrier }: { orderId: string; carrier?: string }) =>
      shipOrder(orderId, { carrier }),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: adminQueryKeys.orders() });
      void qc.invalidateQueries({ queryKey: adminQueryKeys.dashboard() });
    },
  });
}

export function useOrderDeliver() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: deliverOrder,
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: adminQueryKeys.orders() });
      void qc.invalidateQueries({ queryKey: adminQueryKeys.dashboard() });
    },
  });
}

export function useOrderCancel() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ orderId, reason }: { orderId: string; reason?: string }) =>
      cancelOrder(orderId, reason),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: adminQueryKeys.orders() });
      void qc.invalidateQueries({ queryKey: adminQueryKeys.dashboard() });
    },
  });
}

export function useOrderRefund() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ orderId, reason }: { orderId: string; reason?: string }) =>
      refundOrder(orderId, reason),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: adminQueryKeys.orders() });
      void qc.invalidateQueries({ queryKey: adminQueryKeys.dashboard() });
    },
  });
}

export function useAdminCustomers() {
  return useQuery(
    createAdminLiveQueryOptions(
      "customers",
      adminQueryKeys.customers(),
      fetchAdminCustomers
    )
  );
}

export function useAdminTradeApplications(params?: { status?: string }) {
  return useQuery(
    createAdminLiveQueryOptions(
      "trade-applications",
      adminQueryKeys.tradeApplications(params),
      () => fetchTradeApplicationsList(params)
    )
  );
}

export function useAdminSuppliers(params?: { search?: string; status?: string }) {
  return useQuery(
    createAdminLiveQueryOptions(
      "suppliers",
      adminQueryKeys.suppliers(params),
      () => fetchAdminSuppliersList(params)
    )
  );
}

export function useCreateSupplier() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: createAdminSupplier,
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: [...adminQueryKeys.all, "suppliers"] });
    },
  });
}

export function useUpdateSupplier() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({
      id,
      ...payload
    }: {
      id: string;
      name?: string;
      email?: string;
      is_active?: boolean;
    }) => updateAdminSupplier(id, payload),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: [...adminQueryKeys.all, "suppliers"] });
    },
  });
}

export function useRevenueByPeriod(period: RevenuePeriod) {
  return useQuery(
    createAdminLiveQueryOptions(
      `revenue/${period}`,
      adminQueryKeys.revenue(period),
      () => fetchRevenueByPeriod(period)
    )
  );
}

export function useAdminReports() {
  return useQuery(
    createAdminLiveQueryOptions<ReportType[]>(
      "reports",
      adminQueryKeys.reports(),
      fetchAdminReports
    )
  );
}

export function useCompanySettings() {
  return useQuery(
    createAdminLiveQueryOptions<CompanySettings>(
      "settings/company",
      adminQueryKeys.settings.company(),
      () => throwAdminApiUnavailable("company settings")
    )
  );
}

export function useGstSettings() {
  return useQuery(
    createAdminLiveQueryOptions<GstSettings>(
      "settings/gst",
      adminQueryKeys.settings.gst(),
      () => throwAdminApiUnavailable("GST settings")
    )
  );
}

export function useShippingSettings() {
  return useQuery(
    createAdminLiveQueryOptions<ShippingSettings>(
      "settings/shipping",
      adminQueryKeys.settings.shipping(),
      () => throwAdminApiUnavailable("shipping settings")
    )
  );
}

export function useEmailSettings() {
  return useQuery(
    createAdminLiveQueryOptions<EmailSettings>(
      "settings/email",
      adminQueryKeys.settings.email(),
      () => throwAdminApiUnavailable("email settings")
    )
  );
}

export function usePaymentSettings() {
  return useQuery(
    createAdminLiveQueryOptions<PaymentGatewaySettings>(
      "settings/payment",
      adminQueryKeys.settings.payment(),
      () => throwAdminApiUnavailable("payment settings")
    )
  );
}

export function useUpdateTradeApplication() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      id,
      status,
      credit_limit_cents,
    }: {
      id: string;
      status: TradeStatus;
      credit_limit_cents?: number;
    }) =>
      reviewTradeApplication(id, {
        status,
        credit_limit_cents,
      }),
    onSuccess: () => {
      void queryClient.invalidateQueries({
        queryKey: [...adminQueryKeys.all, "trade-applications"],
      });
      void queryClient.invalidateQueries({ queryKey: adminQueryKeys.dashboard() });
    },
  });
}

export function useExportReport() {
  return useMutation({
    mutationFn: ({ reportId, format }: { reportId: string; format: "pdf" | "excel" | "csv" }) =>
      exportAdminReport(reportId, format),
  });
}
