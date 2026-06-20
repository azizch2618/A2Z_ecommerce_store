"use client";

import {
  useMutation,
  useQuery,
  useQueryClient,
  type UseQueryOptions,
} from "@tanstack/react-query";

import { hasAuthTokens } from "../auth/token-storage";
import {
  applyForTradeAccount,
  fetchQuoteById,
  fetchQuotes,
  fetchTradeAccount,
} from "../services/trade-accounts.service";
import type {
  Quote,
  QuoteListParams,
  QuoteListResponse,
  TradeAccount,
  TradeAccountApplyPayload,
} from "../types/trade-account";
import { queryKeys } from "./query-keys";

export function useTradeAccount(
  options?: Omit<UseQueryOptions<TradeAccount, Error>, "queryKey" | "queryFn">
) {
  return useQuery({
    queryKey: queryKeys.tradeAccounts.me(),
    queryFn: fetchTradeAccount,
    enabled: hasAuthTokens(),
    staleTime: 60_000,
    ...options,
  });
}

export function useQuotes(
  params?: QuoteListParams,
  options?: Omit<
    UseQueryOptions<QuoteListResponse, Error>,
    "queryKey" | "queryFn"
  >
) {
  return useQuery({
    queryKey: queryKeys.tradeAccounts.quotes(params),
    queryFn: () => fetchQuotes(params),
    enabled: hasAuthTokens(),
    ...options,
  });
}

export function useQuote(
  quoteId: string,
  options?: Omit<UseQueryOptions<Quote, Error>, "queryKey" | "queryFn">
) {
  return useQuery({
    queryKey: queryKeys.tradeAccounts.quote(quoteId),
    queryFn: () => fetchQuoteById(quoteId),
    enabled: Boolean(quoteId) && hasAuthTokens(),
    ...options,
  });
}

export function useApplyForTradeAccount() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: TradeAccountApplyPayload) =>
      applyForTradeAccount(payload),
    onSuccess: () => {
      void queryClient.invalidateQueries({
        queryKey: queryKeys.tradeAccounts.all,
      });
      void queryClient.invalidateQueries({ queryKey: queryKeys.auth.me() });
    },
  });
}
