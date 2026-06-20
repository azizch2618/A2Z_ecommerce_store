"use client";

import { useQuery } from "@tanstack/react-query";

import { fetchPaymentConfig } from "../services/payments.service";
import { queryKeys } from "./query-keys";

export function usePaymentConfig() {
  return useQuery({
    queryKey: queryKeys.payments.config(),
    queryFn: fetchPaymentConfig,
    staleTime: 300_000,
  });
}
