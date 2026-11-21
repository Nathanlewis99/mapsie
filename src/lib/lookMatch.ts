// When a map style is chosen, the rest of the design follows it: the route line, the
// pins, the transport icons and the stickers. Anything the customer picked themselves
// (not the previous style's suggestion) is left alone.
import type { Design, MarkerStyle, RouteStyle } from "./types";
import { lookOf, PRESETS, themeFromPreset, type Look, type Preset } from "./themes";
import { suggestedStyleFor } from "./stickers";
import type { OriginalStyle } from "./originals";

interface LookExtras {
  route: RouteStyle;
  marker: MarkerStyle;
  /** Mapsie Originals in this look: papercut art becomes `papercut`, line art becomes `line`. */
  originals: { papercut: OriginalStyle; line: OriginalStyle };
}

// Voyages on antique maps were dotted; touring maps used solid red/blue lines.
export const LOOK_EXTRAS: Record<Look, LookExtras> = {
  engraved: { route: "dashed", marker: "dot", originals: { papercut: "engraved", line: "engraved" } },
  antique: { route: "dotted", marker: "dot", originals: { papercut: "handcoloured", line: "engraved" } },
  touring: { route: "solid", marker: "number", originals: { papercut: "handcoloured", line: "engraved" } },
  poster: { route: "solid", marker: "dot", originals: { papercut: "papercut", line: "line" } },
  watercolour: { route: "dashed", marker: "dot", originals: { papercut: "papercut", line: "line" } },
};

const VINTAGE_ORIGINALS = new Set<OriginalStyle>(["engraved", "handcoloured"]);
const backToModern = (s: OriginalStyle): OriginalStyle => (s === "engraved" ? "line" : s === "handcoloured" ? "papercut" : s);

/** The design changes that go with switching to preset `p`. */
export function applyPreset(d: Design, p: Preset): Partial<Design> {
  const prevPreset = PRESETS.find((x) => x.id === d.theme.presetId);
  const prevLook = prevPreset ? lookOf(themeFromPreset(prevPreset)) : undefined;
  const theme = { ...themeFromPreset(p), labels: d.theme.labels };
  const look = lookOf(theme);
  const oldArt = suggestedStyleFor(d.theme.presetId);
  const newArt = suggestedStyleFor(p.id);
  const follows = (art: string | undefined) => !art || art === oldArt;
  const origFor = (s: OriginalStyle | undefined): OriginalStyle => {
    const base = backToModern(s ?? "papercut");
    if (!look) return base;
    const x = LOOK_EXTRAS[look].originals;
    return base === "line" ? x.line : base === "papercut" ? x.papercut : base;
  };
  const extras = look ? LOOK_EXTRAS[look] : null;
  const leaving = !look && prevLook;
  return {
    theme,
    stickerStyle: newArt,
    originals: { ...d.originals, style: look || VINTAGE_ORIGINALS.has(d.originals.style) ? origFor(d.originals.style) : d.originals.style },
    stickers: d.stickers.map((s) =>
      s.kind === "sticker" && follows(s.art) ? { ...s, art: newArt } : s.kind === "original" && (look || leaving) ? { ...s, origStyle: origFor(s.origStyle) } : s,
    ),
    route: {
      ...d.route,
      ...(extras ? { style: extras.route } : leaving ? { style: "auto" as const } : {}),
      ...(follows(d.route.iconArt) || extras ? { iconArt: newArt } : {}),
    },
    markers: { ...d.markers, ...(extras && d.markers.style !== "sticker" ? { style: extras.marker } : {}) },
  };
}

/**
 * Colours for highlighted (visited) countries, one per country in turn. Vintage looks
 * use the antique washes; other styles take the route colour and step round the colour
 * wheel from it, so the set always suits the map.
 */
export function visitedPalette(accent: string, look: Look | undefined, wash: string[]): string[] {
  if (look === "antique" || look === "engraved" || look === "touring") return wash;
  const n = parseInt(accent.slice(1), 16);
  const [r, g, b] = [(n >> 16) & 255, (n >> 8) & 255, n & 255].map((v) => v / 255);
  const max = Math.max(r, g, b), min = Math.min(r, g, b), l = (max + min) / 2;
  const s = max === min ? 0.5 : l > 0.5 ? (max - min) / (2 - max - min) : (max - min) / (max + min);
  let h = 0;
  if (max !== min) h = max === r ? (g - b) / (max - min) + (g < b ? 6 : 0) : max === g ? (b - r) / (max - min) + 2 : (r - g) / (max - min) + 4;
  h *= 60;
  const hsl = (hh: number) => `hsl(${Math.round(hh % 360)}, ${Math.round(Math.max(0.35, Math.min(0.75, s)) * 100)}%, ${Math.round(Math.max(0.4, Math.min(0.62, l)) * 100)}%)`;
  return [0, 72, 144, 216, 288].map((dh) => hsl(h + dh));
}
