import type {
  SearchBrandResult,
  SearchCategoryResult,
  SearchProductResult,
} from "@/types/search";
import { catalogProducts } from "@/config/catalog-page";
import { categoryRegistry } from "@/config/category-registry";
import { getProductImage } from "@/config/visual-assets";
import { buildProductGalleryImages, fallbackImage } from "@/config/visual-assets";

export const popularSearches = [
  "Cisco Switch",
  "UniFi Access Point",
  "Security Camera",
] as const;

export const SEARCH_DEBOUNCE_MS = 280;
export const SEARCH_MIN_QUERY_LENGTH = 1;
export const MAX_PRODUCT_RESULTS = 5;
export const MAX_CATEGORY_RESULTS = 4;
export const MAX_BRAND_RESULTS = 5;

function galleryImage(name: string, brand: string) {
  const image = buildProductGalleryImages(name, brand)[0] ?? fallbackImage;
  return { src: image.src, alt: image.alt };
}

const flagshipProducts: SearchProductResult[] = [
  {
    id: "net-001",
    name: "Catalyst 9200L 24-Port Managed Switch",
    brand: "Cisco",
    sku: "C9200L-24P-4G-E",
    href: "/products/c9200l-24p",
    ...(() => {
      const img = galleryImage("Catalyst 9200L 24-Port Managed Switch", "Cisco");
      return { imageSrc: img.src, imageAlt: img.alt };
    })(),
    priceLabel: "$2,849.00",
  },
  {
    id: "net-008",
    name: "UniFi Dream Machine Pro Max",
    brand: "Ubiquiti",
    sku: "UDM-PRO-MAX",
    href: "/products/udm-pro-max",
    ...(() => {
      const img = galleryImage("UniFi Dream Machine Pro Max", "Ubiquiti");
      return { imageSrc: img.src, imageAlt: img.alt };
    })(),
    priceLabel: "$899.00",
  },
  {
    id: "net-002",
    name: "UniFi 7 Pro Access Point (U7-Pro)",
    brand: "Ubiquiti",
    sku: "U7-PRO",
    href: "/products/u7-pro",
    ...(() => {
      const img = galleryImage("UniFi 7 Pro Access Point (U7-Pro)", "Ubiquiti");
      return { imageSrc: img.src, imageAlt: img.alt };
    })(),
    priceLabel: "$449.00",
  },
];

const catalogSearchProducts: SearchProductResult[] = catalogProducts.map((product) => {
  const image = getProductImage(product.name, product.brand);
  return {
    id: product.id,
    name: product.name,
    brand: product.brand,
    sku: product.sku,
    href: product.href,
    imageSrc: image.src,
    imageAlt: image.alt,
    priceLabel: product.price,
  };
});

export const searchableProducts: SearchProductResult[] = [
  ...flagshipProducts,
  ...catalogSearchProducts.filter(
    (product) => !flagshipProducts.some((item) => item.id === product.id)
  ),
];

export const searchableCategories: SearchCategoryResult[] = Object.values(
  categoryRegistry
).map(({ category }) => ({
  id: category.slug,
  label: category.title,
  href: `/${category.slug}`,
  description: category.description,
}));

const brandMap = new Map<string, SearchBrandResult>();

for (const { category } of Object.values(categoryRegistry)) {
  for (const brand of category.brands) {
    if (!brandMap.has(brand.id)) {
      brandMap.set(brand.id, {
        id: brand.id,
        label: brand.label,
        href: `/brands/${brand.id}`,
        productCount: `${brand.count} products`,
      });
    }
  }
  for (const brand of category.featuredBrands) {
    if (!brandMap.has(brand.id)) {
      brandMap.set(brand.id, {
        id: brand.id,
        label: brand.name,
        href: brand.href,
        productCount: brand.productCount,
      });
    }
  }
}

export const searchableBrands: SearchBrandResult[] = [...brandMap.values()].sort(
  (a, b) => a.label.localeCompare(b.label)
);

export function buildSearchResultsUrl(query: string): string {
  return `/products?q=${encodeURIComponent(query.trim())}`;
}
