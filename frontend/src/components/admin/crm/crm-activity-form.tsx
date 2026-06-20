"use client";

import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { useCreateCrmActivity } from "@/lib/api/admin/crm-hooks";

const ACTIVITY_TYPES = [
  { value: "call", label: "Call" },
  { value: "meeting", label: "Meeting" },
  { value: "email", label: "Email" },
  { value: "follow_up", label: "Follow-up" },
] as const;

export interface CrmActivityFormProps {
  leadId?: string;
  opportunityId?: string;
}

function CrmActivityForm({ leadId, opportunityId }: CrmActivityFormProps) {
  const create = useCreateCrmActivity();
  const [activityType, setActivityType] = useState("call");
  const [subject, setSubject] = useState("");
  const [description, setDescription] = useState("");
  const [scheduledAt, setScheduledAt] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    void create
      .mutateAsync({
        activityType,
        subject,
        description,
        leadId,
        opportunityId,
        scheduledAt: scheduledAt || undefined,
      })
      .then(() => {
        setSubject("");
        setDescription("");
        setScheduledAt("");
      });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-3">
      <div className="grid gap-3 sm:grid-cols-2">
        <div className="space-y-1.5">
          <Label>Type</Label>
          <Select value={activityType} onValueChange={setActivityType}>
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {ACTIVITY_TYPES.map((t) => (
                <SelectItem key={t.value} value={t.value}>
                  {t.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        <div className="space-y-1.5">
          <Label>Scheduled</Label>
          <Input
            type="datetime-local"
            value={scheduledAt}
            onChange={(e) => setScheduledAt(e.target.value)}
          />
        </div>
      </div>
      <div className="space-y-1.5">
        <Label>Subject</Label>
        <Input value={subject} onChange={(e) => setSubject(e.target.value)} required />
      </div>
      <div className="space-y-1.5">
        <Label>Description</Label>
        <Textarea value={description} onChange={(e) => setDescription(e.target.value)} rows={3} />
      </div>
      <Button type="submit" disabled={create.isPending || !subject.trim()}>
        Log activity
      </Button>
    </form>
  );
}

export { CrmActivityForm };
