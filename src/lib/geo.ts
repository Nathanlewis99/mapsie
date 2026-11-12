import type { Stop, LngLat, TravelMode, RouteStyle } from "./types";

// Web-mercator helpers (unit square) so routes curve nicely on the flat map.
const toMerc = ([lng, lat]: LngLat) => {
  const x = (lng + 180) / 360;
  const s = Math.sin((lat * Math.PI) / 180);
  const y = 0.5 - Math.log((1 + s) / (1 - s)) / (4 * Math.PI);
  return [x, y];
};
const fromMerc = ([x, y]: number[]): LngLat => {
  const lng = x * 360 - 180;
  const lat = (Math.atan(Math.sinh(Math.PI * (1 - 2 * y))) * 180) / Math.PI;
  return [lng, lat];
};

/** Gentle arc (or straight line) between two points. */
function arc(a: LngLat, b: LngLat, curved: boolean, flip: boolean, bend = 0.18): LngLat[] {
  if (!curved) return [a, b];
  const [x1, y1] = toMerc(a);
  const [x2, y2] = toMerc(b);
  const dx = x2 - x1;
  const dy = y2 - y1;
  const k = flip ? -bend : bend;
  const cx = (x1 + x2) / 2 - dy * k;
  const cy = (y1 + y2) / 2 + dx * k;
  const pts: LngLat[] = [];
  const n = 48;
  for (let i = 0; i <= n; i++) {
    const t = i / n;
    const x = (1 - t) ** 2 * x1 + 2 * (1 - t) * t * cx + t * t * x2;
    const y = (1 - t) ** 2 * y1 + 2 * (1 - t) * t * cy + t * t * y2;
    pts.push(fromMerc([x, y]));
  }
  return pts;
}

export const MODES: { id: TravelMode; label: string; icon: string }[] = [
  { id: "plane", label: "Flight", icon: "/stickers/airplane.svg" },
  { id: "car", label: "Drive", icon: "/stickers/car.svg" },
  { id: "bus", label: "Bus", icon: "/stickers/bus.svg" },
  { id: "train", label: "Train", icon: "/stickers/train.svg" },
  { id: "boat", label: "Boat", icon: "/stickers/sailboat.svg" },
  { id: "walk", label: "Hike", icon: "/stickers/walking.svg" },
];

export type Dash = "solid" | "dashed" | "dotted" | "rail";

function legLook(mode: TravelMode, override: RouteStyle): Dash {
  if (override !== "auto") return override;
  return mode === "plane" ? "dashed" : mode === "boat" || mode === "walk" ? "dotted" : mode === "train" ? "rail" : "solid";
}

/** Point halfway along a line (by vertex distance, good enough for an icon). */
function midpoint(line: LngLat[]): LngLat {
  if (line.length === 2) return [(line[0][0] + line[1][0]) / 2, (line[0][1] + line[1][1]) / 2];
  let total = 0;
  const seg: number[] = [];
  for (let i = 1; i < line.length; i++) {
    const d = Math.hypot(line[i][0] - line[i - 1][0], line[i][1] - line[i - 1][1]);
    seg.push(d);
    total += d;
  }
  let acc = 0;
  for (let i = 0; i < seg.length; i++) {
    if (acc + seg[i] >= total / 2) {
      const t = (total / 2 - acc) / (seg[i] || 1);
      return [line[i][0] + (line[i + 1][0] - line[i][0]) * t, line[i][1] + (line[i + 1][1] - line[i][1]) * t];
    }
    acc += seg[i];
  }
  return line[Math.floor(line.length / 2)];
}

export const legKey = (a: { lng: number; lat: number }, b: { lng: number; lat: number }) =>
  `${a.lng.toFixed(4)},${a.lat.toFixed(4)}>${b.lng.toFixed(4)},${b.lat.toFixed(4)}`;

export interface Leg {
  mode: TravelMode;
  line: LngLat[];
  mid: LngLat;
}

export function buildLegs(stops: Stop[], curved: boolean): Leg[] {
  const legs: Leg[] = [];
  for (let i = 1; i < stops.length; i++) {
    const a = stops[i - 1];
    const b = stops[i];
    const mode = b.arriveBy ?? "plane";
    const A: LngLat = [a.lng, a.lat];
    const B: LngLat = [b.lng, b.lat];
    let line: LngLat[];
    if ((mode === "car" || mode === "bus") && b.path?.length && b.pathFor === legKey(a, b)) line = b.path;
    else if (mode === "plane") line = arc(A, B, curved, i % 2 === 0);
    else if (mode === "boat") line = arc(A, B, curved, i % 2 === 0, 0.1);
    else line = [A, B];
    legs.push({ mode, line, mid: midpoint(line) });
  }
  return legs;
}

export function routeGeoJSON(legs: Leg[], override: RouteStyle): GeoJSON.FeatureCollection {
  return {
    type: "FeatureCollection",
    features: legs.map((l) => ({
      type: "Feature",
      properties: { dash: legLook(l.mode, override) },
      geometry: { type: "LineString", coordinates: l.line },
    })),
  };
}

/** Straight-line distance in km. */
export function distanceKm(a: { lng: number; lat: number }, b: { lng: number; lat: number }) {
  const R = 6371;
  const dLat = ((b.lat - a.lat) * Math.PI) / 180;
  const dLng = ((b.lng - a.lng) * Math.PI) / 180;
  const h = Math.sin(dLat / 2) ** 2 + Math.cos((a.lat * Math.PI) / 180) * Math.cos((b.lat * Math.PI) / 180) * Math.sin(dLng / 2) ** 2;
  return 2 * R * Math.asin(Math.sqrt(h));
}

/** Sensible default for how someone got from a to b. */
export const guessMode = (a: { lng: number; lat: number }, b: { lng: number; lat: number }): TravelMode =>
  distanceKm(a, b) > 700 ? "plane" : "car";

// Douglas–Peucker, keeps road lines light enough to store in the design.
export function simplify(pts: LngLat[], tol: number): LngLat[] {
  if (pts.length < 3) return pts;
  const [a, b] = [pts[0], pts[pts.length - 1]];
  let max = 0;
  let idx = 0;
  for (let i = 1; i < pts.length - 1; i++) {
    const [x, y] = pts[i];
    const dx = b[0] - a[0];
    const dy = b[1] - a[1];
    const d = Math.abs(dy * x - dx * y + b[0] * a[1] - b[1] * a[0]) / (Math.hypot(dx, dy) || 1);
    if (d > max) {
      max = d;
      idx = i;
    }
  }
  if (max <= tol) return [a, b];
  return [...simplify(pts.slice(0, idx + 1), tol).slice(0, -1), ...simplify(pts.slice(idx), tol)];
}

/**
 * Road routes for consecutive stops, in one request (via our /api/route).
 * One entry per leg: a path, null if there's no sensible road (e.g. across sea),
 * or undefined if the lookup failed (try again later).
 */
export async function fetchRoads(points: { lng: number; lat: number }[]): Promise<(LngLat[] | null | undefined)[]> {
  const legs = points.length - 1;
  try {
    const r = await fetch("/api/route", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ points: points.map((p) => [p.lng, p.lat]) }),
    });
    if (!r.ok) return Array(legs).fill(undefined);
    const j: { legs: ({ distance: number; coordinates: LngLat[] } | null)[] } = await r.json();
    return j.legs.map((leg, i) => {
      if (!leg?.coordinates?.length) return null;
      // Reject "routes" that are mostly ferry/detour nonsense: > 3x the straight distance.
      if (leg.distance / 1000 > distanceKm(points[i], points[i + 1]) * 3 + 50) return null;
      return leg.coordinates;
    });
  } catch {
    return Array(legs).fill(undefined);
  }
}

export function stopsBounds(stops: Stop[]): [LngLat, LngLat] | null {
  if (!stops.length) return null;
  let w = 180, s = 90, e = -180, n = -90;
  for (const p of stops) {
    w = Math.min(w, p.lng); e = Math.max(e, p.lng);
    s = Math.min(s, p.lat); n = Math.max(n, p.lat);
  }
  return [[w, s], [e, n]];
}

export interface PlaceResult {
  name: string;
  detail: string;
  lng: number;
  lat: number;
}

/** Place search, through our server (which tries several services). full=true is the "Enter" search. */
export async function searchPlaces(q: string, signal?: AbortSignal, full = false): Promise<PlaceResult[]> {
  const r = await fetch(`/api/geocode?q=${encodeURIComponent(q)}${full ? "&full=1" : ""}`, { signal });
  if (!r.ok) throw new Error("search failed");
  return r.json();
}

/** Name of the place at a point, or null if there isn't one (e.g. open sea). */
export async function reverseGeocode(lng: number, lat: number): Promise<string | null> {
  try {
    const r = await fetch(`/api/reverse?lng=${lng.toFixed(5)}&lat=${lat.toFixed(5)}`);
    return (await r.json()).name ?? null;
  } catch {
    return null;
  }
}
