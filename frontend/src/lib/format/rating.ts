/** DRF serializes DecimalField as a JSON string (e.g. "4.10"). */
export type ApiDecimalRating = string | number | null;

export function parseProductRating(
  value: ApiDecimalRating | undefined
): number | undefined {
  if (value === null || value === undefined) {
    return undefined;
  }

  const numericRating = typeof value === "number" ? value : Number(value);
  if (!Number.isFinite(numericRating)) {
    return undefined;
  }

  return numericRating;
}

export function parseProductRatingOrZero(
  value: ApiDecimalRating | undefined
): number {
  return parseProductRating(value) ?? 0;
}

export function toDisplayRating(rating: number): number {
  const numericRating = typeof rating === "number" ? rating : Number(rating ?? 0);
  return Number.isFinite(numericRating) ? numericRating : 0;
}
