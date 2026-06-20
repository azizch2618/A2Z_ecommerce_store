"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import type { CrmDashboardCharts } from "@/lib/api/admin/types";

const PIE_COLORS = ["#1e40af", "#059669", "#d97706", "#7c3aed", "#dc2626", "#64748b"];

function formatAud(cents: number): string {
  return new Intl.NumberFormat("en-AU", {
    style: "currency",
    currency: "AUD",
    notation: cents >= 10000000 ? "compact" : "standard",
  }).format(cents / 100);
}

export interface CrmDashboardChartsProps {
  charts: CrmDashboardCharts;
}

function CrmDashboardChartsPanel({ charts }: CrmDashboardChartsProps) {
  const pipelineData = charts.pipelineValue.map((row) => ({
    name: row.label,
    value: row.valueCents / 100,
    count: row.count,
  }));

  const forecastData = charts.forecastRevenue.map((row) => ({
    name: row.label,
    weighted: row.weightedCents / 100,
  }));

  const rateData = [
    { name: "Win rate", value: charts.winRate },
    { name: "Lead conversion", value: charts.conversionRate },
  ];

  return (
    <div className="grid gap-6 xl:grid-cols-2">
      <div className="rounded-xl border border-border bg-card p-4">
        <h3 className="mb-4 text-sm font-semibold">Pipeline value by stage</h3>
        <div className="h-[260px]">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={pipelineData}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="name" tick={{ fontSize: 11 }} />
              <YAxis tickFormatter={(v) => `$${v}`} tick={{ fontSize: 11 }} />
              <Tooltip formatter={(v: number) => formatAud(v * 100)} />
              <Bar dataKey="value" fill="#1e40af" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="rounded-xl border border-border bg-card p-4">
        <h3 className="mb-4 text-sm font-semibold">Forecast revenue (weighted)</h3>
        <div className="h-[260px]">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={forecastData}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="name" tick={{ fontSize: 11 }} />
              <YAxis tickFormatter={(v) => `$${v}`} tick={{ fontSize: 11 }} />
              <Tooltip formatter={(v: number) => formatAud(v * 100)} />
              <Bar dataKey="weighted" fill="#059669" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="rounded-xl border border-border bg-card p-4 xl:col-span-2">
        <h3 className="mb-4 text-sm font-semibold">Win rate & conversion</h3>
        <div className="grid gap-6 md:grid-cols-2">
          <div className="h-[220px]">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={rateData}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={80}
                  label={({ name, value }) => `${name}: ${value}%`}
                >
                  {rateData.map((_, i) => (
                    <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(v: number) => `${v}%`} />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="flex flex-col justify-center gap-4">
            <div>
              <p className="text-sm text-muted-foreground">Win rate</p>
              <p className="text-3xl font-bold tabular-nums">{charts.winRate}%</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Lead conversion</p>
              <p className="text-3xl font-bold tabular-nums">{charts.conversionRate}%</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export { CrmDashboardChartsPanel };
