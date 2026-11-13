// Place search and reverse geocoding, with fallbacks so the editor never depends
// on a single free service. Results are cached in memory.
//
// Search (as you type): Photon (best: includes parks and landmarks) → Open-Meteo
//   (GeoNames: towns, islands, peaks, parks). Photon is skipped for a few minutes
//   after it fails, so a slow outage doesn't slow every keystroke.
// Search (explicit, on Enter): Nominatim, which doesn't allow as-you-type use.
// Reverse (tap on map): Photon → Nominatim → BigDataCloud.
import { formatCoords, parseCoords, type PlaceResult } from "../geo";

const UA = "Mapsie/1.0 (https://mapsie.shop; hello@mapsie.shop)";
const cache = new Map<string, unknown>();
const remember = <T,>(key: string, v: T) => {
  if (cache.size > 5000) cache.delete(cache.keys().next().value!);
  cache.set(key, v);
  return v;
};

let photonDownUntil = 0;
async function getJson(url: string, ms: number) {
  const r = await fetch(url, { headers: { "User-Agent": UA, "Accept-Language": "en" }, signal: AbortSignal.timeout(ms) });
  if (!r.ok) throw new Error(`${r.status}`);
  return r.json();
}
async function photon<T>(url: string): Promise<T | null> {
  if (Date.now() < photonDownUntil) return null;
  try {
    return await getJson(url, 1500);
  } catch {
    photonDownUntil = Date.now() + 5 * 60_000;
    return null;
  }
}

const uniq = (list: PlaceResult[]) => {
  const seen = new Set<string>();
  return list.filter((p) => {
    const k = `${p.name}|${p.detail}`;
    if (seen.has(k)) return false;
    seen.add(k);
    return true;
  });
};

type PhotonFeature = { properties: Record<string, string>; geometry: { coordinates: [number, number] } };
const fromPhoton = (f: PhotonFeature): PlaceResult => {
  const p = f.properties;
  return {
    name: p.name ?? p.city ?? p.country,
    detail: [p.city !== p.name ? p.city : null, p.state, p.country].filter(Boolean).join(", "),
    lng: f.geometry.coordinates[0],
    lat: f.geometry.coordinates[1],
  };
};

type OpenMeteoPlace = { name: string; admin1?: string; country?: string; latitude: number; longitude: number; feature_code?: string; population?: number };

// GeoNames ranks tiny villages that share a name above famous places. Re-rank for
// travellers: parks, islands, peaks and big towns first.
const FEATURE_BOOST: Record<string, number> = {
  PCLI: 4, PPLC: 4, PPLA: 3, PPLA2: 2, PPLA3: 1.5, PRK: 3, RES: 2, ISL: 3, ISLS: 3, ATOL: 3, MT: 2.5, PK: 2.5, VLC: 2.5,
  BCH: 1.5, BAY: 1.5, LK: 1.5, CAPE: 1, GLCR: 2, FLLS: 2, GRGE: 2, RSRT: 2, HSTS: 2, ADM1: 1,
  AIRP: -2, AIRF: -2, PPLX: -1,
};
const plain = (t: string) => t.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
function travelScore(x: OpenMeteoPlace, query: string) {
  const name = plain(x.name);
  const q = plain(query);
  let score = name === q ? 4 : name.startsWith(q) ? 2 : 0;
  score += FEATURE_BOOST[x.feature_code ?? ""] ?? 0;
  if (/national park|world heritage/.test(name)) score += 2;
  score += x.population ? Math.log10(x.population + 1) * 0.8 : x.feature_code === "PPL" ? -1 : 0;
  return score;
}

export async function searchPlaces(q: string, full = false): Promise<PlaceResult[]> {
  // Typed or pasted coordinates (or a map link): drop a pin there, named after the nearest place.
  const at = parseCoords(q);
  if (at) {
    const name = await reversePlace(at.lng, at.lat).catch(() => null);
    return [{ name: name ?? "Pinned spot", detail: `📍 ${formatCoords(at.lat, at.lng)}`, lng: at.lng, lat: at.lat }];
  }
  const query = q.trim().slice(0, 100);
  if (query.length < 2) return [];
  const key = `s:${full ? 1 : 0}:${query.toLowerCase()}`;
  if (cache.has(key)) return cache.get(key) as PlaceResult[];

  const ph = await photon<{ features?: PhotonFeature[] }>(`https://photon.komoot.io/api/?q=${encodeURIComponent(query)}&limit=6&lang=en`);
  if (ph?.features?.length) return remember(key, uniq(ph.features.map(fromPhoton)));

  let results: PlaceResult[] = [];
  try {
    const om = await getJson(`https://geocoding-api.open-meteo.com/v1/search?name=${encodeURIComponent(query)}&count=20&language=en`, 4000);
    results = (om.results ?? [])
      .map((x: OpenMeteoPlace) => ({ x, score: travelScore(x, query) }))
      .sort((a: { score: number }, b: { score: number }) => b.score - a.score)
      .map(({ x }: { x: OpenMeteoPlace }) => ({
        name: x.name,
        detail: [x.admin1 !== x.name ? x.admin1 : null, x.country].filter(Boolean).join(", "),
        lng: x.longitude,
        lat: x.latitude,
      }));
  } catch {
    /* fall through */
  }
  // Pressing Enter asks for a fuller search, which adds Nominatim (landmarks, parks, addresses).
  if (full || results.length === 0) {
    try {
      const nm = await getJson(`https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(query)}&format=jsonv2&limit=6&addressdetails=1`, 5000);
      const more = nm.map((x: { name: string; display_name: string; lat: string; lon: string; address?: Record<string, string> }) => ({
        name: x.name || x.display_name.split(",")[0],
        detail: [x.address?.state, x.address?.country].filter(Boolean).join(", "),
        lng: +x.lon,
        lat: +x.lat,
      }));
      results = full ? [...more, ...results] : more;
    } catch {
      /* nothing more we can do */
    }
  }
  return remember(key, uniq(results).slice(0, 8));
}

export async function reversePlace(lng: number, lat: number): Promise<string | null> {
  const key = `r:${lng.toFixed(3)},${lat.toFixed(3)}`;
  if (cache.has(key)) return cache.get(key) as string;

  const ph = await photon<{ features?: PhotonFeature[] }>(`https://photon.komoot.io/reverse?lon=${lng}&lat=${lat}&lang=en`);
  const pp = ph?.features?.[0]?.properties;
  if (pp) return remember(key, pp.city ?? pp.name ?? pp.state ?? pp.country);

  try {
    const nm = await getJson(`https://nominatim.openstreetmap.org/reverse?lat=${lat}&lon=${lng}&format=jsonv2&zoom=10`, 4000);
    const a = nm.address ?? {};
    const name = a.city ?? a.town ?? a.village ?? a.municipality ?? a.county ?? a.state ?? a.country ?? nm.name;
    if (name) return remember(key, name);
  } catch {
    /* try the next one */
  }
  try {
    const bd = await getJson(`https://api.bigdatacloud.net/data/reverse-geocode-client?latitude=${lat}&longitude=${lng}&localityLanguage=en`, 4000);
    const name = bd.city || bd.locality || bd.principalSubdivision || bd.countryName;
    if (name) return remember(key, name);
  } catch {
    /* give up */
  }
  return null; // e.g. the middle of the ocean
}
