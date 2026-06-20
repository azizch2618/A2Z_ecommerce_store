"use client";

import { useState } from "react";
import { AlertTriangle, ArrowLeftRight, PackageMinus, PackagePlus, SlidersHorizontal } from "lucide-react";

import { AdminCard } from "@/components/admin/shared/admin-card";
import { AdminErrorState } from "@/components/admin/shared/admin-error-state";
import { AdminListPage } from "@/components/admin/shared/admin-list-page";
import { Can } from "@/components/rbac/can";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { FormField } from "@/components/ui/form-field";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Textarea } from "@/components/ui/textarea";
import {
  useCreatePurchaseOrder,
  usePurchaseOrders,
  useReceivePurchaseOrder,
  useSubmitPurchaseOrder,
  useConfirmPurchaseOrder,
  useCancelPurchaseOrder,
  useAdminSuppliers,
  useAdminWarehouses,
} from "@/lib/api/admin/hooks";
import {
  useInventoryLevels,
  useLowStockAlertsApi,
  useStockAdjustmentApi,
  useStockInApi,
  useStockMovementsApi,
  useStockOutApi,
  useStockTransferApi,
  useTransfersApi,
  useUpdateReorderLevels,
} from "@/lib/api/admin/inventory-hooks";
import { NotificationsTab } from "@/components/admin/inventory/inventory-notifications-tab";
import { ValuationTab } from "@/components/admin/inventory/inventory-valuation-tab";
import type { AdminPurchaseOrder } from "@/lib/api/admin/types";
import { hasAuthTokens } from "@/lib/api/auth/token-storage";
import { formatAudFromCents } from "@/lib/format/currency";
import { Permission } from "@/lib/rbac";

function useWarehouseCodes(): string[] {
  const { data } = useAdminWarehouses();
  return data?.map((w) => w.code) ?? [];
}

function AdminAuthGate({
  children,
  message = "Sign in to access live inventory data from the API.",
}: {
  children: React.ReactNode;
  message?: string;
}) {
  if (!hasAuthTokens()) {
    return <AdminErrorState message={message} />;
  }
  return children;
}

function StockLevelsTab() {
  const api = useInventoryLevels();
  const updateReorder = useUpdateReorderLevels();
  const rows = api.data?.data ?? [];

  return (
    <AdminAuthGate>
      <AdminCard title="Stock levels" contentClassName="p-0">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>SKU</TableHead>
              <TableHead>Product</TableHead>
              <TableHead>Warehouse</TableHead>
              <TableHead className="text-right">Qty</TableHead>
              <TableHead className="text-right">Reorder pt / qty</TableHead>
              <TableHead className="text-right">Avg cost (ex GST)</TableHead>
              <TableHead className="text-right">Value (ex GST)</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {api.isLoading ? (
              <TableRow>
                <TableCell colSpan={7} className="text-center text-muted-foreground">
                  Loading stock levels…
                </TableCell>
              </TableRow>
            ) : null}
            {(api.isLoading ? [] : rows).map((row) => (
            <TableRow key={row.id}>
              <TableCell className="font-mono text-xs">{row.sku}</TableCell>
              <TableCell className="font-medium">{row.product_name}</TableCell>
              <TableCell>{row.warehouse_code}</TableCell>
              <TableCell className="text-right">
                <Badge
                  variant={
                    row.quantity_on_hand === 0
                      ? "destructive"
                      : row.quantity_on_hand <= row.reorder_point
                        ? "warning"
                        : "secondary"
                  }
                >
                  {row.quantity_on_hand}
                </Badge>
              </TableCell>
              <TableCell className="text-right text-muted-foreground">
                <span className="inline-flex items-center gap-1">
                  <Input
                    className="h-7 w-14 px-1 text-right text-xs"
                    type="number"
                    min={0}
                    defaultValue={row.reorder_point}
                    onBlur={(e) => {
                      const rp = Number(e.target.value);
                      const rq = row.reorder_quantity || rp * 2;
                      if (rp !== row.reorder_point) {
                        updateReorder.mutate({
                          levelId: row.id,
                          payload: { reorder_point: rp, reorder_quantity: rq },
                        });
                      }
                    }}
                  />
                  <span>/</span>
                  <Input
                    className="h-7 w-14 px-1 text-right text-xs"
                    type="number"
                    min={0}
                    defaultValue={row.reorder_quantity}
                    onBlur={(e) => {
                      const rq = Number(e.target.value);
                      if (rq !== row.reorder_quantity) {
                        updateReorder.mutate({
                          levelId: row.id,
                          payload: {
                            reorder_point: row.reorder_point,
                            reorder_quantity: rq,
                          },
                        });
                      }
                    }}
                  />
                </span>
              </TableCell>
              <TableCell className="text-right tabular-nums">
                {formatAudFromCents(row.cost_price_cents)}
              </TableCell>
              <TableCell className="text-right tabular-nums">
                {formatAudFromCents(row.valuation_ex_gst_cents)}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
      {api.isError ? (
        <p className="p-4 text-sm text-destructive">Failed to load stock levels from the API.</p>
      ) : null}
    </AdminCard>
    </AdminAuthGate>
  );
}

function OperationMessage({ error, success }: { error?: string | null; success?: string | null }) {
  if (error) return <p className="text-sm text-destructive">{error}</p>;
  if (success) return <p className="text-sm text-green-600">{success}</p>;
  return null;
}

function StockInTab() {
  const warehouseCodes = useWarehouseCodes();
  const mutation = useStockInApi();
  const [sku, setSku] = useState("");
  const [warehouse, setWarehouse] = useState("SYD1");
  const [quantity, setQuantity] = useState("1");
  const [cost, setCost] = useState("");
  const [notes, setNotes] = useState("");
  const [msg, setMsg] = useState<string | null>(null);
  const [err, setErr] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErr(null);
    setMsg(null);
    try {
      const result = await mutation.mutateAsync({
        sku,
        warehouse_code: warehouse,
        quantity: Number(quantity),
        cost_price_cents: Math.round(Number(cost) * 100),
        notes,
      });
      setMsg(`Stock in recorded: ${result.movement.movement_number}`);
    } catch (ex) {
      setErr(ex instanceof Error ? ex.message : "Stock in failed");
    }
  };

  return (
    <AdminAuthGate message="Sign in to record stock movements via the API.">
    <Can permission={Permission.INVENTORY_MANAGE}>
      <AdminCard title="Stock In" description="Receive goods into a warehouse.">
        <form onSubmit={handleSubmit} className="grid max-w-lg gap-4">
          <FormField id="si-sku" label="SKU" required>
            <Input id="si-sku" value={sku} onChange={(e) => setSku(e.target.value)} required />
          </FormField>
          <FormField id="si-wh" label="Warehouse" required>
            <Select value={warehouse} onValueChange={setWarehouse}>
              <SelectTrigger id="si-wh"><SelectValue /></SelectTrigger>
              <SelectContent>
                {warehouseCodes.map((c) => (
                  <SelectItem key={c} value={c}>{c}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </FormField>
          <FormField id="si-qty" label="Quantity" required>
            <Input id="si-qty" type="number" min={1} value={quantity} onChange={(e) => setQuantity(e.target.value)} required />
          </FormField>
          <FormField id="si-cost" label="Unit cost (AUD)" required>
            <Input id="si-cost" type="number" min={0} step="0.01" value={cost} onChange={(e) => setCost(e.target.value)} required />
          </FormField>
          <FormField id="si-notes" label="Notes">
            <Textarea id="si-notes" value={notes} onChange={(e) => setNotes(e.target.value)} rows={2} />
          </FormField>
          <OperationMessage error={err} success={msg} />
          <Button type="submit" disabled={mutation.isPending}>
            <PackagePlus className="mr-2 size-4" />
            {mutation.isPending ? "Processing…" : "Record stock in"}
          </Button>
        </form>
      </AdminCard>
    </Can>
    </AdminAuthGate>
  );
}

function StockOutTab() {
  const warehouseCodes = useWarehouseCodes();
  const mutation = useStockOutApi();
  const [sku, setSku] = useState("");
  const [warehouse, setWarehouse] = useState("SYD1");
  const [quantity, setQuantity] = useState("1");
  const [notes, setNotes] = useState("");
  const [msg, setMsg] = useState<string | null>(null);
  const [err, setErr] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErr(null);
    setMsg(null);
    try {
      const result = await mutation.mutateAsync({
        sku,
        warehouse_code: warehouse,
        quantity: Number(quantity),
        notes,
      });
      setMsg(`Stock out recorded: ${result.movement.movement_number}`);
    } catch (ex) {
      setErr(ex instanceof Error ? ex.message : "Stock out failed");
    }
  };

  return (
    <AdminAuthGate message="Sign in to record stock movements via the API.">
    <Can permission={Permission.INVENTORY_MANAGE}>
      <AdminCard title="Stock Out" description="Remove stock for sales, damage, or write-offs.">
        <form onSubmit={handleSubmit} className="grid max-w-lg gap-4">
          <FormField id="so-sku" label="SKU" required>
            <Input id="so-sku" value={sku} onChange={(e) => setSku(e.target.value)} required />
          </FormField>
          <FormField id="so-wh" label="Warehouse" required>
            <Select value={warehouse} onValueChange={setWarehouse}>
              <SelectTrigger id="so-wh"><SelectValue /></SelectTrigger>
              <SelectContent>
                {warehouseCodes.map((c) => (
                  <SelectItem key={c} value={c}>{c}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </FormField>
          <FormField id="so-qty" label="Quantity" required>
            <Input id="so-qty" type="number" min={1} value={quantity} onChange={(e) => setQuantity(e.target.value)} required />
          </FormField>
          <FormField id="so-notes" label="Notes">
            <Textarea id="so-notes" value={notes} onChange={(e) => setNotes(e.target.value)} rows={2} />
          </FormField>
          <OperationMessage error={err} success={msg} />
          <Button type="submit" disabled={mutation.isPending}>
            <PackageMinus className="mr-2 size-4" />
            {mutation.isPending ? "Processing…" : "Record stock out"}
          </Button>
        </form>
      </AdminCard>
    </Can>
    </AdminAuthGate>
  );
}

function AdjustmentTab() {
  const warehouseCodes = useWarehouseCodes();
  const mutation = useStockAdjustmentApi();
  const [sku, setSku] = useState("");
  const [warehouse, setWarehouse] = useState("SYD1");
  const [change, setChange] = useState("");
  const [cost, setCost] = useState("");
  const [notes, setNotes] = useState("");
  const [msg, setMsg] = useState<string | null>(null);
  const [err, setErr] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErr(null);
    setMsg(null);
    const quantityChange = Number(change);
    try {
      const result = await mutation.mutateAsync({
        sku,
        warehouse_code: warehouse,
        quantity_change: quantityChange,
        cost_price_cents: quantityChange > 0 ? Math.round(Number(cost) * 100) : undefined,
        notes,
      });
      setMsg(`Adjustment recorded: ${result.movement.movement_number}`);
    } catch (ex) {
      setErr(ex instanceof Error ? ex.message : "Adjustment failed");
    }
  };

  return (
    <AdminAuthGate message="Sign in to record stock adjustments via the API.">
    <Can permission={Permission.INVENTORY_MANAGE}>
      <AdminCard title="Inventory Adjustments" description="Cycle counts, shrinkage, or corrections (+/−).">
        <form onSubmit={handleSubmit} className="grid max-w-lg gap-4">
          <FormField id="adj-sku" label="SKU" required>
            <Input id="adj-sku" value={sku} onChange={(e) => setSku(e.target.value)} required />
          </FormField>
          <FormField id="adj-wh" label="Warehouse" required>
            <Select value={warehouse} onValueChange={setWarehouse}>
              <SelectTrigger id="adj-wh"><SelectValue /></SelectTrigger>
              <SelectContent>
                {warehouseCodes.map((c) => (
                  <SelectItem key={c} value={c}>{c}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </FormField>
          <FormField id="adj-change" label="Quantity change" hint="Use negative values to reduce stock." required>
            <Input id="adj-change" type="number" value={change} onChange={(e) => setChange(e.target.value)} required />
          </FormField>
          {Number(change) > 0 ? (
            <FormField id="adj-cost" label="Unit cost (AUD)" required>
              <Input id="adj-cost" type="number" min={0} step="0.01" value={cost} onChange={(e) => setCost(e.target.value)} required />
            </FormField>
          ) : null}
          <FormField id="adj-notes" label="Reason / notes">
            <Textarea id="adj-notes" value={notes} onChange={(e) => setNotes(e.target.value)} rows={2} />
          </FormField>
          <OperationMessage error={err} success={msg} />
          <Button type="submit" disabled={mutation.isPending}>
            <SlidersHorizontal className="mr-2 size-4" />
            {mutation.isPending ? "Processing…" : "Apply adjustment"}
          </Button>
        </form>
      </AdminCard>
    </Can>
    </AdminAuthGate>
  );
}

function TransferTab() {
  const warehouseCodes = useWarehouseCodes();
  const mutation = useStockTransferApi();
  const [sku, setSku] = useState("");
  const [fromWh, setFromWh] = useState("SYD1");
  const [toWh, setToWh] = useState("MEL1");
  const [quantity, setQuantity] = useState("1");
  const [notes, setNotes] = useState("");
  const [msg, setMsg] = useState<string | null>(null);
  const [err, setErr] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErr(null);
    setMsg(null);
    try {
      const result = await mutation.mutateAsync({
        sku,
        from_warehouse_code: fromWh,
        to_warehouse_code: toWh,
        quantity: Number(quantity),
        notes,
      });
      setMsg(`Transfer recorded: ${result.movement.movement_number}`);
    } catch (ex) {
      setErr(ex instanceof Error ? ex.message : "Transfer failed");
    }
  };

  return (
    <AdminAuthGate message="Sign in to transfer stock via the API.">
    <Can permission={Permission.INVENTORY_MANAGE}>
      <AdminCard title="Warehouse Transfers" description="Move stock between warehouses.">
        <form onSubmit={handleSubmit} className="grid max-w-lg gap-4">
          <FormField id="tr-sku" label="SKU" required>
            <Input id="tr-sku" value={sku} onChange={(e) => setSku(e.target.value)} required />
          </FormField>
          <div className="grid gap-4 sm:grid-cols-2">
            <FormField id="tr-from" label="From warehouse" required>
              <Select value={fromWh} onValueChange={setFromWh}>
                <SelectTrigger id="tr-from"><SelectValue /></SelectTrigger>
                <SelectContent>
                  {warehouseCodes.map((c) => (
                    <SelectItem key={c} value={c}>{c}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </FormField>
            <FormField id="tr-to" label="To warehouse" required>
              <Select value={toWh} onValueChange={setToWh}>
                <SelectTrigger id="tr-to"><SelectValue /></SelectTrigger>
                <SelectContent>
                  {warehouseCodes.map((c) => (
                    <SelectItem key={c} value={c}>{c}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </FormField>
          </div>
          <FormField id="tr-qty" label="Quantity" required>
            <Input id="tr-qty" type="number" min={1} value={quantity} onChange={(e) => setQuantity(e.target.value)} required />
          </FormField>
          <FormField id="tr-notes" label="Notes">
            <Textarea id="tr-notes" value={notes} onChange={(e) => setNotes(e.target.value)} rows={2} />
          </FormField>
          <OperationMessage error={err} success={msg} />
          <Button type="submit" disabled={mutation.isPending}>
            <ArrowLeftRight className="mr-2 size-4" />
            {mutation.isPending ? "Processing…" : "Transfer stock"}
          </Button>
        </form>
      </AdminCard>
    </Can>
    </AdminAuthGate>
  );
}

function PoStatusBadge({ status }: { status: AdminPurchaseOrder["status"] }) {
  const variant =
    status === "received" ? "secondary" : status === "cancelled" ? "destructive" : "warning";
  return <Badge variant={variant}>{status.replace("_", " ")}</Badge>;
}

function PurchaseOrdersTab() {
  const warehouseCodes = useWarehouseCodes();
  const { data: orders, isError: ordersError } = usePurchaseOrders();
  const { data: suppliers, isError: suppliersError } = useAdminSuppliers();
  const createPo = useCreatePurchaseOrder();
  const receivePo = useReceivePurchaseOrder();
  const submitPo = useSubmitPurchaseOrder();
  const confirmPo = useConfirmPurchaseOrder();
  const cancelPo = useCancelPurchaseOrder();

  const [supplierId, setSupplierId] = useState("");
  const [warehouse, setWarehouse] = useState("");
  const [lineSku, setLineSku] = useState("");
  const [lineQty, setLineQty] = useState("10");
  const [lineCost, setLineCost] = useState("");
  const [msg, setMsg] = useState<string | null>(null);

  if (!hasAuthTokens()) {
    return (
      <AdminErrorState message="Sign in to manage purchase orders via the API." />
    );
  }

  if (ordersError || suppliersError) {
    return (
      <AdminErrorState message="Could not load purchase orders or suppliers from the API." />
    );
  }

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    const supplier = suppliers?.find((s) => s.id === supplierId);
    if (!supplier) return;
    await createPo.mutateAsync({
      payload: {
        supplierId,
        warehouseCode: warehouse,
        lines: [
          {
            sku: lineSku,
            quantity: Number(lineQty),
            unitCostCents: Math.round(Number(lineCost) * 100),
          },
        ],
      },
      supplierName: supplier.name,
    });
    setMsg("Purchase order created");
  };

  const handleReceive = async (po: AdminPurchaseOrder) => {
    const line = po.lines.find((l) => l.quantityReceived < l.quantityOrdered);
    if (!line) return;
    const remaining = line.quantityOrdered - line.quantityReceived;
    await receivePo.mutateAsync({
      poId: po.id,
      receipts: [{ lineId: line.id, quantity: remaining }],
    });
    setMsg(`Received ${remaining} × ${line.sku} for ${po.poNumber}`);
  };

  return (
    <div className="space-y-6">
      <Can permission={Permission.SUPPLIERS_MANAGE}>
        <AdminCard title="Create purchase order" description="Order stock from a supplier into a warehouse.">
          <form onSubmit={handleCreate} className="grid max-w-lg gap-4">
            <FormField id="po-supplier" label="Supplier" required>
              <Select value={supplierId} onValueChange={setSupplierId}>
                <SelectTrigger id="po-supplier"><SelectValue placeholder="Select supplier" /></SelectTrigger>
                <SelectContent>
                  {suppliers?.map((s) => (
                    <SelectItem key={s.id} value={s.id}>{s.name}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </FormField>
            <FormField id="po-wh" label="Receiving warehouse" required>
              <Select value={warehouse} onValueChange={setWarehouse}>
                <SelectTrigger id="po-wh"><SelectValue /></SelectTrigger>
                <SelectContent>
                  {warehouseCodes.map((c) => (
                    <SelectItem key={c} value={c}>{c}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </FormField>
            <FormField id="po-sku" label="SKU" required>
              <Input id="po-sku" value={lineSku} onChange={(e) => setLineSku(e.target.value)} required />
            </FormField>
            <div className="grid gap-4 sm:grid-cols-2">
              <FormField id="po-qty" label="Quantity" required>
                <Input id="po-qty" type="number" min={1} value={lineQty} onChange={(e) => setLineQty(e.target.value)} />
              </FormField>
              <FormField id="po-cost" label="Unit cost (AUD)" required>
                <Input id="po-cost" type="number" min={0} step="0.01" value={lineCost} onChange={(e) => setLineCost(e.target.value)} />
              </FormField>
            </div>
            <Button type="submit" disabled={createPo.isPending}>Create PO</Button>
          </form>
        </AdminCard>
      </Can>

      {msg ? <p className="text-sm text-green-600">{msg}</p> : null}

      <AdminCard title="Purchase orders" contentClassName="p-0">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>PO #</TableHead>
              <TableHead>Supplier</TableHead>
              <TableHead>Warehouse</TableHead>
              <TableHead>Status</TableHead>
              <TableHead className="text-right">Total (ex GST)</TableHead>
              <TableHead />
            </TableRow>
          </TableHeader>
          <TableBody>
            {orders?.map((po) => (
              <TableRow key={po.id}>
                <TableCell className="font-mono text-xs">{po.poNumber}</TableCell>
                <TableCell>{po.supplierName}</TableCell>
                <TableCell>{po.warehouseCode}</TableCell>
                <TableCell><PoStatusBadge status={po.status} /></TableCell>
                <TableCell className="text-right tabular-nums">
                  ${(po.totalExGstCents / 100).toFixed(2)}
                </TableCell>
                <TableCell className="text-right">
                  {po.status === "draft" ? (
                    <Button size="sm" variant="outline" onClick={() => submitPo.mutate(po.id)}>
                      Submit
                    </Button>
                  ) : null}
                  {po.status === "submitted" ? (
                    <Button size="sm" variant="outline" onClick={() => confirmPo.mutate(po.id)}>
                      Approve
                    </Button>
                  ) : null}
                  {po.status === "confirmed" || po.status === "partial_received" ? (
                    <Can permission={Permission.INVENTORY_MANAGE}>
                      <Button size="sm" variant="outline" onClick={() => handleReceive(po)}>
                        Receive
                      </Button>
                    </Can>
                  ) : null}
                  {po.status !== "received" && po.status !== "cancelled" ? (
                    <Button
                      size="sm"
                      variant="ghost"
                      className="text-destructive"
                      onClick={() => cancelPo.mutate(po.id)}
                    >
                      Close
                    </Button>
                  ) : null}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </AdminCard>
    </div>
  );
}

function LowStockTab() {
  const api = useLowStockAlertsApi();
  const data = api.data?.data ?? [];

  return (
    <AdminAuthGate>
      <AdminCard
        title="Low stock alerts"
        description="SKUs at or below reorder point."
        contentClassName="p-0"
      >
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>SKU</TableHead>
              <TableHead>Product</TableHead>
              <TableHead>Warehouse</TableHead>
              <TableHead className="text-right">On hand</TableHead>
              <TableHead className="text-right">Reorder at</TableHead>
              <TableHead className="text-right">Shortfall</TableHead>
              <TableHead>Alert</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {api.isLoading ? (
              <TableRow>
                <TableCell colSpan={7} className="text-center text-muted-foreground">
                  Loading alerts…
                </TableCell>
              </TableRow>
            ) : null}
            {(api.isLoading ? [] : data).map((row) => (
              <TableRow key={row.id}>
                <TableCell className="font-mono text-xs">{row.sku}</TableCell>
                <TableCell className="font-medium">{row.product_name}</TableCell>
                <TableCell>{row.warehouse_code}</TableCell>
                <TableCell className="text-right">{row.quantity_on_hand}</TableCell>
                <TableCell className="text-right">{row.reorder_point}</TableCell>
                <TableCell className="text-right font-medium text-amber-600">{row.shortfall}</TableCell>
                <TableCell>
                  <Badge variant={row.alert_level === "out_of_stock" ? "destructive" : "warning"}>
                    <AlertTriangle className="mr-1 size-3" />
                    {row.alert_level === "out_of_stock" ? "Out of stock" : "Low stock"}
                  </Badge>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
        {api.isError ? (
          <p className="p-4 text-sm text-destructive">Failed to load low stock alerts from the API.</p>
        ) : null}
      </AdminCard>
    </AdminAuthGate>
  );
}

function MovementsTab() {
  const api = useStockMovementsApi();
  const items = api.data?.data ?? [];

  return (
    <AdminAuthGate>
      <AdminCard title="Stock movement ledger" contentClassName="p-0">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Movement #</TableHead>
              <TableHead>Type</TableHead>
              <TableHead>SKU</TableHead>
              <TableHead>Warehouse</TableHead>
              <TableHead className="text-right">Qty</TableHead>
              <TableHead className="text-right">Value ex GST</TableHead>
              <TableHead className="text-right">Balance</TableHead>
              <TableHead>When</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {api.isLoading ? (
              <TableRow>
                <TableCell colSpan={8} className="text-center text-muted-foreground">
                  Loading movements…
                </TableCell>
              </TableRow>
            ) : null}
            {items.map((m) => (
              <TableRow key={m.id}>
                <TableCell className="font-mono text-xs">{m.movement_number}</TableCell>
                <TableCell>{m.transaction_type.replace(/_/g, " ")}</TableCell>
                <TableCell className="font-mono text-xs">{m.sku}</TableCell>
                <TableCell>{m.warehouse_code}</TableCell>
                <TableCell className="text-right">{m.quantity}</TableCell>
                <TableCell className="text-right tabular-nums">
                  {m.value_ex_gst_cents != null ? formatAudFromCents(m.value_ex_gst_cents) : "—"}
                </TableCell>
                <TableCell className="text-right">{m.quantity_after}</TableCell>
                <TableCell className="text-muted-foreground text-xs">
                  {new Date(m.created_at).toLocaleString("en-AU")}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
        {api.isError ? (
          <p className="p-4 text-sm text-destructive">Failed to load stock movements from the API.</p>
        ) : null}
      </AdminCard>
    </AdminAuthGate>
  );
}

function TransfersListTab() {
  const { data, isLoading, isError } = useTransfersApi();

  if (!hasAuthTokens()) {
    return (
      <AdminCard title="Transfer history">
        <AdminErrorState message="Sign in to view the transfer ledger from the API." />
      </AdminCard>
    );
  }

  return (
    <AdminCard title="Warehouse transfer ledger" contentClassName="p-0">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Transfer ID</TableHead>
            <TableHead>SKU</TableHead>
            <TableHead>From → To</TableHead>
            <TableHead className="text-right">Qty</TableHead>
            <TableHead>By</TableHead>
            <TableHead>When</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {isLoading ? (
            <TableRow>
              <TableCell colSpan={6}>Loading…</TableCell>
            </TableRow>
          ) : null}
          {data?.data.map((t) => (
            <TableRow key={t.transfer_group_id}>
              <TableCell className="font-mono text-[10px]">{t.transfer_group_id.slice(0, 8)}…</TableCell>
              <TableCell className="font-mono text-xs">{t.sku}</TableCell>
              <TableCell>
                {t.from_warehouse_code} → {t.to_warehouse_code ?? "—"}
              </TableCell>
              <TableCell className="text-right">{t.quantity}</TableCell>
              <TableCell className="text-xs text-muted-foreground">{t.created_by_email ?? "—"}</TableCell>
              <TableCell className="text-xs text-muted-foreground">
                {new Date(t.created_at).toLocaleString("en-AU")}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
      {isError ? (
        <p className="p-4 text-sm text-destructive">Failed to load transfers from the API.</p>
      ) : null}
    </AdminCard>
  );
}

function InventoryWmsView() {
  return (
    <AdminListPage
      title="Inventory Management"
      description="Production WMS — ledger, transfers, reorder levels, notifications, and AUD valuation (ex-GST)."
    >
      <Tabs defaultValue="levels">
        <TabsList className="flex h-auto flex-wrap gap-1">
          <TabsTrigger value="levels">Stock levels</TabsTrigger>
          <TabsTrigger value="movements">Movement ledger</TabsTrigger>
          <TabsTrigger value="transfer-ledger">Transfer ledger</TabsTrigger>
          <TabsTrigger value="valuation">Valuation</TabsTrigger>
          <TabsTrigger value="notifications">Notifications</TabsTrigger>
          <TabsTrigger value="stock-in">Stock in</TabsTrigger>
          <TabsTrigger value="stock-out">Stock out</TabsTrigger>
          <TabsTrigger value="adjustments">Adjustments</TabsTrigger>
          <TabsTrigger value="transfers">New transfer</TabsTrigger>
          <TabsTrigger value="purchase-orders">Purchase orders</TabsTrigger>
          <TabsTrigger value="alerts">Low stock</TabsTrigger>
        </TabsList>
        <TabsContent value="levels"><StockLevelsTab /></TabsContent>
        <TabsContent value="movements"><MovementsTab /></TabsContent>
        <TabsContent value="transfer-ledger"><TransfersListTab /></TabsContent>
        <TabsContent value="valuation"><ValuationTab /></TabsContent>
        <TabsContent value="notifications"><NotificationsTab /></TabsContent>
        <TabsContent value="stock-in"><StockInTab /></TabsContent>
        <TabsContent value="stock-out"><StockOutTab /></TabsContent>
        <TabsContent value="adjustments"><AdjustmentTab /></TabsContent>
        <TabsContent value="transfers"><TransferTab /></TabsContent>
        <TabsContent value="purchase-orders"><PurchaseOrdersTab /></TabsContent>
        <TabsContent value="alerts"><LowStockTab /></TabsContent>
      </Tabs>
    </AdminListPage>
  );
}

export { InventoryWmsView };
