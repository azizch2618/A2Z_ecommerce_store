"use client";

import * as React from "react";
import { FileText, Send } from "lucide-react";
import { toast } from "sonner";

import type { ProductDetail } from "@/config/product-detail";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";

export interface BulkQuoteDialogProps {
  product: ProductDetail;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  defaultQuantity?: number;
}

function BulkQuoteDialog({
  product,
  open,
  onOpenChange,
  defaultQuantity = 10,
}: BulkQuoteDialogProps) {
  const [company, setCompany] = React.useState("");
  const [email, setEmail] = React.useState("");
  const [quantity, setQuantity] = React.useState(String(defaultQuantity));
  const [message, setMessage] = React.useState("");
  const [isSubmitting, setIsSubmitting] = React.useState(false);

  React.useEffect(() => {
    if (open) setQuantity(String(defaultQuantity));
  }, [open, defaultQuantity]);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setIsSubmitting(true);
    await new Promise((resolve) => setTimeout(resolve, 600));
    setIsSubmitting(false);
    onOpenChange(false);
    toast.success("Quote request submitted", {
      description: `Our team will respond within 1 business day for ${product.sku}.`,
    });
    setCompany("");
    setEmail("");
    setMessage("");
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-h-[90vh] overflow-y-auto sm:max-w-lg">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 text-brand-navy">
            <FileText className="size-5 text-brand-blue" />
            Request bulk quote
          </DialogTitle>
          <DialogDescription>
            Project pricing for <span className="font-medium text-foreground">{product.name}</span>{" "}
            (SKU: {product.sku}). Minimum 10 units for bulk rates.
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="rounded-lg border border-border bg-neutral-50 px-4 py-3 text-sm">
            <p className="font-medium text-brand-navy">{product.brand}</p>
            <p className="text-muted-foreground">{product.name}</p>
            <p className="mt-1 font-mono text-xs">{product.sku}</p>
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="quote-company">Company</Label>
              <Input
                id="quote-company"
                value={company}
                onChange={(event) => setCompany(event.target.value)}
                placeholder="Your business name"
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="quote-email">Work email</Label>
              <Input
                id="quote-email"
                type="email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                placeholder="you@company.com.au"
                required
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="quote-quantity">Estimated quantity</Label>
            <Input
              id="quote-quantity"
              type="number"
              min={10}
              value={quantity}
              onChange={(event) => setQuantity(event.target.value)}
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="quote-message">Project details (optional)</Label>
            <Textarea
              id="quote-message"
              value={message}
              onChange={(event) => setMessage(event.target.value)}
              placeholder="Site location, delivery timeline, configuration requirements…"
              rows={4}
            />
          </div>

          <DialogFooter className="gap-2 sm:gap-0">
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button type="submit" className="gap-2" loading={isSubmitting}>
              <Send className="size-4" />
              Submit request
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}

export { BulkQuoteDialog };
