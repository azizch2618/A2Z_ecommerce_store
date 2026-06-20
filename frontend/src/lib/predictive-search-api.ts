import type { PredictiveSearchResults } from "@/types/search";
import { searchProducts } from "@/lib/api/services/products.service";
import { formatAudFromCents } from "@/lib/format/currency";

export async function searchPredictiveFromApi(query: string): Promise<PredictiveSearchResults> {
  const response = await searchProducts(query, 8);

  return {
    products: response.products.map((product) => ({
      id: product.id,
      name: product.name,
      brand: "",
      sku: product.sku,
      href: `/products/${product.slug}`,
      imageSrc: product.image_url ?? "",
      imageAlt: product.name,
      priceLabel: formatAudFromCents(product.price.amount_inc_gst_cents),
    })),
    categories: response.categories.map((category) => ({
      id: category.id,
      label: category.name,
      description: "Browse category",
      href: `/products?category=${category.slug}`,
    })),
    brands: response.brands.map((brand) => ({
      id: brand.id,
      label: brand.name,
      href: `/products?brand=${brand.slug}`,
      productCount: "",
    })),
  };
}

export function hasSearchResults(results: PredictiveSearchResults): boolean {
  return (
    results.products.length > 0 ||
    results.categories.length > 0 ||
    results.brands.length > 0
  );
}
