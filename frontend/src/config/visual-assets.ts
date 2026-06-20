/**
 * Curated professional B2B imagery — networking, hardware, and field work.
 * All URLs verified HTTP 200 (Unsplash + Pexels, commercial use).
 */

const unsplash = (photoId: string, width = 1200) =>
  `https://images.unsplash.com/${photoId}?auto=format&fit=crop&w=${width}&q=85`;

const pexels = (photoId: number, width = 1200) =>
  `https://images.pexels.com/photos/${photoId}/pexels-photo-${photoId}.jpeg?auto=compress&cs=tinysrgb&w=${width}`;

/** Verified photo IDs — do not add without HTTP verification */
const photos = {
  heroTechnician: "photo-1563986768609-322da13575f3",
  serverRack: "photo-1558494949-ef010cbdcc31",
  electronicsLab: "photo-1581091226825-a6a2a5aee158",
  fieldTechnician: "photo-1581092918056-0c4c3acd3789",
  warehouse: "photo-1586528116311-ad8dd3c8310d",
  circuitBoard: "photo-1518770660439-4636190af475",
  productDefault: "photo-1633356122544-f134324a6cee",
  devWorkspace: "photo-1504384308090-c894fdcc538d",
  hardwareBench: "photo-1587825140708-dfaf72ae4b04",
  techGlobe: "photo-1451187580459-43490279c0fa",
} as const;

const pexelsPhotos = {
  cabling: 442150,
  patchPanel: 325111,
  security: 3861969,
  wireless: 1148820,
  dataCentre: 2599244,
} as const;

export const visualAssets = {
  hero: {
    src: unsplash(photos.heroTechnician, 1600),
    alt: "Professional technician servicing enterprise server racks in a data centre",
  },
  categories: {
    networking: {
      src: unsplash(photos.serverRack, 900),
      alt: "Network server racks in a modern data centre",
    },
    switches: {
      src: unsplash(photos.serverRack, 900),
      alt: "Enterprise network switches in a server rack",
    },
    wireless: {
      src: pexels(pexelsPhotos.wireless, 900),
      alt: "Wireless networking and enterprise Wi-Fi infrastructure",
    },
    routers: {
      src: unsplash(photos.techGlobe, 900),
      alt: "Enterprise routing and WAN infrastructure",
    },
    tools: {
      src: unsplash(photos.electronicsLab, 900),
      alt: "Professional fibre and network installation tools",
    },
    "tools-test": {
      src: unsplash(photos.electronicsLab, 900),
      alt: "Cable certification and network test equipment",
    },
    electrical: {
      src: pexels(pexelsPhotos.cabling, 900),
      alt: "Structured cabling and patch panel installation",
    },
    cabling: {
      src: pexels(pexelsPhotos.patchPanel, 900),
      alt: "Structured cabling and patch panels",
    },
    security: {
      src: pexels(pexelsPhotos.security, 900),
      alt: "Commercial security and surveillance hardware",
    },
    brands: {
      src: unsplash(photos.hardwareBench, 900),
      alt: "Enterprise networking equipment from leading manufacturers",
    },
    trade: {
      src: unsplash(photos.warehouse, 900),
      alt: "Warehouse fulfilment for trade and project orders",
    },
    products: {
      src: unsplash(photos.productDefault, 900),
      alt: "Enterprise networking hardware product catalog",
    },
  },
  brands: {
    cisco: {
      src: unsplash(photos.serverRack, 700),
      alt: "Cisco enterprise networking infrastructure",
    },
    ubiquiti: {
      src: pexels(pexelsPhotos.wireless, 700),
      alt: "Ubiquiti UniFi wireless and switching solutions",
    },
    aruba: {
      src: unsplash(photos.serverRack, 700),
      alt: "Aruba campus networking equipment",
    },
    netgear: {
      src: pexels(pexelsPhotos.cabling, 700),
      alt: "Netgear ProSAFE business networking",
    },
    "tp-link": {
      src: unsplash(photos.productDefault, 700),
      alt: "TP-Link Omada managed networking",
    },
    mikrotik: {
      src: unsplash(photos.fieldTechnician, 700),
      alt: "MikroTik router and wireless platforms",
    },
    "d-link": {
      src: unsplash(photos.devWorkspace, 700),
      alt: "D-Link business switching and wireless",
    },
    fluke: {
      src: unsplash(photos.electronicsLab, 700),
      alt: "Fluke Networks cable certification tools",
    },
    "fluke-networks": {
      src: unsplash(photos.electronicsLab, 700),
      alt: "Fluke Networks cable and fibre test equipment",
    },
    hikvision: {
      src: pexels(pexelsPhotos.security, 700),
      alt: "Hikvision commercial security systems",
    },
    klein: {
      src: unsplash(photos.electronicsLab, 700),
      alt: "Klein Tools professional electrical and network tools",
    },
    default: {
      src: unsplash(photos.productDefault, 700),
      alt: "Professional networking hardware",
    },
  },
  products: {
    switch: {
      src: unsplash(photos.serverRack, 900),
      alt: "Enterprise network switch in server rack",
    },
    accessPoint: {
      src: pexels(pexelsPhotos.wireless, 900),
      alt: "Wireless access point and structured fibre backbone",
    },
    router: {
      src: unsplash(photos.techGlobe, 900),
      alt: "Enterprise router and rack infrastructure",
    },
    firewall: {
      src: pexels(pexelsPhotos.security, 900),
      alt: "Secure network appliance in data centre",
    },
    tool: {
      src: unsplash(photos.electronicsLab, 900),
      alt: "Network cable tester and installation toolkit",
    },
    camera: {
      src: pexels(pexelsPhotos.security, 900),
      alt: "Commercial IP security camera",
    },
    cabling: {
      src: pexels(pexelsPhotos.patchPanel, 900),
      alt: "Structured cabling patch panel",
    },
    technician: {
      src: unsplash(photos.fieldTechnician, 900),
      alt: "Field technician terminating network cabling",
    },
    default: {
      src: unsplash(photos.productDefault, 900),
      alt: "Professional networking hardware",
    },
  },
  gallery: {
    rack: {
      src: pexels(pexelsPhotos.dataCentre, 1400),
      alt: "Server rack with enterprise switching",
    },
    cabling: {
      src: pexels(pexelsPhotos.cabling, 1400),
      alt: "Structured cabling and patch panels",
    },
    fiber: {
      src: unsplash(photos.circuitBoard, 1400),
      alt: "Fibre optic backbone cabling",
    },
    technician: {
      src: unsplash(photos.fieldTechnician, 1400),
      alt: "Technician installing network infrastructure",
    },
    datacenter: {
      src: unsplash(photos.serverRack, 1400),
      alt: "Enterprise data centre environment",
    },
    tools: {
      src: unsplash(photos.electronicsLab, 1400),
      alt: "Professional network installation tools",
    },
  },
} as const;

/** Last-resort image when a remote URL fails at runtime */
export const fallbackImage = visualAssets.products.default;

export type ProductImageKind =
  | "switch"
  | "accessPoint"
  | "router"
  | "firewall"
  | "tool"
  | "camera"
  | "cabling"
  | "default";

export function getCategoryImage(categoryId: string) {
  const key = categoryId.toLowerCase();
  const image =
    visualAssets.categories[key as keyof typeof visualAssets.categories];
  return image ?? visualAssets.categories.networking;
}

export function getBrandImage(brandId: string) {
  const key = brandId.toLowerCase().replace(/\s+/g, "-");
  return (
    visualAssets.brands[key as keyof typeof visualAssets.brands] ??
    visualAssets.brands.default
  );
}

export function inferProductImageKind(name: string, brand?: string): ProductImageKind {
  const value = `${brand ?? ""} ${name}`.toLowerCase();

  if (
    value.includes("access point") ||
    value.includes("u7") ||
    value.includes("u6") ||
    value.includes("ap-") ||
    value.includes("hap") ||
    value.includes("mr46") ||
    value.includes("wireless")
  ) {
    return "accessPoint";
  }
  if (value.includes("switch") || value.includes("catalyst") || value.includes("jetstream")) {
    return "switch";
  }
  if (
    value.includes("router") ||
    value.includes("dream machine") ||
    value.includes("ccr") ||
    value.includes("isr") ||
    value.includes("orbi")
  ) {
    return "router";
  }
  if (value.includes("firewall") || value.includes("secure")) {
    return "firewall";
  }
  if (
    value.includes("tester") ||
    value.includes("fluke") ||
    value.includes("linkiq") ||
    value.includes("dsx") ||
    value.includes("otdr") ||
    value.includes("crimp")
  ) {
    return "tool";
  }
  if (
    value.includes("cable") ||
    value.includes("patch") ||
    value.includes("fibre") ||
    value.includes("fiber") ||
    value.includes("cat6") ||
    value.includes("cat6a")
  ) {
    return "cabling";
  }
  if (value.includes("camera") || value.includes("hikvision") || value.includes("nvr")) {
    return "camera";
  }
  return "default";
}

export function getProductImage(name: string, brand?: string) {
  const kind = inferProductImageKind(name, brand);
  return visualAssets.products[kind];
}

export function buildProductGalleryImages(name: string, brand: string) {
  const kind = inferProductImageKind(name, brand);
  const primary = visualAssets.products[kind];

  const sets: Record<ProductImageKind, Array<{ id: string; label: string }>> = {
    switch: [
      { id: "front", label: "Rack" },
      { id: "ports", label: "Cabling" },
      { id: "angle", label: "Facility" },
      { id: "detail", label: "Fibre" },
    ],
    accessPoint: [
      { id: "front", label: "Wireless" },
      { id: "cabling", label: "Cabling" },
      { id: "install", label: "Install" },
      { id: "rack", label: "Rack" },
    ],
    router: [
      { id: "front", label: "Router" },
      { id: "rack", label: "Rack" },
      { id: "tech", label: "Tech" },
      { id: "cabling", label: "Ports" },
    ],
    firewall: [
      { id: "front", label: "Security" },
      { id: "dc", label: "Data centre" },
      { id: "rack", label: "Rack" },
      { id: "cabling", label: "Cabling" },
    ],
    tool: [
      { id: "front", label: "Toolkit" },
      { id: "fiber", label: "Fibre" },
      { id: "cabling", label: "Cabling" },
      { id: "tech", label: "Field" },
    ],
    camera: [
      { id: "front", label: "Camera" },
      { id: "install", label: "Install" },
      { id: "cabling", label: "Cabling" },
      { id: "rack", label: "NVR" },
    ],
    cabling: [
      { id: "front", label: "Cabling" },
      { id: "rack", label: "Patch panel" },
      { id: "cabling", label: "Terminations" },
      { id: "tech", label: "Install" },
    ],
    default: [
      { id: "front", label: "Product" },
      { id: "rack", label: "Rack" },
      { id: "cabling", label: "Cabling" },
      { id: "tech", label: "Tech" },
    ],
  };

  const galleryMap: Record<string, { src: string; alt: string }> = {
    front: primary,
    rack: visualAssets.gallery.rack,
    cabling: visualAssets.gallery.cabling,
    ports: visualAssets.gallery.cabling,
    angle: visualAssets.gallery.datacenter,
    detail: visualAssets.gallery.fiber,
    fiber: visualAssets.gallery.fiber,
    install: visualAssets.gallery.technician,
    tech: visualAssets.gallery.technician,
    dc: visualAssets.gallery.datacenter,
    wireless: visualAssets.gallery.fiber,
    security: visualAssets.gallery.datacenter,
    toolkit: visualAssets.gallery.tools,
    field: visualAssets.gallery.technician,
    product: primary,
    nvr: visualAssets.gallery.rack,
    router: visualAssets.products.router,
    camera: visualAssets.products.camera,
  };

  return sets[kind].map((item) => {
    const asset = galleryMap[item.id] ?? primary;
    return {
      id: item.id,
      label: item.label,
      alt: `${brand} ${name} — ${asset.alt}`,
      src: asset.src,
    };
  });
}
