"use client";

import { useState } from "react";

import { AdminCard } from "@/components/admin/shared/admin-card";
import { AdminErrorState } from "@/components/admin/shared/admin-error-state";
import { AdminPageHeader } from "@/components/admin/shared/admin-page-header";
import { KpiGrid } from "@/components/admin/dashboard/kpi-grid";
import { LowStockWidget } from "@/components/admin/dashboard/low-stock-widget";
import { OutOfStockWidget } from "@/components/admin/dashboard/out-of-stock-widget";
import { RecentCustomersTable } from "@/components/admin/dashboard/recent-customers-table";
import { RecentOrdersTable } from "@/components/admin/dashboard/recent-orders-table";
import { SupplierPanel } from "@/components/admin/dashboard/supplier-panel";
import { TradeApplicationsPanel } from "@/components/admin/dashboard/trade-applications-panel";
import {
  CustomerTrendChart,
  OrderStatusChart,
  PieChartWidget,
  RevenueChart,
} from "@/components/admin/charts/admin-charts-lazy";
import { useAdminDashboard } from "@/lib/api/admin/hooks";
import type { RevenuePeriod } from "@/lib/api/admin/types";
import { Spinner } from "@/components/ui/spinner";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { Download } from "lucide-react";

function AdminDashboardView() {
  const { data, isLoading, isError, error } = useAdminDashboard();
  const [revenuePeriod, setRevenuePeriod] = useState<RevenuePeriod>("weekly");

  if (isLoading) {
    return (
      <div className="flex min-h-[50vh] items-center justify-center">
        <Spinner className="size-8" />
      </div>
    );
  }

  if (isError || !data) {
    return (
      <AdminErrorState
        title="Dashboard unavailable"
        message={
          error instanceof Error
            ? error.message
            : "Failed to load dashboard data from the API."
        }
      />
    );
  }

  const revenueData = data.revenue[revenuePeriod];
  const categoryPie = data.productAnalytics.topCategories.map((c) => ({
    name: c.name,
    value: c.revenue,
  }));

  return (
    <div className="space-y-8">
      <AdminPageHeader
        title="Dashboard"
        description="Overview of sales, inventory, and operations across A2Z Tools."
        actions={
          <Button variant="outline" size="sm">
            <Download className="mr-2 size-4" />
            Export summary
          </Button>
        }
      />

      <KpiGrid metrics={data.kpis} />

      <div className="grid gap-6 xl:grid-cols-3">
        <AdminCard
          title="Revenue overview"
          description="Sales performance by period"
          className="xl:col-span-2"
          action={
            <Tabs
              value={revenuePeriod}
              onValueChange={(v) => setRevenuePeriod(v as RevenuePeriod)}
            >
              <TabsList className="h-8">
                <TabsTrigger value="daily" className="text-xs">Daily</TabsTrigger>
                <TabsTrigger value="weekly" className="text-xs">Weekly</TabsTrigger>
                <TabsTrigger value="monthly" className="text-xs">Monthly</TabsTrigger>
              </TabsList>
            </Tabs>
          }
          contentClassName="pt-2"
        >
          <RevenueChart data={revenueData} />
        </AdminCard>

        <AdminCard title="Order analytics" description="Orders by status">
          <div className="mb-4 grid grid-cols-3 gap-2 text-center">
            <div className="rounded-lg bg-muted/50 p-3">
              <p className="text-xs text-muted-foreground">Total</p>
              <p className="text-lg font-bold">{data.orderAnalytics.total}</p>
            </div>
            <div className="rounded-lg bg-muted/50 p-3">
              <p className="text-xs text-muted-foreground">Completed</p>
              <p className="text-lg font-bold text-success">{data.orderAnalytics.completed}</p>
            </div>
            <div className="rounded-lg bg-muted/50 p-3">
              <p className="text-xs text-muted-foreground">Cancelled</p>
              <p className="text-lg font-bold text-error">{data.orderAnalytics.cancelled}</p>
            </div>
          </div>
          <OrderStatusChart data={data.orderAnalytics.byStatus} />
        </AdminCard>
      </div>

      <div className="grid gap-6 lg:grid-cols-2 xl:grid-cols-3">
        <AdminCard title="Best sellers" description="Top products by revenue">
          <ul className="space-y-3">
            {data.productAnalytics.bestSellers.map((p, i) => (
              <li key={p.sku} className="flex items-center justify-between gap-2">
                <div className="flex items-center gap-3 min-w-0">
                  <span className="flex size-7 shrink-0 items-center justify-center rounded-full bg-muted text-xs font-bold">
                    {i + 1}
                  </span>
                  <div className="min-w-0">
                    <p className="truncate text-sm font-medium">{p.name}</p>
                    <p className="text-xs text-muted-foreground">{p.sku}</p>
                  </div>
                </div>
                <p className="shrink-0 text-sm font-semibold tabular-nums">
                  ${p.revenue.toLocaleString("en-AU")}
                </p>
              </li>
            ))}
          </ul>
        </AdminCard>

        <AdminCard title="Top categories" description="Revenue share">
          <PieChartWidget data={categoryPie} />
        </AdminCard>

        <AdminCard title="Customer analytics" description="New vs returning">
          <div className="mb-4 grid grid-cols-2 gap-2">
            <div className="rounded-lg bg-muted/50 p-3 text-center">
              <p className="text-xs text-muted-foreground">New</p>
              <p className="text-xl font-bold">{data.customerAnalytics.newCustomers}</p>
            </div>
            <div className="rounded-lg bg-muted/50 p-3 text-center">
              <p className="text-xs text-muted-foreground">Returning</p>
              <p className="text-xl font-bold">{data.customerAnalytics.returningCustomers}</p>
            </div>
          </div>
          <CustomerTrendChart data={data.customerAnalytics.trend} />
        </AdminCard>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <AdminCard title="Low stock alerts" description="Below reorder level">
          <LowStockWidget items={data.lowStock} />
        </AdminCard>
        <AdminCard title="Out of stock" description="Requires purchase">
          <OutOfStockWidget items={data.outOfStock} />
        </AdminCard>
      </div>

      <AdminCard title="Recent orders" description="Latest customer orders">
        <RecentOrdersTable orders={data.recentOrders} />
      </AdminCard>

      <div className="grid gap-6 lg:grid-cols-2">
        <AdminCard title="Recent customers" description="New and active accounts">
          <RecentCustomersTable customers={data.recentCustomers} />
        </AdminCard>
        <AdminCard title="Suppliers" description="Active procurement partners">
          <SupplierPanel suppliers={data.suppliers} />
        </AdminCard>
      </div>

      <AdminCard title="Trade account applications" description="Pending review and status">
        <TradeApplicationsPanel applications={data.tradeApplications} />
      </AdminCard>
    </div>
  );
}

export { AdminDashboardView };
