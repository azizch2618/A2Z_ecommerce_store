/** Australian dollar formatting — ex-GST and inc-GST (10% GST). */

export function formatAud(amount: number): string {
  return new Intl.NumberFormat("en-AU", {
    style: "currency",
    currency: "AUD",
  }).format(amount);
}

export function formatAudFromCents(cents: number, _incGst = true): string {
  const dollars = cents / 100;
  return formatAud(dollars);
}

export function formatExGst(cents: number): string {
  return `${formatAudFromCents(cents, false)} ex GST`;
}

export function formatIncGst(cents: number): string {
  return `${formatAudFromCents(cents, true)} inc GST`;
}

export function formatGstLabel(rate: number): string {
  return `GST ${(rate * 100).toFixed(0)}%`;
}
