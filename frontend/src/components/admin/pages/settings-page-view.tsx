"use client";

import { AdminCard } from "@/components/admin/shared/admin-card";
import { AdminListPage } from "@/components/admin/shared/admin-list-page";
import {
  useCompanySettings,
  useEmailSettings,
  useGstSettings,
  usePaymentSettings,
  useShippingSettings,
} from "@/lib/api/admin/hooks";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Separator } from "@/components/ui/separator";
import { Spinner } from "@/components/ui/spinner";

function SettingsField({
  label,
  value,
  readOnly = true,
}: {
  label: string;
  value: string | number | boolean;
  readOnly?: boolean;
}) {
  if (typeof value === "boolean") {
    return (
      <div className="flex items-center gap-2">
        <Checkbox checked={value} disabled={readOnly} />
        <Label className="font-normal">{label}</Label>
      </div>
    );
  }
  return (
    <div className="space-y-1.5">
      <Label>{label}</Label>
      <Input value={String(value)} readOnly={readOnly} />
    </div>
  );
}

function SettingsPageView() {
  const company = useCompanySettings();
  const gst = useGstSettings();
  const shipping = useShippingSettings();
  const email = useEmailSettings();
  const payment = usePaymentSettings();

  const loading =
    company.isLoading ||
    gst.isLoading ||
    shipping.isLoading ||
    email.isLoading ||
    payment.isLoading;

  if (loading) {
    return (
      <div className="flex min-h-[40vh] items-center justify-center">
        <Spinner className="size-8" />
      </div>
    );
  }

  return (
    <AdminListPage
      title="Settings"
      description="Company, GST, shipping, email, and payment gateway configuration."
      actions={<Button size="sm">Save changes</Button>}
    >
      <div className="grid gap-6 lg:grid-cols-2">
        <AdminCard title="Company information">
          {company.data ? (
            <div className="space-y-4">
              <SettingsField label="Legal name" value={company.data.legalName} />
              <SettingsField label="Trading name" value={company.data.tradingName} />
              <SettingsField label="ABN" value={company.data.abn} />
              <SettingsField label="Address" value={company.data.address} />
              <SettingsField label="Phone" value={company.data.phone} />
              <SettingsField label="Email" value={company.data.email} />
            </div>
          ) : null}
        </AdminCard>

        <AdminCard title="GST settings (Australia)">
          {gst.data ? (
            <div className="space-y-4">
              <SettingsField label="GST rate" value={`${(gst.data.rate * 100).toFixed(0)}%`} />
              <SettingsField label="Display prices inc. GST" value={gst.data.displayPricesIncGst} />
              <SettingsField label="Tax invoice prefix" value={gst.data.taxInvoicePrefix} />
            </div>
          ) : null}
        </AdminCard>

        <AdminCard title="Shipping settings">
          {shipping.data ? (
            <div className="space-y-4">
              <SettingsField
                label="Free shipping threshold (AUD)"
                value={(shipping.data.freeShippingThresholdCents / 100).toFixed(2)}
              />
              <SettingsField label="Default carrier" value={shipping.data.defaultCarrier} />
              <SettingsField
                label="Standard rate ex. GST (AUD)"
                value={(shipping.data.standardRateCents / 100).toFixed(2)}
              />
            </div>
          ) : null}
        </AdminCard>

        <AdminCard title="Email settings">
          {email.data ? (
            <div className="space-y-4">
              <SettingsField label="From name" value={email.data.fromName} />
              <SettingsField label="From email" value={email.data.fromEmail} />
              <Separator />
              <SettingsField label="Order confirmation emails" value={email.data.orderConfirmation} />
              <SettingsField label="Shipping notification emails" value={email.data.shippingNotification} />
            </div>
          ) : null}
        </AdminCard>

        <AdminCard title="Payment gateway" className="lg:col-span-2">
          {payment.data ? (
            <div className="grid gap-4 sm:grid-cols-2">
              <SettingsField label="Provider" value={payment.data.provider} />
              <SettingsField label="Mode" value={payment.data.mode} />
              <div className="sm:col-span-2 space-y-1.5">
                <Label>Enabled methods</Label>
                <p className="text-sm text-muted-foreground">
                  {payment.data.enabledMethods.join(", ")}
                </p>
              </div>
            </div>
          ) : null}
        </AdminCard>
      </div>
    </AdminListPage>
  );
}

export { SettingsPageView };
