"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { christmasState, niceDate, type ChristmasState } from "@/lib/christmas";
import { guessRegion, type RegionId } from "@/lib/products";

function region(): RegionId {
  try {
    return JSON.parse(localStorage.getItem("mapsie-design") ?? "{}").state?.region ?? guessRegion();
  } catch {
    return guessRegion();
  }
}

/** "Order by … for Christmas" for the visitor's country (nothing outside the season). */
export default function ChristmasBanner() {
  const [s, setS] = useState<ChristmasState>({ kind: "none" });
  useEffect(() => setS(christmasState(region())), []);
  if (s.kind === "none") return null;
  return (
    <div className="bg-[#1f4d3a] text-white text-sm text-center px-4 py-2 font-semibold">
      🎄{" "}
      {s.kind === "standard" && <>Order by <b>{niceDate(s.date)}</b> for delivery before Christmas (or {niceDate(s.express)} with express).</>}
      {s.kind === "express" && <>Last days for Christmas: order by <b>{niceDate(s.date)}</b> with <b>express delivery</b>.</>}
      {s.kind === "digital" && <>Too late for delivery before Christmas? Choose the <b>digital file</b>: it&apos;s emailed in minutes, ready to give.</>}{" "}
      <Link href="/maps/christmas-travel-map-gift" className="underline underline-offset-2 whitespace-nowrap">Gift ideas</Link>
    </div>
  );
}
