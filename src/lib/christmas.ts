// Christmas "order by" dates, per country. The last day to order (UK time) for
// delivery before Christmas, allowing for print time, framing and courier delays.
// Check against Prodigi's published cut-offs each year and adjust here.
import type { RegionId } from "./products";

export const CHRISTMAS = {
  year: 2026,
  showFrom: "2026-11-01",
  lastOrder: {
    // Prodigi 2026 (prodigi.com/christmas-delivery-dates), one day earlier to allow for
    // finishing the design and our cancellation hold. Unframed and framed use the earlier
    // of the two; Australia uses the WA/TAS/NT dates so every state is covered.
    GB: { standard: "2026-12-16", express: "2026-12-16" }, // Prodigi: prints 17/17, framed 17/21
    US: { standard: "2026-12-12", express: "2026-12-16" }, // Prodigi: prints 13/17, framed 15/17
    AU: { standard: "2026-12-12", express: "2026-12-15" }, // Prodigi WA/TAS/NT: 13/16 (other states 15/17)
  } satisfies Record<RegionId, { standard: string; express: string }>,
};

export type ChristmasState =
  | { kind: "none" }
  | { kind: "standard"; date: string; express: string }
  | { kind: "express"; date: string }
  | { kind: "digital" };

/** What to tell a customer in this country today. Dates are inclusive (order by the end of that day). */
export function christmasState(region: RegionId, now = new Date()): ChristmasState {
  const day = now.toISOString().slice(0, 10);
  const xmas = `${CHRISTMAS.year}-12-25`;
  if (day < CHRISTMAS.showFrom || day >= xmas) return { kind: "none" };
  const d = CHRISTMAS.lastOrder[region];
  if (day <= d.standard) return { kind: "standard", date: d.standard, express: d.express };
  if (day <= d.express) return { kind: "express", date: d.express };
  return { kind: "digital" };
}

export const niceDate = (iso: string) =>
  new Date(`${iso}T12:00:00Z`).toLocaleDateString("en-GB", { weekday: "short", day: "numeric", month: "long", timeZone: "UTC" });
