import { NextResponse } from "next/server";

// Road routing, proxied through our server so we can cache results, queue
// requests (the public OSRM server is rate limited) and swap providers later
// (e.g. set OSRM_URL to a self-hosted OSRM or a paid service).
const OSRM = process.env.OSRM_URL ?? "https://router.project-osrm.org";
const cache = new Map<string, unknown>();
let queue: Promise<unknown> = Promise.resolve();

const num = (v: string | null) => (v !== null && Number.isFinite(+v) ? +(+v).toFixed(5) : null);

export async function GET(req: Request) {
  const q = new URL(req.url).searchParams;
  const [a, b, c, d] = ["fromLng", "fromLat", "toLng", "toLat"].map((k) => num(q.get(k)));
  if (a === null || b === null || c === null || d === null) return NextResponse.json({ error: "bad coordinates" }, { status: 400 });
  const key = `${a},${b};${c},${d}`;
  if (cache.has(key)) return NextResponse.json(cache.get(key));

  // One request at a time, with a small gap, to stay within the public server's limits.
  const run = queue.then(async () => {
    for (let attempt = 0; attempt < 3; attempt++) {
      const r = await fetch(`${OSRM}/route/v1/driving/${key}?overview=full&geometries=geojson`, { headers: { "User-Agent": "Mapsie/1.0" } });
      if (r.status === 429) {
        await new Promise((res) => setTimeout(res, 1200 * (attempt + 1)));
        continue;
      }
      const j = await r.json();
      const route = j.routes?.[0];
      const out = route ? { distance: route.distance, coordinates: route.geometry.coordinates } : { distance: 0, coordinates: [] };
      cache.set(key, out);
      await new Promise((res) => setTimeout(res, 250));
      return out;
    }
    return { distance: 0, coordinates: [], error: "busy" };
  });
  queue = run.catch(() => null);
  try {
    return NextResponse.json(await run);
  } catch {
    return NextResponse.json({ error: "routing failed" }, { status: 502 });
  }
}
