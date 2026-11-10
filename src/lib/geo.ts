import type { Stop, LngLat } from "./types";

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

/** One leg of the route: a gentle arc (or straight line) between two stops. */
function leg(a: LngLat, b: LngLat, curved: boolean, flip: boolean): LngLat[] {
  if (!curved) return [a, b];
  const [x1, y1] = toMerc(a);
  const [x2, y2] = toMerc(b);
  const dx = x2 - x1;
  const dy = y2 - y1;
  const k = flip ? -0.18 : 0.18;
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

export function routeGeoJSON(stops: Stop[], curved: boolean): GeoJSON.FeatureCollection {
  const features: GeoJSON.Feature[] = [];
  for (let i = 0; i < stops.length - 1; i++) {
    const a = stops[i];
    const b = stops[i + 1];
    features.push({
      type: "Feature",
      properties: {},
      geometry: { type: "LineString", coordinates: leg([a.lng, a.lat], [b.lng, b.lat], curved, i % 2 === 1) },
    });
  }
  return { type: "FeatureCollection", features };
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

// Place search via Photon (OpenStreetMap-based, free).
export async function searchPlaces(q: string, signal?: AbortSignal): Promise<PlaceResult[]> {
  const r = await fetch(`https://photon.komoot.io/api/?q=${encodeURIComponent(q)}&limit=6&lang=en`, { signal });
  const j = await r.json();
  return (j.features ?? []).map((f: { properties: Record<string, string>; geometry: { coordinates: LngLat } }) => {
    const p = f.properties;
    return {
      name: p.name ?? p.city ?? p.country,
      detail: [p.city !== p.name ? p.city : null, p.state, p.country].filter(Boolean).join(", "),
      lng: f.geometry.coordinates[0],
      lat: f.geometry.coordinates[1],
    };
  });
}

export async function reverseGeocode(lng: number, lat: number): Promise<string> {
  try {
    const r = await fetch(`https://photon.komoot.io/reverse?lon=${lng}&lat=${lat}&lang=en`);
    const j = await r.json();
    const p = j.features?.[0]?.properties;
    return p?.city ?? p?.name ?? p?.state ?? p?.country ?? "New stop";
  } catch {
    return "New stop";
  }
}
