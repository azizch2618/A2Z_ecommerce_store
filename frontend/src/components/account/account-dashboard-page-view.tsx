"use client";

import * as React from "react";
import Link from "next/link";
import { Loader2 } from "lucide-react";

import { getAccountBreadcrumbs } from "@/config/account";
import { mapApiOrderToAccountOrder } from "@/lib/api/mappers/account-mapper";
import { useAuth, useCurrentUser } from "@/lib/api/hooks/use-auth";
import { useOrders } from "@/lib/api/hooks/use-orders";
import { useQuotes } from "@/lib/api/hooks/use-trade-account";
import { useWishlistQuery } from "@/lib/api/hooks/use-wishlist";
import {
  AccountOrdersTable,
  AccountShell,
  AccountStatsGrid,
} from "@/components/account";
import { PageBreadcrumbs } from "@/components/layout/breadcrumbs";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { ArrowRight, Package } from "lucide-react";

function AccountDashboardPageView() {
  const { isLoading: authLoading } = useAuth();
  const { data: user } = useCurrentUser();
  const { data: ordersData, isLoading: ordersLoading } = useOrders({ limit: 100 });
  const { data: wishlist } = useWishlistQuery();
  const { data: quotesData } = useQuotes({ limit: 5 });

  if (authLoading || ordersLoading) {
    return (
      <div className="flex min-h-[40vh] items-center justify-center">
        <Loader2 className="size-8 animate-spin text-brand-blue" />
      </div>
    );
  }

  const orders = (ordersData?.data ?? []).map(mapApiOrderToAccountOrder);
  const activeOrders = orders.filter(
    (order) => order.status === "processing" || order.status === "shipped"
  ).length;
  const quotes = quotesData?.data ?? [];
  const memberSince = user?.created_at
    ? new Intl.DateTimeFormat("en-AU", { month: "long", year: "numeric" }).format(
        new Date(user.created_at)
      )
    : "";

  return (
    <>
      <PageBreadcrumbs items={getAccountBreadcrumbs("Dashboard")} />
      <AccountShell
        title={`G'day, ${user?.first_name ?? "there"}`}
        description={
          user?.organization?.trading_name || user?.organization?.legal_name
            ? `Member since ${memberSince} · ${user.organization.trading_name ?? user.organization.legal_name}`
            : memberSince
              ? `Member since ${memberSince}`
              : "Your A2Z Tools account"
        }
      >
        <div className="space-y-8">
          <AccountStatsGrid
            stats={{
              totalOrders: orders.length,
              activeOrders,
              wishlistItems: wishlist?.item_count ?? 0,
              savedQuotes: quotes.length,
            }}
          />

          <Card>
            <CardHeader className="flex flex-row items-center justify-between gap-4 space-y-0">
              <div>
                <CardTitle className="text-lg">Recent orders</CardTitle>
                <CardDescription>Your latest purchases and deliveries</CardDescription>
              </div>
              <Package className="size-5 text-brand-blue" aria-hidden />
            </CardHeader>
            <CardContent>
              <AccountOrdersTable orders={orders} limit={3} showViewAll />
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Active quotes</CardTitle>
              <CardDescription>Project quotes awaiting approval or acceptance</CardDescription>
            </CardHeader>
            <CardContent>
              {quotes.length === 0 ? (
                <p className="text-sm text-muted-foreground">No active quotes.</p>
              ) : (
                <ul className="space-y-3">
                  {quotes
                    .filter((q) => q.status === "sent" || q.status === "draft")
                    .slice(0, 2)
                    .map((quote) => (
                      <li
                        key={quote.id}
                        className="flex items-center justify-between gap-4 rounded-lg border border-border px-4 py-3"
                      >
                        <div className="min-w-0">
                          <p className="truncate text-sm font-medium text-foreground">
                            {`Quote ${quote.quote_number}`}
                          </p>
                        </div>
                        <Button asChild variant="ghost" size="sm" className="shrink-0 gap-1">
                          <Link href="/account/trade">
                            View
                            <ArrowRight className="size-3.5" />
                          </Link>
                        </Button>
                      </li>
                    ))}
                </ul>
              )}
            </CardContent>
          </Card>
        </div>
      </AccountShell>
    </>
  );
}

export { AccountDashboardPageView };
