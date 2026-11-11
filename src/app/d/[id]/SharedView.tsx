"use client";
import Link from "next/link";
import dynamic from "next/dynamic";
import type { Design } from "@/lib/types";

const FramedPoster = dynamic(() => import("@/components/FramedPoster"), { ssr: false });

export default function SharedView({ design }: { design: Design }) {
  return (
    <div className="min-h-dvh">
      <header className="max-w-5xl mx-auto px-6 py-5 flex justify-between items-center">
        <Link href="/" className="font-display text-2xl font-extrabold">Mapsie<span className="text-coral">.</span></Link>
      </header>
      <main className="max-w-5xl mx-auto px-6 pb-16 grid md:grid-cols-[1fr_1fr] gap-10 items-center">
        <div className="grid place-items-center rounded-3xl bg-sand/70 p-6 sm:p-10">
          <FramedPoster design={design} width={Math.min(360, design.view.refWidth)} />
        </div>
        <div className="space-y-5">
          <div className="text-sm font-extrabold text-coral">✈️ SOMEONE SHARED THEIR TRIP</div>
          <h1 className="font-display text-4xl sm:text-5xl font-extrabold leading-tight">{design.title}</h1>
          <ol className="flex flex-wrap gap-2">
            {design.stops.map((s, i) => (
              <li key={s.id} className="rounded-full bg-white px-3 py-1.5 text-sm font-bold shadow-sm">
                <span className="text-coral mr-1">{i + 1}</span>{s.name}
              </li>
            ))}
          </ol>
          <p className="text-ink/60">Turn your own adventures into a print like this. Add your stops, pick a style, stick on your memories.</p>
          <div className="flex flex-wrap gap-3">
            <Link href={`/create?d=${design.id}`} className="rounded-full bg-coral px-6 py-3.5 font-extrabold text-white shadow-lg shadow-coral/30 hover:bg-coral-dark">Use this as a starting point</Link>
            <Link href="/create" className="rounded-full border-2 border-ink/15 px-6 py-3.5 font-extrabold hover:border-ink/40">Start from scratch</Link>
          </div>
        </div>
      </main>
    </div>
  );
}
