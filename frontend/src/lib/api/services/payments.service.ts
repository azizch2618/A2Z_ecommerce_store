import { apiGet } from "../client";
import { API_ENDPOINTS } from "../config";

export interface PaymentConfig {
  publishable_key: string;
  stripe_enabled: boolean;
}

export async function fetchPaymentConfig(): Promise<PaymentConfig> {
  return apiGet<PaymentConfig>(API_ENDPOINTS.payments.config);
}
