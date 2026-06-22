"use client";

import { AdminCard } from "@/components/admin/shared/admin-card";
import { AdminListPage } from "@/components/admin/shared/admin-list-page";
import { RevenueChart } from "@/components/admin/charts/admin-charts-lazy";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useBiSnapshot } from "@/lib/api/admin/bi-hooks";
import type { ExecutiveKpis } from "@/lib/api/admin/bi-types";

function formatAud(cents: number): string {
  return new Intl.NumberFormat("en-AU", { style: "currency", currency: "AUD" }).format(
    cents / 100
  );
}

function ExecutiveKpiGrid({ kpis }: { kpis: ExecutiveKpis }) {
  const items = [
    { label: "Revenue (30d)", value: formatAud(kpis.revenueCents) },
    { label: "Gross margin", value: `${formatAud(kpis.grossMarginCents)} (${kpis.grossMarginPct}%)` },
    { label: "Inventory value", value: formatAud(kpis.inventoryValueCents) },
    { label: "Open orders", value: String(kpis.openOrders) },
    { label: "Open quotes", value: String(kpis.openQuotes) },
    { label: "Cash position", value: formatAud(kpis.cashPositionCents) },
    { label: "Payroll cost YTD", value: formatAud(kpis.payrollCostYtdCents) },
    { label: "Headcount", value: String(kpis.headcount) },
  ];

  return (
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      {items.map((item) => (
        <AdminCard key={item.label} title={item.label}>
          <p className="text-2xl font-bold tracking-tight">{item.value}</p>
        </AdminCard>
      ))}
    </div>
  );
}

function ExecutiveBiDashboardPageView() {
  const { data, isLoading, isError, error } = useBiSnapshot();

  return (
    <AdminListPage
      title="Executive BI"
      description="Cross-module KPIs, analytics, and configurable reporting."
      isLoading={isLoading}
      isError={isError}
      errorMessage={error instanceof Error ? error.message : "Failed to load executive BI data."}
    >
      {data ? (
        <div className="space-y-6">
          <ExecutiveKpiGrid kpis={data.executive.executiveKpis} />

          <Tabs defaultValue="sales">
            <TabsList>
              <TabsTrigger value="sales">Sales</TabsTrigger>
              <TabsTrigger value="inventory">Inventory</TabsTrigger>
              <TabsTrigger value="procurement">Procurement</TabsTrigger>
              <TabsTrigger value="finance">Finance</TabsTrigger>
              <TabsTrigger value="hr">HR</TabsTrigger>
              <TabsTrigger value="kpis">KPI Engine</TabsTrigger>
            </TabsList>

            <TabsContent value="sales" className="space-y-6 pt-4">
              <AdminCard title="Revenue by month">
                <RevenueChart
                  data={data.sales.revenueByMonth.map((row) => ({
                    label: row.label,
                    revenue: row.revenueCents / 100,
                    orders: row.orderCount,
                  }))}
                  className="h-[360px]"
                />
              </AdminCard>
              <div className="grid gap-6 lg:grid-cols-2">
                <AdminCard title="Top customers">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Customer</TableHead>
                        <TableHead className="text-right">Revenue</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {data.sales.revenueByCustomer.slice(0, 10).map((row) => (
                        <TableRow key={row.customerId ?? row.customerName}>
                          <TableCell>{row.customerName}</TableCell>
                          <TableCell className="text-right">{formatAud(row.revenueCents)}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </AdminCard>
                <AdminCard title="Quote conversion">
                  <dl className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <dt className="text-muted-foreground">Conversion rate</dt>
                      <dd className="text-2xl font-bold">{data.sales.quoteConversion.conversionRatePct}%</dd>
                    </div>
                    <div>
                      <dt className="text-muted-foreground">Converted</dt>
                      <dd className="text-2xl font-bold">{data.sales.quoteConversion.converted}</dd>
                    </div>
                    <div>
                      <dt className="text-muted-foreground">Open quotes</dt>
                      <dd>{data.sales.quoteConversion.draftQuotes + data.sales.quoteConversion.pendingApproval}</dd>
                    </div>
                    <div>
                      <dt className="text-muted-foreground">Accepted</dt>
                      <dd>{data.sales.quoteConversion.accepted}</dd>
                    </div>
                  </dl>
                </AdminCard>
              </div>
            </TabsContent>

            <TabsContent value="inventory" className="space-y-6 pt-4">
              <div className="grid gap-4 sm:grid-cols-3">
                <AdminCard title="Inventory turns">
                  <p className="text-3xl font-bold">{data.inventory.inventoryTurns}</p>
                </AdminCard>
                <AdminCard title="Warehouse utilization">
                  <p className="text-3xl font-bold">{data.inventory.warehouseUtilization.utilizationPct}%</p>
                  <p className="text-sm text-muted-foreground">
                    {data.inventory.warehouseUtilization.usedBins} / {data.inventory.warehouseUtilization.totalBins} bins
                  </p>
                </AdminCard>
                <AdminCard title="Inventory value">
                  <p className="text-3xl font-bold">{formatAud(data.inventory.inventoryValueCents)}</p>
                </AdminCard>
              </div>
              <div className="grid gap-6 lg:grid-cols-2">
                <AdminCard title="Fast moving products">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>SKU</TableHead>
                        <TableHead>Product</TableHead>
                        <TableHead className="text-right">Units (30d)</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {data.inventory.fastMovingProducts.map((row) => (
                        <TableRow key={row.sku}>
                          <TableCell>{row.sku}</TableCell>
                          <TableCell>{row.productName}</TableCell>
                          <TableCell className="text-right">{row.unitsSold}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </AdminCard>
                <AdminCard title="Dead stock">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>SKU</TableHead>
                        <TableHead className="text-right">Value</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {data.inventory.deadStock.slice(0, 10).map((row) => (
                        <TableRow key={`${row.sku}-${row.warehouse}`}>
                          <TableCell>{row.sku}</TableCell>
                          <TableCell className="text-right">{formatAud(row.valueCents)}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </AdminCard>
              </div>
            </TabsContent>

            <TabsContent value="procurement" className="space-y-6 pt-4">
              <AdminCard title="Spend by supplier">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Supplier</TableHead>
                      <TableHead className="text-right">Spend</TableHead>
                      <TableHead className="text-right">POs</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {data.procurement.spendBySupplier.map((row) => (
                      <TableRow key={row.supplierId}>
                        <TableCell>{row.supplierName}</TableCell>
                        <TableCell className="text-right">{formatAud(row.spendCents)}</TableCell>
                        <TableCell className="text-right">{row.orderCount}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </AdminCard>
            </TabsContent>

            <TabsContent value="finance" className="space-y-6 pt-4">
              <div className="grid gap-4 sm:grid-cols-3">
                <AdminCard title="Cash position">
                  <p className="text-3xl font-bold">{formatAud(data.finance.cashFlow.cashPositionCents)}</p>
                </AdminCard>
                <AdminCard title="AR outstanding">
                  <p className="text-3xl font-bold">{formatAud(data.finance.cashFlow.arOutstandingCents)}</p>
                </AdminCard>
                <AdminCard title="Net position">
                  <p className="text-3xl font-bold">{formatAud(data.finance.profitability.netPositionCents)}</p>
                </AdminCard>
              </div>
              <div className="grid gap-6 lg:grid-cols-2">
                <AdminCard title="AR aging">
                  <Table>
                    <TableBody>
                      {Object.entries(data.finance.arAging).map(([bucket, cents]) => (
                        <TableRow key={bucket}>
                          <TableCell className="capitalize">{bucket.replace(/Cents$/, "").replace(/([A-Z])/g, " $1")}</TableCell>
                          <TableCell className="text-right">{formatAud(cents)}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </AdminCard>
                <AdminCard title="AP aging">
                  <Table>
                    <TableBody>
                      {Object.entries(data.finance.apAging).map(([bucket, cents]) => (
                        <TableRow key={bucket}>
                          <TableCell className="capitalize">{bucket.replace(/Cents$/, "").replace(/([A-Z])/g, " $1")}</TableCell>
                          <TableCell className="text-right">{formatAud(cents)}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </AdminCard>
              </div>
            </TabsContent>

            <TabsContent value="hr" className="space-y-6 pt-4">
              <div className="grid gap-4 sm:grid-cols-3">
                <AdminCard title="Headcount">
                  <p className="text-3xl font-bold">{data.hr.headcount}</p>
                </AdminCard>
                <AdminCard title="On leave today">
                  <p className="text-3xl font-bold">{data.hr.onLeaveToday}</p>
                </AdminCard>
                <AdminCard title="Payroll YTD">
                  <p className="text-3xl font-bold">{formatAud(data.hr.payrollYtdCents)}</p>
                </AdminCard>
              </div>
              <AdminCard title="Payroll cost by department">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Department</TableHead>
                      <TableHead>Headcount</TableHead>
                      <TableHead className="text-right">Total</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {data.hr.payrollCostByDepartment.map((row) => (
                      <TableRow key={row.departmentName}>
                        <TableCell>{row.departmentName}</TableCell>
                        <TableCell>{row.headcount}</TableCell>
                        <TableCell className="text-right">{formatAud(row.totalCents)}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </AdminCard>
            </TabsContent>

            <TabsContent value="kpis" className="space-y-6 pt-4">
              <AdminCard title="Configured KPIs">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>KPI</TableHead>
                      <TableHead>Category</TableHead>
                      <TableHead className="text-right">Value</TableHead>
                      <TableHead className="text-right">Target</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {data.kpis.map((kpi) => (
                      <TableRow key={kpi.id}>
                        <TableCell>{kpi.name}</TableCell>
                        <TableCell className="capitalize">{kpi.category}</TableCell>
                        <TableCell className="text-right">
                          {kpi.value === null
                            ? "—"
                            : kpi.unit === "currency"
                              ? formatAud(Number(kpi.value))
                              : kpi.unit === "percent"
                                ? `${kpi.value}%`
                                : String(kpi.value)}
                        </TableCell>
                        <TableCell className="text-right">
                          {kpi.targetValue ?? "—"}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </AdminCard>
            </TabsContent>
          </Tabs>
        </div>
      ) : null}
    </AdminListPage>
  );
}

export { ExecutiveBiDashboardPageView };
