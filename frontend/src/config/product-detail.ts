import type { BreadcrumbItemData } from "@/components/layout/breadcrumbs";
import type { ProductStockStatus } from "@/types/product";
import { catalogProducts } from "@/config/catalog-page";
import { buildProductGalleryImages } from "@/config/visual-assets";

export interface ProductImage {
  id: string;
  label: string;
  alt: string;
  src: string;
}

export interface ProductSpecification {
  group: string;
  items: { label: string; value: string }[];
}

export interface ProductDownload {
  id: string;
  title: string;
  type: "PDF" | "ZIP" | "Firmware";
  size: string;
  href: string;
}

export interface ProductReview {
  id: string;
  author: string;
  company: string;
  role: string;
  rating: number;
  title: string;
  body: string;
  date: string;
  verified: boolean;
}

export interface ProductDetail {
  id: string;
  slug: string;
  name: string;
  sku: string;
  brand: string;
  brandHref: string;
  category: string;
  categoryHref: string;
  price: string;
  priceValue: number;
  tradePrice?: string;
  stock: ProductStockStatus;
  stockCount?: number;
  badge?: string;
  shortDescription: string;
  longDescription: string;
  highlights: string[];
  images: ProductImage[];
  specifications: ProductSpecification[];
  downloads: ProductDownload[];
  reviews: ProductReview[];
  relatedProductIds: string[];
  breadcrumbs: BreadcrumbItemData[];
  warranty: string;
  deliveryNote: string;
  rating?: number;
  reviewCount?: number;
  /** Live API default variant — used for add-to-cart */
  defaultVariantId?: string;
}

const u7ProDetail: ProductDetail = {
  id: "net-002",
  slug: "u7-pro",
  name: "UniFi 7 Pro Access Point (U7-Pro)",
  sku: "U7-PRO",
  brand: "Ubiquiti",
  brandHref: "/brands/ubiquiti",
  category: "Networking",
  categoryHref: "/networking",
  price: "$449.00",
  priceValue: 449,
  tradePrice: "$389.00",
  stock: "in_stock",
  stockCount: 84,
  badge: "New",
  shortDescription:
    "Enterprise Wi-Fi 7 access point with 6 spatial streams, 2.5 GbE uplink, and seamless UniFi Network integration.",
  longDescription:
    "The UniFi 7 Pro delivers next-generation wireless performance for high-density offices, warehouses, and hospitality venues. With tri-band Wi-Fi 7, 320 MHz channel support on 6 GHz, and a 2.5 GbE uplink, it eliminates bottlenecks for bandwidth-intensive applications. Managed through UniFi Network, it deploys in minutes with zero-touch provisioning and scales from a single site to distributed enterprise rollouts.",
  highlights: [
    "Wi-Fi 7 tri-band (2.4 / 5 / 6 GHz)",
    "6 spatial streams, up to 9.3 Gbps aggregate",
    "2.5 GbE RJ45 uplink with PoE+ input",
    "Ceiling or wall mount — included kit",
    "UniFi Network managed, zero-touch setup",
  ],
  images: buildProductGalleryImages("UniFi 7 Pro Access Point (U7-Pro)", "Ubiquiti"),
  specifications: [
    {
      group: "Wireless",
      items: [
        { label: "Wi-Fi Standard", value: "802.11be (Wi-Fi 7)" },
        { label: "Spatial Streams", value: "6" },
        { label: "Max Data Rate", value: "9.3 Gbps aggregate" },
        { label: "Bands", value: "2.4 GHz, 5 GHz, 6 GHz" },
        { label: "Channel Width", value: "Up to 320 MHz (6 GHz)" },
        { label: "MIMO", value: "4×4 MU-MIMO" },
      ],
    },
    {
      group: "Networking",
      items: [
        { label: "Uplink", value: "1× 2.5 GbE RJ45" },
        { label: "Power", value: "PoE+ (802.3at)" },
        { label: "Max Power Draw", value: "21W" },
        { label: "Management", value: "UniFi Network" },
      ],
    },
    {
      group: "Physical",
      items: [
        { label: "Dimensions", value: "Ø 220 × 48 mm" },
        { label: "Weight", value: "680 g" },
        { label: "Mounting", value: "Ceiling / wall" },
        { label: "Operating Temp", value: "-10°C to 60°C" },
        { label: "IP Rating", value: "IP54" },
      ],
    },
  ],
  downloads: [
    {
      id: "ds",
      title: "U7-Pro Datasheet",
      type: "PDF",
      size: "1.2 MB",
      href: "#",
    },
    {
      id: "qg",
      title: "Quick Start Guide",
      type: "PDF",
      size: "840 KB",
      href: "#",
    },
    {
      id: "dim",
      title: "Mechanical Drawings",
      type: "PDF",
      size: "2.4 MB",
      href: "#",
    },
    {
      id: "fw",
      title: "Firmware Release Notes",
      type: "Firmware",
      size: "—",
      href: "#",
    },
  ],
  reviews: [
    {
      id: "r1",
      author: "James Mitchell",
      company: "Mitchell IT Solutions",
      role: "Director",
      rating: 5,
      title: "Flawless Wi-Fi 7 rollout for a 200-seat office",
      body: "Deployed 24 units across three floors. Coverage is exceptional on 6 GHz and the 2.5G uplink keeps pace with our fibre backhaul. UniFi provisioning saved us hours on site.",
      date: "2026-02-14",
      verified: true,
    },
    {
      id: "r2",
      author: "Sarah Chen",
      company: "Pacific Networks",
      role: "Senior Engineer",
      rating: 5,
      title: "Best AP in the UniFi lineup for high density",
      body: "We replaced Wi-Fi 6 APs in a warehouse with U7-Pro units. Handoff is seamless and throughput on scanners and VoIP handsets improved noticeably.",
      date: "2026-01-28",
      verified: true,
    },
    {
      id: "r3",
      author: "David O'Brien",
      company: "O'Brien Electrical",
      role: "Installer",
      rating: 4,
      title: "Solid hardware, stock availability matters",
      body: "Great performance and clean industrial design. Would like more mounting options in the box, but A2Z had stock when others didn't.",
      date: "2025-12-03",
      verified: true,
    },
  ],
  relatedProductIds: ["net-008", "net-015", "net-001", "net-005"],
  breadcrumbs: [
    { label: "Home", href: "/" },
    { label: "Products", href: "/products" },
    { label: "Networking", href: "/networking" },
    { label: "UniFi 7 Pro Access Point" },
  ],
  warranty: "1-year manufacturer warranty. Extended coverage available.",
  deliveryNote: "Ships same day from Sydney warehouse for orders before 2pm AEST.",
  rating: 4.9,
  reviewCount: 128,
};

const c9200Detail: ProductDetail = {
  id: "net-001",
  slug: "c9200l-24p",
  name: "Catalyst 9200L 24-Port Managed Switch",
  sku: "C9200L-24P-4G-E",
  brand: "Cisco",
  brandHref: "/brands/cisco",
  category: "Networking",
  categoryHref: "/networking",
  price: "$2,849.00",
  priceValue: 2849,
  tradePrice: "$2,449.00",
  stock: "in_stock",
  stockCount: 12,
  badge: "Bestseller",
  shortDescription:
    "Layer 2/3 access switch with 24 PoE+ ports, 4×1G uplinks, and Cisco DNA-ready management.",
  longDescription:
    "The Cisco Catalyst 9200L Series brings enterprise-class switching to access layers with flexible stacking, robust security, and simplified operations through Cisco DNA Center. Ideal for branch offices, campus access, and mid-size deployments requiring PoE+ for phones, cameras, and access points.",
  highlights: [
    "24× Gigabit PoE+ ports",
    "370W PoE power budget",
    "4× 1G SFP uplinks",
    "Stackable up to 8 units",
    "Cisco DNA ready",
  ],
  images: buildProductGalleryImages("Catalyst 9200L 24-Port Managed Switch", "Cisco"),
  specifications: [
    {
      group: "Performance",
      items: [
        { label: "Switching Capacity", value: "56 Gbps" },
        { label: "Forwarding Rate", value: "41.67 Mpps" },
        { label: "Stacking", value: "Up to 8 members" },
      ],
    },
    {
      group: "PoE",
      items: [
        { label: "PoE Ports", value: "24× PoE+" },
        { label: "PoE Budget", value: "370W" },
        { label: "Per-Port Max", value: "30W" },
      ],
    },
    {
      group: "Physical",
      items: [
        { label: "Form Factor", value: "1U rack mount" },
        { label: "Dimensions", value: "44 × 30 × 4.4 cm" },
        { label: "Weight", value: "4.5 kg" },
        { label: "Operating Temp", value: "0°C to 50°C" },
      ],
    },
    {
      group: "Management & Security",
      items: [
        { label: "Management", value: "Cisco DNA Center, CLI, SNMP" },
        { label: "Stacking Bandwidth", value: "80 Gbps" },
        { label: "MACsec", value: "Supported" },
        { label: "802.1X", value: "Supported" },
      ],
    },
  ],
  downloads: [
    {
      id: "ds",
      title: "C9200L Series Datasheet",
      type: "PDF",
      size: "3.1 MB",
      href: "#",
    },
    {
      id: "install",
      title: "Hardware Installation Guide",
      type: "PDF",
      size: "1.8 MB",
      href: "#",
    },
    {
      id: "release",
      title: "Cisco IOS XE Release Notes",
      type: "PDF",
      size: "920 KB",
      href: "#",
    },
    {
      id: "fw",
      title: "Recommended Firmware 17.12.04",
      type: "Firmware",
      size: "412 MB",
      href: "#",
    },
  ],
  reviews: [
    {
      id: "r1",
      author: "Mark Thompson",
      company: "Thompson Systems",
      role: "Network Architect",
      rating: 5,
      title: "Reliable campus access workhorse",
      body: "We've standardised on 9200L for access layers across 14 sites. DNA integration and stacking make operations straightforward, and PoE budget handles phones plus APs without a second switch.",
      date: "2026-01-10",
      verified: true,
    },
    {
      id: "r2",
      author: "Priya Nair",
      company: "Nair Communications",
      role: "Project Manager",
      rating: 5,
      title: "Perfect for mid-size branch rollouts",
      body: "Deployed 48 units for a healthcare client. A2Z staged delivery by floor and provided tax invoices per shipment — made procurement painless.",
      date: "2025-11-22",
      verified: true,
    },
    {
      id: "r3",
      author: "Chris Walker",
      company: "Walker IT",
      role: "Senior Engineer",
      rating: 4,
      title: "Solid switch, plan your stacking cables",
      body: "Performance and reliability are excellent. Only note: order stacking cables separately if you're expanding beyond two units in a stack.",
      date: "2025-09-14",
      verified: true,
    },
  ],
  relatedProductIds: ["net-002", "net-005", "net-010", "net-011"],
  breadcrumbs: [
    { label: "Home", href: "/" },
    { label: "Products", href: "/products" },
    { label: "Networking", href: "/networking" },
    { label: "Catalyst 9200L 24-Port" },
  ],
  warranty: "Limited lifetime hardware warranty with Smart Net optional.",
  deliveryNote: "Freight delivery available for rack-mount equipment.",
  rating: 4.8,
  reviewCount: 42,
};

const udmProMaxDetail: ProductDetail = {
  id: "net-008",
  slug: "udm-pro-max",
  name: "UniFi Dream Machine Pro Max",
  sku: "UDM-PRO-MAX",
  brand: "Ubiquiti",
  brandHref: "/brands/ubiquiti",
  category: "Networking",
  categoryHref: "/networking",
  price: "$899.00",
  priceValue: 899,
  tradePrice: "$799.00",
  stock: "low_stock",
  stockCount: 6,
  badge: "New",
  shortDescription:
    "All-in-one security gateway with dual-WAN, IDS/IPS, NVR storage, and full UniFi application suite for demanding sites.",
  longDescription:
    "The UniFi Dream Machine Pro Max is Ubiquiti's flagship integrated security gateway and network controller. It combines enterprise routing, a full UniFi Network and Protect stack, and high-throughput IDS/IPS in a 1U rackmount form factor. With dual 10G SFP+ WAN/LAN, redundant storage for UniFi Protect, and a colour touchscreen for at-a-glance monitoring, it anchors mid-size and enterprise UniFi deployments from a single appliance.",
  highlights: [
    "8× GbE + 2× 10G SFP+ ports",
    "Dual-WAN load balancing & failover",
    "10 Gbps IDS/IPS throughput",
    "Redundant 3.5″ storage bay for NVR",
    "Integrated UniFi Network, Protect, Access, Talk",
  ],
  images: buildProductGalleryImages("UniFi Dream Machine Pro Max", "Ubiquiti"),
  specifications: [
    {
      group: "Performance",
      items: [
        { label: "IDS/IPS Throughput", value: "10 Gbps" },
        { label: "Firewall Throughput", value: "12 Gbps" },
        { label: "Concurrent Clients", value: "5,000+" },
        { label: "VPN Throughput", value: "2 Gbps" },
      ],
    },
    {
      group: "Connectivity",
      items: [
        { label: "LAN Ports", value: "8× 1 GbE RJ45" },
        { label: "SFP+", value: "2× 10 GbE" },
        { label: "WAN", value: "Dual-WAN capable" },
        { label: "Storage", value: "2× 3.5″ HDD bays (RAID1)" },
      ],
    },
    {
      group: "UniFi Applications",
      items: [
        { label: "Network", value: "Included controller" },
        { label: "Protect", value: "NVR with AI events" },
        { label: "Access", value: "Door access control" },
        { label: "Talk", value: "Intercom & paging" },
      ],
    },
    {
      group: "Physical",
      items: [
        { label: "Form Factor", value: "1U rack mount" },
        { label: "Display", value: "1.3″ colour touchscreen" },
        { label: "Power", value: "100–240V AC, 50W max" },
        { label: "Dimensions", value: "442 × 325 × 44 mm" },
      ],
    },
  ],
  downloads: [
    {
      id: "ds",
      title: "UDM-Pro-Max Datasheet",
      type: "PDF",
      size: "2.6 MB",
      href: "#",
    },
    {
      id: "install",
      title: "Rack Installation Guide",
      type: "PDF",
      size: "1.1 MB",
      href: "#",
    },
    {
      id: "unifi",
      title: "UniFi Network User Guide",
      type: "PDF",
      size: "4.8 MB",
      href: "#",
    },
    {
      id: "fw",
      title: "UniFi OS Release Notes",
      type: "Firmware",
      size: "—",
      href: "#",
    },
  ],
  reviews: [
    {
      id: "r1",
      author: "Tom Hughes",
      company: "Hughes AV & Networks",
      role: "Integrator",
      rating: 5,
      title: "One box to run the whole UniFi stack",
      body: "Replaced separate cloud keys and NVRs with UDM-Pro-Max on a warehouse project. Protect storage and 10G uplinks are exactly what we needed.",
      date: "2026-03-01",
      verified: true,
    },
    {
      id: "r2",
      author: "Lisa Park",
      company: "Park Managed Services",
      role: "CTO",
      rating: 5,
      title: "IDS/IPS without a dedicated appliance",
      body: "Throughput holds up on a 1 Gbps fibre link with Protect recording 40 cameras. Touchscreen is handy for quick health checks on site.",
      date: "2026-01-18",
      verified: true,
    },
    {
      id: "r3",
      author: "Andrew Fraser",
      company: "Fraser Electrical",
      role: "Installer",
      rating: 4,
      title: "Plan rack depth and airflow",
      body: "Powerful unit — runs warm under full load so give it proper rack ventilation. A2Z had stock when Ubiquiti AU was back-ordered.",
      date: "2025-12-08",
      verified: true,
    },
  ],
  relatedProductIds: ["net-002", "net-015", "net-001", "net-017"],
  breadcrumbs: [
    { label: "Home", href: "/" },
    { label: "Products", href: "/products" },
    { label: "Networking", href: "/networking" },
    { label: "UniFi Dream Machine Pro Max" },
  ],
  warranty: "1-year manufacturer warranty. RMA via authorised distributor.",
  deliveryNote: "Ships from Sydney. Rack-mount freight available on request.",
  rating: 4.8,
  reviewCount: 67,
};

const productDetails: Record<string, ProductDetail> = {
  "u7-pro": u7ProDetail,
  "c9200l-24p": c9200Detail,
  "udm-pro-max": udmProMaxDetail,
};

function slugFromHref(href: string): string {
  return href.replace(/^\/products\//, "");
}

const allListingProducts = catalogProducts;

const categoryByCatalogId: Record<string, { label: string; href: string }> = {
  switches: { label: "Networking", href: "/networking" },
  wireless: { label: "Networking", href: "/networking" },
  routers: { label: "Networking", href: "/networking" },
  "tools-test": { label: "Tools", href: "/tools" },
  cabling: { label: "Electrical", href: "/electrical" },
  security: { label: "Security", href: "/security" },
};

function buildFallbackReview(listing: (typeof allListingProducts)[number]): ProductReview[] {
  if (!listing.reviewCount || !listing.rating) return [];

  return [
    {
      id: `review-${listing.id}`,
      author: "Michael T.",
      company: "Metro Cabling Pty Ltd",
      role: "Lead Installer",
      rating: Math.min(5, Math.max(1, Math.round(listing.rating))),
      title: "Solid trade purchase",
      body: `Used on a recent commercial fit-out. Stock was accurate, delivery was on schedule, and the tax invoice was ready for our accounts team.`,
      date: "2025-11-18",
      verified: true,
    },
  ];
}

/** Build a minimal PDP from catalog listing data when no rich detail exists. */
function buildFallbackDetail(slug: string): ProductDetail | null {
  const listing = allListingProducts.find(
    (product) => slugFromHref(product.href) === slug
  );
  if (!listing) return null;

  const categoryMeta =
    categoryByCatalogId[listing.categoryId] ?? {
      label: "Products",
      href: "/products",
    };

  const brandSlug = listing.brand.toLowerCase().replace(/\s+/g, "-");

  return {
    id: listing.id,
    slug,
    name: listing.name,
    sku: listing.sku,
    brand: listing.brand,
    brandHref: `/brands/${brandSlug}`,
    category: categoryMeta.label,
    categoryHref: categoryMeta.href,
    price: listing.price,
    priceValue: listing.priceValue,
    tradePrice: listing.tradePrice,
    stock: listing.availability,
    stockCount:
      listing.availability === "in_stock"
        ? 24
        : listing.availability === "low_stock"
          ? 6
          : undefined,
    badge: listing.badge,
    shortDescription: `${listing.brand} ${listing.name} — professional-grade equipment with Australian stock, GST-inclusive pricing, and trade account options.`,
    longDescription: `The ${listing.name} is available from A2Z Tools with competitive trade pricing, fast Australia-wide delivery, and local technical support. Sourced from authorised distributors with full manufacturer warranty. Contact our team for project pricing, bulk orders, and staged delivery to site.`,
    highlights: [
      "Australian warehouse stock",
      "GST-inclusive pricing with tax invoice",
      "Trade account & Net 30 terms available",
      "Free delivery on orders over $150",
    ],
    images: buildProductGalleryImages(listing.name, listing.brand),
    specifications: [
      {
        group: "General",
        items: [
          { label: "SKU", value: listing.sku },
          { label: "Brand", value: listing.brand },
          { label: "Category", value: categoryMeta.label },
          { label: "Availability", value: listing.availability.replace("_", " ") },
        ],
      },
      {
        group: "Ordering",
        items: [
          { label: "Price (inc GST)", value: listing.price },
          ...(listing.tradePrice
            ? [{ label: "Trade price (inc GST)", value: listing.tradePrice }]
            : []),
          { label: "Warranty", value: "Manufacturer standard warranty" },
        ],
      },
    ],
    downloads: [
      {
        id: "ds",
        title: "Product Datasheet",
        type: "PDF",
        size: "1.0 MB",
        href: "#",
      },
    ],
    reviews: buildFallbackReview(listing),
    relatedProductIds: allListingProducts
      .filter((p) => p.id !== listing.id && p.brand === listing.brand)
      .slice(0, 2)
      .concat(
        allListingProducts
          .filter((p) => p.id !== listing.id && p.brand !== listing.brand)
          .slice(0, 2)
      )
      .map((p) => p.id),
    breadcrumbs: [
      { label: "Home", href: "/" },
      { label: "Products", href: "/products" },
      { label: categoryMeta.label, href: categoryMeta.href },
      { label: listing.name },
    ],
    warranty: "Standard manufacturer warranty applies.",
    deliveryNote: "Free delivery on orders over $150 Australia-wide.",
    rating: listing.rating,
    reviewCount: listing.reviewCount,
  };
}

export function getProductBySlug(slug: string): ProductDetail | null {
  return productDetails[slug] ?? buildFallbackDetail(slug);
}

export function getAllProductSlugs(): string[] {
  const fromListings = allListingProducts.map((p) => slugFromHref(p.href));
  const fromDetails = Object.keys(productDetails);
  return [...new Set([...fromDetails, ...fromListings])];
}

export function getRelatedProducts(product: ProductDetail) {
  return allListingProducts.filter((p) =>
    product.relatedProductIds.includes(p.id)
  );
}

export { productDetails, u7ProDetail, c9200Detail, udmProMaxDetail };
