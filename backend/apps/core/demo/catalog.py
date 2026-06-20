"""Demo product catalog definitions for seed_demo."""

from __future__ import annotations

from typing import Any, TypedDict


class DemoReview(TypedDict):
    author: str
    company: str
    role: str
    rating: int
    title: str
    body: str
    date: str
    verified: bool


class DemoSpecGroup(TypedDict):
    group: str
    items: list[dict[str, str]]


class DemoProduct(TypedDict):
    name: str
    slug: str
    sku: str
    brand: str
    brand_slug: str
    category: str
    category_slug: str
    price_ex_gst_cents: int
    stock: int
    reorder_point: int
    short_description: str
    description: str
    highlights: list[str]
    image_url: str
    average_rating: float
    review_count: int
    specifications: list[DemoSpecGroup]
    reviews: list[DemoReview]
    badge: str | None


IMG = {
    "network": "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?auto=format&fit=crop&w=1200&q=85",
    "wireless": "https://images.pexels.com/photos/1148820/pexels-photo-1148820.jpeg?auto=compress&cs=tinysrgb&w=1200",
    "security": "https://images.pexels.com/photos/3861969/pexels-photo-3861969.jpeg?auto=compress&cs=tinysrgb&w=1200",
    "tools": "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?auto=format&fit=crop&w=1200&q=85",
    "electrical": "https://images.pexels.com/photos/442150/pexels-photo-442150.jpeg?auto=compress&cs=tinysrgb&w=1200",
    "rack": "https://images.unsplash.com/photo-1633356122544-f134324a6cee?auto=format&fit=crop&w=1200&q=85",
}

DEMO_CATEGORIES: list[dict[str, Any]] = [
    {"name": "Networking", "slug": "networking", "description": "Enterprise switches, routers, and Wi-Fi."},
    {"name": "Security", "slug": "security", "description": "IP cameras, NVRs, and surveillance."},
    {"name": "Tools", "slug": "tools", "description": "Certification, fibre, and hand tools."},
    {"name": "Electrical", "slug": "electrical", "description": "Test equipment and cable management."},
]

DEMO_BRANDS: list[dict[str, str]] = [
    {"name": "Cisco", "slug": "cisco", "description": "Enterprise networking leader."},
    {"name": "Ubiquiti", "slug": "ubiquiti", "description": "UniFi networking ecosystem."},
    {"name": "TP-Link", "slug": "tp-link", "description": "Omada business networking."},
    {"name": "Hikvision", "slug": "hikvision", "description": "Commercial video surveillance."},
    {"name": "Fluke", "slug": "fluke", "description": "Professional test and measurement."},
    {"name": "Panduit", "slug": "panduit", "description": "Infrastructure and cable management."},
]

DEMO_PRODUCTS: list[DemoProduct] = [
    {
        "name": "Cisco Catalyst 9200 48-Port Switch",
        "slug": "cisco-catalyst-9200",
        "sku": "C9200-48P",
        "brand": "Cisco",
        "brand_slug": "cisco",
        "category": "Networking",
        "category_slug": "networking",
        "price_ex_gst_cents": 772727,
        "stock": 18,
        "reorder_point": 5,
        "short_description": "48-port PoE+ stackable access switch with Cisco DNA Essentials readiness.",
        "description": "The Cisco Catalyst 9200 Series delivers secure, programmable access for branch and campus deployments across Australia. Ideal for contractors rolling out PoE access layers with 10G uplinks and MACsec-capable hardware.",
        "highlights": [
            "48× Gigabit PoE+ ports, 740W budget",
            "Modular uplinks — 1G / 10G / 25G",
            "Cisco DNA Center ready",
            "MACsec and Trustworthy Systems",
        ],
        "image_url": IMG["network"],
        "average_rating": 4.8,
        "review_count": 24,
        "badge": "Bestseller",
        "specifications": [
            {
                "group": "Hardware",
                "items": [
                    {"label": "Ports", "value": "48× 10/100/1000 PoE+"},
                    {"label": "PoE Budget", "value": "740 W"},
                    {"label": "Uplinks", "value": "4× 1G/10G SFP+"},
                ],
            },
        ],
        "reviews": [
            {
                "author": "James Mitchell",
                "company": "Sydney Cabling Co",
                "role": "Network Engineer",
                "rating": 5,
                "title": "Rock-solid campus rollout",
                "body": "Deployed twelve units across a school campus in Parramatta. DNA onboarding saved days of staging.",
                "date": "2026-03-12",
                "verified": True,
            },
        ],
    },
    {
        "name": "Cisco Catalyst 9300 24-Port Switch",
        "slug": "cisco-catalyst-9300",
        "sku": "C9300-24U",
        "brand": "Cisco",
        "brand_slug": "cisco",
        "category": "Networking",
        "category_slug": "networking",
        "price_ex_gst_cents": 1136364,
        "stock": 9,
        "reorder_point": 4,
        "short_description": "High-performance modular core/access switch with 25G uplink options.",
        "description": "Catalyst 9300 Series switches are the workhorse for Australian enterprise LAN cores and high-density access. StackWise-480 delivers 480 Gbps stacking bandwidth with sub-second failover.",
        "highlights": [
            "24× multigigabit ports",
            "StackWise-480 up to 8 members",
            "Encrypted traffic analytics",
            "Australian warranty via authorised channel",
        ],
        "image_url": IMG["rack"],
        "average_rating": 4.7,
        "review_count": 18,
        "badge": None,
        "specifications": [
            {
                "group": "Performance",
                "items": [
                    {"label": "Switching capacity", "value": "502 Gbps"},
                    {"label": "Stacking", "value": "StackWise-480"},
                ],
            },
        ],
        "reviews": [],
    },
    {
        "name": "UniFi Dream Machine Pro",
        "slug": "unifi-dream-machine-pro",
        "sku": "UDM-PRO",
        "brand": "Ubiquiti",
        "brand_slug": "ubiquiti",
        "category": "Networking",
        "category_slug": "networking",
        "price_ex_gst_cents": 59091,
        "stock": 42,
        "reorder_point": 10,
        "short_description": "All-in-one UniFi gateway with 10G SFP+ WAN and integrated NVR HDD bay.",
        "description": "Dream Machine Pro consolidates routing, firewall, UniFi Network controller, and Protect NVR in a single 1U appliance — popular with Australian MSPs and trade integrators.",
        "highlights": [
            "10G SFP+ WAN/LAN",
            "Integrated UniFi Protect NVR",
            "IDS/IPS throughput 3.5 Gbps",
            "Rack-mountable 1U chassis",
        ],
        "image_url": IMG["wireless"],
        "average_rating": 4.6,
        "review_count": 56,
        "badge": "New",
        "specifications": [
            {
                "group": "Interfaces",
                "items": [
                    {"label": "WAN", "value": "1× 10G SFP+"},
                    {"label": "LAN", "value": "8× GbE + 1× 10G SFP+"},
                ],
            },
        ],
        "reviews": [],
    },
    {
        "name": "UniFi Switch Pro 24 PoE",
        "slug": "unifi-switch-pro-24",
        "sku": "USW-PRO-24-POE",
        "brand": "Ubiquiti",
        "brand_slug": "ubiquiti",
        "category": "Networking",
        "category_slug": "networking",
        "price_ex_gst_cents": 109091,
        "stock": 31,
        "reorder_point": 8,
        "short_description": "24-port Layer 3 PoE switch with 10G SFP+ uplinks and LCD touchscreen.",
        "description": "UniFi Switch Pro 24 delivers silent fanless operation for office IDFs with full Layer 3 routing and 400W PoE budget for APs and cameras.",
        "highlights": [
            "24× GbE PoE+ (400 W)",
            "2× 10G SFP+ uplinks",
            "Layer 3 static routing",
            "Touchscreen status display",
        ],
        "image_url": IMG["network"],
        "average_rating": 4.5,
        "review_count": 33,
        "badge": None,
        "specifications": [],
        "reviews": [],
    },
    {
        "name": "TP-Link Omada EAP670 WiFi 6 Access Point",
        "slug": "tp-link-omada-access-point",
        "sku": "EAP670",
        "brand": "TP-Link",
        "brand_slug": "tp-link",
        "category": "Networking",
        "category_slug": "networking",
        "price_ex_gst_cents": 16364,
        "stock": 67,
        "reorder_point": 15,
        "short_description": "Ceiling-mount WiFi 6 AP with 2.5G PoE+ and Omada SDN management.",
        "description": "Omada EAP670 is a cost-effective WiFi 6 choice for retail, hospitality, and warehouse offices across Australia with centralised cloud or on-prem controller.",
        "highlights": [
            "WiFi 6 dual-band 3.0 Gbps",
            "2.5 GbE uplink",
            "Omada SDN managed",
            "Includes mounting kit",
        ],
        "image_url": IMG["wireless"],
        "average_rating": 4.4,
        "review_count": 41,
        "badge": None,
        "specifications": [],
        "reviews": [],
    },
    {
        "name": "Hikvision 8MP AcuSense Turret Camera",
        "slug": "hikvision-ip-camera-8mp",
        "sku": "DS-2CD2387G2-LU",
        "brand": "Hikvision",
        "brand_slug": "hikvision",
        "category": "Security",
        "category_slug": "security",
        "price_ex_gst_cents": 29091,
        "stock": 54,
        "reorder_point": 12,
        "short_description": "8MP ColorVu turret with AcuSense human/vehicle classification and audio.",
        "description": "Professional turret camera for Australian commercial installs — 24/7 colour imaging, built-in mic, and H.265+ compression to reduce NVR storage costs.",
        "highlights": [
            "8MP 1/1.8\" sensor",
            "AcuSense deep learning",
            "ColorVu low-light colour",
            "IP67 weather rated",
        ],
        "image_url": IMG["security"],
        "average_rating": 4.6,
        "review_count": 29,
        "badge": None,
        "specifications": [],
        "reviews": [],
    },
    {
        "name": "Hikvision 32-Channel NVR 4K",
        "slug": "hikvision-nvr-32ch",
        "sku": "DS-7732NI-K4",
        "brand": "Hikvision",
        "brand_slug": "hikvision",
        "category": "Security",
        "category_slug": "security",
        "price_ex_gst_cents": 80909,
        "stock": 14,
        "reorder_point": 4,
        "short_description": "32-channel 4K NVR with 4 SATA bays and H.265+ smart search.",
        "description": "Rack-friendly NVR for mid-size surveillance projects. Supports up to 32 IP cameras with RAID-ready storage expansion for Australian compliance retention policies.",
        "highlights": [
            "32× IP channels @ 4K",
            "4× SATA (up to 16 TB each)",
            "HDMI/VGA simultaneous output",
            "ANZ firmware stock",
        ],
        "image_url": IMG["security"],
        "average_rating": 4.5,
        "review_count": 15,
        "badge": None,
        "specifications": [],
        "reviews": [],
    },
    {
        "name": "Fluke Networks LinkIQ Cable Tester",
        "slug": "fluke-cable-tester-linkiq",
        "sku": "LIQ-100",
        "brand": "Fluke",
        "brand_slug": "fluke",
        "category": "Tools",
        "category_slug": "tools",
        "price_ex_gst_cents": 218182,
        "stock": 8,
        "reorder_point": 3,
        "short_description": "Cable + network tester with PoE load testing and switch negotiation display.",
        "description": "LinkIQ validates copper and fibre links, displays switch port info, and performs PoE load tests — the go-to certifier alternative for Australian field techs.",
        "highlights": [
            "Cable pair mapping to 1000 m",
            "PoE class and load test",
            "Switch VLAN/speed discovery",
            "Colour touchscreen UI",
        ],
        "image_url": IMG["tools"],
        "average_rating": 4.9,
        "review_count": 12,
        "badge": "Bestseller",
        "specifications": [],
        "reviews": [],
    },
    {
        "name": "Professional Fibre Optic Tool Kit",
        "slug": "fibre-optic-tool-kit",
        "sku": "FIB-TOOL-PRO",
        "brand": "Panduit",
        "brand_slug": "panduit",
        "category": "Tools",
        "category_slug": "tools",
        "price_ex_gst_cents": 40909,
        "stock": 22,
        "reorder_point": 6,
        "short_description": "Complete fibre termination kit with cleaver, power meter, and VFL.",
        "description": "Field kit for LC/SC termination including visual fault locator, optical power meter, and Kevlar scissors — stocked for Australian fibre rollout crews.",
        "highlights": [
            "LC/SC cleaver included",
            "-50 to +26 dBm power meter",
            "1 mW VFL",
            "Hard case with foam inserts",
        ],
        "image_url": IMG["tools"],
        "average_rating": 4.3,
        "review_count": 8,
        "badge": None,
        "specifications": [],
        "reviews": [],
    },
    {
        "name": "RJ45 Pass-Through Crimping Tool Set",
        "slug": "crimping-tool-set-rj45",
        "sku": "CRIMP-RJ45-SET",
        "brand": "Panduit",
        "brand_slug": "panduit",
        "category": "Tools",
        "category_slug": "tools",
        "price_ex_gst_cents": 8645,
        "stock": 120,
        "reorder_point": 25,
        "short_description": "Ratchet crimper with stripper and 100 Cat6 pass-through connectors.",
        "description": "Trade-grade crimping set for Cat6/Cat6A pass-through connectors — ergonomic grip for high-volume patch panel work.",
        "highlights": [
            "Pass-through RJ45 compatible",
            "Built-in stripper & cutter",
            "100× Cat6 connectors included",
            "Lifetime tool warranty",
        ],
        "image_url": IMG["tools"],
        "average_rating": 4.2,
        "review_count": 37,
        "badge": None,
        "specifications": [],
        "reviews": [],
    },
    {
        "name": "Industrial True-RMS Multimeter",
        "slug": "industrial-multimeter",
        "sku": "DMM-IND-600",
        "brand": "Fluke",
        "brand_slug": "fluke",
        "category": "Electrical",
        "category_slug": "electrical",
        "price_ex_gst_cents": 25455,
        "stock": 36,
        "reorder_point": 8,
        "short_description": "CAT IV 600V industrial multimeter with logging and temperature input.",
        "description": "True-RMS measurements for noisy plant environments — Australian electricians use this for switchboard verification and HVAC commissioning.",
        "highlights": [
            "CAT IV 600 V safety rating",
            "True-RMS AC accuracy",
            "Min/max logging",
            "K-type temperature probe",
        ],
        "image_url": IMG["electrical"],
        "average_rating": 4.7,
        "review_count": 21,
        "badge": None,
        "specifications": [],
        "reviews": [],
    },
    {
        "name": "Vertical Cable Manager 42U (Pair)",
        "slug": "cable-management-42u",
        "sku": "CM-42U-VRT",
        "brand": "Panduit",
        "brand_slug": "panduit",
        "category": "Electrical",
        "category_slug": "electrical",
        "price_ex_gst_cents": 5909,
        "stock": 85,
        "reorder_point": 20,
        "short_description": "Pair of 42U vertical cable managers with fingers and cover panels.",
        "description": "Keeps rack installs tidy for data centre and comms room standards — powder-coated steel, shipped flat-packed from Sydney DC.",
        "highlights": [
            "Sold as pair (left + right)",
            "Finger pass-through design",
            "Tool-less mounting",
            "Black powder coat",
        ],
        "image_url": IMG["electrical"],
        "average_rating": 4.1,
        "review_count": 14,
        "badge": None,
        "specifications": [],
        "reviews": [],
    },
]

DEMO_PASSWORD = "Demo@2026!"

DEMO_ACCOUNTS: list[dict[str, Any]] = [
    {
        "email": "customer@demo.a2ztools.com",
        "first_name": "Sarah",
        "last_name": "Chen",
        "customer_type": "retail",
        "role": "customer",
    },
    {
        "email": "trade@demo.a2ztools.com",
        "first_name": "Michael",
        "last_name": "O'Brien",
        "customer_type": "trade",
        "role": "trade-customer",
        "organization": {
            "legal_name": "O'Brien Electrical & Data Pty Ltd",
            "trading_name": "O'Brien Electrical",
            "abn": "51824753556",
            "segment": "trade",
        },
    },
    {
        "email": "business@demo.a2ztools.com",
        "first_name": "Priya",
        "last_name": "Sharma",
        "customer_type": "business",
        "role": "trade-customer",
        "organization": {
            "legal_name": "Metro Facilities Group Pty Ltd",
            "trading_name": "Metro Facilities",
            "abn": "53004085616",
            "segment": "business",
        },
    },
    {
        "email": "admin@demo.a2ztools.com",
        "first_name": "Alex",
        "last_name": "Nguyen",
        "is_staff": True,
        "role": "manager",
    },
]
