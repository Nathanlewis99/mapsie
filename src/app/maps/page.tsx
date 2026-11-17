import type { Metadata } from "next";
import Link from "next/link";
import Logo from "@/components/Logo";
import SiteFooter from "@/components/SiteFooter";
import { OCCASIONS } from "@/lib/occasions";
import { EXAMPLES } from "@/lib/seo";

export const metadata: Metadata = {
  title: "Travel Map Print Ideas: Honeymoons, Road Trips & Gifts | Mapsie",
  description: "Ideas for a personalised travel map print: honeymoons, road trips, gap years, Interrail, anniversaries and Christmas gifts.",
  alternates: { canonical: "/maps" },
};

export default function MapIdeas() {
  return (
    <div className="min-h-dvh">
      <header className="max-w-6xl mx-auto px-6 py-5 flex justify-between items-center">
        <Link href="/" className="font-display text-3xl font-extrabold"><Logo /></Link>
        <Link href="/create" className="rounded-full bg-ink text-white px-5 py-2.5 font-extrabold">Start designing</Link>
      </header>
      <main className="max-w-6xl mx-auto px-6 pb-16">
        <h1 className="font-display text-4xl sm:text-5xl font-extrabold mt-6">Map print ideas</h1>
        <p className="mt-4 text-lg text-ink/70 max-w-2xl">Every trip makes a different map. Pick the one closest to yours for ideas and a head start in the designer.</p>
        <div className="mt-10 grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {OCCASIONS.map((o) => {
            const ex = EXAMPLES.find((e) => e.slug === o.example) ?? EXAMPLES[0];
            return (
              <Link key={o.slug} href={`/maps/${o.slug}`} className="rounded-3xl bg-white p-2 shadow-sm hover:-translate-y-0.5 transition">
                <img src={`/examples/${ex.slug}-600.webp`} alt={ex.alt} width={600} height={450} loading="lazy" className="rounded-2xl w-full h-auto" />
                <div className="p-3">
                  <div className="font-extrabold text-lg">{o.nav}</div>
                  <p className="text-sm text-ink/60 mt-1">{o.description}</p>
                </div>
              </Link>
            );
          })}
        </div>
      </main>
      <SiteFooter />
    </div>
  );
}
