export interface BrandProfile {
  id: string;
  name: string;
  description: string;
  authorised: boolean;
  href: string;
}

const profiles: Record<string, BrandProfile> = {
  ubiquiti: {
    id: "ubiquiti",
    name: "Ubiquiti",
    description:
      "Authorised Ubiquiti distributor. UniFi switching, Wi-Fi 7 access points, and Dream Machine gateways with Australian warranty and local firmware support.",
    authorised: true,
    href: "/brands/ubiquiti",
  },
  cisco: {
    id: "cisco",
    name: "Cisco",
    description:
      "Cisco Select partner stocking Catalyst switching, Meraki cloud-managed wireless, ISR routing, and Secure Firewall appliances for enterprise and MSP deployments.",
    authorised: true,
    href: "/brands/cisco",
  },
  "tp-link": {
    id: "tp-link",
    name: "TP-Link Omada",
    description:
      "TP-Link Omada managed switches and access points for SMB and mid-market networks — centralised cloud or on-prem controller options.",
    authorised: true,
    href: "/brands/tp-link",
  },
  "fluke-networks": {
    id: "fluke-networks",
    name: "Fluke Networks",
    description:
      "Certified cable analysers, fibre testers, and network verification tools for structured cabling contractors and data centre teams.",
    authorised: true,
    href: "/brands/fluke-networks",
  },
  hikvision: {
    id: "hikvision",
    name: "Hikvision",
    description:
      "Hikvision commercial IP cameras, NVRs, and access control hardware with Australian compliance documentation and RMA support.",
    authorised: true,
    href: "/brands/hikvision",
  },
  aruba: {
    id: "aruba",
    name: "Aruba",
    description:
      "HPE Aruba campus switching and Wi-Fi for education, healthcare, and enterprise — Instant On and Aruba Central options.",
    authorised: true,
    href: "/brands/aruba",
  },
  netgear: {
    id: "netgear",
    name: "Netgear",
    description:
      "Netgear ProSAFE and Orbi Pro business networking for SOHO through mid-size deployments.",
    authorised: true,
    href: "/brands/netgear",
  },
  mikrotik: {
    id: "mikrotik",
    name: "MikroTik",
    description:
      "MikroTik RouterOS platforms for WISPs, integrators, and power users — routers, switches, and wireless in one ecosystem.",
    authorised: true,
    href: "/brands/mikrotik",
  },
  "d-link": {
    id: "d-link",
    name: "D-Link",
    description:
      "D-Link business switches and wireless for cost-effective commercial installations.",
    authorised: true,
    href: "/brands/d-link",
  },
};

export function getBrandProfile(brandName: string): BrandProfile {
  const key = brandName.toLowerCase().replace(/\s+/g, "-");
  const normalized = key.includes("fluke")
    ? "fluke-networks"
    : key.includes("tp-link") || key === "tp-link"
      ? "tp-link"
      : key;

  return (
    profiles[normalized] ?? {
      id: normalized,
      name: brandName,
      description: `${brandName} professional hardware supplied through authorised Australian distribution with manufacturer warranty.`,
      authorised: true,
      href: `/brands/${normalized}`,
    }
  );
}
