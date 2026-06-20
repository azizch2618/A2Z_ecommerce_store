import type { CompareProduct } from "@/types/compare";
import { buildProductGalleryImages, fallbackImage } from "@/config/visual-assets";

export const MAX_COMPARE_PRODUCTS = 4;
export const MIN_COMPARE_PRODUCTS = 2;

function galleryImage(name: string, brand: string) {
  const image = buildProductGalleryImages(name, brand)[0] ?? fallbackImage;
  return { src: image.src, alt: image.alt };
}

const u7 = galleryImage("UniFi 7 Pro Access Point (U7-Pro)", "Ubiquiti");
const c9200 = galleryImage("Catalyst 9200L 24-Port Managed Switch", "Cisco");
const sg2428 = galleryImage("Omada 24-Port Gigabit PoE+ Switch", "TP-Link");
const udm = galleryImage("UniFi Dream Machine Pro Max", "Ubiquiti");

export const compareBreadcrumbs = [
  { label: "Home", href: "/" },
  { label: "Products", href: "/products" },
  { label: "Compare" },
];

export const mockCompareProducts: CompareProduct[] = [
  {
    id: "net-002",
    slug: "u7-pro",
    name: "UniFi 7 Pro Access Point (U7-Pro)",
    brand: "Ubiquiti",
    sku: "U7-PRO",
    priceIncGst: 449,
    tradePriceIncGst: 389,
    rating: 4.9,
    reviewCount: 128,
    stock: "in_stock",
    imageSrc: u7.src,
    imageAlt: u7.alt,
    href: "/products/u7-pro",
    specs: {
      ports: "1× 2.5 GbE RJ45 uplink",
      speed: "Wi-Fi 7 — 9.3 Gbps aggregate",
      powerConsumption: "21W max (PoE+ powered)",
      poeSupport: "Powered by PoE+ (802.3at)",
      warranty: "1-year manufacturer warranty",
      dimensions: "Ø 220 × 48 mm",
      weight: "680 g",
    },
  },
  {
    id: "net-001",
    slug: "c9200l-24p",
    name: "Catalyst 9200L 24-Port Managed Switch",
    brand: "Cisco",
    sku: "C9200L-24P-4G-E",
    priceIncGst: 2849,
    tradePriceIncGst: 2449,
    rating: 4.8,
    reviewCount: 42,
    stock: "in_stock",
    imageSrc: c9200.src,
    imageAlt: c9200.alt,
    href: "/products/c9200l-24p",
    specs: {
      ports: "24× GbE RJ45 + 4× 1G SFP uplinks",
      speed: "56 Gbps switching capacity",
      powerConsumption: "450W max system / 370W PoE budget",
      poeSupport: "24× PoE+ (802.3at), 30W per port",
      warranty: "Limited lifetime hardware warranty",
      dimensions: "44 × 30 × 4.4 cm (1U rack)",
      weight: "4.5 kg",
    },
  },
  {
    id: "net-007",
    slug: "sg2428p",
    name: "Omada 24-Port Gigabit PoE+ Switch",
    brand: "TP-Link",
    sku: "SG2428P",
    priceIncGst: 379,
    tradePriceIncGst: 329,
    rating: 4.6,
    reviewCount: 56,
    stock: "low_stock",
    imageSrc: sg2428.src,
    imageAlt: sg2428.alt,
    href: "/products/sg2428p",
    specs: {
      ports: "24× GbE RJ45 + 4× SFP+ uplinks",
      speed: "56 Gbps switching capacity",
      powerConsumption: "195W PoE budget / 280W max",
      poeSupport: "24× PoE+ (802.3at), 30W per port",
      warranty: "5-year limited warranty",
      dimensions: "44 × 20 × 4.4 cm (1U rack)",
      weight: "3.2 kg",
    },
  },
  {
    id: "net-008",
    slug: "udm-pro-max",
    name: "UniFi Dream Machine Pro Max",
    brand: "Ubiquiti",
    sku: "UDM-PRO-MAX",
    priceIncGst: 899,
    tradePriceIncGst: 779,
    rating: 4.9,
    reviewCount: 67,
    stock: "low_stock",
    imageSrc: udm.src,
    imageAlt: udm.alt,
    href: "/products/udm-pro-max",
    specs: {
      ports: "8× GbE RJ45 + 2× 10G SFP+",
      speed: "12 Gbps firewall / 10 Gbps IDS/IPS",
      powerConsumption: "50W max (100–240V AC)",
      poeSupport: "No — security gateway appliance",
      warranty: "1-year manufacturer warranty",
      dimensions: "442 × 325 × 44 mm (1U rack)",
      weight: "5.1 kg",
    },
  },
];

export const compareSpecRows = [
  { key: "ports" as const, label: "Ports" },
  { key: "speed" as const, label: "Speed" },
  { key: "powerConsumption" as const, label: "Power consumption" },
  { key: "poeSupport" as const, label: "PoE support" },
  { key: "warranty" as const, label: "Warranty" },
  { key: "dimensions" as const, label: "Dimensions" },
  { key: "weight" as const, label: "Weight" },
];
