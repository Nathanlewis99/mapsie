import type { Metadata } from "next";
import HomeClient from "./HomeClient";
import JsonLd from "@/components/seo/JsonLd";
import { Faq, Gallery, OccasionLinks } from "@/components/seo/Sections";
import { Reviews } from "@/components/seo/Reviews";
import { homeJsonLd } from "@/lib/seo";
import { listReviews, reviewSummary, type Review } from "@/lib/server/db";

export const metadata: Metadata = {
  title: "Custom Travel Map Prints of Your Trip | Mapsie",
  description: "Design a custom travel map print of your trip: every stop, the real route, stickers and your own photos. Framed or unframed, printed and delivered in the UK, US and Australia.",
  alternates: { canonical: "/" },
};

// Rebuilt every 10 minutes, so new approved reviews appear without a deploy.
export const revalidate = 600;

async function loadReviews(): Promise<{ items: Review[]; count: number; average: number }> {
  try {
    const [all, sum] = await Promise.all([listReviews("approved", 30), reviewSummary()]);
    return { items: all.filter((r) => r.publish), ...sum };
  } catch {
    return { items: [], count: 0, average: 0 }; // e.g. no database at build time
  }
}

export default async function Home() {
  const reviews = await loadReviews();
  return (
    <HomeClient>
      <Gallery />
      <Reviews {...reviews} />
      <OccasionLinks />
      <Faq />
      <JsonLd data={homeJsonLd({ count: reviews.count, average: reviews.average, items: reviews.items.map((r) => ({ name: r.name, rating: r.rating, text: r.text, date: r.createdAt })) })} />
    </HomeClient>
  );
}
