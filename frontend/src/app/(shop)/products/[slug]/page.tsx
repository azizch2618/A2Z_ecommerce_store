import { ProductDetailPageClient } from "@/components/product-detail/product-detail-page-client";

interface ProductPageProps {
  params: Promise<{ slug: string }>;
}

export async function generateMetadata({ params }: ProductPageProps) {
  const { slug } = await params;
  return {
    title: `${slug.replace(/-/g, " ")} | A2Z Tools`,
    description: "Australian hardware and networking equipment — GST included.",
  };
}

export default async function ProductDetailPage({ params }: ProductPageProps) {
  const { slug } = await params;
  return <ProductDetailPageClient slug={slug} />;
}
