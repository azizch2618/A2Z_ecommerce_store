"use client";

import * as React from "react";
import { toast } from "sonner";

import type { ListingProduct } from "@/types/product";
import { getProductStock } from "@/types/product";
import { getProductImage } from "@/config/visual-assets";
import { brandIdFromLabel } from "@/config/category-page";
import type { CategoryProduct } from "@/config/category-page";
import type { ProductPlaceholder } from "@/config/homepage";
import { useWishlist } from "@/components/wishlist";
import { ProductCard } from "@/components/product/product-card";
import { ProductQuickView } from "@/components/product/product-quick-view";
import { useAddToCart } from "@/lib/api/hooks/use-cart";
import { cn } from "@/lib/utils";

const productDescriptions: Record<string, { description: string; highlights: string[] }> = {
  "net-001": {
    description:
      "Layer 2/3 access switch with 24 PoE+ ports, 4×1G uplinks, and Cisco DNA-ready management for campus and branch deployments.",
    highlights: ["370W PoE budget", "Stackable up to 8 units", "Limited lifetime warranty"],
  },
  "net-002": {
    description:
      "Wi-Fi 7 access point with 6 spatial streams, 2.5 GbE uplink, and UniFi Network integration for high-density environments.",
    highlights: ["6 GHz support", "320 MHz channels", "Ceiling or wall mount"],
  },
  "net-003": {
    description:
      "Smart-managed Gigabit switch with 24 PoE+ ports and 4 SFP+ uplinks — ideal for SMB and mid-market networks.",
    highlights: ["195W PoE", "Cloud or local management", "Fanless design"],
  },
  "net-005": {
    description:
      "Cloud-managed 802.11ax access point with integrated Bluetooth Low Energy and Meraki dashboard visibility.",
    highlights: ["MU-MIMO", "Self-configuring mesh", "Enterprise security"],
  },
  "net-008": {
    description:
      "All-in-one security gateway with dual-WAN, IDS/IPS, and full UniFi application suite for demanding sites.",
    highlights: ["8× GbE ports", "Redundant storage", "10 Gbps IDS/IPS"],
  },
  "net-015": {
    description:
      "Layer 3 switch with 48 PoE++ ports, 600W budget, and 10G SFP+ uplinks for aggregation and access.",
    highlights: ["Etherlighting™", "UniFi Network managed", "Rack mountable"],
  },
  "tool-001": {
    description:
      "Dual-purpose cable and network tester for copper and active Ethernet links — ideal for field technicians certifying installs.",
    highlights: ["PoE load testing", "Switch/port ID", "Printable reports"],
  },
  "tool-002": {
    description:
      "Industry-standard Cat 6A/Class EA certification with modular design for enterprise structured cabling projects.",
    highlights: ["10-second autotest", "TIA-1152-A compliant", "LinkWare PC reporting"],
  },
  "tool-003": {
    description:
      "Compact live fibre detector for safe troubleshooting without disconnecting patch leads in active networks.",
    highlights: ["No batteries required", "Audible & visual alert", "Pocket-sized"],
  },
  "tool-004": {
    description:
      "PoE cable verifier with wiremap, length, and PoE class detection for quick field validation.",
    highlights: ["PoE class display", "Wiremap faults", "Rugged housing"],
  },
  "tool-005": {
    description:
      "Professional toner and probe kit for tracing and identifying copper pairs in noisy cable environments.",
    highlights: ["SmartTone™ technology", "Intermittent fault detection", "Includes probe"],
  },
  "tool-006": {
    description:
      "Enterprise OTDR for fibre troubleshooting with intuitive touchscreen workflow and cloud reporting.",
    highlights: ["Multi-mode & single-mode", "SmartLoop™ testing", "LinkWare Live ready"],
  },
  "cab-001": {
    description:
      "Shielded 24-port Cat6A patch panel for Omada rack deployments with numbered ports and cable management.",
    highlights: ["1U rack mount", "Shielded ports", "Omada ecosystem"],
  },
  "cab-002": {
    description:
      "Genuine Cisco 10GBASE-SR SFP+ transceiver pair for short-reach multimode fibre uplinks.",
    highlights: ["DOM support", "Multimode fibre", "Hot-swappable"],
  },
  "sec-001": {
    description:
      "4MP AcuSense turret camera with human/vehicle classification, built-in mic, and smart hybrid light for Australian commercial installs.",
    highlights: ["AcuSense analytics", "IP67 rated", "H.265+ compression"],
  },
  "sec-002": {
    description:
      "16-channel PoE NVR with 16× PoE ports, up to 10 TB storage, and Hik-Connect remote access for SMB surveillance.",
    highlights: ["16× PoE ports", "4K decode", "RAID support"],
  },
  "sec-003": {
    description:
      "24-port unmanaged PoE switch purpose-built for IP camera deployments with extended PoE range.",
    highlights: ["370W PoE budget", "6 KV surge protection", "Fanless"],
  },
  "sec-004": {
    description:
      "DeepinView bullet camera with motorised varifocal lens, licence plate capture, and perimeter intrusion detection.",
    highlights: ["2.7–12mm motorised lens", "DarkFighter imaging", "ANPR capable"],
  },
  "sec-005": {
    description:
      "QR code and fingerprint access terminal with face recognition for commercial door entry and time attendance.",
    highlights: ["Touchscreen UI", "Wiegand output", "Hik-Connect ready"],
  },
};

function toListingProduct(
  product: CategoryProduct | ProductPlaceholder
): ListingProduct {
  const stock = getProductStock(
    "availability" in product
      ? { stock: product.stock, availability: product.availability }
      : { stock: product.stock }
  );
  const extras = productDescriptions[product.id];
  const image = getProductImage(product.name, product.brand);

  return {
    id: product.id,
    brand: product.brand,
    brandId: brandIdFromLabel(product.brand),
    name: product.name,
    sku: product.sku,
    price: product.price,
    tradePrice: product.tradePrice,
    stock,
    badge: product.badge,
    href: product.href,
    priceValue: "priceValue" in product ? product.priceValue : undefined,
    rating: "rating" in product ? product.rating : undefined,
    reviewCount: "reviewCount" in product ? product.reviewCount : undefined,
    imageSrc: image.src,
    imageAlt: image.alt,
    description: extras?.description,
    highlights: extras?.highlights,
    defaultVariantId:
      "defaultVariantId" in product ? product.defaultVariantId : undefined,
  };
}

export interface ProductListingGridProps {
  products: Array<CategoryProduct | ProductPlaceholder>;
  layout?: "grid" | "list";
  className?: string;
}

function ProductListingGrid({
  products,
  layout = "grid",
  className,
}: ProductListingGridProps) {
  const listingProducts = React.useMemo(
    () => products.map(toListingProduct),
    [products]
  );

  const { isWishlisted, toggleFromListing } = useWishlist();
  const [quickViewProduct, setQuickViewProduct] = React.useState<ListingProduct | null>(null);
  const addToCart = useAddToCart();

  const handleToggleWishlist = React.useCallback(
    (productId: string) => {
      const product = listingProducts.find((item) => item.id === productId);
      if (product) toggleFromListing(product);
    },
    [listingProducts, toggleFromListing]
  );

  const handleAddToCart = React.useCallback(
    (product: ListingProduct) => {
      if (product.stock === "out_of_stock") return;
      if (!product.defaultVariantId) {
        toast.error("Unable to add to cart", {
          description: "Open the product page to add this item.",
        });
        return;
      }
      addToCart.mutate(
        { variant_id: product.defaultVariantId, quantity: 1 },
        {
          onSuccess: () => {
            toast.success(
              product.stock === "back_order"
                ? `${product.name} added to back order`
                : `${product.name} added to cart`
            );
          },
          onError: () => {
            toast.error("Could not add to cart", { description: "Please try again." });
          },
        }
      );
    },
    [addToCart]
  );

  return (
    <>
      <div
        className={cn(
          layout === "grid"
            ? "grid gap-4 sm:grid-cols-2 xl:grid-cols-3"
            : "flex flex-col gap-4",
          className
        )}
      >
        {listingProducts.map((product) => (
          <ProductCard
            key={product.id}
            product={product}
            layout={layout}
            isWishlisted={isWishlisted(product.id)}
            onToggleWishlist={handleToggleWishlist}
            onAddToCart={handleAddToCart}
            onQuickView={setQuickViewProduct}
          />
        ))}
      </div>

      <ProductQuickView
        product={quickViewProduct}
        open={quickViewProduct !== null}
        onOpenChange={(open) => {
          if (!open) setQuickViewProduct(null);
        }}
        isWishlisted={quickViewProduct ? isWishlisted(quickViewProduct.id) : false}
        onToggleWishlist={handleToggleWishlist}
        onAddToCart={handleAddToCart}
      />
    </>
  );
}

export { ProductListingGrid, toListingProduct };
