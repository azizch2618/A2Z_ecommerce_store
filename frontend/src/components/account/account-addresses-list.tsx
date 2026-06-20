"use client";

import * as React from "react";
import { MapPin, Pencil, Star, Trash2 } from "lucide-react";
import { toast } from "sonner";

import type { SavedAddress } from "@/types/account";
import type { AustralianState } from "@/lib/api/types/common";
import {
  useCreateAddress,
  useDeleteAddress,
  useUpdateAddress,
} from "@/lib/api/hooks/use-auth";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { FormField } from "@/components/ui/form-field";
import { Input } from "@/components/ui/input";

const AU_STATES: AustralianState[] = [
  "NSW",
  "VIC",
  "QLD",
  "SA",
  "WA",
  "TAS",
  "NT",
  "ACT",
];

const emptyForm = {
  label: "",
  line1: "",
  line2: "",
  suburb: "",
  state: "NSW" as AustralianState,
  postcode: "",
};

export interface AccountAddressesListProps {
  addresses: SavedAddress[];
}

function AccountAddressesList({ addresses }: AccountAddressesListProps) {
  const createAddress = useCreateAddress();
  const updateAddress = useUpdateAddress();
  const deleteAddress = useDeleteAddress();
  const [showForm, setShowForm] = React.useState(false);
  const [editingId, setEditingId] = React.useState<string | null>(null);
  const [form, setForm] = React.useState(emptyForm);

  const resetForm = () => {
    setForm(emptyForm);
    setEditingId(null);
    setShowForm(false);
  };

  const startEdit = (address: SavedAddress) => {
    setEditingId(address.id);
    setForm({
      label: address.label,
      line1: address.line1,
      line2: address.line2 ?? "",
      suburb: address.city,
      state: address.state as AustralianState,
      postcode: address.postcode,
    });
    setShowForm(true);
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    const payload = {
      label: form.label || "Address",
      line1: form.line1,
      line2: form.line2 || undefined,
      suburb: form.suburb,
      state: form.state,
      postcode: form.postcode,
      country: "AU",
    };

    try {
      if (editingId) {
        await updateAddress.mutateAsync({ addressId: editingId, payload });
        toast.success("Address updated");
      } else {
        await createAddress.mutateAsync(payload);
        toast.success("Address added");
      }
      resetForm();
    } catch {
      toast.error(editingId ? "Could not update address" : "Could not add address");
    }
  };

  const handleDelete = async (addressId: string) => {
    try {
      await deleteAddress.mutateAsync(addressId);
      toast.success("Address removed");
      if (editingId === addressId) resetForm();
    } catch {
      toast.error("Could not remove address");
    }
  };

  const isSaving = createAddress.isPending || updateAddress.isPending;

  return (
    <div className="space-y-4">
      <ul className="grid gap-4 md:grid-cols-2">
        {addresses.map((address) => (
          <li
            key={address.id}
            className="rounded-xl border border-border bg-card p-5 shadow-sm"
          >
            <div className="flex items-start justify-between gap-3">
              <div className="flex items-center gap-2">
                <MapPin className="size-4 text-brand-blue" aria-hidden />
                <h3 className="font-semibold text-foreground">{address.label}</h3>
              </div>
              {address.isDefault ? (
                <Badge variant="outline" className="gap-1 border-brand-blue/30 text-brand-blue">
                  <Star className="size-3" aria-hidden />
                  Default
                </Badge>
              ) : null}
            </div>
            <address className="mt-3 not-italic text-sm leading-relaxed text-muted-foreground">
              {address.line1}
              {address.line2 ? (
                <>
                  <br />
                  {address.line2}
                </>
              ) : null}
              <br />
              {address.city} {address.state} {address.postcode}
              <br />
              {address.country}
            </address>
            <div className="mt-4 flex gap-2">
              <Button
                type="button"
                variant="outline"
                size="sm"
                className="gap-1.5"
                onClick={() => startEdit(address)}
              >
                <Pencil className="size-3.5" />
                Edit
              </Button>
              <Button
                type="button"
                variant="ghost"
                size="sm"
                className="gap-1.5 text-muted-foreground"
                loading={deleteAddress.isPending}
                onClick={() => void handleDelete(address.id)}
              >
                <Trash2 className="size-3.5" />
                Remove
              </Button>
            </div>
          </li>
        ))}
      </ul>

      {showForm ? (
        <form
          onSubmit={handleSubmit}
          className="rounded-xl border border-border bg-card p-5 shadow-sm md:p-6"
        >
          <h3 className="text-lg font-semibold text-foreground">
            {editingId ? "Edit address" : "Add new address"}
          </h3>
          <div className="mt-4 grid gap-4 sm:grid-cols-2">
            <FormField id="address-label" label="Label" className="sm:col-span-2">
              <Input
                value={form.label}
                onChange={(e) => setForm((c) => ({ ...c, label: e.target.value }))}
                placeholder="Head office"
              />
            </FormField>
            <FormField id="address-line1" label="Street address" required className="sm:col-span-2">
              <Input
                value={form.line1}
                onChange={(e) => setForm((c) => ({ ...c, line1: e.target.value }))}
                required
              />
            </FormField>
            <FormField id="address-line2" label="Line 2" className="sm:col-span-2">
              <Input
                value={form.line2}
                onChange={(e) => setForm((c) => ({ ...c, line2: e.target.value }))}
              />
            </FormField>
            <FormField id="address-suburb" label="Suburb" required>
              <Input
                value={form.suburb}
                onChange={(e) => setForm((c) => ({ ...c, suburb: e.target.value }))}
                required
              />
            </FormField>
            <FormField id="address-state" label="State" required>
              <select
                id="address-state"
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                value={form.state}
                onChange={(e) =>
                  setForm((c) => ({ ...c, state: e.target.value as AustralianState }))
                }
              >
                {AU_STATES.map((state) => (
                  <option key={state} value={state}>
                    {state}
                  </option>
                ))}
              </select>
            </FormField>
            <FormField id="address-postcode" label="Postcode" required>
              <Input
                value={form.postcode}
                onChange={(e) =>
                  setForm((c) => ({
                    ...c,
                    postcode: e.target.value.replace(/\D/g, "").slice(0, 4),
                  }))
                }
                inputMode="numeric"
                required
              />
            </FormField>
          </div>
          <div className="mt-5 flex flex-wrap gap-2">
            <Button type="submit" loading={isSaving}>
              {editingId ? "Save address" : "Add address"}
            </Button>
            <Button type="button" variant="ghost" onClick={resetForm}>
              Cancel
            </Button>
          </div>
        </form>
      ) : (
        <div className="flex min-h-[120px] flex-col items-center justify-center rounded-xl border border-dashed border-border bg-muted/20 p-5 text-center">
          <MapPin className="size-8 text-muted-foreground" aria-hidden />
          <p className="mt-2 text-sm font-medium text-foreground">Add new address</p>
          <Button
            type="button"
            variant="outline"
            size="sm"
            className="mt-3"
            onClick={() => setShowForm(true)}
          >
            Add address
          </Button>
        </div>
      )}
    </div>
  );
}

export { AccountAddressesList };
