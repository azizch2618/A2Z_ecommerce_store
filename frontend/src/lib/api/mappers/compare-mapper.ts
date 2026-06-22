import type { ProductDetail } from "@/lib/api/types/product";
import { parseProductRating } from "@/lib/format/rating";
import type { CompareProduct } from "@/types/compare";

function stockFromApi(status: string): CompareProduct["stock"] {
  if (status === "in_stock" || status === "low_stock" || status === "out_of_stock") {
    return status;
  }
  if (status === "backorder" || status === "back_order") {
    return "back_order";
  }
  return "in_stock";
}

function buildSpecs(product: ProductDetail): Record<string, string> {
  const specs: Record<string, string> = {};
  for (const group of product.attributes ?? []) {
    for (const item of group.items) {
      specs[item.name] = item.value;
    }
  }
  return specs;
}

export function mapApiProductToCompareProduct(product: ProductDetail): CompareProduct {
  const variant = product.variants.find((v) => v.is_default) ?? product.variants[0];
  const incCents = variant?.price.amount_inc_gst_cents ?? 0;
  const image = product.images[0];

  return {
    id: product.id,
    slug: product.slug,
    name: product.name,
    brand: product.brand?.name ?? "Unknown",
    sku: variant?.sku ?? "",
    priceIncGst: incCents / 100,
    tradePriceIncGst: variant?.price.is_trade_price
      ? incCents / 100
      : undefined,
    rating: parseProductRating(product.average_rating),
    reviewCount: product.review_count,
    stock: stockFromApi(variant?.stock.status ?? "in_stock"),
    imageSrc: image?.url ?? "",
    imageAlt: image?.alt_text ?? product.name,
    href: `/products/${product.slug}`,
    specs: buildSpecs(product),
  };
}

export function mapListingToCompareProduct(product: {
  id: string;
  slug?: string;
  name: string;
  brand: string;
  sku: string;
  priceValue?: number;
  stock: CompareProduct["stock"];
  imageSrc?: string;
  imageAlt?: string;
  href: string;
  rating?: number;
  reviewCount?: number;
}): CompareProduct {
  return {
    id: product.id,
    slug: product.slug ?? product.id,
    name: product.name,
    brand: product.brand,
    sku: product.sku,
    priceIncGst: product.priceValue ?? 0,
    stock: product.stock,
    imageSrc: product.imageSrc ?? "",
    imageAlt: product.imageAlt ?? product.name,
    href: product.href,
    rating: product.rating,
    reviewCount: product.reviewCount,
    specs: {},
  };
}
