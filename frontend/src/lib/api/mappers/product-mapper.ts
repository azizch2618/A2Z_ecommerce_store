import type { CategoryProduct } from "@/config/category-page";
import type { ProductDetail as UiProductDetail } from "@/config/product-detail";
import type { ProductDetail as ApiProductDetail, ProductSummary } from "@/lib/api/types/product";
import type { ListingProduct } from "@/types/product";
import { formatAudFromCents } from "@/lib/format/currency";
import { parseProductRating, parseProductRatingOrZero } from "@/lib/format/rating";

const UNKNOWN_BRAND = "Unknown";

function stockFromApi(status: string): ListingProduct["stock"] {
  if (status === "in_stock" || status === "low_stock" || status === "out_of_stock") {
    return status;
  }
  if (status === "backorder" || status === "back_order") {
    return "back_order";
  }
  return "in_stock";
}

export function mapApiProductToListing(product: ProductSummary): ListingProduct {
  const incCents = product.price?.amount_inc_gst_cents ?? 0;
  return {
    id: product.id,
    brand: product.brand?.name ?? UNKNOWN_BRAND,
    brandId: product.brand?.slug ?? undefined,
    name: product.name,
    sku: product.default_variant?.sku ?? "",
    price: formatAudFromCents(incCents),
    priceValue: incCents / 100,
    stock: stockFromApi(product.stock?.status ?? "out_of_stock"),
    href: `/products/${product.slug}`,
    description: product.short_description ?? undefined,
    rating: parseProductRating(product.average_rating),
    reviewCount: product.review_count ?? undefined,
    imageSrc: product.primary_image?.url ?? undefined,
    imageAlt: product.primary_image?.alt_text ?? product.name,
    badge: product.badges?.[0],
    defaultVariantId: product.default_variant?.id,
  };
}

export function mapApiProductToCategoryProduct(product: ProductSummary): CategoryProduct {
  const listing = mapApiProductToListing(product);
  const { stock: rawStock, ...listingRest } = listing;
  const stock: CategoryProduct["stock"] =
    rawStock === "back_order" ? "in_stock" : rawStock;
  return {
    ...listingRest,
    stock,
    priceValue: listing.priceValue ?? 0,
    popularity: product.review_count ?? 0,
    createdAt: new Date().toISOString(),
    availability: stock,
    rating: parseProductRatingOrZero(product.average_rating),
    reviewCount: product.review_count ?? 0,
    categoryId: product.brand?.slug,
  };
}

export function mapApiProductToDetail(product: ApiProductDetail): UiProductDetail {
  const variant = product.variants.find((v) => v.is_default) ?? product.variants[0];
  const incCents = variant?.price?.amount_inc_gst_cents ?? 0;
  const primaryCategory = product.categories.find((c) => c.is_primary) ?? product.categories[0];
  const stockStatus = stockFromApi(variant?.stock?.status ?? "out_of_stock");
  const brandSlug = product.brand?.slug;

  return {
    id: product.id,
    slug: product.slug,
    name: product.name,
    sku: variant?.sku ?? "",
    brand: product.brand?.name ?? UNKNOWN_BRAND,
    brandHref: brandSlug ? `/brands/${brandSlug}` : "/products",
    category: primaryCategory?.name ?? "Products",
    categoryHref: primaryCategory ? `/products?category=${primaryCategory.slug}` : "/products",
    price: formatAudFromCents(incCents),
    priceValue: incCents / 100,
    stock: stockStatus === "back_order" ? "in_stock" : stockStatus,
    stockCount: variant?.stock?.quantity_available ?? 0,
    shortDescription: product.short_description ?? "",
    longDescription: product.description,
    highlights: product.highlights ?? [],
    images: (product.images ?? []).map((img, index) => ({
      id: String(img.id ?? index),
      label: img.alt_text ?? product.name,
      alt: img.alt_text ?? product.name,
      src: img.url,
    })),
    specifications: (product.attributes ?? []).map((group) => ({
      group: group.group,
      items: group.items.map((item) => ({
        label: item.name,
        value: item.value,
      })),
    })),
    downloads: [],
    reviews: (product.reviews ?? []).map((review) => ({
      id: String(review.id),
      author: review.author_name,
      company: review.author_company,
      role: review.author_role,
      rating: review.rating,
      title: review.title,
      body: review.body,
      date: review.created_at,
      verified: review.is_verified_purchase,
    })),
    relatedProductIds: (product.related_products ?? []).map((p) => p.id),
    breadcrumbs: [
      { label: "Home", href: "/" },
      { label: "Products", href: "/products" },
      { label: product.name, href: `/products/${product.slug}` },
    ],
    warranty: "Manufacturer warranty applies. See product documentation for terms.",
    deliveryNote: "Ships Australia-wide from Sydney DC. GST included.",
    rating: parseProductRatingOrZero(product.average_rating),
    reviewCount: product.review_count ?? 0,
    defaultVariantId: variant?.id,
  };
}
