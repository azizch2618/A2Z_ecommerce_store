"use client";

import { useState } from "react";

import { AdminCard } from "@/components/admin/shared/admin-card";
import { AdminListPage } from "@/components/admin/shared/admin-list-page";
import {
  CustomerTrendChart,
  OrderStatusChart,
  PieChartWidget,
  RevenueChart,
} from "@/components/admin/charts/admin-charts-lazy";
import { useAdminDashboard } from "@/lib/api/admin/hooks";
import type { RevenuePeriod } from "@/lib/api/admin/types";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";

function AnalyticsPageView() {
  const { data, isLoading, isError, error } = useAdminDashboard();
  const [period, setPeriod] = useState<RevenuePeriod>("monthly");

  return (
    <AdminListPage
      title="Analytics"
      description="Deep-dive into revenue, orders, products, and customers."
      isLoading={isLoading}
      isError={isError}
      errorMessage={
        error instanceof Error ? error.message : "Failed to load analytics from the API."
      }
    >
      {data ? (
        <div className="space-y-6">
          <AdminCard
            title="Revenue overview"
            action={
              <Tabs value={period} onValueChange={(v) => setPeriod(v as RevenuePeriod)}>
                <TabsList className="h-8">
                  <TabsTrigger value="daily" className="text-xs">Daily</TabsTrigger>
                  <TabsTrigger value="weekly" className="text-xs">Weekly</TabsTrigger>
                  <TabsTrigger value="monthly" className="text-xs">Monthly</TabsTrigger>
                </TabsList>
              </Tabs>
            }
          >
            <RevenueChart data={data.revenue[period]} className="h-[360px]" />
          </AdminCard>

          <div className="grid gap-6 lg:grid-cols-2">
            <AdminCard title="Order analytics">
              <OrderStatusChart data={data.orderAnalytics.byStatus} />
            </AdminCard>
            <AdminCard title="Top brands">
              <PieChartWidget
                data={data.productAnalytics.topBrands.map((b) => ({
                  name: b.name,
                  value: b.revenue,
                }))}
              />
            </AdminCard>
          </div>

          <AdminCard title="Customer analytics">
            <CustomerTrendChart data={data.customerAnalytics.trend} />
          </AdminCard>
        </div>
      ) : null}
    </AdminListPage>
  );
}

export { AnalyticsPageView };
