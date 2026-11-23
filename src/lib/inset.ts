// Geometry for the overview ("locator") map in a corner of the poster: the whole country (or
// countries) the trip is in, with the route on it and a box showing what the main map shows.
// Pure functions, so they're easy to test; drawn as SVG by components/InsetMap.tsx.
import type { Stop } from "./types";

export type LngLat = [number, number];
type Ring = number[][];
type Poly = Ring[];

/** Web Mercator, scaled so the world is 0..1 on both axes (y down, like the screen). */
export function merc([lng, lat]: LngLat): [number, number] {
  const clamped = Math.max(-85, Math.min(85, lat));
  const y = Math.log(Math.tan(Math.PI / 4 + (clamped * Math.PI) / 360));
  return [(lng + 180) / 360, 0.5 - y / (2 * Math.PI)];
}

const polysOf = (g: GeoJSON.Geometry): Poly[] => (g.type === "Polygon" ? [g.coordinates] : g.type === "MultiPolygon" ? g.coordinates : []);

function inRing([x, y]: number[], ring: Ring) {
  let inside = false;
  for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) {
    const [xi, yi] = ring[i];
    const [xj, yj] = ring[j];
    if (yi > y !== yj > y && x < ((xj - xi) * (y - yi)) / (yj - yi) + xi) inside = !inside;
  }
  return inside;
}
const inPoly = (p: number[], poly: Poly) => inRing(p, poly[0]) && !poly.slice(1).some((h) => inRing(p, h));

export interface Box { x0: number; y0: number; x1: number; y1: number }
const grow = (b: Box | null, x: number, y: number): Box => (b ? { x0: Math.min(b.x0, x), y0: Math.min(b.y0, y), x1: Math.max(b.x1, x), y1: Math.max(b.y1, y) } : { x0: x, y0: y, x1: x, y1: y });

/**
 * The area the overview should show: the land masses the stops are on (e.g. mainland Australia
 * for an East Coast trip, not every island far away), padded a little so nearby coast fits.
 * Null when it wouldn't add anything (no stops on land).
 */
export function insetExtent(countries: GeoJSON.FeatureCollection, stops: Pick<Stop, "lng" | "lat">[]): Box | null {
  let box: Box | null = null;
  const used = new Set<Poly>();
  for (const s of stops) {
    for (const f of countries.features) {
      if (!f.geometry) continue;
      const hit = polysOf(f.geometry).find((p) => inPoly([s.lng, s.lat], p));
      if (hit) {
        if (!used.has(hit)) {
          used.add(hit);
          for (const pt of hit[0]) {
            const [x, y] = merc(pt as LngLat);
            box = grow(box, x, y);
          }
        }
        break;
      }
    }
  }
  // Stops at sea or on tiny islands still count.
  for (const s of stops) {
    const [x, y] = merc([s.lng, s.lat]);
    box = grow(box, x, y);
  }
  if (!box || !used.size) return null;
  // Something spanning more than half the world (e.g. across the date line) isn't worth an overview.
  if (box.x1 - box.x0 > 0.5) return null;
  const w = box.x1 - box.x0;
  const h = box.y1 - box.y0;
  const pad = Math.max(w, h) * 0.1 + 0.002;
  return { x0: box.x0 - pad, y0: box.y0 - pad, x1: box.x1 + pad, y1: box.y1 + pad };
}

/** The part of the world the main map shows (Web Mercator units), from its centre, zoom and size in px. */
export function viewBox(center: LngLat, zoom: number, widthPx: number, heightPx: number): Box {
  const [cx, cy] = merc(center);
  const world = 512 * 2 ** zoom; // MapLibre's world size in px at this zoom
  const hw = widthPx / 2 / world;
  const hh = heightPx / 2 / world;
  return { x0: cx - hw, y0: cy - hh, x1: cx + hw, y1: cy + hh };
}

/** SVG path data for a set of polygons, in a w × h box showing `ext`. Drops points closer than ~0.6px. */
export function pathFor(polys: Poly[], ext: Box, w: number, h: number) {
  const sx = w / (ext.x1 - ext.x0);
  const sy = h / (ext.y1 - ext.y0);
  let d = "";
  for (const poly of polys) {
    for (const ring of poly) {
      let last: [number, number] | null = null;
      let n = 0;
      for (const pt of ring) {
        const [mx, my] = merc(pt as LngLat);
        const x = (mx - ext.x0) * sx;
        const y = (my - ext.y0) * sy;
        if (last && Math.abs(x - last[0]) < 0.6 && Math.abs(y - last[1]) < 0.6) continue;
        // A jump of half the world is a shape crossing the date line: lift the pen, don't draw across.
        const wrap = last && Math.abs(x - last[0]) > w * 0.5 * ((ext.x1 - ext.x0) > 0 ? 1 / (ext.x1 - ext.x0) : 1);
        d += `${n && !wrap ? "L" : "M"}${x.toFixed(1)} ${y.toFixed(1)}`;
        last = [x, y];
        n++;
      }
      if (n) d += "Z";
    }
  }
  return d;
}

/** Does a country's outline come anywhere near the area shown? */
export function overlaps(g: GeoJSON.Geometry | null, ext: Box) {
  if (!g) return false;
  let b: Box | null = null;
  for (const poly of polysOf(g)) for (const pt of poly[0]) {
    const [x, y] = merc(pt as LngLat);
    b = grow(b, x, y);
  }
  return !!b && b.x0 < ext.x1 && b.x1 > ext.x0 && b.y0 < ext.y1 && b.y1 > ext.y0;
}

export const polygonsOf = polysOf;
