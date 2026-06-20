export interface NavLink {
  label: string;
  href: string;
}

export interface NavColumn {
  title: string;
  links: NavLink[];
}

export interface FeaturedItem {
  brand: string;
  title: string;
  description: string;
  href: string;
}

export interface MegaMenuCategory {
  id: string;
  label: string;
  href: string;
  columns: NavColumn[];
  featured?: FeaturedItem;
}

export interface FooterLinkGroup {
  title: string;
  links: NavLink[];
}

export const announcementMessages = {
  primary:
    "Free delivery on orders over $150 — Australia-wide. Trade accounts get Net 30 terms.",
  tradeCta: { label: "Open a Trade Account", href: "/trade" },
} as const;

export const megaMenuCategories: MegaMenuCategory[] = [
  {
    id: "networking",
    label: "Networking",
    href: "/networking",
    columns: [
      {
        title: "Switches",
        links: [
          { label: "Managed Switches", href: "/networking/switches/managed" },
          { label: "Unmanaged Switches", href: "/networking/switches/unmanaged" },
          { label: "PoE Switches", href: "/networking/switches/poe" },
          { label: "Industrial Switches", href: "/networking/switches/industrial" },
        ],
      },
      {
        title: "Routers",
        links: [
          { label: "Enterprise Routers", href: "/networking/routers/enterprise" },
          { label: "SOHO Routers", href: "/networking/routers/soho" },
          { label: "4G / 5G Routers", href: "/networking/routers/cellular" },
          { label: "Firewall Appliances", href: "/networking/routers/firewall" },
        ],
      },
      {
        title: "Wireless",
        links: [
          { label: "Access Points", href: "/networking/wireless/access-points" },
          { label: "Controllers", href: "/networking/wireless/controllers" },
          { label: "Bridges", href: "/networking/wireless/bridges" },
          { label: "Antennas & Cables", href: "/networking/wireless/antennas" },
        ],
      },
    ],
    featured: {
      brand: "Ubiquiti",
      title: "UniFi 7 Access Point",
      description: "Wi-Fi 7 for high-density installs",
      href: "/brands/ubiquiti",
    },
  },
  {
    id: "tools",
    label: "Tools",
    href: "/tools",
    columns: [
      {
        title: "Hand Tools",
        links: [
          { label: "Crimpers & Strippers", href: "/tools/hand/crimpers" },
          { label: "Screwdrivers & Kits", href: "/tools/hand/screwdrivers" },
          { label: "Punch Down Tools", href: "/tools/hand/punch-down" },
        ],
      },
      {
        title: "Test Equipment",
        links: [
          { label: "Cable Testers", href: "/tools/test/cable" },
          { label: "Network Analysers", href: "/tools/test/network" },
          { label: "Tone & Probe Kits", href: "/tools/test/tone-probe" },
        ],
      },
      {
        title: "Power Tools",
        links: [
          { label: "Drills & Drivers", href: "/tools/power/drills" },
          { label: "Cutting Tools", href: "/tools/power/cutting" },
          { label: "Vacuums & Dust Extraction", href: "/tools/power/vacuums" },
        ],
      },
    ],
    featured: {
      brand: "Fluke Networks",
      title: "LinkIQ Cable Tester",
      description: "PoE testing and cable qualification",
      href: "/brands/fluke-networks",
    },
  },
  {
    id: "electrical",
    label: "Electrical",
    href: "/electrical",
    columns: [
      {
        title: "Cable & Conduit",
        links: [
          { label: "Cat6 & Cat6A", href: "/electrical/cable/cat6" },
          { label: "Fibre Optic", href: "/electrical/cable/fibre" },
          { label: "Conduit & Trunking", href: "/electrical/conduit" },
        ],
      },
      {
        title: "Components",
        links: [
          { label: "Outlets & Faceplates", href: "/electrical/components/outlets" },
          { label: "Patch Panels", href: "/electrical/components/patch-panels" },
          { label: "Keystone Jacks", href: "/electrical/components/keystones" },
        ],
      },
      {
        title: "Racks & Cabinets",
        links: [
          { label: "Wall Racks", href: "/electrical/racks/wall" },
          { label: "Floor Cabinets", href: "/electrical/racks/floor" },
          { label: "Cable Management", href: "/electrical/racks/management" },
        ],
      },
    ],
  },
  {
    id: "security",
    label: "Security",
    href: "/security",
    columns: [
      {
        title: "Surveillance",
        links: [
          { label: "IP Cameras", href: "/security/surveillance/ip-cameras" },
          { label: "NVRs & Recorders", href: "/security/surveillance/nvr" },
          { label: "Mounts & Housings", href: "/security/surveillance/mounts" },
        ],
      },
      {
        title: "Access Control",
        links: [
          { label: "Door Controllers", href: "/security/access/controllers" },
          { label: "Readers & Keypads", href: "/security/access/readers" },
          { label: "Electric Strikes", href: "/security/access/strikes" },
        ],
      },
      {
        title: "Alarms",
        links: [
          { label: "Panels & Keypads", href: "/security/alarms/panels" },
          { label: "Sensors", href: "/security/alarms/sensors" },
          { label: "Sirens & Strobes", href: "/security/alarms/sirens" },
        ],
      },
    ],
    featured: {
      brand: "Cisco",
      title: "Meraki MV Cameras",
      description: "Cloud-managed video security",
      href: "/brands/cisco",
    },
  },
  {
    id: "brands",
    label: "Brands",
    href: "/brands",
    columns: [
      {
        title: "Networking",
        links: [
          { label: "Cisco", href: "/brands/cisco" },
          { label: "Ubiquiti", href: "/brands/ubiquiti" },
          { label: "TP-Link Omada", href: "/brands/tp-link" },
          { label: "MikroTik", href: "/brands/mikrotik" },
        ],
      },
      {
        title: "Tools & Test",
        links: [
          { label: "Fluke Networks", href: "/brands/fluke-networks" },
          { label: "Klein Tools", href: "/brands/klein" },
          { label: "Ideal Industries", href: "/brands/ideal" },
        ],
      },
      {
        title: "Security",
        links: [
          { label: "Hikvision", href: "/brands/hikvision" },
          { label: "Axis", href: "/brands/axis" },
          { label: "Dahua", href: "/brands/dahua" },
        ],
      },
    ],
  },
];

export const tradeNavLink: NavLink = {
  label: "Trade",
  href: "/trade",
};

export const mobileQuickLinks: NavLink[] = [
  { label: "Quick Order", href: "/trade/quick-order" },
  { label: "Contact Sales", href: "/contact/sales" },
];

export const mobileAccountLinks: NavLink[] = [
  { label: "Dashboard", href: "/account" },
  { label: "My Orders", href: "/account/orders" },
  { label: "Wishlist", href: "/wishlist" },
  { label: "Saved Addresses", href: "/account/addresses" },
  { label: "Trade Account", href: "/account/trade" },
  { label: "Settings", href: "/account/settings" },
];

export const footerLinkGroups: FooterLinkGroup[] = [
  {
    title: "Shop",
    links: [
      { label: "Networking", href: "/networking" },
      { label: "Tools", href: "/tools" },
      { label: "Electrical", href: "/electrical" },
      { label: "Security", href: "/security" },
      { label: "Brands", href: "/brands" },
    ],
  },
  {
    title: "Trade & B2B",
    links: [
      { label: "Trade Account", href: "/trade" },
      { label: "Bulk Order", href: "/trade/bulk-order" },
      { label: "Request Quote", href: "/trade/quote" },
      { label: "Price Lists", href: "/trade/price-lists" },
      { label: "Credit Terms", href: "/trade/credit-terms" },
    ],
  },
  {
    title: "Support",
    links: [
      { label: "Contact Us", href: "/contact" },
      { label: "Delivery", href: "/delivery" },
      { label: "Returns", href: "/returns" },
      { label: "FAQs", href: "/faqs" },
      { label: "Track Order", href: "/track-order" },
    ],
  },
  {
    title: "Company",
    links: [
      { label: "About A2Z", href: "/about" },
      { label: "Careers", href: "/careers" },
      { label: "Blog", href: "/blog" },
      { label: "Privacy Policy", href: "/privacy" },
      { label: "Terms of Service", href: "/terms" },
    ],
  },
];

export const popularSearchCategories = [
  { label: "PoE Switches", href: "/networking/switches/poe" },
  { label: "UniFi Access Points", href: "/networking/wireless/access-points" },
  { label: "Cat6A Cable", href: "/electrical/cable/cat6" },
  { label: "Cable Testers", href: "/tools/test/cable" },
];

export const searchPlaceholder = "Search 5,000+ products, SKUs, and brands…";

export const paymentMethods = [
  "Visa",
  "Mastercard",
  "Amex",
  "PayPal",
  "Bank Transfer",
] as const;

export const socialLinks = [
  { label: "LinkedIn", href: "https://linkedin.com" },
  { label: "Facebook", href: "https://facebook.com" },
  { label: "YouTube", href: "https://youtube.com" },
] as const;
