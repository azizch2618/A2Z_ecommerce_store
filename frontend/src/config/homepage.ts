export interface HeroContent {
  eyebrow: string;
  title: string;
  description: string;
  primaryCta: { label: string; href: string };
  secondaryCta: { label: string; href: string };
  highlights: string[];
}

export interface CategoryTile {
  id: string;
  label: string;
  description: string;
  href: string;
  productCount: string;
}

export interface ProductPlaceholder {
  id: string;
  brand: string;
  name: string;
  sku: string;
  price: string;
  tradePrice?: string;
  stock: "in_stock" | "low_stock" | "out_of_stock";
  badge?: string;
  href: string;
}

export interface BrandPlaceholder {
  id: string;
  name: string;
  description: string;
  href: string;
}

export interface ValueProp {
  id: string;
  title: string;
  description: string;
}

export interface Testimonial {
  id: string;
  quote: string;
  author: string;
  role: string;
  company: string;
}

export const heroContent: HeroContent = {
  eyebrow: "Australian hardware & networking specialists",
  title: "Enterprise-grade gear for every install",
  description:
    "Switches, wireless, tools, and security from trusted brands — with trade pricing, fast delivery, and local support.",
  primaryCta: { label: "Shop Networking", href: "/networking" },
  secondaryCta: { label: "Open Trade Account", href: "/trade" },
  highlights: [
    "5,000+ SKUs in stock",
    "Free delivery over $150",
    "Net 30 for trade accounts",
  ],
};

export const categoryTiles: CategoryTile[] = [
  {
    id: "networking",
    label: "Networking",
    description: "Switches, routers & wireless",
    href: "/networking",
    productCount: "1,200+ products",
  },
  {
    id: "tools",
    label: "Tools",
    description: "Crimpers, testers & kits",
    href: "/tools",
    productCount: "850+ products",
  },
  {
    id: "electrical",
    label: "Electrical",
    description: "Cable, racks & panels",
    href: "/electrical",
    productCount: "2,100+ products",
  },
  {
    id: "security",
    label: "Security",
    description: "Cameras & access control",
    href: "/security",
    productCount: "640+ products",
  },
  {
    id: "brands",
    label: "Brands",
    description: "Cisco, Ubiquiti & more",
    href: "/brands",
    productCount: "40+ brands",
  },
  {
    id: "trade",
    label: "Trade",
    description: "Bulk order & quotes",
    href: "/trade",
    productCount: "B2B pricing",
  },
];

export const featuredProducts: ProductPlaceholder[] = [
  {
    id: "1",
    brand: "Ubiquiti",
    name: "UniFi 7 Pro Access Point",
    sku: "U7-PRO-AU",
    price: "$449.00",
    tradePrice: "$389.00",
    stock: "in_stock",
    badge: "New",
    href: "/products/unifi-7-pro",
  },
  {
    id: "2",
    brand: "Cisco",
    name: "Catalyst 9200 24-Port PoE+ Switch",
    sku: "C9200-24P",
    price: "$3,299.00",
    tradePrice: "$2,949.00",
    stock: "in_stock",
    href: "/products/c9200-24p",
  },
  {
    id: "3",
    brand: "TP-Link",
    name: "Omada 24-Port Gigabit PoE Switch",
    sku: "SG2428P",
    price: "$599.00",
    tradePrice: "$529.00",
    stock: "low_stock",
    badge: "Sale",
    href: "/products/sg2428p",
  },
  {
    id: "4",
    brand: "Fluke Networks",
    name: "LinkIQ Cable + Network Tester",
    sku: "LIQ-100",
    price: "$1,899.00",
    stock: "in_stock",
    href: "/products/linkiq-100",
  },
  {
    id: "5",
    brand: "Hikvision",
    name: "4MP AcuSense Dome Camera",
    sku: "DS-2CD2147G2",
    price: "$289.00",
    tradePrice: "$249.00",
    stock: "in_stock",
    href: "/products/ds-2cd2147g2",
  },
  {
    id: "6",
    brand: "Panduit",
    name: "Cat6A UTP Cable 305m Box",
    sku: "PU6A-305",
    price: "$419.00",
    stock: "in_stock",
    href: "/products/pu6a-305",
  },
];

export const featuredBrands: BrandPlaceholder[] = [
  {
    id: "cisco",
    name: "Cisco",
    description: "Enterprise switching & security",
    href: "/brands/cisco",
  },
  {
    id: "ubiquiti",
    name: "Ubiquiti",
    description: "UniFi wireless & networking",
    href: "/brands/ubiquiti",
  },
  {
    id: "tp-link",
    name: "TP-Link Omada",
    description: "SMB managed networking",
    href: "/brands/tp-link",
  },
  {
    id: "fluke",
    name: "Fluke Networks",
    description: "Cable & network testing",
    href: "/brands/fluke-networks",
  },
  {
    id: "hikvision",
    name: "Hikvision",
    description: "Video surveillance",
    href: "/brands/hikvision",
  },
  {
    id: "klein",
    name: "Klein Tools",
    description: "Professional hand tools",
    href: "/brands/klein",
  },
];

export const valueProps: ValueProp[] = [
  {
    id: "stock",
    title: "Real stock, real availability",
    description:
      "Live inventory across Australian warehouses — know what's ready to ship before you quote the job.",
  },
  {
    id: "trade",
    title: "Built for trade professionals",
    description:
      "Trade accounts, bulk ordering, price lists, and Net 30 terms for qualified businesses.",
  },
  {
    id: "support",
    title: "Local technical support",
    description:
      "Australian-based team who understand installs, specs, and job-site deadlines.",
  },
  {
    id: "delivery",
    title: "Nationwide delivery",
    description:
      "Express shipping to metro and regional areas, with click & collect available.",
  },
];

export const testimonials: Testimonial[] = [
  {
    id: "1",
    quote:
      "A2Z Tools is our go-to for UniFi and structured cabling. Stock is accurate and orders arrive when we need them on site.",
    author: "James Mitchell",
    role: "Operations Manager",
    company: "Pacific Network Solutions",
  },
  {
    id: "2",
    quote:
      "Trade pricing and quick quotes save our team hours every week. The bulk order form is exactly what we needed.",
    author: "Sarah Chen",
    role: "Procurement Lead",
    company: "Metro Electrical Group",
  },
  {
    id: "3",
    quote:
      "Reliable Cisco stock, clear GST pricing, and delivery across Queensland without the runaround.",
    author: "David O'Brien",
    role: "Senior Installer",
    company: "Coastal Comms Pty Ltd",
  },
];

export const tradeCtaContent = {
  title: "Unlock trade pricing & Net 30 terms",
  description:
    "Join thousands of Australian electricians, installers, and IT professionals saving on every order.",
  primaryCta: { label: "Apply for Trade Account", href: "/trade" },
  secondaryCta: { label: "Request a Quote", href: "/trade/quote" },
  stats: [
    { label: "Trade members", value: "12,000+" },
    { label: "Brands", value: "40+" },
    { label: "Avg. savings", value: "15%" },
  ],
};

export const newsletterContent = {
  title: "Get the A2Z trade digest",
  description:
    "New products, buying guides, and exclusive offers — straight to your inbox.",
  placeholder: "you@company.com.au",
  buttonLabel: "Subscribe",
  note: "We respect your privacy. Unsubscribe anytime.",
};
