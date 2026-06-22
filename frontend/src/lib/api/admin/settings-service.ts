import { apiGet } from "../client";
import { API_DEFAULTS, API_ENDPOINTS } from "../config";
import { hasAuthTokens } from "../auth/token-storage";
import type {
  CompanySettings,
  EmailSettings,
  GstSettings,
  PaymentGatewaySettings,
  ShippingSettings,
} from "./types";
import { withAdminApiLog } from "./log-admin-api-error";

interface CompanyApiResponse {
  legal_name: string;
  trading_name: string;
  abn: string;
  email: string;
  phone: string;
  metadata?: { address?: string };
}

interface PlatformSettingRow {
  key: string;
  value: Record<string, unknown>;
}

interface PlatformSettingsResponse {
  data: PlatformSettingRow[];
}

function requireAuth(): void {
  if (!hasAuthTokens()) {
    throw new Error("Admin authentication required");
  }
}

async function fetchPlatformSettingsMap(): Promise<Map<string, Record<string, unknown>>> {
  const response = await apiGet<PlatformSettingsResponse>(API_ENDPOINTS.platform.settings);
  return new Map(response.data.map((row) => [row.key, row.value ?? {}]));
}

function readSetting<T>(
  settings: Map<string, Record<string, unknown>>,
  key: string,
  field: string,
  fallback: T
): T {
  const value = settings.get(key)?.[field];
  return (value === undefined ? fallback : value) as T;
}

export async function fetchCompanySettings(): Promise<CompanySettings> {
  requireAuth();
  return withAdminApiLog("settings/company", async () => {
    const company = await apiGet<CompanyApiResponse>(API_ENDPOINTS.platform.company);
    return {
      legalName: company.legal_name,
      tradingName: company.trading_name ?? "",
      abn: company.abn ?? "",
      address: company.metadata?.address ?? "",
      phone: company.phone ?? "",
      email: company.email ?? "",
    };
  });
}

export async function fetchGstSettings(): Promise<GstSettings> {
  requireAuth();
  return withAdminApiLog("settings/gst", async () => {
    const settings = await fetchPlatformSettingsMap();
    return {
      rate: readSetting(settings, "gst", "rate", API_DEFAULTS.gstRate),
      displayPricesIncGst: readSetting(settings, "gst", "display_prices_inc_gst", true),
      taxInvoicePrefix: readSetting(settings, "gst", "tax_invoice_prefix", "INV"),
    };
  });
}

export async function fetchShippingSettings(): Promise<ShippingSettings> {
  requireAuth();
  return withAdminApiLog("settings/shipping", async () => {
    const settings = await fetchPlatformSettingsMap();
    return {
      freeShippingThresholdCents: readSetting(
        settings,
        "shipping",
        "free_shipping_threshold_cents",
        15000
      ),
      defaultCarrier: readSetting(settings, "shipping", "default_carrier", "Australia Post"),
      standardRateCents: readSetting(settings, "shipping", "standard_rate_cents", 1295),
    };
  });
}

export async function fetchEmailSettings(): Promise<EmailSettings> {
  requireAuth();
  return withAdminApiLog("settings/email", async () => {
    const settings = await fetchPlatformSettingsMap();
    return {
      fromName: readSetting(settings, "email", "from_name", "A2Z Tools"),
      fromEmail: readSetting(settings, "email", "from_email", "noreply@a2ztools.com.au"),
      orderConfirmation: readSetting(settings, "email", "order_confirmation", true),
      shippingNotification: readSetting(settings, "email", "shipping_notification", true),
    };
  });
}

export async function fetchPaymentSettings(): Promise<PaymentGatewaySettings> {
  requireAuth();
  return withAdminApiLog("settings/payment", async () => {
    const settings = await fetchPlatformSettingsMap();
    const rawMode = readSetting<string>(settings, "payment", "mode", "test");
    return {
      provider: readSetting(settings, "payment", "provider", "stripe"),
      mode: rawMode === "live" ? "live" : "test",
      enabledMethods: readSetting(settings, "payment", "enabled_methods", [
        "card",
        "paypal",
        "trade_credit",
      ]),
    };
  });
}
