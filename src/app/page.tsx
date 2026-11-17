import type { Metadata } from "next";
import HomeClient from "./HomeClient";
import JsonLd from "@/components/seo/JsonLd";
import { Faq, Gallery, OccasionLinks } from "@/components/seo/Sections";
import { homeJsonLd } from "@/lib/seo";

export const metadata: Metadata = {
  title: "Custom Travel Map Prints of Your Trip | Mapsie",
  description: "Design a custom travel map print of your trip: every stop, the real route, stickers and your own photos. Framed or unframed, printed and delivered in the UK, US and Australia.",
  alternates: { canonical: "/" },
};

export default function Home() {
  return (
    <HomeClient>
      <Gallery />
      <OccasionLinks />
      <Faq />
      <JsonLd data={homeJsonLd()} />
    </HomeClient>
  );
}
