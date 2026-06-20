import type { CartItem } from "@/types/cart";
import { buildProductGalleryImages, fallbackImage } from "@/config/visual-assets";

function firstGalleryImage(name: string, brand: string) {
  const image = buildProductGalleryImages(name, brand)[0] ?? fallbackImage;
  return { src: image.src, alt: image.alt };
}

const u7Images = firstGalleryImage("UniFi 7 Pro Access Point (U7-Pro)", "Ubiquiti");
const c9200Images = firstGalleryImage(
  "Catalyst 9200L 24-Port Managed Switch",
  "Cisco"
);
const sg2428Images = firstGalleryImage("Omada 24-Port Gigabit PoE+ Switch", "TP-Link");

export function getMockCartItemCount(): number {
  return mockCartItems.reduce((sum, item) => sum + item.quantity, 0);
}
export const mockCartItems: CartItem[] = [
  {
    id: "cart-1",
    productId: "net-002",
    slug: "u7-pro",
    brand: "Ubiquiti",
    name: "UniFi 7 Pro Access Point (U7-Pro)",
    sku: "U7-PRO",
    priceValue: 449,
    tradePriceValue: 389,
    quantity: 4,
    imageSrc: u7Images.src,
    imageAlt: u7Images.alt,
    href: "/products/u7-pro",
    maxQuantity: 99,
  },
  {
    id: "cart-2",
    productId: "net-001",
    slug: "c9200l-24p",
    brand: "Cisco",
    name: "Catalyst 9200L 24-Port Managed Switch",
    sku: "C9200L-24P-4G-E",
    priceValue: 2849,
    tradePriceValue: 2449,
    quantity: 1,
    imageSrc: c9200Images.src,
    imageAlt: c9200Images.alt,
    href: "/products/c9200l-24p",
    maxQuantity: 12,
  },
  {
    id: "cart-3",
    productId: "net-007",
    slug: "sg2428p",
    brand: "TP-Link",
    name: "Omada 24-Port Gigabit PoE+ Switch",
    sku: "SG2428P",
    priceValue: 379,
    tradePriceValue: 329,
    quantity: 2,
    imageSrc: sg2428Images.src,
    imageAlt: sg2428Images.alt,
    href: "/products/sg2428p",
    maxQuantity: 99,
  },
];

export const cartPageBreadcrumbs = [
  { label: "Home", href: "/" },
  { label: "Products", href: "/products" },
  { label: "Shopping cart" },
];
