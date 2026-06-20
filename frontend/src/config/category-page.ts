import type { BreadcrumbItemData } from "@/components/layout/breadcrumbs";
import type { ProductPlaceholder } from "@/config/homepage";

export type SortOption =
  | "featured"
  | "best-selling"
  | "newest"
  | "price-asc"
  | "price-desc";

export type AvailabilityFilter =
  | "in_stock"
  | "low_stock"
  | "back_order"
  | "out_of_stock";

export interface PriceRangeFilter {
  id: string;
  label: string;
  min: number;
  max: number | null;
}

export interface BrandFilter {
  id: string;
  label: string;
  count: number;
}

export interface RatingFilter {
  id: string;
  label: string;
  min: number;
}

export interface CategoryFilterOption {
  id: string;
  label: string;
  count: number;
}

export interface FeaturedBrand {
  id: string;
  name: string;
  description: string;
  productCount: string;
  href: string;
  filterBrandId: string;
}

export interface CategoryPageData {
  slug: string;
  title: string;
  description: string;
  longDescription: string;
  eyebrow: string;
  productCountLabel: string;
  breadcrumbs: BreadcrumbItemData[];
  subcategories: { label: string; href: string }[];
  featuredBrands: FeaturedBrand[];
  brands: BrandFilter[];
  priceRanges: PriceRangeFilter[];
  availabilityOptions: { id: AvailabilityFilter; label: string }[];
  ratingOptions: RatingFilter[];
  categories?: CategoryFilterOption[];
}

export interface CategoryProduct extends ProductPlaceholder {
  priceValue: number;
  popularity: number;
  createdAt: string;
  availability: AvailabilityFilter;
  rating: number;
  reviewCount: number;
  featured?: boolean;
  categoryId?: string;
  /** Live API default variant — used for add-to-cart from listings */
  defaultVariantId?: string;
}

export const LISTING_PAGE_SIZE = 12;

export const networkingCategory: CategoryPageData = {
  slug: "networking",
  title: "Networking",
  description:
    "Enterprise switches, routers, wireless access points, and infrastructure from Cisco, Ubiquiti, Aruba, and more — backed by Australian stock and trade pricing.",
  longDescription:
    "A2Z Tools stocks Australia's widest range of professional networking hardware for installers, MSPs, and enterprise IT teams. From campus switching and Wi-Fi 7 access points to SD-WAN routers and firewall appliances, every SKU is sourced from authorised distributors with full manufacturer warranty. Trade accounts receive project pricing, staged delivery, and Net 30 terms on approved orders.",
  eyebrow: "Category",
  productCountLabel: "1,247 products",
  breadcrumbs: [
    { label: "Home", href: "/" },
    { label: "Networking" },
  ],
  subcategories: [
    { label: "Managed Switches", href: "/networking/switches/managed" },
    { label: "PoE Switches", href: "/networking/switches/poe" },
    { label: "Access Points", href: "/networking/wireless/access-points" },
    { label: "Enterprise Routers", href: "/networking/routers/enterprise" },
    { label: "Firewall Appliances", href: "/networking/routers/firewall" },
  ],
  featuredBrands: [
    {
      id: "cisco",
      name: "Cisco",
      description: "Enterprise switching & routing",
      productCount: "312 SKUs",
      href: "/brands/cisco",
      filterBrandId: "cisco",
    },
    {
      id: "ubiquiti",
      name: "Ubiquiti",
      description: "UniFi wireless & switching",
      productCount: "198 SKUs",
      href: "/brands/ubiquiti",
      filterBrandId: "ubiquiti",
    },
    {
      id: "aruba",
      name: "Aruba",
      description: "Campus & edge networking",
      productCount: "156 SKUs",
      href: "/brands/aruba",
      filterBrandId: "aruba",
    },
    {
      id: "netgear",
      name: "Netgear",
      description: "ProSAFE & Orbi Pro",
      productCount: "124 SKUs",
      href: "/brands/netgear",
      filterBrandId: "netgear",
    },
    {
      id: "tp-link",
      name: "TP-Link",
      description: "Omada & JetStream",
      productCount: "98 SKUs",
      href: "/brands/tp-link",
      filterBrandId: "tp-link",
    },
    {
      id: "mikrotik",
      name: "MikroTik",
      description: "Routers & wireless",
      productCount: "87 SKUs",
      href: "/brands/mikrotik",
      filterBrandId: "mikrotik",
    },
  ],
  brands: [
    { id: "cisco", label: "Cisco", count: 312 },
    { id: "ubiquiti", label: "Ubiquiti", count: 198 },
    { id: "aruba", label: "Aruba", count: 156 },
    { id: "netgear", label: "Netgear", count: 124 },
    { id: "tp-link", label: "TP-Link", count: 98 },
    { id: "mikrotik", label: "MikroTik", count: 87 },
    { id: "d-link", label: "D-Link", count: 64 },
  ],
  priceRanges: [
    { id: "under-100", label: "Under $100", min: 0, max: 99.99 },
    { id: "100-500", label: "$100 – $500", min: 100, max: 500 },
    { id: "500-1000", label: "$500 – $1,000", min: 500, max: 1000 },
    { id: "1000-plus", label: "$1,000+", min: 1000, max: null },
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

export const networkingProducts: CategoryProduct[] = [
  {
    id: "net-001",
    brand: "Cisco",
    name: "Catalyst 9200L 24-Port Managed Switch",
    sku: "C9200L-24P-4G-E",
    price: "$2,849.00",
    tradePrice: "$2,449.00",
    priceValue: 2849,
    popularity: 98,
    rating: 4.8,
    reviewCount: 42,
    featured: true,
    createdAt: "2025-11-12",
    availability: "in_stock",
    stock: "in_stock",
    badge: "Bestseller",
    href: "/products/c9200l-24p",
  },
  {
    id: "net-002",
    brand: "Ubiquiti",
    name: "UniFi 7 Pro Access Point (U7-Pro)",
    sku: "U7-PRO",
    price: "$449.00",
    tradePrice: "$389.00",
    priceValue: 449,
    popularity: 96,
    rating: 4.9,
    reviewCount: 128,
    featured: true,
    createdAt: "2026-01-08",
    availability: "in_stock",
    stock: "in_stock",
    badge: "New",
    href: "/products/u7-pro",
  },
  {
    id: "net-003",
    brand: "Aruba",
    name: "Instant On 1930 24G 4SFP+ Switch",
    sku: "JL682A",
    price: "$1,299.00",
    tradePrice: "$1,149.00",
    priceValue: 1299,
    popularity: 88,
    rating: 4.6,
    reviewCount: 31,
    createdAt: "2025-09-20",
    availability: "in_stock",
    stock: "in_stock",
    href: "/products/jl682a",
  },
  {
    id: "net-004",
    brand: "Netgear",
    name: "ProSAFE 24-Port PoE+ Smart Switch",
    sku: "GS724TPv2",
    price: "$649.00",
    tradePrice: "$579.00",
    priceValue: 649,
    popularity: 82,
    rating: 4.4,
    reviewCount: 56,
    createdAt: "2025-08-14",
    availability: "low_stock",
    stock: "low_stock",
    href: "/products/gs724tpv2",
  },
  {
    id: "net-005",
    brand: "Cisco",
    name: "Meraki MR46 Cloud-Managed Access Point",
    sku: "MR46-HW",
    price: "$1,189.00",
    tradePrice: "$1,049.00",
    priceValue: 1189,
    popularity: 91,
    rating: 4.7,
    reviewCount: 24,
    createdAt: "2025-10-02",
    availability: "in_stock",
    stock: "in_stock",
    href: "/products/mr46-hw",
  },
  {
    id: "net-006",
    brand: "MikroTik",
    name: "CCR2004-16G-2S+ Cloud Core Router",
    sku: "CCR2004-16G-2S+",
    price: "$899.00",
    tradePrice: "$799.00",
    priceValue: 899,
    popularity: 74,
    rating: 4.5,
    reviewCount: 18,
    createdAt: "2025-07-18",
    availability: "in_stock",
    stock: "in_stock",
    href: "/products/ccr2004",
  },
  {
    id: "net-007",
    brand: "TP-Link",
    name: "Omada 24-Port Gigabit PoE+ Switch",
    sku: "SG2428P",
    price: "$379.00",
    tradePrice: "$329.00",
    priceValue: 379,
    popularity: 79,
    rating: 4.3,
    reviewCount: 89,
    createdAt: "2025-12-01",
    availability: "in_stock",
    stock: "in_stock",
    badge: "Sale",
    href: "/products/sg2428p",
  },
  {
    id: "net-008",
    brand: "Ubiquiti",
    name: "UniFi Dream Machine Pro Max",
    sku: "UDM-PRO-MAX",
    price: "$899.00",
    tradePrice: "$799.00",
    priceValue: 899,
    popularity: 94,
    rating: 4.8,
    reviewCount: 67,
    featured: true,
    createdAt: "2026-02-15",
    availability: "low_stock",
    stock: "low_stock",
    badge: "New",
    href: "/products/udm-pro-max",
  },
  {
    id: "net-009",
    brand: "D-Link",
    name: "DGS-1210-28MP 28-Port PoE Switch",
    sku: "DGS-1210-28MP",
    price: "$549.00",
    priceValue: 549,
    popularity: 65,
    rating: 4.1,
    reviewCount: 14,
    createdAt: "2025-06-22",
    availability: "back_order",
    stock: "out_of_stock",
    href: "/products/dgs-1210-28mp",
  },
  {
    id: "net-010",
    brand: "Cisco",
    name: "ISR 1100 4-Port Integrated Services Router",
    sku: "C1111-4P",
    price: "$1,749.00",
    tradePrice: "$1,549.00",
    priceValue: 1749,
    popularity: 71,
    rating: 4.6,
    reviewCount: 19,
    createdAt: "2025-05-10",
    availability: "in_stock",
    stock: "in_stock",
    href: "/products/c1111-4p",
  },
  {
    id: "net-011",
    brand: "Aruba",
    name: "AP-635 Wi-Fi 6E Campus Access Point",
    sku: "JZ356A",
    price: "$1,099.00",
    tradePrice: "$979.00",
    priceValue: 1099,
    popularity: 85,
    rating: 4.7,
    reviewCount: 22,
    createdAt: "2025-11-28",
    availability: "in_stock",
    stock: "in_stock",
    href: "/products/jz356a",
  },
  {
    id: "net-012",
    brand: "Netgear",
    name: "Orbi Pro WiFi 6 AX6000 Tri-Band Router",
    sku: "SXR80",
    price: "$1,299.00",
    priceValue: 1299,
    popularity: 68,
    rating: 3.9,
    reviewCount: 11,
    createdAt: "2025-04-03",
    availability: "out_of_stock",
    stock: "out_of_stock",
    href: "/products/sxr80",
  },
  {
    id: "net-013",
    brand: "TP-Link",
    name: "JetStream 48-Port Gigabit L2+ Switch",
    sku: "T1600G-52TS",
    price: "$89.00",
    tradePrice: "$79.00",
    priceValue: 89,
    popularity: 77,
    rating: 4.5,
    reviewCount: 143,
    createdAt: "2025-10-18",
    availability: "in_stock",
    stock: "in_stock",
    href: "/products/t1600g-52ts",
  },
  {
    id: "net-014",
    brand: "MikroTik",
    name: "hAP ax³ Wi-Fi 6 Access Point Router",
    sku: "hAP-ax3",
    price: "$189.00",
    tradePrice: "$169.00",
    priceValue: 189,
    popularity: 83,
    rating: 4.6,
    reviewCount: 37,
    createdAt: "2026-03-01",
    availability: "in_stock",
    stock: "in_stock",
    badge: "New",
    href: "/products/hap-ax3",
  },
  {
    id: "net-015",
    brand: "Ubiquiti",
    name: "UniFi Switch Pro 48 PoE",
    sku: "USW-Pro-48-POE",
    price: "$1,649.00",
    tradePrice: "$1,449.00",
    priceValue: 1649,
    popularity: 90,
    rating: 4.8,
    reviewCount: 45,
    featured: true,
    createdAt: "2025-08-30",
    availability: "in_stock",
    stock: "in_stock",
    href: "/products/usw-pro-48-poe",
  },
  {
    id: "net-016",
    brand: "Cisco",
    name: "Catalyst 1000 16-Port Gigabit Switch",
    sku: "C1000-16T-2G-L",
    price: "$429.00",
    tradePrice: "$379.00",
    priceValue: 429,
    popularity: 86,
    rating: 4.5,
    reviewCount: 33,
    createdAt: "2025-12-20",
    availability: "in_stock",
    stock: "in_stock",
    href: "/products/c1000-16t",
  },
  {
    id: "net-017",
    brand: "Ubiquiti",
    name: "UniFi 6 Long-Range Access Point",
    sku: "U6-LR",
    price: "$279.00",
    tradePrice: "$249.00",
    priceValue: 279,
    popularity: 92,
    rating: 4.7,
    reviewCount: 201,
    createdAt: "2025-03-15",
    availability: "in_stock",
    stock: "in_stock",
    href: "/products/u6-lr",
  },
  {
    id: "net-018",
    brand: "Cisco",
    name: "Catalyst 9300 48-Port PoE+ Switch",
    sku: "C9300-48P-A",
    price: "$8,990.00",
    tradePrice: "$7,890.00",
    priceValue: 8990,
    popularity: 76,
    rating: 4.9,
    reviewCount: 15,
    createdAt: "2025-07-01",
    availability: "in_stock",
    stock: "in_stock",
    href: "/products/c9300-48p",
  },
  {
    id: "net-019",
    brand: "Aruba",
    name: "Instant On 1960 48G 4SFP+ Switch",
    sku: "JL724A",
    price: "$2,199.00",
    tradePrice: "$1,949.00",
    priceValue: 2199,
    popularity: 70,
    rating: 4.4,
    reviewCount: 12,
    createdAt: "2025-06-10",
    availability: "in_stock",
    stock: "in_stock",
    href: "/products/jl724a",
  },
  {
    id: "net-020",
    brand: "Netgear",
    name: "M4250-26G4F-PoE+ AV Line Switch",
    sku: "GSM4230P",
    price: "$1,899.00",
    tradePrice: "$1,699.00",
    priceValue: 1899,
    popularity: 64,
    rating: 4.2,
    reviewCount: 8,
    createdAt: "2025-05-22",
    availability: "in_stock",
    stock: "in_stock",
    href: "/products/gsm4230p",
  },
  {
    id: "net-021",
    brand: "TP-Link",
    name: "Omada 8-Port PoE+ Switch with 2 SFP",
    sku: "SG2210MP",
    price: "$159.00",
    tradePrice: "$139.00",
    priceValue: 159,
    popularity: 81,
    rating: 4.4,
    reviewCount: 76,
    createdAt: "2025-09-05",
    availability: "in_stock",
    stock: "in_stock",
    href: "/products/sg2210mp",
  },
  {
    id: "net-022",
    brand: "MikroTik",
    name: "RB5009UG+S+IN Router",
    sku: "RB5009UG+S+IN",
    price: "$329.00",
    tradePrice: "$299.00",
    priceValue: 329,
    popularity: 88,
    rating: 4.8,
    reviewCount: 52,
    createdAt: "2025-11-01",
    availability: "in_stock",
    stock: "in_stock",
    href: "/products/rb5009",
  },
  {
    id: "net-023",
    brand: "D-Link",
    name: "DAP-X2850 Wi-Fi 6 Access Point",
    sku: "DAP-X2850",
    price: "$299.00",
    priceValue: 299,
    popularity: 58,
    rating: 3.8,
    reviewCount: 6,
    createdAt: "2025-04-18",
    availability: "low_stock",
    stock: "low_stock",
    href: "/products/dap-x2850",
  },
  {
    id: "net-024",
    brand: "Cisco",
    name: "Secure Firewall 3105 Appliance",
    sku: "FPR-3105",
    price: "$12,450.00",
    tradePrice: "$11,200.00",
    priceValue: 12450,
    popularity: 62,
    rating: 4.7,
    reviewCount: 9,
    featured: true,
    createdAt: "2026-01-20",
    availability: "in_stock",
    stock: "in_stock",
    badge: "New",
    href: "/products/fpr-3105",
  },
];

export const sortOptions: { value: SortOption; label: string }[] = [
  { value: "featured", label: "Featured" },
  { value: "best-selling", label: "Best Selling" },
  { value: "newest", label: "Newest" },
  { value: "price-asc", label: "Price: Low to High" },
  { value: "price-desc", label: "Price: High to Low" },
];

export function brandIdFromLabel(brand: string): string {
  return brand.toLowerCase().replace(/\s+/g, "-");
}
