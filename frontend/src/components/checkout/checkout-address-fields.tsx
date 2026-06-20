"use client";

import type { CheckoutAddress } from "@/types/checkout";
import { AUSTRALIAN_STATES } from "@/lib/australian-address";
import { FormField } from "@/components/ui/form-field";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

export interface CheckoutAddressFieldsProps {
  idPrefix: string;
  address: CheckoutAddress;
  errors?: Partial<Record<keyof CheckoutAddress, string>>;
  onChange: (field: keyof CheckoutAddress, value: string) => void;
}

function CheckoutAddressFields({
  idPrefix,
  address,
  errors = {},
  onChange,
}: CheckoutAddressFieldsProps) {
  return (
    <div className="grid gap-4 sm:grid-cols-2">
      <FormField
        id={`${idPrefix}-line1`}
        label="Address Line 1"
        required
        error={errors.line1}
        className="sm:col-span-2"
      >
        <Input
          value={address.line1}
          onChange={(event) => onChange("line1", event.target.value)}
          placeholder="Unit / street number and name"
          autoComplete="address-line1"
        />
      </FormField>

      <FormField
        id={`${idPrefix}-line2`}
        label="Address Line 2"
        className="sm:col-span-2"
      >
        <Input
          value={address.line2}
          onChange={(event) => onChange("line2", event.target.value)}
          placeholder="Suite, level, building (optional)"
          autoComplete="address-line2"
        />
      </FormField>

      <FormField
        id={`${idPrefix}-city`}
        label="City"
        required
        error={errors.city}
      >
        <Input
          value={address.city}
          onChange={(event) => onChange("city", event.target.value)}
          placeholder="e.g. Parramatta"
          autoComplete="address-level2"
        />
      </FormField>

      <FormField
        id={`${idPrefix}-state`}
        label="State"
        required
        error={errors.state}
      >
        <Select
          value={address.state || undefined}
          onValueChange={(value) => onChange("state", value)}
        >
          <SelectTrigger id={`${idPrefix}-state`}>
            <SelectValue placeholder="Select state" />
          </SelectTrigger>
          <SelectContent>
            {AUSTRALIAN_STATES.map((state) => (
              <SelectItem key={state.value} value={state.value}>
                {state.value}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </FormField>

      <FormField
        id={`${idPrefix}-postcode`}
        label="Postcode"
        required
        error={errors.postcode}
        hint="4-digit Australian postcode"
      >
        <Input
          value={address.postcode}
          onChange={(event) =>
            onChange("postcode", event.target.value.replace(/\D/g, "").slice(0, 4))
          }
          placeholder="e.g. 2150"
          inputMode="numeric"
          autoComplete="postal-code"
          maxLength={4}
        />
      </FormField>

      <FormField id={`${idPrefix}-country`} label="Country">
        <Input value={address.country} disabled readOnly className="bg-muted/50" />
      </FormField>
    </div>
  );
}

export { CheckoutAddressFields };
