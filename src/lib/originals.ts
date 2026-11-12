import catalogue from "./originals.json";

// Mapsie Originals: our own activity artwork, drawn in design/activity-art and
// exported here by `python3 design/activity-art/build.py --export`.
// Each concept comes in two styles and several palettes:
//   /stickers/originals/<id>/papercut-<palette>.svg
//   /stickers/originals/<id>/line-<colourway>.svg

export type OriginalStyle = "papercut" | "line";

export interface OriginalDef {
  id: string;
  activity: string;
  title: string; // the concept, e.g. "Safari jeep"
  label: string; // the activity, e.g. "Safari"
  category: string;
  keywords?: string; // e.g. the region for animals: "Africa wildlife animal"
  lat?: number; // landmarks: where it is
  lng?: number;
  group?: string; // landmarks: europe | asia | americas | africa_oceania
  papercut: string[];
  line: string[];
}

export const ORIGINALS = catalogue as OriginalDef[];
export const ORIGINAL_CATEGORIES = [...new Set(ORIGINALS.map((o) => o.category))];

export const PALETTE_NAMES: Record<OriginalStyle, Record<string, string>> = {
  papercut: { golden: "Golden hour", coastal: "Coastal", meadow: "Meadow", blush: "Blush", dusk: "Dusk" },
  line: { classic: "Classic", forest: "Forest", ocean: "Ocean", night: "Night" },
};

/** Swatch colours for the palette picker. */
export const PALETTE_SWATCH: Record<string, [string, string, string]> = {
  golden: ["#FDE7C8", "#F6A96B", "#3E7CB1"],
  coastal: ["#E6F6F7", "#5FBCC6", "#FF7A5C"],
  meadow: ["#EEF6E4", "#8CC084", "#E76F51"],
  blush: ["#FDE2E4", "#E5989B", "#6D9DC5"],
  dusk: ["#1F2A44", "#4F5D8A", "#F2C14E"],
  classic: ["#FFFFFF", "#1D2D44", "#E4572E"],
  forest: ["#FFFDF6", "#2D3A2E", "#E9A23B"],
  ocean: ["#FFFFFF", "#12354A", "#2BB3A6"],
  night: ["#1F2A44", "#F3E9D2", "#F2C14E"],
};

/** Which Originals palette suits each map style. */
const MATCH: Record<string, Record<OriginalStyle, string>> = {
  vintage: { papercut: "golden", line: "classic" },
  minimal: { papercut: "coastal", line: "classic" },
  topo: { papercut: "meadow", line: "forest" },
  tropical: { papercut: "coastal", line: "ocean" },
  midnight: { papercut: "dusk", line: "night" },
  blush: { papercut: "blush", line: "classic" },
  terrain: { papercut: "meadow", line: "forest" },
  atlas: { papercut: "golden", line: "classic" },
  nautical: { papercut: "coastal", line: "ocean" },
  explorer: { papercut: "golden", line: "forest" },
  blueprint: { papercut: "dusk", line: "night" },
  ink: { papercut: "coastal", line: "classic" },
};

export const matchedPalette = (presetId: string, style: OriginalStyle) => MATCH[presetId]?.[style] ?? (style === "papercut" ? "golden" : "classic");

/** "auto" follows the map style. */
export const resolvePalette = (palette: string, presetId: string, style: OriginalStyle) => (palette === "auto" ? matchedPalette(presetId, style) : palette);

export const getOriginal = (id: string) => ORIGINALS.find((o) => o.id === id);

/** File for a concept; if the palette isn't available for it (it would clash), use the nearest one that is. */
export function originalSrc(id: string, style: OriginalStyle, palette: string): string {
  const def = getOriginal(id);
  const have = def ? def[style] : [];
  const fallbackOrder = style === "papercut" ? ["golden", "coastal", "meadow", "blush", "dusk"] : ["classic", "forest", "ocean", "night"];
  const dark = palette === "dusk" || palette === "night";
  const pick = have.includes(palette)
    ? palette
    : // keep dark with dark, light with light
      fallbackOrder.find((p) => have.includes(p) && (p === "dusk" || p === "night") === dark) ?? have[0] ?? palette;
  return `/stickers/originals/${id}/${style}-${pick}.svg`;
}

export function searchOriginals(q: string): OriginalDef[] {
  const words = q.toLowerCase().trim().split(/\s+/).filter(Boolean);
  if (!words.length) return ORIGINALS;
  return ORIGINALS.filter((o) => {
    const hay = `${o.label} ${o.title} ${o.category} ${o.keywords ?? ""} ${o.activity.replace(/-/g, " ")}`.toLowerCase();
    return words.every((w) => hay.includes(w));
  });
}

export const LANDMARK_REGIONS: Record<string, string> = {
  europe: "Europe",
  asia: "Asia & the Middle East",
  americas: "The Americas",
  africa_oceania: "Africa & Oceania",
};

/** Landmarks within `km` of any of these points, nearest first. */
export function landmarksNear(points: { lng: number; lat: number }[], km = 200): OriginalDef[] {
  const R = 6371, rad = Math.PI / 180;
  const dist = (a: { lng: number; lat: number }, b: { lng: number; lat: number }) => {
    const h = Math.sin(((b.lat - a.lat) * rad) / 2) ** 2 + Math.cos(a.lat * rad) * Math.cos(b.lat * rad) * Math.sin(((b.lng - a.lng) * rad) / 2) ** 2;
    return 2 * R * Math.asin(Math.sqrt(h));
  };
  return ORIGINALS.filter((o) => o.lat !== undefined && o.lng !== undefined)
    .map((o) => ({ o, d: Math.min(...points.map((p) => dist(p, { lng: o.lng!, lat: o.lat! }))) }))
    .filter((x) => x.d <= km)
    .sort((a, b) => a.d - b.d)
    .map((x) => x.o);
}
