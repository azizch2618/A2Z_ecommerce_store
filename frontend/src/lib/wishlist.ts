import type { ProductDetail } from "@/config/product-detail";
import type { ListingProduct } from "@/types/product";
import type { WishlistItem } from "@/types/wishlist";
import { getProductImage } from "@/config/visual-assets";

function parseAudPrice(value?: string): number | undefined {
  if (!value) return undefined;
  const parsed = Number.parseFloat(value.replace(/[^0-9.]/g, ""));
  return Number.isFinite(parsed) ? parsed : undefined;
}

export function listingProductToWishlistItem(product: ListingProduct): WishlistItem {
  const image = product.imageSrc
    ? { src: product.imageSrc, alt: product.imageAlt ?? product.name }
    : getProductImage(product.name, product.brand);

  return {
    id: `wl-${product.id}`,
    productId: product.id,
    slug: product.href.replace(/^\/products\//, "") || product.id,
    name: product.name,
    brand: product.brand,
    sku: product.sku,
    priceIncGst: product.priceValue ?? parseAudPrice(product.price) ?? 0,
    tradePriceIncGst: parseAudPrice(product.tradePrice),
    imageSrc: image.src,
    imageAlt: image.alt,
    href: product.href,
    stock: product.stock,
    variantId: product.defaultVariantId,
  };
}

export function productDetailToWishlistItem(product: ProductDetail): WishlistItem {
  const image = product.images[0];

  return {
    id: `wl-${product.id}`,
    productId: product.id,
    slug: product.slug,
    name: product.name,
    brand: product.brand,
    sku: product.sku,
    priceIncGst: product.priceValue,
    tradePriceIncGst: parseAudPrice(product.tradePrice),
    imageSrc: image?.src ?? getProductImage(product.name, product.brand).src,
    imageAlt: image?.alt ?? product.name,
    href: `/products/${product.slug}`,
    stock: product.stock,
    variantId: product.defaultVariantId,
  };
}

export function mergeWishlistItem(existing: WishlistItem, incoming: WishlistItem): WishlistItem {
  return { ...existing, ...incoming, id: existing.id };
}
