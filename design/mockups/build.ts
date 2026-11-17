// Builds the showcase designs in design/mockups/trips.ts into full Mapsie designs:
// real road routes for car/bus/tuk-tuk legs (from mapsie.shop's router), a map view
// fitted to the trip, and the theme. Writes design/mockups/designs/<slug>.json.
//   npx tsx design/mockups/build.ts
import { mkdirSync, writeFileSync } from "node:fs";
import { TRIPS } from "./trips";
import { PRESETS, themeFromPreset } from "../../src/lib/themes";
import { followsRoads, legKey } from "../../src/lib/geo";
import { stickerSrc } from "../../src/lib/stickers";
import { normalizeDesign, type Design, type LngLat, type Stop } from "../../src/lib/types";
import { posterAspect } from "../../src/lib/products";

const API = process.env.MAPSIE_URL ?? "https://mapsie.shop";
const REF_W = 400;

async function roads(stops: Stop[]) {
  // One request per run of consecutive road legs, like the editor does.
  for (let i = 1; i < stops.length; i++) {
    if (!followsRoads(stops[i].arriveBy)) continue;
    let j = i;
    while (j + 1 < stops.length && followsRoads(stops[j + 1].arriveBy)) j++;
    const pts = stops.slice(i - 1, j + 1);
    const r = await fetch(`${API}/api/route`, { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ points: pts.map((p) => [p.lng, p.lat]) }) });
    const legs: ({ coordinates: LngLat[] } | null)[] = r.ok ? (await r.json()).legs : [];
    legs.forEach((leg, k) => {
      const s = stops[i + k];
      if (leg?.coordinates?.length) Object.assign(s, { path: leg.coordinates, pathFor: legKey(stops[i + k - 1], s) });
    });
    console.log(`  roads ${pts.map((p) => p.name).join(" → ")}: ${legs.filter(Boolean).length}/${pts.length - 1} legs`);
    i = j;
  }
}

/** Centre and zoom that fit every stop (and sticker) inside the map area, with a margin. */
function fit(d: Design, mapFrac: number, adj: { zoom?: number; up?: number } = {}, topFrac = mapFrac) {
  const pts: LngLat[] = d.stops.map((s) => [s.lng, s.lat] as LngLat);
  const y = (lat: number) => Math.log(Math.tan(Math.PI / 4 + (lat * Math.PI) / 360));
  const lngs = pts.map((p) => p[0]);
  const ys = pts.map((p) => y(p[1]));
  const [w, e] = [Math.min(...lngs), Math.max(...lngs)];
  const [s, n] = [Math.min(...ys), Math.max(...ys)];
  const W = REF_W;
  const H = REF_W * posterAspect(d.productId, d.orientation) * mapFrac;
  const zx = Math.log2((W * 0.72 * 360) / (512 * Math.max(e - w, 0.001)));
  const zy = Math.log2((H * 0.7 * 2 * Math.PI) / (512 * Math.max(n - s, 0.00001)));
  const zoom = Math.min(zx, zy) + (adj.zoom ?? 0);
  // Shift the trip up when only the top part of the map is clear (title over the map),
  // plus any hand-tuned nudge. Units: fraction of the map's height.
  const fullH = REF_W * posterAspect(d.productId, d.orientation) * mapFrac;
  const shiftPx = (fullH - REF_W * posterAspect(d.productId, d.orientation) * topFrac) / 2 + (adj.up ?? 0) * fullH;
  const cy = (s + n) / 2 - (shiftPx * 2 * Math.PI) / (512 * 2 ** zoom);
  const lat = (Math.atan(Math.sinh(cy)) * 180) / Math.PI;
  return { center: [(w + e) / 2, lat] as LngLat, zoom: +zoom.toFixed(2), bearing: 0, refWidth: REF_W };
}

async function main() {
  mkdirSync("design/mockups/designs", { recursive: true });
  for (const t of TRIPS) {
    console.log(t.slug);
    const { preset, themePatch, ...rest } = t.design;
    const p = PRESETS.find((x) => x.id === preset)!;
    const theme = { ...themeFromPreset(p), ...(themePatch ?? {}) };
    if (themePatch?.details) theme.details = { ...themeFromPreset(p).details, ...themePatch.details };
    const d = normalizeDesign({
      id: t.slug,
      subtitle: "",
      font: "playfair",
      layout: "band",
      productId: "a3",
      orientation: "portrait",
      frame: t.frame,
      paper: "ema",
      mount: "none",
      glaze: "perspex",
      stickerStyle: "illustrated",
      ...rest,
      theme,
      view: { center: [0, 0], zoom: 2, bearing: 0, refWidth: REF_W },
      stickers: (rest.stickers ?? []).map((s) => (s.kind === "sticker" && s.name ? { ...s, src: stickerSrc(s.name, s.art) } : s)),
      text: { ...(rest.text ?? {}) } as Design["text"],
    } as Design);
    if (t.slug === "london-pub-crawl") {
      d.stops = d.stops.map((s, i) => ({ ...s, marker: { kind: "sticker", name: i === d.stops.length - 1 ? "pizza" : "beer", art: "illustrated" } }));
    }
    await roads(d.stops);
    const band = d.layout === "overlay" || d.layout === "none" ? 1 : d.orientation === "landscape" ? 0.78 : 0.84;
    d.view = fit(d, band, t.view ?? {}, d.layout === "overlay" ? 0.76 : band);
    writeFileSync(`design/mockups/designs/${t.slug}.json`, JSON.stringify(d, null, 1));
  }
}
main();
