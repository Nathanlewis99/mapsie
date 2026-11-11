"use client";
import Link from "next/link";
import dynamic from "next/dynamic";
import { useEffect, useState } from "react";
import { SAMPLE } from "@/lib/sample";
import { guessRegion, money, PRODUCTS, REGIONS, type RegionId } from "@/lib/products";

const Poster = dynamic(() => import("@/components/Poster"), { ssr: false });

const FEATURES = [
  { icon: "✈️", title: "Every way you travelled", text: "Flights arc across oceans, road trips follow the real roads, trains, boats and hikes each get their own line." },
  { icon: "🌍", title: "Countries you've been", text: "Light up every country on your route with one tap." },
  { icon: "✍️", title: "Notes & photos", text: "Write “swam with turtles!” right on the map, or pin your own photos where they were taken." },
  { icon: "🎨", title: "Endless styles", text: "Vintage, topographic, midnight… then change any colour to make it yours." },
  { icon: "🖼️", title: "Framed & ready to hang", text: "A4 up to A1, with black, white or oak frames. Preview it on a wall before you buy." },
  { icon: "🚚", title: "Printed near you", text: `Made to order and delivered across ${REGIONS.map((r) => r.label).join(", ").replace(/, ([^,]*)$/, " and $1")}.` },
];

const STEPS = [
  { icon: "📍", title: "Add your stops", text: "Search the places you went. We draw the route between them." },
  { icon: "🎨", title: "Make it yours", text: "Pick a style, tweak every colour, choose your fonts and layout." },
  { icon: "🐊", title: "Stick on memories", text: "Scuba divers, crocodiles, temples, your own photos — drag them anywhere." },
  { icon: "📦", title: "We print & deliver", text: "Museum-quality print, made to order and sent to your door." },
];

export default function Home() {
  const [region, setRegion] = useState<RegionId>("GB");
  useEffect(() => setRegion(guessRegion()), []);
  const from = Math.min(...PRODUCTS.map((p) => p.price[region]));
  return (
    <div className="min-h-dvh overflow-x-hidden">
      <header className="max-w-6xl mx-auto px-6 py-5 flex justify-between items-center">
        <span className="font-display text-3xl font-extrabold">Mapsie<span className="text-coral">.</span></span>
        <Link href="/create" className="rounded-full bg-ink text-white px-5 py-2.5 font-extrabold hover:bg-ink/85">Start designing</Link>
      </header>

      <main>
        <section className="max-w-6xl mx-auto px-6 pt-8 pb-20 grid lg:grid-cols-[1.1fr_1fr] gap-12 items-center">
          <div>
            <div className="inline-block rounded-full bg-coral/15 text-coral-dark px-4 py-1.5 text-sm font-extrabold mb-6">✈️ For travellers who want more than photos on a phone</div>
            <h1 className="font-display text-5xl sm:text-6xl font-extrabold leading-[1.02] tracking-tight">
              Your trip,<br />
              <span className="text-coral">on your wall.</span>
            </h1>
            <p className="mt-6 text-lg text-ink/70 max-w-lg">
              Design a one-of-a-kind map print of your adventure. Every stop, the route between them and stickers of everything you got up to, beautifully printed and delivered.
            </p>
            <div className="mt-8 flex flex-wrap gap-3 items-center">
              <Link href="/create" className="rounded-full bg-coral px-7 py-4 text-lg font-extrabold text-white shadow-xl shadow-coral/30 hover:bg-coral-dark hover:-translate-y-0.5 transition">
                Create my map →
              </Link>
              <span className="text-sm text-ink/50 font-semibold">From {money(region, from)} · Free delivery · Ships to 🇬🇧 🇺🇸 🇦🇺</span>
            </div>
          </div>
          <div className="relative grid place-items-center">
            <div className="absolute w-[420px] h-[420px] rounded-full bg-sea/20 blur-3xl -z-10" />
            <div className="rotate-2 shadow-[0_40px_80px_-20px_rgba(31,36,48,0.45)] pointer-events-none">
              <Poster design={SAMPLE} width={400} />
            </div>
          </div>
        </section>

        <section className="bg-white/60 border-y border-ink/5">
          <div className="max-w-6xl mx-auto px-6 py-16 grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {STEPS.map((s, i) => (
              <div key={s.title} className="rounded-3xl bg-cream p-6">
                <div className="text-4xl">{s.icon}</div>
                <div className="mt-4 text-xs font-extrabold text-coral">STEP {i + 1}</div>
                <div className="font-extrabold text-lg">{s.title}</div>
                <p className="text-ink/60 mt-1 text-sm">{s.text}</p>
              </div>
            ))}
          </div>
        </section>

        <section className="max-w-6xl mx-auto px-6 py-20">
          <h2 className="font-display text-4xl font-extrabold text-center">Made for the trip <span className="text-coral">you</span> took</h2>
          <div className="mt-10 grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
            {FEATURES.map((f) => (
              <div key={f.title} className="rounded-3xl bg-white p-6 shadow-sm">
                <div className="text-3xl">{f.icon}</div>
                <div className="font-extrabold text-lg mt-3">{f.title}</div>
                <p className="text-ink/60 mt-1 text-sm">{f.text}</p>
              </div>
            ))}
          </div>
          <div className="mt-12 text-center">
            <Link href="/create" className="inline-block rounded-full bg-coral px-8 py-4 text-lg font-extrabold text-white shadow-xl shadow-coral/30 hover:bg-coral-dark hover:-translate-y-0.5 transition">
              Start my map, it&apos;s free to design →
            </Link>
          </div>
        </section>
      </main>

      <footer className="max-w-6xl mx-auto px-6 py-10 text-xs text-ink/40 flex flex-wrap gap-x-6 gap-y-2 justify-between">
        <span>© {new Date().getFullYear()} Mapsie</span>
        <span>Map data © OpenStreetMap contributors · Tiles by OpenFreeMap · Stickers: Twemoji (CC-BY 4.0)</span>
      </footer>
    </div>
  );
}
