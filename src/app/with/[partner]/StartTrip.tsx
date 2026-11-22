"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import type { PartnerTrip } from "@/lib/partners";

// One of a partner's routes: optional name / detail boxes, then straight into the designer.
export default function StartTrip({ partnerId, trip, highlight }: { partnerId: string; trip: PartnerTrip; highlight?: boolean }) {
  const router = useRouter();
  const [name, setName] = useState("");
  const [detail, setDetail] = useState("");
  const go = (e: React.FormEvent) => {
    e.preventDefault();
    const q = new URLSearchParams({ partner: partnerId, trip: trip.id, ...(name.trim() ? { n: name.trim() } : {}), ...(detail.trim() ? { x: detail.trim() } : {}) });
    router.push(`/create?${q}`);
  };
  return (
    <form onSubmit={go} className={`rounded-3xl bg-white p-6 shadow-sm ${highlight ? "ring-2 ring-coral" : ""}`}>
      <div className="flex items-start gap-4">
        <div className="text-4xl leading-none">{trip.emoji}</div>
        <div className="min-w-0 flex-1">
          <div className="font-display text-2xl font-extrabold">{trip.name}</div>
          <div className="text-ink/60 mt-1">{trip.stops.map((s) => s[0]).join(" → ")}</div>
        </div>
      </div>
      <div className="mt-5 flex flex-wrap items-end gap-3">
        {trip.ask?.name && (
          <label className="flex-1 min-w-[12rem]">
            <span className="text-sm font-bold text-ink/60">{trip.ask.name}</span>
            <input value={name} onChange={(e) => setName(e.target.value)} maxLength={60} className="mt-1 w-full rounded-xl border border-ink/15 px-3 py-2.5" />
          </label>
        )}
        {trip.ask?.detail && (
          <label className="flex-1 min-w-[12rem]">
            <span className="text-sm font-bold text-ink/60">{trip.ask.detail}</span>
            <input value={detail} onChange={(e) => setDetail(e.target.value)} maxLength={60} className="mt-1 w-full rounded-xl border border-ink/15 px-3 py-2.5" />
          </label>
        )}
        <button className="rounded-full bg-coral px-6 py-3.5 font-extrabold text-white shadow-lg shadow-coral/30 hover:bg-coral-dark">Design my map →</button>
      </div>
    </form>
  );
}
