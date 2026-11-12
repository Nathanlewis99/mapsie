import { NextResponse } from "next/server";
import { getCachedRoute, putCachedRoute } from "@/lib/server/db";
import { distanceKm, simplify } from "@/lib/geo";
import type { LngLat } from "@/lib/types";

// Road routing for a run of consecutive stops. One OSRM request covers every leg
// (much faster than one request per leg), results are cached per leg in the
// database, and requests to the public server go one at a time.
// Set OSRM_URL to use a self-hosted or paid router instead.
const OSRM = process.env.OSRM_URL ?? "https://router.project-osrm.org";
type Leg = { distance: number; coordinates: LngLat[] } | null;

let queue: Promise<unknown> = Promise.resolve();
const serial = <T,>(fn: () => Promise<T>): Promise<T> => {
  const run = queue.then(fn);
  queue = run.catch(() => null);
  return run;
};

const round = (p: LngLat): LngLat => [+p[0].toFixed(5), +p[1].toFixed(5)];
const legKey = (a: LngLat, b: LngLat) => `osrm:${a.join(",")};${b.join(",")}`;

/** Ask OSRM for a route through all points. Returns per-leg geometry, or null if it can't route them all. */
async function osrm(points: LngLat[]): Promise<Leg[] | null> {
  for (let attempt = 0; attempt < 3; attempt++) {
    const r = await fetch(`${OSRM}/route/v1/driving/${points.map((p) => p.join(",")).join(";")}?overview=false&steps=true&geometries=geojson`, {
      headers: { "User-Agent": "Mapsie/1.0 (https://mapsie.shop)" },
      signal: AbortSignal.timeout(20_000),
    });
    if (r.status === 429) {
      await new Promise((res) => setTimeout(res, 1000 * (attempt + 1)));
      continue;
    }
    const j = await r.json();
    if (j.code !== "Ok" || !j.routes?.[0]) return null; // e.g. NoRoute: a leg crosses the sea
    return j.routes[0].legs.map((leg: { distance: number; steps: { geometry: { coordinates: LngLat[] } }[] }, i: number) => {
      const coords = leg.steps.flatMap((s) => s.geometry.coordinates);
      const km = distanceKm({ lng: points[i][0], lat: points[i][1] }, { lng: points[i + 1][0], lat: points[i + 1][1] });
      return { distance: leg.distance, coordinates: simplify(coords, Math.max(0.0005, km / 100000)).map(round) };
    });
  }
  throw new Error("router busy");
}

export async function POST(req: Request) {
  const body = (await req.json()) as { points?: unknown };
  const pts = Array.isArray(body.points) ? (body.points as unknown[]) : [];
  if (pts.length < 2 || pts.length > 25 || !pts.every((p) => Array.isArray(p) && p.length === 2 && p.every(Number.isFinite))) {
    return NextResponse.json({ error: "bad points" }, { status: 400 });
  }
  const points = (pts as LngLat[]).map(round);
  const keys = points.slice(1).map((p, i) => legKey(points[i], p));
  const cached = (await Promise.all(keys.map((k) => getCachedRoute(k)))) as (Leg | undefined)[];
  if (cached.every((c) => c !== undefined)) return NextResponse.json({ legs: cached });

  try {
    let legs = await serial(() => osrm(points));
    // One impossible leg makes the whole run fail: fall back to leg by leg.
    if (!legs) {
      legs = [];
      for (let i = 0; i < keys.length; i++) {
        legs.push(cached[i] !== undefined ? cached[i]! : ((await serial(() => osrm([points[i], points[i + 1]])))?.[0] ?? null));
      }
    }
    await Promise.all(legs.map((leg, i) => putCachedRoute(keys[i], leg)));
    return NextResponse.json({ legs });
  } catch {
    return NextResponse.json({ error: "routing failed" }, { status: 502 });
  }
}
