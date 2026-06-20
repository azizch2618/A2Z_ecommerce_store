import type { PredictiveSearchResults } from "@/types/search";
import {
  MAX_BRAND_RESULTS,
  MAX_CATEGORY_RESULTS,
  MAX_PRODUCT_RESULTS,
  searchableBrands,
  searchableCategories,
  searchableProducts,
} from "@/config/search-data";

function normalize(value: string): string {
  return value.toLowerCase().trim();
}

function tokenize(query: string): string[] {
  return normalize(query).split(/\s+/).filter(Boolean);
}

function matchesTokens(haystack: string, tokens: string[]): boolean {
  const normalized = normalize(haystack);
  return tokens.every((token) => normalized.includes(token));
}

function scoreMatch(haystack: string, tokens: string[]): number {
  const normalized = normalize(haystack);
  let score = 0;

  for (const token of tokens) {
    if (normalized.startsWith(token)) score += 12;
    else if (normalized.split(/\s+/).some((word) => word.startsWith(token))) score += 8;
    else if (normalized.includes(token)) score += 4;
  }

  return score;
}

export function searchPredictive(query: string): PredictiveSearchResults {
  const tokens = tokenize(query);
  if (tokens.length === 0) {
    return { products: [], categories: [], brands: [] };
  }

  const products = searchableProducts
    .filter((product) =>
      matchesTokens(
        `${product.name} ${product.brand} ${product.sku}`,
        tokens
      )
    )
    .map((product) => ({
      product,
      score:
        scoreMatch(product.name, tokens) * 2 +
        scoreMatch(product.brand, tokens) +
        scoreMatch(product.sku, tokens),
    }))
    .sort((a, b) => b.score - a.score)
    .slice(0, MAX_PRODUCT_RESULTS)
    .map((entry) => entry.product);

  const categories = searchableCategories
    .filter((category) =>
      matchesTokens(`${category.label} ${category.description}`, tokens)
    )
    .map((category) => ({
      category,
      score:
        scoreMatch(category.label, tokens) * 2 +
        scoreMatch(category.description, tokens),
    }))
    .sort((a, b) => b.score - a.score)
    .slice(0, MAX_CATEGORY_RESULTS)
    .map((entry) => entry.category);

  const brands = searchableBrands
    .filter((brand) => matchesTokens(brand.label, tokens))
    .map((brand) => ({
      brand,
      score: scoreMatch(brand.label, tokens),
    }))
    .sort((a, b) => b.score - a.score)
    .slice(0, MAX_BRAND_RESULTS)
    .map((entry) => entry.brand);

  return { products, categories, brands };
}

export function hasSearchResults(results: PredictiveSearchResults): boolean {
  return (
    results.products.length > 0 ||
    results.categories.length > 0 ||
    results.brands.length > 0
  );
}
