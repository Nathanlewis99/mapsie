import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import Logo from "@/components/Logo";
import SiteFooter from "@/components/SiteFooter";
import { Gallery } from "@/components/seo/Sections";
import { getPartner } from "@/lib/server/partners";
import StartTrip from "./StartTrip";

export const dynamic = "force-dynamic";

export async function generateMetadata({ params }: { params: Promise<{ partner: string }> }): Promise<Metadata> {
  const p = await getPartner((await params).partner);
  if (!p?.active) return {};
  return { title: `${p.name} × Mapsie: your trip as a map print`, robots: { index: false }, description: `A map print of your trip with ${p.name}: the real route, your photos and your names. Designed in minutes, framed and delivered.` };
}

// A partner's own page: mapsie.shop/with/<partner>[?trip=<id>]. Their routes, ready to personalise.
export default async function PartnerPage({ params, searchParams }: { params: Promise<{ partner: string }>; searchParams: Promise<{ trip?: string }> }) {
  const p = await getPartner((await params).partner);
  if (!p?.active) notFound();
  const want = (await searchParams).trip;
  const trips = want ? [...p.trips].sort((a, b) => (a.id === want ? -1 : b.id === want ? 1 : 0)) : p.trips;
  return (
    <div className="min-h-dvh overflow-x-hidden">
      <header className="max-w-6xl mx-auto px-6 py-5 flex justify-between items-center gap-4">
        <div className="flex items-baseline gap-3 min-w-0">
          <Link href="/" className="font-display text-3xl font-extrabold"><Logo /></Link>
          <span className="text-ink/40 font-bold">×</span>
          <span className="font-display text-xl font-extrabold truncate">{p.name}</span>
        </div>
      </header>
      <main>
        <section className="max-w-4xl mx-auto px-6 pt-6 pb-10">
          <h1 className="font-display text-4xl sm:text-5xl font-extrabold leading-tight tracking-tight">
            {p.welcome || `Your ${p.kind === "event" ? "challenge" : "trip"} with ${p.name}, as a map for your wall`}
          </h1>
          <p className="mt-5 text-lg text-ink/70">
            We&apos;ve drawn the route for you. Add your name, your photos and the moments you&apos;ll remember, choose a style and a frame,
            and we&apos;ll print it and deliver it to your door.
          </p>
          {p.promoCode && (
            <p className="mt-5 inline-block rounded-2xl bg-sand px-4 py-3 font-bold">
              🎁 {p.discountPct}% off for {p.name} customers: use code <span className="font-mono">{p.promoCode}</span> at checkout
            </p>
          )}
        </section>
        {(p.designs ?? []).some((d) => d.published) && (
          <section className="max-w-4xl mx-auto px-6 pb-10">
            <h2 className="font-display text-2xl font-extrabold">Ready-made maps from {p.name}</h2>
            <p className="text-ink/60 mt-1">Order one as it is, or add your own touches first.</p>
            <div className="mt-4 grid sm:grid-cols-2 gap-4">
              {(p.designs ?? []).filter((d) => d.published).map((d) => (
                <div key={d.id} className="rounded-3xl bg-white p-5 shadow-sm flex flex-col gap-3">
                  <div className="font-display text-xl font-extrabold">{d.name}</div>
                  <div className="flex flex-wrap gap-3 mt-auto">
                    <Link href={`/create?d=${d.id}`} className="rounded-full bg-coral px-5 py-2.5 font-extrabold text-white">Buy this map →</Link>
                    <a href={`/d/${d.id}`} target="_blank" rel="noreferrer" className="rounded-full border-2 border-ink/15 px-5 py-2 font-extrabold hover:border-coral">Preview</a>
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}
        <section className="max-w-4xl mx-auto px-6 pb-12 grid gap-4">
          {trips.map((t) => (
            <StartTrip key={t.id} partnerId={p.id} trip={t} highlight={t.id === want} />
          ))}
          <div className="rounded-3xl border-2 border-dashed border-ink/15 p-6 flex flex-wrap items-center justify-between gap-4">
            <div>
              <div className="font-extrabold text-lg">Did your own thing?</div>
              <div className="text-ink/60">Start with a blank map and add your own stops.</div>
            </div>
            <Link href={`/create?partner=${p.id}&new=1`} className="rounded-full border-2 border-ink/15 px-5 py-3 font-extrabold hover:border-coral">Start from scratch →</Link>
          </div>
        </section>
        <Gallery title="Maps made with Mapsie" />
        <p className="max-w-4xl mx-auto px-6 pb-12 text-center text-sm text-ink/50">Free to design · from £19 · free delivery in the UK, US and Australia</p>
      </main>
      <SiteFooter />
    </div>
  );
}
