"use client";

import Link from "next/link";
import { ArrowLeft, Loader2 } from "lucide-react";

import { AdminCard } from "@/components/admin/shared/admin-card";
import { CrmActivityForm } from "@/components/admin/crm/crm-activity-form";
import { CrmNoteForm } from "@/components/admin/crm/crm-note-form";
import { CrmTimelineFeed } from "@/components/admin/crm/crm-timeline-feed";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { useConvertCrmLead, useCrmLeadDetail, useCrmTimeline } from "@/lib/api/admin/crm-hooks";

function formatAud(cents: number): string {
  return new Intl.NumberFormat("en-AU", { style: "currency", currency: "AUD" }).format(cents / 100);
}

export interface CrmLeadDetailPageViewProps {
  leadId: string;
}

function CrmLeadDetailPageView({ leadId }: CrmLeadDetailPageViewProps) {
  const { data: lead, isLoading, isError } = useCrmLeadDetail(leadId);
  const { data: timeline } = useCrmTimeline({ leadId });
  const convert = useConvertCrmLead();

  if (isLoading) {
    return (
      <div className="flex min-h-[40vh] items-center justify-center">
        <Loader2 className="size-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (isError || !lead) {
    return (
      <div className="space-y-4">
        <Button variant="outline" asChild>
          <Link href="/admin-dashboard/crm/leads">
            <ArrowLeft className="mr-2 size-4" />
            Back to leads
          </Link>
        </Button>
        <p className="text-muted-foreground">Lead not found.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <Button variant="ghost" size="sm" asChild className="mb-2 -ml-2">
            <Link href="/admin-dashboard/crm/leads">
              <ArrowLeft className="mr-1 size-4" />
              Leads
            </Link>
          </Button>
          <h1 className="text-2xl font-bold tracking-tight">{lead.title}</h1>
          <div className="mt-2 flex flex-wrap gap-2">
            <Badge className="capitalize">{lead.status.replace("_", " ")}</Badge>
            <Badge variant="secondary" className="capitalize">
              {lead.source.replace("_", " ")}
            </Badge>
          </div>
        </div>
        <Button
          onClick={() =>
            void convert.mutateAsync({
              id: leadId,
              name: lead.title,
              expectedRevenueCents: 0,
            })
          }
          disabled={convert.isPending}
        >
          Convert to opportunity
        </Button>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <AdminCard title="Lead info" className="lg:col-span-1">
          <dl className="space-y-3 text-sm">
            <div>
              <dt className="text-muted-foreground">Company</dt>
              <dd className="font-medium">{lead.companyName || "—"}</dd>
            </div>
            <div>
              <dt className="text-muted-foreground">Contact</dt>
              <dd className="font-medium">{lead.contactName || "—"}</dd>
              <dd className="text-muted-foreground">{lead.contactEmail}</dd>
              <dd className="text-muted-foreground">{lead.contactPhone}</dd>
            </div>
            <div>
              <dt className="text-muted-foreground">Assigned to</dt>
              <dd className="font-medium">{lead.assignedTo?.name ?? "—"}</dd>
            </div>
            {lead.party ? (
              <div>
                <dt className="text-muted-foreground">Party</dt>
                <dd className="font-medium">{lead.party.displayName}</dd>
              </div>
            ) : null}
            {lead.notesSummary ? (
              <div>
                <dt className="text-muted-foreground">Summary</dt>
                <dd>{lead.notesSummary}</dd>
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
              <CrmNoteForm leadId={leadId} />
            </AdminCard>
            <AdminCard title="Log activity">
              <CrmActivityForm leadId={leadId} />
            </AdminCard>
          </div>

          <AdminCard title="Notes">
            {lead.notes.length === 0 ? (
              <p className="text-sm text-muted-foreground">No notes yet.</p>
            ) : (
              <ul className="space-y-3">
                {lead.notes.map((note) => (
                  <li key={note.id} className="rounded-lg border border-border p-3 text-sm">
                    <p>{note.body}</p>
                    <p className="mt-1 text-xs text-muted-foreground">
                      {note.createdBy?.email ?? "System"} ·{" "}
                      {new Date(note.createdAt).toLocaleString("en-AU")}
                    </p>
                  </li>
                ))}
              </ul>
            )}
          </AdminCard>

          <AdminCard title="Activities">
            {lead.activities.length === 0 ? (
              <p className="text-sm text-muted-foreground">No activities logged.</p>
            ) : (
              <ul className="space-y-2 text-sm">
                {lead.activities.map((a) => (
                  <li key={a.id} className="flex justify-between gap-2 border-b border-border pb-2">
                    <span>
                      <span className="font-medium">{a.subject}</span>
                      <span className="ml-2 capitalize text-muted-foreground">
                        ({a.activityType.replace("_", " ")})
                      </span>
                    </span>
                    <span className="text-xs text-muted-foreground">
                      {new Date(a.createdAt).toLocaleDateString("en-AU")}
                    </span>
                  </li>
                ))}
              </ul>
            )}
          </AdminCard>

          <AdminCard title="Opportunities">
            {lead.opportunities.length === 0 ? (
              <p className="text-sm text-muted-foreground">No linked opportunities.</p>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Name</TableHead>
                    <TableHead>Stage</TableHead>
                    <TableHead className="text-right">Expected</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {lead.opportunities.map((opp) => (
                    <TableRow key={opp.id}>
                      <TableCell>
                        <Link
                          href={`/admin-dashboard/crm/opportunities/${opp.id}`}
                          className="font-medium hover:underline"
                        >
                          {opp.name}
                        </Link>
                      </TableCell>
                      <TableCell className="capitalize">{opp.stage.replace("_", " ")}</TableCell>
                      <TableCell className="text-right tabular-nums">
                        {formatAud(opp.expectedRevenueCents)}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </AdminCard>
        </div>
      </div>
    </div>
  );
}

export { CrmLeadDetailPageView };
