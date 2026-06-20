/**
 * Rich PDP content keyed by catalog slug — merged with live API data in demo mode.
 */
import type { ProductDetail } from "@/config/product-detail";

type Enrichment = Pick<
  ProductDetail,
  "highlights" | "specifications" | "reviews" | "downloads" | "warranty" | "deliveryNote"
>;

const enrichments: Record<string, Enrichment> = {
  "cisco-catalyst-9200": {
    highlights: [
      "48× Gigabit PoE+ ports, 740W budget",
      "Modular uplinks — 1G / 10G / 25G",
      "Cisco DNA Center ready",
      "MACsec and Trustworthy Systems",
    ],
    specifications: [
      {
        group: "Hardware",
        items: [
          { label: "Ports", value: "48× 10/100/1000 PoE+" },
          { label: "PoE Budget", value: "740 W" },
          { label: "Uplinks", value: "4× 1G/10G SFP+" },
        ],
      },
    ],
    reviews: [
      {
        id: "r1",
        author: "James Mitchell",
        company: "Sydney Cabling Co",
        role: "Network Engineer",
        rating: 5,
        title: "Rock-solid campus rollout",
        body: "Deployed twelve units across a school campus in Parramatta. DNA onboarding saved days of staging.",
        date: "2026-03-12",
        verified: true,
      },
    ],
    downloads: [],
    warranty: "3-year Cisco enhanced limited hardware warranty via authorised Australian reseller.",
    deliveryNote: "Ships from Sydney DC. Express metro delivery available.",
  },
  "unifi-dream-machine-pro": {
    highlights: [
      "10G SFP+ WAN/LAN",
      "Integrated UniFi Protect NVR",
      "IDS/IPS throughput 3.5 Gbps",
      "Rack-mountable 1U chassis",
    ],
    specifications: [
      {
        group: "Interfaces",
        items: [
          { label: "WAN", value: "1× 10G SFP+" },
          { label: "LAN", value: "8× GbE + 1× 10G SFP+" },
        ],
      },
    ],
    reviews: [
      {
        id: "r2",
        author: "Lisa Tran",
        company: "North Shore IT",
        role: "MSP Owner",
        rating: 5,
        title: "Perfect MSP gateway",
        body: "Single appliance for routing, firewall, and NVR — clients love the unified UniFi experience.",
        date: "2026-02-20",
        verified: true,
      },
    ],
    downloads: [],
    warranty: "1-year Ubiquiti limited warranty.",
    deliveryNote: "Usually ships within 1 business day from Sydney.",
  },
  "fluke-cable-tester-linkiq": {
    highlights: [
      "Cable pair mapping to 1000 m",
      "PoE class and load test",
      "Switch VLAN/speed discovery",
      "Colour touchscreen UI",
    ],
    specifications: [
      {
        group: "Capabilities",
        items: [
          { label: "Cable types", value: "Twisted pair, coax" },
          { label: "PoE test", value: "Up to 90W load" },
        ],
      },
    ],
    reviews: [
      {
        id: "r3",
        author: "Dave Wilson",
        company: "Wilson Comms",
        role: "Field Technician",
        rating: 5,
        title: "Worth every dollar",
        body: "Replaced our aging certifier for 80% of jobs. PoE load test alone pays for itself.",
        date: "2026-01-08",
        verified: true,
      },
    ],
    downloads: [],
    warranty: "Fluke Networks 3-year warranty.",
    deliveryNote: "Serialised asset — signature on delivery.",
  },
};

const defaultEnrichment: Enrichment = {
  highlights: [],
  specifications: [],
  reviews: [],
  downloads: [],
  warranty: "Australian consumer law applies. Manufacturer warranty per product documentation.",
  deliveryNote: "Standard delivery across Australia. GST included in displayed price.",
};

export function getProductEnrichment(slug: string): Enrichment {
  return enrichments[slug] ?? defaultEnrichment;
}
