import type {
  BrandFilter,
  CategoryFilterOption,
  CategoryPageData,
  CategoryProduct,
} from "@/config/category-page";
import {
  brandIdFromLabel,
  networkingProducts,
} from "@/config/category-page";

export interface CatalogProduct extends CategoryProduct {
  categoryId: string;
}

const categoryLabels: Record<string, string> = {
  switches: "Managed Switches",
  wireless: "Wireless Access Points",
  routers: "Routers & Security",
  "tools-test": "Tools & Test Equipment",
  cabling: "Cabling & Infrastructure",
  security: "Security & Surveillance",
};

function withCategory(
  product: CategoryProduct,
  categoryId: string
): CatalogProduct {
  return { ...product, categoryId };
}

function pickNetworking(index: number, categoryId: string): CatalogProduct {
  const product = networkingProducts[index];
  if (!product) {
    throw new Error(`Missing networking product at index ${index}`);
  }
  return withCategory(product, categoryId);
}

const networkingCatalogProducts: CatalogProduct[] = [
  pickNetworking(0, "switches"),
  pickNetworking(1, "wireless"),
  pickNetworking(2, "switches"),
  pickNetworking(3, "switches"),
  pickNetworking(4, "wireless"),
  pickNetworking(5, "routers"),
  pickNetworking(6, "switches"),
  pickNetworking(7, "routers"),
  pickNetworking(8, "switches"),
  pickNetworking(9, "routers"),
  pickNetworking(10, "wireless"),
  pickNetworking(11, "wireless"),
  pickNetworking(12, "switches"),
  pickNetworking(13, "wireless"),
  pickNetworking(14, "switches"),
  pickNetworking(15, "switches"),
  pickNetworking(16, "wireless"),
  pickNetworking(17, "switches"),
  pickNetworking(18, "switches"),
  pickNetworking(19, "switches"),
  pickNetworking(20, "switches"),
  pickNetworking(21, "routers"),
  pickNetworking(22, "wireless"),
  pickNetworking(23, "routers"),
];

const flukeCatalogProducts: CatalogProduct[] = [
  {
    id: "tool-001",
    brand: "Fluke Networks",
    name: "LinkIQ Duo Cable + Network Tester",
    sku: "LIQ-100",
    price: "$1,299.00",
    tradePrice: "$1,149.00",
    priceValue: 1299,
    popularity: 93,
    rating: 4.9,
    reviewCount: 87,
    featured: true,
    createdAt: "2026-02-10",
    availability: "in_stock",
    stock: "in_stock",
    badge: "Bestseller",
    href: "/products/liq-100",
    categoryId: "tools-test",
  },
  {
    id: "tool-002",
    brand: "Fluke Networks",
    name: "DSX-8000 CableAnalyzer",
    sku: "DSX-8000",
    price: "$12,450.00",
    tradePrice: "$11,200.00",
    priceValue: 12450,
    popularity: 78,
    rating: 4.9,
    reviewCount: 34,
    featured: true,
    createdAt: "2025-10-15",
    availability: "in_stock",
    stock: "in_stock",
    href: "/products/dsx-8000",
    categoryId: "tools-test",
  },
  {
    id: "tool-003",
    brand: "Fluke Networks",
    name: "FiberLert Live Fiber Detector",
    sku: "FIBERLERT",
    price: "$89.00",
    tradePrice: "$79.00",
    priceValue: 89,
    popularity: 84,
    rating: 4.6,
    reviewCount: 156,
    createdAt: "2025-08-22",
    availability: "in_stock",
    stock: "in_stock",
    href: "/products/fiberlert",
    categoryId: "tools-test",
  },
  {
    id: "tool-004",
    brand: "Fluke Networks",
    name: "MicroScanner PoE Cable Verifier",
    sku: "MS-POE",
    price: "$549.00",
    tradePrice: "$489.00",
    priceValue: 549,
    popularity: 81,
    rating: 4.7,
    reviewCount: 62,
    createdAt: "2025-11-05",
    availability: "in_stock",
    stock: "in_stock",
    href: "/products/ms-poe",
    categoryId: "tools-test",
  },
  {
    id: "tool-005",
    brand: "Fluke Networks",
    name: "IntelliTone Pro 200 Toner & Probe Kit",
    sku: "MT-8200-60A",
    price: "$399.00",
    tradePrice: "$359.00",
    priceValue: 399,
    popularity: 72,
    rating: 4.5,
    reviewCount: 41,
    createdAt: "2025-06-18",
    availability: "low_stock",
    stock: "low_stock",
    href: "/products/intellitone-pro-200",
    categoryId: "tools-test",
  },
  {
    id: "tool-006",
    brand: "Fluke Networks",
    name: "OptiFiber Pro OTDR",
    sku: "OFP-100-Q",
    price: "$8,990.00",
    tradePrice: "$7,890.00",
    priceValue: 8990,
    popularity: 69,
    rating: 4.8,
    reviewCount: 19,
    createdAt: "2025-12-12",
    availability: "in_stock",
    stock: "in_stock",
    badge: "New",
    href: "/products/ofp-100-q",
    categoryId: "tools-test",
  },
];

const cablingCatalogProducts: CatalogProduct[] = [
  {
    id: "cab-001",
    brand: "TP-Link",
    name: "Omada 24-Port Cat6A Patch Panel",
    sku: "OP-PP24",
    price: "$129.00",
    tradePrice: "$109.00",
    priceValue: 129,
    popularity: 66,
    rating: 4.3,
    reviewCount: 28,
    createdAt: "2025-09-30",
    availability: "in_stock",
    stock: "in_stock",
    href: "/products/op-pp24",
    categoryId: "cabling",
  },
  {
    id: "cab-002",
    brand: "Cisco",
    name: "SFP-10G-SR 10G Fibre Module (Pair)",
    sku: "SFP-10G-SR",
    price: "$189.00",
    tradePrice: "$169.00",
    priceValue: 189,
    popularity: 75,
    rating: 4.6,
    reviewCount: 94,
    createdAt: "2025-07-25",
    availability: "in_stock",
    stock: "in_stock",
    href: "/products/sfp-10g-sr",
    categoryId: "cabling",
  },
];

const hikvisionCatalogProducts: CatalogProduct[] = [
  {
    id: "sec-001",
    brand: "Hikvision",
    name: "DS-2CD2147G2-LU 4MP AcuSense Turret Camera",
    sku: "DS-2CD2147G2-LU",
    price: "$329.00",
    tradePrice: "$289.00",
    priceValue: 329,
    popularity: 88,
    rating: 4.7,
    reviewCount: 112,
    featured: true,
    createdAt: "2026-01-15",
    availability: "in_stock",
    stock: "in_stock",
    badge: "Bestseller",
    href: "/products/ds-2cd2147g2-lu",
    categoryId: "security",
  },
  {
    id: "sec-002",
    brand: "Hikvision",
    name: "DS-7616NI-K2/16P 16-Channel PoE NVR",
    sku: "DS-7616NI-K2/16P",
    price: "$649.00",
    tradePrice: "$579.00",
    priceValue: 649,
    popularity: 82,
    rating: 4.6,
    reviewCount: 48,
    createdAt: "2025-10-20",
    availability: "in_stock",
    stock: "in_stock",
    href: "/products/ds-7616ni-k2",
    categoryId: "security",
  },
  {
    id: "sec-003",
    brand: "Hikvision",
    name: "DS-3E0326P-E 24-Port PoE Switch",
    sku: "DS-3E0326P-E",
    price: "$449.00",
    tradePrice: "$399.00",
    priceValue: 449,
    popularity: 76,
    rating: 4.5,
    reviewCount: 36,
    createdAt: "2025-08-08",
    availability: "in_stock",
    stock: "in_stock",
    href: "/products/ds-3e0326p-e",
    categoryId: "security",
  },
  {
    id: "sec-004",
    brand: "Hikvision",
    name: "iDS-2CD7A26G0-IZHSY 2MP DeepinView Bullet",
    sku: "iDS-2CD7A26G0-IZHSY",
    price: "$1,199.00",
    tradePrice: "$1,049.00",
    priceValue: 1199,
    popularity: 71,
    rating: 4.8,
    reviewCount: 22,
    createdAt: "2025-12-05",
    availability: "low_stock",
    stock: "low_stock",
    badge: "New",
    href: "/products/ids-2cd7a26g0",
    categoryId: "security",
  },
  {
    id: "sec-005",
    brand: "Hikvision",
    name: "DS-K1T342MFWX QR & Fingerprint Terminal",
    sku: "DS-K1T342MFWX",
    price: "$899.00",
    tradePrice: "$799.00",
    priceValue: 899,
    popularity: 68,
    rating: 4.4,
    reviewCount: 19,
    createdAt: "2025-07-12",
    availability: "in_stock",
    stock: "in_stock",
    href: "/products/ds-k1t342mfwx",
    categoryId: "security",
  },
];

export const catalogProducts: CatalogProduct[] = [
  ...networkingCatalogProducts,
  ...flukeCatalogProducts,
  ...cablingCatalogProducts,
  ...hikvisionCatalogProducts,
];

function countBy<T extends string>(
  items: CatalogProduct[],
  getKey: (item: CatalogProduct) => T
): Map<T, number> {
  const counts = new Map<T, number>();
  for (const item of items) {
    const key = getKey(item);
    counts.set(key, (counts.get(key) ?? 0) + 1);
  }
  return counts;
}

function buildBrandFilters(products: CatalogProduct[]): BrandFilter[] {
  const counts = countBy(products, (p) => brandIdFromLabel(p.brand));
  const brandNames = new Map<string, string>();
  for (const product of products) {
    brandNames.set(brandIdFromLabel(product.brand), product.brand);
  }

  return [...counts.entries()]
    .map(([id, count]) => ({
      id,
      label: brandNames.get(id) ?? id,
      count,
    }))
    .sort((a, b) => b.count - a.count);
}

function buildCategoryFilters(products: CatalogProduct[]): CategoryFilterOption[] {
  const counts = countBy(products, (p) => p.categoryId);
  return [...counts.entries()]
    .map(([id, count]) => ({
      id,
      label: categoryLabels[id] ?? id,
      count,
    }))
    .sort((a, b) => a.label.localeCompare(b.label));
}

const brandFilters = buildBrandFilters(catalogProducts);
const categoryFilters = buildCategoryFilters(catalogProducts);

export const catalogPage: CategoryPageData = {
  slug: "products",
  title: "All Products",
  description:
    "Professional networking, security, and test equipment from Cisco, Ubiquiti, TP-Link Omada, Fluke Networks, and Hikvision — Australian stock with GST-inclusive trade pricing.",
  longDescription:
    "Browse the full A2Z Tools catalogue of enterprise switches, wireless access points, routers, security appliances, cable certification tools, and structured cabling. Every product is sourced from authorised distributors with manufacturer warranty and GST-inclusive pricing for Australian trade and IT professionals.",
  eyebrow: "Catalogue",
  productCountLabel: `${catalogProducts.length} products`,
  breadcrumbs: [
    { label: "Home", href: "/" },
    { label: "Products" },
  ],
  subcategories: categoryFilters.map((category) => ({
    label: category.label,
    href: `/products?category=${category.id}`,
  })),
  featuredBrands: [
    {
      id: "cisco",
      name: "Cisco",
      description: "Enterprise switching & security",
      productCount: `${brandFilters.find((b) => b.id === "cisco")?.count ?? 0} SKUs`,
      href: "/brands/cisco",
      filterBrandId: "cisco",
    },
    {
      id: "ubiquiti",
      name: "Ubiquiti",
      description: "UniFi wireless & switching",
      productCount: `${brandFilters.find((b) => b.id === "ubiquiti")?.count ?? 0} SKUs`,
      href: "/brands/ubiquiti",
      filterBrandId: "ubiquiti",
    },
    {
      id: "tp-link",
      name: "TP-Link Omada",
      description: "Managed switches & wireless",
      productCount: `${brandFilters.find((b) => b.id === "tp-link")?.count ?? 0} SKUs`,
      href: "/brands/tp-link",
      filterBrandId: "tp-link",
    },
    {
      id: "fluke-networks",
      name: "Fluke Networks",
      description: "Cable & fibre test tools",
      productCount: `${brandFilters.find((b) => b.id === "fluke-networks")?.count ?? 0} SKUs`,
      href: "/brands/fluke",
      filterBrandId: "fluke-networks",
    },
    {
      id: "hikvision",
      name: "Hikvision",
      description: "IP cameras & NVR systems",
      productCount: `${brandFilters.find((b) => b.id === "hikvision")?.count ?? 0} SKUs`,
      href: "/brands/hikvision",
      filterBrandId: "hikvision",
    },
  ],
  brands: brandFilters,
  categories: categoryFilters,
  priceRanges: [
    { id: "under-100", label: "Under $100", min: 0, max: 99.99 },
    { id: "100-500", label: "$100 – $500", min: 100, max: 500 },
    { id: "500-1000", label: "$500 – $1,000", min: 500, max: 1000 },
    { id: "1000-5000", label: "$1,000 – $5,000", min: 1000, max: 5000 },
    { id: "5000-plus", label: "$5,000+", min: 5000, max: null },
  ],
  availabilityOptions: [
    { id: "in_stock", label: "In stock" },
    { id: "low_stock", label: "Low stock" },
    { id: "back_order", label: "Back order" },
    { id: "out_of_stock", label: "Out of stock" },
  ],
  ratingOptions: [
    { id: "4-plus", label: "4★ & above", min: 4 },
    { id: "3-plus", label: "3★ & above", min: 3 },
    { id: "2-plus", label: "2★ & above", min: 2 },
  ],
};

