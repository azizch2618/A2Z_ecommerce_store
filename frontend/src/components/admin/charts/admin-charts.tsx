"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import type { RevenueDataPoint } from "@/lib/api/admin/types";
import { cn } from "@/lib/utils";

const CHART_COLORS = {
  primary: "hsl(var(--brand-primary, 217 91% 40%))",
  secondary: "hsl(var(--brand-secondary, 38 92% 50%))",
  success: "hsl(142 76% 36%)",
  muted: "hsl(var(--muted-foreground))",
  grid: "hsl(var(--border))",
};

const PIE_COLORS = ["#1e40af", "#d97706", "#059669", "#7c3aed", "#dc2626"];

export interface ChartTooltipProps {
  active?: boolean;
  payload?: { name: string; value: number; color: string }[];
  label?: string;
}

function ChartTooltip({ active, payload, label }: ChartTooltipProps) {
  if (!active || !payload?.length) return null;
  return (
    <div className="rounded-lg border border-border bg-card px-3 py-2 shadow-lg">
      {label ? <p className="mb-1 text-xs font-medium text-muted-foreground">{label}</p> : null}
      {payload.map((entry) => (
        <p key={entry.name} className="text-sm font-semibold" style={{ color: entry.color }}>
          {entry.name}: {typeof entry.value === "number" && entry.name.toLowerCase().includes("revenue")
            ? `$${entry.value.toLocaleString("en-AU")}`
            : entry.value.toLocaleString("en-AU")}
        </p>
      ))}
    </div>
  );
}

export interface RevenueChartProps {
  data: RevenueDataPoint[];
  className?: string;
}

function RevenueChart({ data, className }: RevenueChartProps) {
  return (
    <div className={cn("h-[300px] w-full", className)}>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke={CHART_COLORS.grid} vertical={false} />
          <XAxis dataKey="label" tick={{ fontSize: 12 }} stroke={CHART_COLORS.muted} />
          <YAxis
            tick={{ fontSize: 12 }}
            stroke={CHART_COLORS.muted}
            tickFormatter={(v) => `$${(v / 1000).toFixed(0)}k`}
          />
          <Tooltip content={<ChartTooltip />} />
          <Legend />
          <Line
            type="monotone"
            dataKey="revenue"
            name="Revenue"
            stroke={CHART_COLORS.primary}
            strokeWidth={2}
            dot={{ r: 4 }}
            activeDot={{ r: 6 }}
          />
          <Line
            type="monotone"
            dataKey="orders"
            name="Orders"
            stroke={CHART_COLORS.secondary}
            strokeWidth={2}
            dot={{ r: 4 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

export interface OrderStatusChartProps {
  data: { status: string; count: number }[];
  className?: string;
}

function OrderStatusChart({ data, className }: OrderStatusChartProps) {
  return (
    <div className={cn("h-[280px] w-full", className)}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke={CHART_COLORS.grid} vertical={false} />
          <XAxis dataKey="status" tick={{ fontSize: 11 }} stroke={CHART_COLORS.muted} />
          <YAxis tick={{ fontSize: 12 }} stroke={CHART_COLORS.muted} />
          <Tooltip content={<ChartTooltip />} />
          <Bar dataKey="count" name="Orders" radius={[4, 4, 0, 0]}>
            {data.map((_, index) => (
              <Cell key={`cell-${index}`} fill={PIE_COLORS[index % PIE_COLORS.length]} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export interface PieChartWidgetProps {
  data: { name: string; value: number }[];
  className?: string;
}

function PieChartWidget({ data, className }: PieChartWidgetProps) {
  return (
    <div className={cn("h-[240px] w-full", className)}>
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            innerRadius={50}
            outerRadius={80}
            paddingAngle={2}
            dataKey="value"
            nameKey="name"
          >
            {data.map((_, index) => (
              <Cell key={`cell-${index}`} fill={PIE_COLORS[index % PIE_COLORS.length]} />
            ))}
          </Pie>
          <Tooltip />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}

export interface CustomerTrendChartProps {
  data: { label: string; new: number; returning: number }[];
  className?: string;
}

function CustomerTrendChart({ data, className }: CustomerTrendChartProps) {
  return (
    <div className={cn("h-[260px] w-full", className)}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke={CHART_COLORS.grid} vertical={false} />
          <XAxis dataKey="label" tick={{ fontSize: 12 }} stroke={CHART_COLORS.muted} />
          <YAxis tick={{ fontSize: 12 }} stroke={CHART_COLORS.muted} />
          <Tooltip content={<ChartTooltip />} />
          <Legend />
          <Bar dataKey="new" name="New" fill={CHART_COLORS.primary} radius={[4, 4, 0, 0]} stackId="a" />
          <Bar dataKey="returning" name="Returning" fill={CHART_COLORS.secondary} radius={[4, 4, 0, 0]} stackId="a" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export { RevenueChart, OrderStatusChart, PieChartWidget, CustomerTrendChart };
