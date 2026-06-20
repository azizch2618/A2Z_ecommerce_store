import { SiteLayout } from "@/components/layout";
import {
  CategoriesSection,
  FeaturedBrandsSection,
  FeaturedProductsSection,
  HeroSection,
  NewsletterSection,
  TestimonialsSection,
  TradeCtaSection,
  WhyChooseUsSection,
} from "@/components/home";

export default function HomePage() {
  return (
    <SiteLayout>
      <HeroSection />
      <CategoriesSection />
      <FeaturedProductsSection />
      <FeaturedBrandsSection />
      <WhyChooseUsSection />
      <TradeCtaSection />
      <TestimonialsSection />
      <NewsletterSection />
    </SiteLayout>
  );
}
