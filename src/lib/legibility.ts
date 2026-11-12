import type { Design, Stop } from "./types";
import { PRODUCTS, getProduct, posterAspect } from "./products";

// Where stops land on the poster, whether they collide, and how big the
// smallest text will be once printed. All poster measurements are in % of the
// poster width (the same unit the markers and labels are sized in).

const TILE = 512; // MapLibre world size at zoom 0, in px

function project(lng: number, lat: number, zoom: number) {
  const world = TILE * 2 ** zoom;
  const s = Math.sin((Math.max(-85, Math.min(85, lat)) * Math.PI) / 180);
  return { x: ((lng + 180) / 360) * world, y: (0.5 - Math.log((1 + s) / (1 - s)) / (4 * Math.PI)) * world, world };
}

/** Each stop's position on the poster in % of poster width, relative to the map centre. */
export function stopPositions(d: Design) {
  const { center, zoom, refWidth } = d.view;
  const c = project(center[0], center[1], zoom);
  const pct = 100 / refWidth; // px at refWidth -> % of poster width
  return d.stops.map((s) => {
    const p = project(s.lng, s.lat, zoom);
    let dx = p.x - c.x;
    dx -= Math.round(dx / c.world) * c.world; // nearest world copy
    return { id: s.id, x: dx * pct, y: (p.y - c.y) * pct };
  });
}

const markerScale = (d: Design, s: Stop) => d.markers.size * (s.markerScale ?? 1);
const labelScale = (d: Design, s: Stop) => d.markers.labelSize * (s.labelScale ?? 1);

/** Marker radius in % of poster width. */
function markerRadius(d: Design, s: Stop) {
  const base = { number: 1.5, dot: 0.9, pin: 1.5, heart: 1.6, sticker: 3 }[d.markers.style] ?? 1.5;
  return base * markerScale(d, s);
}

/** Approximate label box (in % of poster width) around a stop at (x, y). */
function labelBox(d: Design, s: Stop, x: number, y: number) {
  if (!s.showLabel) return null;
  const k = labelScale(d, s);
  const font = 2 * k;
  const w = s.name.length * font * 0.56 + 2 * k; // text + padding
  const h = font * 1.2 + 0.7 * k + (d.markers.showDates && s.date ? 1.6 * k : 0);
  const [ox, oy] = s.labelOffset ?? [0, 0];
  const m = markerRadius(d, s);
  const left = x + m + 0.8 * markerScale(d, s) + ox;
  const top = y - h / 2 + oy;
  return { l: left, r: left + w, t: top, b: top + h };
}

type Box = { l: number; r: number; t: number; b: number };
const boxesHit = (a: Box, b: Box) => a.l < b.r && b.l < a.r && a.t < b.b && b.t < a.b;
const circleBox = (x: number, y: number, r: number): Box => ({ l: x - r, r: x + r, t: y - r, b: y + r });

/** Stops whose pins or labels collide with another stop's, as pairs of ids. */
/** Whether a poster position is on the map (not off the edge). */
function onMap(d: Design, p: { x: number; y: number }) {
  const halfH = (posterAspect(d.productId, d.orientation) * 100) / 2;
  return Math.abs(p.x) < 52 && Math.abs(p.y) < halfH + 2;
}

export function crowding(d: Design) {
  const pos = stopPositions(d);
  const pairs: [string, string][] = [];
  for (let i = 0; i < d.stops.length; i++) {
    if (!onMap(d, pos[i])) continue;
    for (let j = i + 1; j < d.stops.length; j++) {
      if (!onMap(d, pos[j])) continue;
      const a = d.stops[i], b = d.stops[j];
      const pa = pos[i], pb = pos[j];
      const ra = markerRadius(d, a), rb = markerRadius(d, b);
      const pinsHit = Math.hypot(pa.x - pb.x, pa.y - pb.y) < (ra + rb) * 0.75; // touching is fine, covering isn't
      const la = labelBox(d, a, pa.x, pa.y), lb = labelBox(d, b, pb.x, pb.y);
      const labelsHit =
        (la && lb && boxesHit(la, lb)) || (la && boxesHit(la, circleBox(pb.x, pb.y, rb * 0.8))) || (lb && boxesHit(lb, circleBox(pa.x, pa.y, ra * 0.8)));
      // Pins already at their smallest that only touch: nothing more to do.
      const tiny = markerScale(d, a) <= TINY_PIN && markerScale(d, b) <= TINY_PIN;
      if ((pinsHit && !tiny) || labelsHit) pairs.push([a.id, b.id]);
    }
  }
  return pairs;
}

export const MIN_STOP_SCALE = 0.25;
/** Below this marker scale a numbered pin is drawn as a plain dot (the number would be unreadable). */
export const TINY_PIN = 0.45;

/** Label offsets that put the name right, left, above or below its pin. */
function placements(d: Design, s: Stop): [number, number][] {
  const k = labelScale(d, s);
  const font = 2 * k;
  const w = s.name.length * font * 0.56 + 2 * k;
  const h = font * 1.2 + 0.7 * k;
  const m = markerRadius(d, s);
  const gap = 0.8 * markerScale(d, s);
  const r = (n: number) => Math.round(n * 10) / 10;
  return [
    [0, 0],
    [r(-(2 * m + 2 * gap + w)), 0],
    [r(-(m + gap) - w / 2), r(-(m + h / 2 + 0.4))],
    [r(-(m + gap) - w / 2), r(m + h / 2 + 0.4)],
  ];
}

/** How many other stops a stop collides with. */
function hits(d: Design, i: number, pos: { x: number; y: number }[]) {
  const a = d.stops[i];
  const la = labelBox(d, a, pos[i].x, pos[i].y);
  const ra = markerRadius(d, a);
  let n = 0;
  if (la) {
    const halfH = (posterAspect(d.productId, d.orientation) * 100) / 2;
    if (la.l < -49 || la.r > 49 || la.t < -halfH || la.b > halfH) n += 5;
  }
  d.stops.forEach((b, j) => {
    if (j === i) return;
    const rb = markerRadius(d, b);
    const lb = labelBox(d, b, pos[j].x, pos[j].y);
    if (Math.hypot(pos[i].x - pos[j].x, pos[i].y - pos[j].y) < (ra + rb) * 0.9) n++;
    if (la && lb && boxesHit(la, lb)) n++;
    if (la && boxesHit(la, circleBox(pos[j].x, pos[j].y, rb * 0.8))) n++;
    if (lb && boxesHit(lb, circleBox(pos[i].x, pos[i].y, ra * 0.8))) n++;
  });
  return n;
}

/**
 * Untangle stops that collide. First try moving each crowded name to the left,
 * above or below its pin (names the user has dragged are left alone); then
 * shrink only the stops that still collide, a step at a time. Others keep their size.
 */
export function tidyCrowded(d: Design): Record<string, Partial<Stop>> {
  const pos = stopPositions(d);
  const stops = d.stops.map((s) => ({ ...s }));
  const cur = () => ({ ...d, stops });
  // Tight groups (3+ stops packed into a small area) get their names listed in a column.
  const dense = denseGroups(d, pos);
  for (const idx of dense) {
    // Pins just small enough not to sit on top of each other.
    let nn = Infinity;
    for (const a of idx) for (const b of idx) if (a < b) nn = Math.min(nn, Math.hypot(pos[a].x - pos[b].x, pos[a].y - pos[b].y));
    const base = markerRadius(d, { ...stops[idx[0]], markerScale: 1 });
    const ms = Math.round(Math.max(MIN_STOP_SCALE, Math.min(1, nn / (2.1 * base))) * 100) / 100;
    for (const i of idx) stops[i] = { ...stops[i], markerScale: Math.min(stops[i].markerScale ?? 1, ms) };
    stackGroup(cur(), stops, pos, idx);
  }
  const fixed = new Set(dense.flat());
  for (let round = 0; round < 16; round++) {
    const crowded = new Set(crowding(cur()).flat().filter((id) => !fixed.has(stops.findIndex((s) => s.id === id))));
    if (!crowded.size) break;
    // 1. reposition names
    for (let pass = 0; pass < 2; pass++) {
      stops.forEach((s, i) => {
        if (!crowded.has(s.id) || !s.showLabel) return;
        const moved = d.stops[i].labelOffset && (d.stops[i].labelOffset![0] !== 0 || d.stops[i].labelOffset![1] !== 0);
        if (moved && round === 0) return;
        let best = s.labelOffset ?? [0, 0], bestHits = hits(cur(), i, pos);
        for (const o of placements(cur(), s)) {
          stops[i] = { ...s, labelOffset: o };
          const n = hits(cur(), i, pos);
          if (n < bestHits) {
            best = o;
            bestHits = n;
          }
        }
        stops[i] = { ...s, labelOffset: best[0] === 0 && best[1] === 0 ? undefined : best };
      });
    }
    // 2. shrink what still collides
    const still = new Set(crowding(cur()).flat().filter((id) => !fixed.has(stops.findIndex((s) => s.id === id))));
    if (!still.size) break;
    let changed = false;
    stops.forEach((s, i) => {
      if (!still.has(s.id)) return;
      const ms = s.markerScale ?? 1, ls = s.labelScale ?? 1;
      const nms = Math.max(MIN_STOP_SCALE, ms * 0.88), nls = Math.max(MIN_STOP_SCALE, ls * 0.88);
      if (nms === ms && nls === ls) return;
      changed = true;
      const f = nls / ls;
      const off = s.labelOffset ? ([Math.round(s.labelOffset[0] * f * 10) / 10, Math.round(s.labelOffset[1] * f * 10) / 10] as [number, number]) : undefined;
      stops[i] = { ...s, markerScale: Math.round(nms * 100) / 100, labelScale: Math.round(nls * 100) / 100, labelOffset: off };
    });
    if (!changed) break;
  }
  const out: Record<string, Partial<Stop>> = {};
  stops.forEach((s, i) => {
    const o = d.stops[i];
    if (s.markerScale !== o.markerScale || s.labelScale !== o.labelScale || JSON.stringify(s.labelOffset) !== JSON.stringify(o.labelOffset))
      out[s.id] = { markerScale: s.markerScale, labelScale: s.labelScale, labelOffset: s.labelOffset };
  });
  return out;
}

/** Groups of 3+ on-map stops whose pins sit within a few % of each other. */
function denseGroups(d: Design, pos: { x: number; y: number }[]) {
  const n = d.stops.length;
  const parent = Array.from({ length: n }, (_, i) => i);
  const find = (a: number): number => (parent[a] === a ? a : (parent[a] = find(parent[a])));
  const near = 4 * Math.max(1, d.markers.size); // % of poster width
  for (let i = 0; i < n; i++)
    for (let j = i + 1; j < n; j++)
      if (onMap(d, pos[i]) && onMap(d, pos[j]) && Math.hypot(pos[i].x - pos[j].x, pos[i].y - pos[j].y) < near) parent[find(i)] = find(j);
  const groups = new Map<number, number[]>();
  for (let i = 0; i < n; i++) if (onMap(d, pos[i])) groups.set(find(i), [...(groups.get(find(i)) ?? []), i]);
  return [...groups.values()].filter((g) => g.length >= 3);
}

/**
 * List a tight group's names in a tidy column beside it, each linked to its pin
 * by a thin line (e.g. several stops on a small island on a continent-wide map).
 */
function stackGroup(d: Design, stops: Stop[], pos: { x: number; y: number }[], idx: number[]) {
  const named = idx.filter((i) => stops[i].showLabel).sort((a, b) => pos[a].y - pos[b].y);
  if (!named.length) return;
  const xs = idx.map((i) => pos[i].x), ys = idx.map((i) => pos[i].y);
  const cx = xs.reduce((a, b) => a + b, 0) / xs.length;
  const k = Math.max(0.55, Math.min(1, ...named.map((i) => stops[i].labelScale ?? 1)));
  const lk = d.markers.labelSize * k;
  const rowH = 2 * lk * 1.2 + 0.7 * lk + 0.5;
  const colW = Math.max(...named.map((i) => stops[i].name.length * 2 * lk * 0.56 + 2 * lk));
  const right = cx < 0 || Math.max(...xs) + 4 + colW < 48; // whichever side has room
  const colX = right ? Math.max(...xs) + 4 : Math.min(...xs) - 4 - colW;
  const halfH = (posterAspect(d.productId, d.orientation) * 100) / 2;
  const total = (named.length - 1) * rowH;
  const midY = Math.max(-halfH + 3 + total / 2, Math.min(halfH * 0.7 - total / 2, (Math.min(...ys) + Math.max(...ys)) / 2));
  const r = (n: number) => Math.round(n * 10) / 10;
  named.forEach((i, row) => {
    const s = stops[i];
    const defaultLeft = pos[i].x + markerRadius(d, s) + 0.8 * markerScale(d, s);
    const cy = midY + (row - (named.length - 1) / 2) * rowH;
    stops[i] = { ...s, labelScale: k, labelOffset: [r(colX - defaultLeft), r(cy - pos[i].y)] };
  });
}

// --- printed sizes ----------------------------------------------------------
// Below about 6pt a place name gets hard to read on a wall; 7pt+ is comfortable.
export const MIN_PT = 6;
export const GOOD_PT = 7;

const posterWidthCm = (productId: string, orientation: Design["orientation"]) => {
  const p = getProduct(productId);
  return orientation === "portrait" ? p.widthCm : p.heightCm;
};
const pctToPt = (pct: number, widthCm: number) => ((pct / 100) * widthCm * 72) / 2.54;

/** Smallest printed text on the poster (stop names, and numbers inside markers). */
export function smallestText(d: Design, productId = d.productId) {
  const wcm = posterWidthCm(productId, d.orientation);
  let label = Infinity, labelStop = "";
  for (const s of d.stops) {
    if (!s.showLabel) continue;
    const pt = pctToPt(2 * labelScale(d, s), wcm);
    if (pt < label) {
      label = pt;
      labelStop = s.name;
    }
  }
  let number = Infinity;
  if (d.markers.style === "number")
    for (const s of d.stops) if (markerScale(d, s) > TINY_PIN) number = Math.min(number, pctToPt(1.5 * markerScale(d, s), wcm));
  return { label, labelStop, number, pt: Math.min(label, number) };
}

/** The smallest print size where every name reads comfortably (null if none does). */
export function recommendedProduct(d: Design) {
  const sorted = [...PRODUCTS].sort((a, b) => a.widthCm - b.widthCm);
  return sorted.find((p) => smallestText(d, p.id).pt >= GOOD_PT) ?? null;
}

export function readability(pt: number): "good" | "small" | "tiny" {
  return pt >= GOOD_PT ? "good" : pt >= MIN_PT ? "small" : "tiny";
}

/** A short note for a print size in the size picker. */
export function sizeNote(design: Design, productId: string) {
  const r = readability(smallestText(design, productId).pt);
  if (r !== "good") return r === "tiny" ? "Names too small" : "Small names";
  // Only point out the recommended size when smaller sizes would be a squeeze.
  const rec = recommendedProduct(design);
  const smallest = [...PRODUCTS].sort((a, b) => a.widthCm - b.widthCm)[0];
  return rec && rec.id === productId && rec.id !== smallest.id ? "Recommended" : undefined;
}
