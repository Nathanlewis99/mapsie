// Christmas "order by" dates, per country. The last day to order (UK time) for
// delivery before Christmas, allowing for print time, framing and courier delays.
// Check against Prodigi's published cut-offs each year and adjust here.
import type { RegionId } from "./products";

export const CHRISTMAS = {
  year: 2026,
  showFrom: "2026-11-01",
  lastOrder: {
    GB: { standard: "2026-12-14", express: "2026-12-18" },
    US: { standard: "2026-12-09", express: "2026-12-15" },
    AU: { standard: "2026-12-07", express: "2026-12-13" },
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
