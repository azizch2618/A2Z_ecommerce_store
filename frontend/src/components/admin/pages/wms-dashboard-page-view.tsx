"use client";

import Link from "next/link";

import { AdminCard } from "@/components/admin/shared/admin-card";
import { AdminListPage } from "@/components/admin/shared/admin-list-page";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  useBinInventory,
  useWmsBins,
  useWmsDashboard,
  useWmsPicks,
  useWmsTransfers,
} from "@/lib/api/admin/wms-hooks";

function formatAud(cents: number): string {
  return new Intl.NumberFormat("en-AU", { style: "currency", currency: "AUD" }).format(
    cents / 100
  );
}

function WmsKpiGrid({
  kpis,
}: {
  kpis: {
    inventoryValueCents: number;
    openTransfers: number;
    openPicks: number;
    cycleCountAccuracyPct: number;
  };
}) {
  const items = [
    { label: "Inventory value", value: formatAud(kpis.inventoryValueCents) },
    { label: "Open transfers", value: String(kpis.openTransfers) },
    { label: "Open picks", value: String(kpis.openPicks) },
    { label: "Cycle count accuracy", value: `${kpis.cycleCountAccuracyPct.toFixed(1)}%` },
  ];
  return (
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      {items.map((item) => (
        <AdminCard key={item.label} title={item.label}>
          <p className="text-3xl font-bold tracking-tight">{item.value}</p>
        </AdminCard>
      ))}
    </div>
  );
}

function WmsDashboardPageView() {
  const dashboard = useWmsDashboard();
  const bins = useWmsBins();
  const binInv = useBinInventory();
  const picks = useWmsPicks();
  const transfers = useWmsTransfers();

  return (
    <AdminListPage
      title="Warehouse Management"
      description="Bin locations, transfers, picks, putaway, and cycle counts."
      isLoading={dashboard.isLoading}
      isError={dashboard.isError}
      actions={
        <Button variant="outline" asChild>
          <Link href="/warehouse-mobile">Mobile floor app</Link>
        </Button>
      }
    >
      {dashboard.data ? <WmsKpiGrid kpis={dashboard.data} /> : null}

      <div className="grid gap-6 lg:grid-cols-2">
        <AdminCard title="Bin locations">
          {(bins.data ?? []).length === 0 ? (
            <p className="text-sm text-muted-foreground">No bins configured.</p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Location</TableHead>
                  <TableHead>Type</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {(bins.data ?? []).slice(0, 8).map((bin) => (
                  <TableRow key={bin.id}>
                    <TableCell className="font-medium">{bin.locationCode}</TableCell>
                    <TableCell className="capitalize">{bin.binType}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </AdminCard>

        <AdminCard title="Bin inventory">
          {(binInv.data ?? []).length === 0 ? (
            <p className="text-sm text-muted-foreground">No stock in bins yet.</p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Location</TableHead>
                  <TableHead>SKU</TableHead>
                  <TableHead className="text-right">Qty</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {(binInv.data ?? []).slice(0, 8).map((row) => (
                  <TableRow key={row.id}>
                    <TableCell>{row.locationCode}</TableCell>
                    <TableCell>{row.sku}</TableCell>
                    <TableCell className="text-right">{row.quantityOnHand}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </AdminCard>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <AdminCard title="Open pick lists">
          {(picks.data ?? []).slice(0, 6).map((pick) => (
            <div key={pick.id} className="flex justify-between border-b py-2 text-sm last:border-0">
              <span className="font-medium">{pick.pickNumber}</span>
              <span className="capitalize text-muted-foreground">{pick.status}</span>
            </div>
          ))}
        </AdminCard>
        <AdminCard title="Open transfers">
          {(transfers.data ?? []).slice(0, 6).map((tr) => (
            <div key={tr.id} className="flex justify-between border-b py-2 text-sm last:border-0">
              <span className="font-medium">{tr.transferNumber}</span>
              <span className="capitalize text-muted-foreground">{tr.status}</span>
            </div>
          ))}
        </AdminCard>
      </div>
    </AdminListPage>
  );
}

export { WmsDashboardPageView };
