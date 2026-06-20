"use client";

import * as React from "react";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { FormField } from "@/components/ui/form-field";
import { Input } from "@/components/ui/input";
import { Separator } from "@/components/ui/separator";

export interface AccountSettingsFormProps {
  initialValues: {
    firstName: string;
    lastName: string;
    company: string;
    email: string;
    phone: string;
  };
  onSave: (values: {
    firstName: string;
    lastName: string;
    phone: string;
  }) => Promise<void>;
  isSaving?: boolean;
}

function AccountSettingsForm({
  initialValues,
  onSave,
  isSaving = false,
}: AccountSettingsFormProps) {
  const [form, setForm] = React.useState({
    ...initialValues,
    orderUpdates: true,
    quoteAlerts: true,
    marketingEmails: false,
  });

  React.useEffect(() => {
    setForm((current) => ({ ...current, ...initialValues }));
  }, [initialValues]);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    await onSave({
      firstName: form.firstName,
      lastName: form.lastName,
      phone: form.phone,
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-8">
      <section className="rounded-xl border border-border bg-card p-5 shadow-sm md:p-6">
        <h3 className="text-lg font-semibold text-foreground">Profile</h3>
        <p className="mt-1 text-sm text-muted-foreground">
          Update your contact details and business information.
        </p>
        <div className="mt-5 grid gap-4 sm:grid-cols-2">
          <FormField id="settings-firstName" label="First name">
            <Input
              value={form.firstName}
              onChange={(e) => setForm((c) => ({ ...c, firstName: e.target.value }))}
            />
          </FormField>
          <FormField id="settings-lastName" label="Last name">
            <Input
              value={form.lastName}
              onChange={(e) => setForm((c) => ({ ...c, lastName: e.target.value }))}
            />
          </FormField>
          <FormField id="settings-company" label="Company name" className="sm:col-span-2">
            <Input value={form.company} disabled />
          </FormField>
          <FormField id="settings-email" label="Email">
            <Input type="email" value={form.email} disabled />
          </FormField>
          <FormField id="settings-phone" label="Phone">
            <Input
              type="tel"
              value={form.phone}
              onChange={(e) => setForm((c) => ({ ...c, phone: e.target.value }))}
            />
          </FormField>
        </div>
      </section>

      <section className="rounded-xl border border-border bg-card p-5 shadow-sm md:p-6">
        <h3 className="text-lg font-semibold text-foreground">Notifications</h3>
        <p className="mt-1 text-sm text-muted-foreground">
          Choose which emails you receive from A2Z Tools.
        </p>
        <div className="mt-5 space-y-4">
          {[
            {
              key: "orderUpdates" as const,
              label: "Order updates",
              description: "Shipping, delivery, and invoice notifications.",
            },
            {
              key: "quoteAlerts" as const,
              label: "Quote alerts",
              description: "When quotes are sent, accepted, or expiring.",
            },
            {
              key: "marketingEmails" as const,
              label: "Product updates",
              description: "New arrivals, promotions, and trade offers.",
            },
          ].map(({ key, label, description }) => (
            <div
              key={key}
              className="flex items-center justify-between gap-4 rounded-lg border border-border/80 px-4 py-3"
            >
              <div>
                <p className="text-sm font-medium text-foreground">{label}</p>
                <p className="text-xs text-muted-foreground">{description}</p>
              </div>
              <Checkbox
                checked={form[key]}
                onCheckedChange={(checked) =>
                  setForm((c) => ({ ...c, [key]: checked === true }))
                }
                aria-label={label}
              />
            </div>
          ))}
        </div>
      </section>

      <section className="rounded-xl border border-border bg-card p-5 shadow-sm md:p-6">
        <h3 className="text-lg font-semibold text-foreground">Password</h3>
        <p className="mt-1 text-sm text-muted-foreground">
          Change your password or enable two-factor authentication (coming soon).
        </p>
        <Separator className="my-5" />
        <Button type="button" variant="outline">
          Change password
        </Button>
      </section>

      <div className="flex justify-end">
        <Button type="submit" loading={isSaving}>
          Save changes
        </Button>
      </div>
    </form>
  );
}

export { AccountSettingsForm };
