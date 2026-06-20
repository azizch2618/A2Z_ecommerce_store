import { notFound } from "next/navigation";

import { SiteLayout } from "@/components/layout";
import { CategoryPageView } from "@/components/category";
import { getCategoryEntry, categorySlugs } from "@/config/category-registry";

interface CategoryPageProps {
  params: Promise<{ slug: string }>;
}

export function generateStaticParams() {
  return categorySlugs.map((slug) => ({ slug }));
}

export async function generateMetadata({ params }: CategoryPageProps) {
  const { slug } = await params;
  const entry = getCategoryEntry(slug);
  if (!entry) return { title: "Not Found | A2Z Tools" };

  return {
    title: `${entry.category.title} | A2Z Tools`,
    description: entry.category.description,
  };
}

export default async function CategoryRoutePage({ params }: CategoryPageProps) {
  const { slug } = await params;
  const entry = getCategoryEntry(slug);
  if (!entry) notFound();

  return (
    <SiteLayout>
      <CategoryPageView category={entry.category} products={entry.products} />
    </SiteLayout>
  );
}
