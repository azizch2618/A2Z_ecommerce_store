"use client";

import Link from "next/link";
import { Loader2, Package, ScanLine, Truck } from "lucide-react";
import { useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  useCompleteWmsPick,
  usePutawayTasks,
  useRecordWmsPick,
  useStartWmsPick,
  useWmsPickDetail,
  useWmsPicks,
} from "@/lib/api/admin/wms-hooks";

function MobileTile({
  href,
  icon: Icon,
  label,
  description,
}: {
  href: string;
  icon: typeof Package;
  label: string;
  description: string;
}) {
  return (
    <Link
      href={href}
      className="flex min-h-[120px] flex-col items-center justify-center gap-2 rounded-xl border bg-card p-6 text-center shadow-sm active:scale-[0.98]"
    >
      <Icon className="size-10 text-brand-navy" />
      <span className="text-lg font-semibold">{label}</span>
      <span className="text-xs text-muted-foreground">{description}</span>
    </Link>
  );
}

function PickDetailMobile({ pickId }: { pickId: string }) {
  const { data: pick, isLoading } = useWmsPickDetail(pickId);
  const start = useStartWmsPick();
  const record = useRecordWmsPick();
  const complete = useCompleteWmsPick();
  const [qty, setQty] = useState("1");

  if (isLoading || !pick) {
    return <Loader2 className="mx-auto size-8 animate-spin" />;
  }

  const nextLine = pick.lines.find((l) => l.quantityPicked < l.quantityRequired);

  return (
    <div className="space-y-4">
      <Button variant="ghost" size="sm" asChild>
        <Link href="/warehouse-mobile/picks">← Back</Link>
      </Button>
      <div>
        <h1 className="text-xl font-bold">{pick.pickNumber}</h1>
        <Badge className="mt-2 capitalize">{pick.status}</Badge>
      </div>
      {pick.status === "assigned" || pick.status === "draft" ? (
        <Button className="w-full" size="lg" onClick={() => void start.mutateAsync(pickId)}>
          Start picking
        </Button>
      ) : null}
      {nextLine && pick.status === "picking" ? (
        <div className="space-y-3 rounded-xl border bg-card p-4">
          <p className="font-medium">{nextLine.productName}</p>
          <p className="text-sm text-muted-foreground">SKU: {nextLine.sku}</p>
          <p className="text-sm">
            Pick {nextLine.quantityRequired - nextLine.quantityPicked} of{" "}
            {nextLine.quantityRequired}
          </p>
          <Input
            type="number"
            min={1}
            value={qty}
            onChange={(e) => setQty(e.target.value)}
            className="h-12 text-lg"
          />
          <Button
            className="w-full"
            size="lg"
            onClick={() =>
              void record.mutateAsync({
                id: pickId,
                lineId: nextLine.id,
                quantity: Number(qty) || 1,
              })
            }
          >
            Confirm pick
          </Button>
        </div>
      ) : null}
      {pick.status === "picked" ? (
        <Button className="w-full" size="lg" onClick={() => void complete.mutateAsync(pickId)}>
          Complete pick list
        </Button>
      ) : null}
    </div>
  );
}

function WarehouseMobileHomeView() {
  return (
    <div className="mx-auto min-h-screen max-w-lg space-y-6 bg-muted/30 p-4 pb-12">
      <div>
        <h1 className="text-2xl font-bold">Warehouse Floor</h1>
        <p className="text-sm text-muted-foreground">Tablet-optimised operations</p>
      </div>
      <div className="grid gap-4 sm:grid-cols-2">
        <MobileTile href="/warehouse-mobile/picks" icon={ScanLine} label="Pick" description="Sales order picks" />
        <MobileTile href="/warehouse-mobile/putaway" icon={Truck} label="Putaway" description="GRN to bin" />
        <MobileTile href="/warehouse-mobile/counts" icon={Package} label="Count" description="Cycle counts" />
      </div>
    </div>
  );
}

function WarehouseMobilePicksView() {
  const picks = useWmsPicks({ status: "assigned" });
  const allPicks = useWmsPicks();

  const rows = [...(picks.data ?? []), ...(allPicks.data ?? [])].filter(
    (p, i, arr) => arr.findIndex((x) => x.id === p.id) === i && p.status !== "completed"
  );

  return (
    <div className="mx-auto min-h-screen max-w-lg space-y-4 p-4">
      <Button variant="ghost" size="sm" asChild>
        <Link href="/warehouse-mobile">← Floor</Link>
      </Button>
      <h1 className="text-xl font-bold">Pick lists</h1>
      {picks.isLoading ? (
        <Loader2 className="mx-auto size-8 animate-spin" />
      ) : (
        <div className="space-y-2">
          {rows.map((pick) => (
            <Link
              key={pick.id}
              href={`/warehouse-mobile/picks/${pick.id}`}
              className="block rounded-xl border bg-card p-4 active:scale-[0.99]"
            >
              <p className="font-semibold">{pick.pickNumber}</p>
              <p className="text-sm capitalize text-muted-foreground">{pick.status}</p>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}

function WarehouseMobilePutawayView() {
  const tasks = usePutawayTasks({ status: "pending" });
  const inProgress = usePutawayTasks({ status: "in_progress" });
  const rows = [...(tasks.data ?? []), ...(inProgress.data ?? [])];

  return (
    <div className="mx-auto min-h-screen max-w-lg space-y-4 p-4">
      <Button variant="ghost" size="sm" asChild>
        <Link href="/warehouse-mobile">← Floor</Link>
      </Button>
      <h1 className="text-xl font-bold">Putaway tasks</h1>
      {rows.length === 0 ? (
        <p className="text-sm text-muted-foreground">No open putaway tasks.</p>
      ) : (
        rows.map((task) => (
          <div key={task.id} className="rounded-xl border bg-card p-4">
            <p className="font-semibold">{task.taskNumber}</p>
            <p className="text-sm text-muted-foreground">GRN {task.grnNumber}</p>
            <p className="text-sm capitalize">{task.status.replace(/_/g, " ")}</p>
          </div>
        ))
      )}
    </div>
  );
}

export {
  WarehouseMobileHomeView,
  WarehouseMobilePicksView,
  PickDetailMobile,
  WarehouseMobilePutawayView,
};
