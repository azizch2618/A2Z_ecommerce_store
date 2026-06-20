"use client";

import Link from "next/link";
import {
  DndContext,
  DragOverlay,
  PointerSensor,
  useDraggable,
  useDroppable,
  useSensor,
  useSensors,
  type DragEndEvent,
  type DragStartEvent,
} from "@dnd-kit/core";
import { CSS } from "@dnd-kit/utilities";
import { useState } from "react";

import { useMoveCrmPipelineLead } from "@/lib/api/admin/crm-hooks";
import type { CrmLead, CrmLeadStatus, CrmPipelineColumns } from "@/lib/api/admin/types";
import { cn } from "@/lib/utils";

export const CRM_PIPELINE_STAGES: { id: CrmLeadStatus; label: string }[] = [
  { id: "new", label: "New" },
  { id: "contacted", label: "Contacted" },
  { id: "qualified", label: "Qualified" },
  { id: "proposal_sent", label: "Proposal Sent" },
  { id: "won", label: "Won" },
  { id: "lost", label: "Lost" },
];

function LeadCard({ lead, isDragging }: { lead: CrmLead; isDragging?: boolean }) {
  return (
    <div
      className={cn(
        "rounded-lg border border-border bg-card p-3 shadow-sm",
        isDragging && "opacity-60 shadow-md"
      )}
    >
      <Link href={`/admin-dashboard/crm/leads/${lead.id}`} className="font-medium hover:underline">
        {lead.title}
      </Link>
      <p className="mt-1 text-xs text-muted-foreground">{lead.companyName || lead.contactName || "—"}</p>
      {lead.assignedTo ? (
        <p className="mt-2 text-xs text-muted-foreground">{lead.assignedTo.name}</p>
      ) : null}
    </div>
  );
}

function DraggableLeadCard({ lead }: { lead: CrmLead }) {
  const { attributes, listeners, setNodeRef, transform, isDragging } = useDraggable({
    id: lead.id,
    data: { lead },
  });

  return (
    <div
      ref={setNodeRef}
      style={{ transform: CSS.Translate.toString(transform) }}
      {...attributes}
      {...listeners}
      className="cursor-grab active:cursor-grabbing"
    >
      <LeadCard lead={lead} isDragging={isDragging} />
    </div>
  );
}

function DroppableColumn({
  stageId,
  label,
  leads,
}: {
  stageId: CrmLeadStatus;
  label: string;
  leads: CrmLead[];
}) {
  const { setNodeRef, isOver } = useDroppable({ id: stageId });

  return (
    <div
      ref={setNodeRef}
      className={cn(
        "min-w-[240px] flex-1 rounded-xl border border-border bg-muted/30 p-3",
        isOver && "ring-2 ring-brand-blue/40"
      )}
    >
      <div className="mb-3 flex items-center justify-between">
        <h3 className="text-sm font-semibold">{label}</h3>
        <span className="text-xs text-muted-foreground">{leads.length}</span>
      </div>
      <div className="min-h-[120px] space-y-2">
        {leads.map((lead) => (
          <DraggableLeadCard key={lead.id} lead={lead} />
        ))}
      </div>
    </div>
  );
}

export interface CrmKanbanBoardProps {
  columns: CrmPipelineColumns;
}

function CrmKanbanBoard({ columns }: CrmKanbanBoardProps) {
  const moveLead = useMoveCrmPipelineLead();
  const [activeLead, setActiveLead] = useState<CrmLead | null>(null);
  const sensors = useSensors(useSensor(PointerSensor, { activationConstraint: { distance: 6 } }));

  const handleDragStart = (event: DragStartEvent) => {
    const lead = event.active.data.current?.lead as CrmLead | undefined;
    setActiveLead(lead ?? null);
  };

  const handleDragEnd = (event: DragEndEvent) => {
    setActiveLead(null);
    const leadId = String(event.active.id);
    const overId = event.over?.id;
    if (!overId) return;
    const newStatus = String(overId);
    if (!CRM_PIPELINE_STAGES.some((s) => s.id === newStatus)) return;
    const lead = Object.values(columns)
      .flat()
      .find((l) => l.id === leadId);
    if (!lead || lead.status === newStatus) return;
    void moveLead.mutateAsync({ leadId, status: newStatus });
  };

  return (
    <DndContext sensors={sensors} onDragStart={handleDragStart} onDragEnd={handleDragEnd}>
      <div className="flex gap-4 overflow-x-auto pb-4">
        {CRM_PIPELINE_STAGES.map((stage) => (
          <DroppableColumn
            key={stage.id}
            stageId={stage.id}
            label={stage.label}
            leads={columns[stage.id] ?? []}
          />
        ))}
      </div>
      <DragOverlay>{activeLead ? <LeadCard lead={activeLead} /> : null}</DragOverlay>
    </DndContext>
  );
}

export { CrmKanbanBoard };
