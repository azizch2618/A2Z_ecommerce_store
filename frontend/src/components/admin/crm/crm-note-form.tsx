"use client";

import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { useCreateCrmNote } from "@/lib/api/admin/crm-hooks";

export interface CrmNoteFormProps {
  leadId?: string;
  opportunityId?: string;
}

function CrmNoteForm({ leadId, opportunityId }: CrmNoteFormProps) {
  const create = useCreateCrmNote();
  const [body, setBody] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    void create.mutateAsync({ body, leadId, opportunityId }).then(() => setBody(""));
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-3">
      <div className="space-y-1.5">
        <Label>Note</Label>
        <Textarea value={body} onChange={(e) => setBody(e.target.value)} rows={3} required />
      </div>
      <Button type="submit" disabled={create.isPending || !body.trim()}>
        Add note
      </Button>
    </form>
  );
}

export { CrmNoteForm };
