"use client";

import { AdminCard } from "@/components/admin/shared/admin-card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { useValuationSummary } from "@/lib/api/admin/inventory-hooks";
import { formatAudFromCents, formatGstLabel } from "@/lib/format/currency";
import { hasAuthTokens } from "@/lib/api/auth/token-storage";

function ValuationTab() {
  const { data, isLoading } = useValuationSummary();

  if (!hasAuthTokens()) {
    return (
      <AdminCard title="Inventory valuation">
        <p className="text-sm text-muted-foreground">
          Sign in with a staff account to view live valuation from the API.
          Demo mode uses mock data without GST breakdown.
        </p>
      </AdminCard>
    );
  }

  if (isLoading || !data) {
    return <AdminCard title="Inventory valuation"><p className="text-sm text-muted-foreground">Loading…</p></AdminCard>;
  }

  return (
    <div className="space-y-6">
      <AdminCard
        title="Inventory valuation (weighted average)"
        description={data.tax_note}
      >
        <dl className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <div>
            <dt className="text-xs text-muted-foreground">Total ex GST</dt>
            <dd className="text-xl font-semibold tabular-nums">
              {formatAudFromCents(data.amount_ex_gst_cents)}
            </dd>
          </div>
          <div>
            <dt className="text-xs text-muted-foreground">{formatGstLabel(data.gst_rate)}</dt>
            <dd className="text-xl font-semibold tabular-nums">
              {formatAudFromCents(data.gst_cents)}
            </dd>
          </div>
          <div>
            <dt className="text-xs text-muted-foreground">Total inc GST</dt>
            <dd className="text-xl font-semibold tabular-nums">
              {formatAudFromCents(data.amount_inc_gst_cents)}
            </dd>
          </div>
          <div>
            <dt className="text-xs text-muted-foreground">SKUs / units</dt>
            <dd className="text-xl font-semibold">
              {data.sku_count} / {data.total_units.toLocaleString("en-AU")}
            </dd>
          </div>
        </dl>
        <p className="mt-4 text-xs text-muted-foreground">
          Low-stock exposure (ex GST):{" "}
          {formatAudFromCents(data.low_stock_value.amount_ex_gst_cents)} ·{" "}
          {data.currency_code} · {data.valuation_method.replace(/_/g, " ")}
        </p>
      </AdminCard>

      {data.by_warehouse.length > 0 ? (
        <AdminCard title="By warehouse" contentClassName="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Warehouse</TableHead>
                <TableHead className="text-right">SKUs</TableHead>
                <TableHead className="text-right">Units</TableHead>
                <TableHead className="text-right">Ex GST</TableHead>
                <TableHead className="text-right">GST</TableHead>
                <TableHead className="text-right">Inc GST</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {data.by_warehouse.map((wh) => (
                <TableRow key={wh.warehouse_code}>
                  <TableCell>
                    <span className="font-mono text-xs">{wh.warehouse_code}</span>
                    <span className="ml-2 text-muted-foreground">{wh.warehouse_name}</span>
                  </TableCell>
                  <TableCell className="text-right">{wh.sku_count}</TableCell>
                  <TableCell className="text-right">{wh.total_units}</TableCell>
                  <TableCell className="text-right tabular-nums">
                    {formatAudFromCents(wh.amount_ex_gst_cents)}
                  </TableCell>
                  <TableCell className="text-right tabular-nums">
                    {formatAudFromCents(wh.gst_cents)}
                  </TableCell>
                  <TableCell className="text-right tabular-nums">
                    {formatAudFromCents(wh.amount_inc_gst_cents)}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </AdminCard>
      ) : null}

      <AdminCard title="Top SKUs by value" contentClassName="p-0">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>SKU</TableHead>
              <TableHead>Product</TableHead>
              <TableHead>Warehouse</TableHead>
              <TableHead className="text-right">Qty</TableHead>
              <TableHead className="text-right">Value ex GST</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {data.top_skus_by_value.map((row) => (
              <TableRow key={`${row.sku}-${row.warehouse_code}`}>
                <TableCell className="font-mono text-xs">{row.sku}</TableCell>
                <TableCell>{row.product_name}</TableCell>
                <TableCell>{row.warehouse_code}</TableCell>
                <TableCell className="text-right">{row.quantity_on_hand}</TableCell>
                <TableCell className="text-right tabular-nums">
                  {formatAudFromCents(row.amount_ex_gst_cents)}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </AdminCard>
    </div>
  );
}

export { ValuationTab };
