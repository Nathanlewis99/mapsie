"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { christmasState, niceDate, type ChristmasState } from "@/lib/christmas";
import { guessRegion, type RegionId } from "@/lib/products";
import { BLACK_FRIDAY, blackFridayOn } from "@/lib/offers";

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
  const [bf, setBf] = useState(false);
  useEffect(() => (setS(christmasState(region())), setBf(blackFridayOn())), []);
  if (s.kind === "none" && !bf) return null;
  return (
    <>
    {bf && (
      <div className="bg-ink text-white text-sm text-center px-4 py-2 font-semibold">
        🏷️ Black Friday launch sale: <b>{BLACK_FRIDAY.pct}% off everything</b> with code <b className="tracking-wider">{BLACK_FRIDAY.code}</b> · ends Monday
      </div>
    )}
    {s.kind !== "none" && (
    <div className="bg-[#1f4d3a] text-white text-sm text-center px-4 py-2 font-semibold">
      🎄{" "}
      {s.kind === "standard" && <>Order by <b>{niceDate(s.date)}</b> for delivery before Christmas{s.express !== s.date ? ` (or ${niceDate(s.express)} with express)` : ""}.</>}
      {s.kind === "express" && <>Last days for Christmas: order by <b>{niceDate(s.date)}</b> with <b>express delivery</b>.</>}
      {s.kind === "digital" && <>Too late for delivery before Christmas? Give a <b>gift card</b> or the <b>digital file</b>: both arrive by email in minutes.</>}{" "}
      <Link href="/gift" className="underline underline-offset-2 whitespace-nowrap">Gift cards</Link>
    </div>
    )}
    </>
  );
}
