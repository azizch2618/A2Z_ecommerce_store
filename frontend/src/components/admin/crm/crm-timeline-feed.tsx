import type { CrmTimelineEntry } from "@/lib/api/admin/types";

export interface CrmTimelineFeedProps {
  entries: CrmTimelineEntry[];
}

function CrmTimelineFeed({ entries }: CrmTimelineFeedProps) {
  if (entries.length === 0) {
    return <p className="text-sm text-muted-foreground">No activity yet.</p>;
  }

  return (
    <ol className="relative space-y-4 border-l border-border pl-4">
      {entries.map((entry) => (
        <li key={entry.id} className="space-y-1">
          <div className="flex flex-wrap items-center gap-2 text-sm">
            <span className="font-medium">{entry.title}</span>
            {entry.activityType ? (
              <span className="rounded bg-muted px-1.5 py-0.5 text-xs capitalize text-muted-foreground">
                {entry.activityType.replace("_", " ")}
              </span>
            ) : null}
            <time className="text-xs text-muted-foreground">
              {new Date(entry.occurredAt).toLocaleString("en-AU")}
            </time>
          </div>
          {entry.body ? <p className="text-sm text-muted-foreground">{entry.body}</p> : null}
          {entry.actorEmail ? (
            <p className="text-xs text-muted-foreground">by {entry.actorEmail}</p>
          ) : null}
        </li>
      ))}
    </ol>
  );
}

export { CrmTimelineFeed };
