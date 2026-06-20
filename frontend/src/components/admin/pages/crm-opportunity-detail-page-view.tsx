"use client";

import Link from "next/link";
import { ArrowLeft, Loader2 } from "lucide-react";

import { AdminCard } from "@/components/admin/shared/admin-card";
import { CrmActivityForm } from "@/components/admin/crm/crm-activity-form";
import { CrmNoteForm } from "@/components/admin/crm/crm-note-form";
import { CrmTimelineFeed } from "@/components/admin/crm/crm-timeline-feed";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useCrmOpportunityDetail, useCrmTimeline, useUpdateCrmOpportunity } from "@/lib/api/admin/crm-hooks";

function formatAud(cents: number): string {
  return new Intl.NumberFormat("en-AU", { style: "currency", currency: "AUD" }).format(cents / 100);
}

export interface CrmOpportunityDetailPageViewProps {
  opportunityId: string;
}

function CrmOpportunityDetailPageView({ opportunityId }: CrmOpportunityDetailPageViewProps) {
  const { data: opp, isLoading, isError } = useCrmOpportunityDetail(opportunityId);
  const { data: timeline } = useCrmTimeline({ opportunityId });
  const update = useUpdateCrmOpportunity();

  if (isLoading) {
    return (
      <div className="flex min-h-[40vh] items-center justify-center">
        <Loader2 className="size-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (isError || !opp) {
    return (
      <div className="space-y-4">
        <Button variant="outline" asChild>
          <Link href="/admin-dashboard/crm/opportunities">
            <ArrowLeft className="mr-2 size-4" />
            Back to opportunities
          </Link>
        </Button>
        <p className="text-muted-foreground">Opportunity not found.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <Button variant="ghost" size="sm" asChild className="mb-2 -ml-2">
            <Link href="/admin-dashboard/crm/opportunities">
              <ArrowLeft className="mr-1 size-4" />
              Opportunities
            </Link>
          </Button>
          <h1 className="text-2xl font-bold tracking-tight">{opp.name}</h1>
          <div className="mt-2 flex flex-wrap gap-2">
            <Badge variant="secondary" className="capitalize">
              {opp.stage.replace("_", " ")}
            </Badge>
            <Badge className="capitalize">{opp.status}</Badge>
          </div>
        </div>
        {opp.status === "open" ? (
          <div className="flex gap-2">
            <Button
              variant="outline"
              onClick={() => void update.mutateAsync({ id: opportunityId, status: "lost" })}
              disabled={update.isPending}
            >
              Mark lost
            </Button>
            <Button
              onClick={() => void update.mutateAsync({ id: opportunityId, status: "won" })}
              disabled={update.isPending}
            >
              Mark won
            </Button>
          </div>
        ) : null}
      </div>

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <div className="rounded-xl border border-border bg-card p-4">
          <p className="text-sm text-muted-foreground">Expected revenue</p>
          <p className="mt-1 text-xl font-bold tabular-nums">{formatAud(opp.expectedRevenueCents)}</p>
        </div>
        <div className="rounded-xl border border-border bg-card p-4">
          <p className="text-sm text-muted-foreground">Probability</p>
          <p className="mt-1 text-xl font-bold tabular-nums">{opp.probability}%</p>
        </div>
        <div className="rounded-xl border border-border bg-card p-4">
          <p className="text-sm text-muted-foreground">Weighted forecast</p>
          <p className="mt-1 text-xl font-bold tabular-nums">{formatAud(opp.weightedRevenueCents)}</p>
        </div>
        <div className="rounded-xl border border-border bg-card p-4">
          <p className="text-sm text-muted-foreground">Expected close</p>
          <p className="mt-1 text-xl font-bold">{opp.expectedCloseDate ?? "—"}</p>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <AdminCard title="Linked records" className="lg:col-span-1">
          <dl className="space-y-4 text-sm">
            <div>
              <dt className="text-muted-foreground">Party</dt>
              <dd className="font-medium">{opp.party.displayName}</dd>
              <dd className="text-muted-foreground">{opp.party.email}</dd>
            </div>
            {opp.customer ? (
              <div>
                <dt className="text-muted-foreground">Customer</dt>
                <dd className="font-medium">{opp.customer.organizationName ?? opp.customer.email}</dd>
                <dd className="text-muted-foreground">{opp.customer.customerType}</dd>
              </div>
            ) : (
              <p className="text-muted-foreground">No customer linked.</p>
            )}
            {opp.tradeAccount ? (
              <div>
                <dt className="text-muted-foreground">Trade account</dt>
                <dd className="font-medium">{opp.tradeAccount.accountNumber}</dd>
                <dd className="text-muted-foreground">{opp.tradeAccount.organizationName}</dd>
              </div>
            ) : (
              <p className="text-muted-foreground">No trade account linked.</p>
            )}
            {opp.quoteDraft ? (
              <div className="rounded-lg border border-success/30 bg-success-light/20 p-3">
                <dt className="text-muted-foreground">Quotation draft</dt>
                <dd className="font-semibold">
                  {opp.quoteDraft.id ? (
                    <Link
                      href={`/admin-dashboard/quotes/${opp.quoteDraft.id}`}
                      className="hover:underline"
                    >
                      {opp.quoteDraft.quoteNumber}
                    </Link>
                  ) : (
                    opp.quoteDraft.quoteNumber
                  )}
                </dd>
                <dd className="text-muted-foreground">{formatAud(opp.quoteDraft.totalIncGstCents)}</dd>
                <dd className="text-xs text-muted-foreground capitalize">
                  {opp.quoteDraft.status?.replace(/_/g, " ") ?? "draft"} · Valid until{" "}
                  {new Date(opp.quoteDraft.validUntil).toLocaleDateString("en-AU")}
                </dd>
              </div>
            ) : null}
          </dl>
        </AdminCard>

        <div className="space-y-6 lg:col-span-2">
          <AdminCard title="Timeline">
            <CrmTimelineFeed entries={timeline ?? []} />
          </AdminCard>
          <div className="grid gap-6 md:grid-cols-2">
            <AdminCard title="Add note">
              <CrmNoteForm opportunityId={opportunityId} />
            </AdminCard>
            <AdminCard title="Log activity">
              <CrmActivityForm opportunityId={opportunityId} />
            </AdminCard>
          </div>
        </div>
      </div>
    </div>
  );
}

export { CrmOpportunityDetailPageView };
