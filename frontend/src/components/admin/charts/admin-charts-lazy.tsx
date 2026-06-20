"use client";

import dynamic from "next/dynamic";

import { Spinner } from "@/components/ui/spinner";

function ChartLoading() {
  return (
    <div className="flex h-[280px] items-center justify-center">
      <Spinner className="size-6" />
    </div>
  );
}

export const RevenueChart = dynamic(
  () => import("./admin-charts").then((module) => module.RevenueChart),
  { ssr: false, loading: ChartLoading }
);

export const OrderStatusChart = dynamic(
  () => import("./admin-charts").then((module) => module.OrderStatusChart),
  { ssr: false, loading: ChartLoading }
);

export const CustomerTrendChart = dynamic(
  () => import("./admin-charts").then((module) => module.CustomerTrendChart),
  { ssr: false, loading: ChartLoading }
);

export const PieChartWidget = dynamic(
  () => import("./admin-charts").then((module) => module.PieChartWidget),
  { ssr: false, loading: ChartLoading }
);
