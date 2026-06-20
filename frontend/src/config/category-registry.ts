import type { CategoryPageData, CategoryProduct } from "@/config/category-page";
import {
  networkingCategory,
  networkingProducts,
} from "@/config/category-page";
import {
  catalogProducts,
  type CatalogProduct,
} from "@/config/catalog-page";
import { featuredBrands } from "@/config/homepage";
import { brandIdFromLabel } from "@/config/category-page";

const sharedFilters = {
  priceRanges: networkingCategory.priceRanges,
  availabilityOptions: networkingCategory.availabilityOptions,
  ratingOptions: networkingCategory.ratingOptions,
} as const;

function stripCatalogFields(product: CatalogProduct): CategoryProduct {
  const { categoryId: _categoryId, ...rest } = product;
  return rest;
}

function catalogByCategory(categoryId: string): CategoryProduct[] {
  return catalogProducts
    .filter((product) => product.categoryId === categoryId)
    .map(stripCatalogFields);
}

function buildBrandFilters(products: CategoryProduct[]) {
  const counts = new Map<string, { label: string; count: number }>();
  for (const product of products) {
    const id = brandIdFromLabel(product.brand);
    const existing = counts.get(id);
    if (existing) {
      existing.count += 1;
    } else {
      counts.set(id, { label: product.brand, count: 1 });
    }
  }
  return [...counts.entries()]
    .map(([id, { label, count }]) => ({ id, label, count }))
    .sort((a, b) => b.count - a.count);
}

export const toolsCategory: CategoryPageData = {
  slug: "tools",
  title: "Tools",
  description:
    "Professional hand tools, cable testers, network analysers, and installation equipment from Fluke Networks, Klein, and more.",
  longDescription:
    "Equip your team with certified cable analysers, tone and probe kits, crimpers, punch-down tools, and power tools for structured cabling and network installation. Trade pricing and same-day dispatch on in-stock testers and toolkits.",
  eyebrow: "Category",
  productCountLabel: "186 products",
  breadcrumbs: [{ label: "Home", href: "/" }, { label: "Tools" }],
  subcategories: [
    { label: "Crimpers & Strippers", href: "/tools/hand/crimpers" },
    { label: "Cable Testers", href: "/tools/test/cable" },
    { label: "Network Analysers", href: "/tools/test/network" },
    { label: "Tone & Probe Kits", href: "/tools/test/tone-probe" },
  ],
  featuredBrands: [
    {
      id: "fluke-networks",
      name: "Fluke Networks",
      description: "Cable & fibre certification",
      productCount: "42 SKUs",
      href: "/brands/fluke-networks",
      filterBrandId: "fluke-networks",
    },
    {
      id: "klein",
      name: "Klein Tools",
      description: "Professional hand tools",
      productCount: "68 SKUs",
      href: "/brands/klein",
      filterBrandId: "klein",
    },
  ],
  brands: [
    { id: "fluke-networks", label: "Fluke Networks", count: 42 },
    { id: "klein", label: "Klein Tools", count: 68 },
    { id: "ideal", label: "Ideal Industries", count: 34 },
  ],
  ...sharedFilters,
};

export const toolsProducts: CategoryProduct[] = catalogByCategory("tools-test");

export const electricalCategory: CategoryPageData = {
  slug: "electrical",
  title: "Electrical",
  description:
    "Structured cabling, fibre, patch panels, racks, and electrical infrastructure for commercial installations.",
  longDescription:
    "From Cat6A bulk cable and keystone jacks to floor cabinets and cable management, A2Z Tools supplies everything needed for structured cabling projects. Project pricing and staged delivery available for trade accounts.",
  eyebrow: "Category",
  productCountLabel: "324 products",
  breadcrumbs: [{ label: "Home", href: "/" }, { label: "Electrical" }],
  subcategories: [
    { label: "Cat6 & Cat6A", href: "/electrical/cable/cat6" },
    { label: "Fibre Optic", href: "/electrical/cable/fibre" },
    { label: "Patch Panels", href: "/electrical/components/patch-panels" },
    { label: "Floor Cabinets", href: "/electrical/racks/floor" },
  ],
  featuredBrands: [
    {
      id: "panduit",
      name: "Panduit",
      description: "Structured cabling systems",
      productCount: "89 SKUs",
      href: "/brands/panduit",
      filterBrandId: "panduit",
    },
    {
      id: "tp-link",
      name: "TP-Link",
      description: "Patch panels & accessories",
      productCount: "24 SKUs",
      href: "/brands/tp-link",
      filterBrandId: "tp-link",
    },
    {
      id: "cisco",
      name: "Cisco",
      description: "Fibre modules & optics",
      productCount: "56 SKUs",
      href: "/brands/cisco",
      filterBrandId: "cisco",
    },
  ],
  brands: [
    { id: "panduit", label: "Panduit", count: 89 },
    { id: "tp-link", label: "TP-Link", count: 24 },
    { id: "cisco", label: "Cisco", count: 56 },
  ],
  ...sharedFilters,
};

export const electricalProducts: CategoryProduct[] = [
  ...catalogByCategory("cabling"),
  {
    id: "elec-001",
    brand: "Panduit",
    name: "Cat6A UTP Cable 305m Box",
    sku: "PU6A-305",
    price: "$419.00",
    tradePrice: "$379.00",
    priceValue: 419,
    popularity: 74,
    rating: 4.5,
    reviewCount: 38,
    createdAt: "2025-08-10",
    availability: "in_stock",
    stock: "in_stock",
    href: "/products/pu6a-305",
  },
  {
    id: "elec-002",
    brand: "Panduit",
    name: "48-Port Cat6A Patch Panel",
    sku: "CP48BLY",
    price: "$289.00",
    tradePrice: "$259.00",
    priceValue: 289,
    popularity: 68,
    rating: 4.4,
    reviewCount: 21,
    createdAt: "2025-10-05",
    availability: "in_stock",
    stock: "in_stock",
    href: "/products/cp48bly",
  },
  {
    id: "elec-003",
    brand: "Panduit",
    name: "12U Wall-Mount Network Cabinet",
    sku: "WMPFSE12",
    price: "$549.00",
    tradePrice: "$489.00",
    priceValue: 549,
    popularity: 62,
    rating: 4.3,
    reviewCount: 14,
    createdAt: "2025-07-20",
    availability: "in_stock",
    stock: "in_stock",
    href: "/products/wmpfse12",
  },
];

export const securityCategory: CategoryPageData = {
  slug: "security",
  title: "Security",
  description:
    "IP cameras, NVRs, access control, and alarm hardware for commercial and industrial sites.",
  longDescription:
    "Secure your projects with Hikvision IP cameras, PoE switches, NVRs, and access control terminals. All products are sourced from authorised Australian distributors with manufacturer warranty and firmware support.",
  eyebrow: "Category",
  productCountLabel: "218 products",
  breadcrumbs: [{ label: "Home", href: "/" }, { label: "Security" }],
  subcategories: [
    { label: "IP Cameras", href: "/security/surveillance/ip-cameras" },
    { label: "NVRs & Recorders", href: "/security/surveillance/nvr" },
    { label: "Door Controllers", href: "/security/access/controllers" },
    { label: "Alarm Panels", href: "/security/alarms/panels" },
  ],
  featuredBrands: [
    {
      id: "hikvision",
      name: "Hikvision",
      description: "IP cameras & NVR systems",
      productCount: "124 SKUs",
      href: "/brands/hikvision",
      filterBrandId: "hikvision",
    },
    {
      id: "axis",
      name: "Axis",
      description: "Enterprise surveillance",
      productCount: "48 SKUs",
      href: "/brands/axis",
      filterBrandId: "axis",
    },
    {
      id: "dahua",
      name: "Dahua",
      description: "Commercial security",
      productCount: "36 SKUs",
      href: "/brands/dahua",
      filterBrandId: "dahua",
    },
  ],
  brands: [
    { id: "hikvision", label: "Hikvision", count: 124 },
    { id: "axis", label: "Axis", count: 48 },
    { id: "dahua", label: "Dahua", count: 36 },
  ],
  ...sharedFilters,
};

export const securityProducts: CategoryProduct[] = catalogByCategory("security");

const allBrandProducts = catalogProducts.map(stripCatalogFields);

export const brandsCategory: CategoryPageData = {
  slug: "brands",
  title: "Brands",
  description:
    "Shop authorised networking, tools, and security brands with Australian warranty and trade pricing.",
  longDescription:
    "A2Z Tools is an authorised reseller for Cisco, Ubiquiti, TP-Link Omada, Fluke Networks, Hikvision, and more. Browse by manufacturer to find switches, access points, testers, cameras, and cabling from the brands your projects depend on.",
  eyebrow: "Directory",
  productCountLabel: `${allBrandProducts.length} products`,
  breadcrumbs: [{ label: "Home", href: "/" }, { label: "Brands" }],
  subcategories: featuredBrands.map((brand) => ({
    label: brand.name,
    href: brand.href,
  })),
  featuredBrands: featuredBrands.map((brand) => ({
    id: brand.id,
    name: brand.name,
    description: brand.description,
    productCount: `${buildBrandFilters(allBrandProducts).find((b) => b.id === brand.id)?.count ?? 0} SKUs`,
    href: brand.href,
    filterBrandId: brand.id === "fluke" ? "fluke-networks" : brand.id,
  })),
  brands: buildBrandFilters(allBrandProducts),
  ...sharedFilters,
};

export const brandsProducts: CategoryProduct[] = allBrandProducts;

export type CategorySlug =
  | "networking"
  | "tools"
  | "electrical"
  | "security"
  | "brands";

export const categoryRegistry: Record<
  CategorySlug,
  { category: CategoryPageData; products: CategoryProduct[] }
> = {
  networking: { category: networkingCategory, products: networkingProducts },
  tools: { category: toolsCategory, products: toolsProducts },
  electrical: { category: electricalCategory, products: electricalProducts },
  security: { category: securityCategory, products: securityProducts },
  brands: { category: brandsCategory, products: brandsProducts },
};

export function getCategoryEntry(slug: string) {
  return categoryRegistry[slug as CategorySlug] ?? null;
}

export const categorySlugs = Object.keys(categoryRegistry) as CategorySlug[];
