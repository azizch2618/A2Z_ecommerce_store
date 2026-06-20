import { calculateGstFromInclusive, formatAud } from "@/lib/cart";
import { cn } from "@/lib/utils";

export interface ProductGstPricingProps {
  priceValue: number;
  tradePriceValue?: number;
  quantity?: number;
  className?: string;
}

function ProductGstPricing({
  priceValue,
  tradePriceValue,
  quantity = 1,
  className,
}: ProductGstPricingProps) {
  const lineIncGst = priceValue * quantity;
  const retail = calculateGstFromInclusive(lineIncGst);
  const trade =
    tradePriceValue !== undefined
      ? calculateGstFromInclusive(tradePriceValue * quantity)
      : null;

  return (
    <dl
      className={cn(
        "grid gap-2 rounded-lg border border-border/80 bg-white/60 p-3 text-xs",
        className
      )}
    >
      <div className="flex justify-between gap-4">
        <dt className="text-muted-foreground">
          {quantity > 1 ? `Subtotal (${quantity} units) ex GST` : "Price ex GST"}
        </dt>
        <dd className="font-mono font-medium tabular-nums text-foreground">
          {formatAud(retail.exGst)}
        </dd>
      </div>
      <div className="flex justify-between gap-4">
        <dt className="text-muted-foreground">GST (10%)</dt>
        <dd className="font-mono font-medium tabular-nums text-foreground">
          {formatAud(retail.gstAmount)}
        </dd>
      </div>
      <div className="flex justify-between gap-4 border-t border-border/60 pt-2 font-medium">
        <dt className="text-brand-navy">
          {quantity > 1 ? "Line total inc GST" : "Total inc GST"}
        </dt>
        <dd className="font-mono tabular-nums text-brand-navy">
          {formatAud(lineIncGst)}
        </dd>
      </div>
      {trade ? (
        <div className="flex justify-between gap-4 border-t border-dashed border-brand-blue/20 pt-2 text-brand-blue">
          <dt>Trade line total inc GST</dt>
          <dd className="font-mono font-semibold tabular-nums">
            {formatAud(tradePriceValue! * quantity)}
          </dd>
        </div>
      ) : null}
    </dl>
  );
}

export { ProductGstPricing };
