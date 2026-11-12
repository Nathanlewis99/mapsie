import { rank } from "./search";
import catalog from "./sticker-catalog.json";
import availability from "./sticker-availability.json";

// ---------------------------------------------------------------- artwork
// Artwork sets (downloaded by scripts/fetch-stickers.mjs):
//   cartoon  Twemoji (CC-BY 4.0)               /stickers/<name>.svg
//   flat     Fluent Emoji Flat (MIT)           /stickers/flat/<name>.svg
//   color    Fluent Emoji Color (MIT)          /stickers/color/<name>.svg
//   line     Fluent Emoji High Contrast (MIT)  /stickers/line/<name>.svg
type ArtSet = "cartoon" | "flat" | "color" | "line";

// Finishes are SVG filters (see StickerFilters.tsx), drawn in the poster's own
// colours. They're vector effects, so they stay crisp at 300 dpi.
export type Finish = "none" | "diecut" | "stamp" | "watercolour" | "retro" | "gold" | "neon" | "ink";

export type ArtStyleId = "cartoon" | "flat" | "illustrated" | "sticker" | "line" | "stamp" | "watercolour" | "retro" | "gold" | "neon";

export interface ArtStyle {
  id: ArtStyleId;
  name: string;
  blurb: string;
  set: ArtSet;
  finish: Finish;
  blend?: "multiply"; // sits "in" the paper rather than on top of it
}

export const ART_STYLES: ArtStyle[] = [
  { id: "illustrated", name: "Illustrated", blurb: "Rich, painterly colour", set: "color", finish: "none" },
  { id: "watercolour", name: "Watercolour", blurb: "Soft washes that bleed into the paper", set: "color", finish: "watercolour", blend: "multiply" },
  { id: "stamp", name: "Vintage stamp", blurb: "Inked like an old explorer's chart", set: "flat", finish: "stamp", blend: "multiply" },
  { id: "line", name: "Fine line", blurb: "Elegant pen drawing in your ink colour", set: "line", finish: "ink" },
  { id: "gold", name: "Gold foil", blurb: "Gleaming metallic gold", set: "flat", finish: "gold" },
  { id: "retro", name: "Retro print", blurb: "Two-tone, in your map's colours", set: "flat", finish: "retro" },
  { id: "sticker", name: "Die-cut sticker", blurb: "Glossy vinyl stickers with a white edge", set: "color", finish: "diecut" },
  { id: "neon", name: "Neon", blurb: "Glowing signs — best on dark maps", set: "line", finish: "neon" },
  { id: "flat", name: "Flat", blurb: "Clean and modern", set: "flat", finish: "none" },
  { id: "cartoon", name: "Cartoon", blurb: "Bold and playful", set: "cartoon", finish: "none" },
];

export const getArtStyle = (id: string | undefined) => ART_STYLES.find((s) => s.id === id) ?? ART_STYLES[0];

/** Which sticker style suits each map style. */
export const SUGGESTED_STYLE: Record<string, ArtStyleId> = {
  vintage: "stamp",
  minimal: "line",
  topo: "illustrated",
  tropical: "sticker",
  midnight: "gold",
  blush: "watercolour",
  terrain: "illustrated",
  atlas: "illustrated",
  nautical: "stamp",
  explorer: "stamp",
  blueprint: "line",
  ink: "line",
  custom: "illustrated",
};
export const suggestedStyleFor = (presetId: string): ArtStyleId => SUGGESTED_STYLE[presetId] ?? "illustrated";

// ---------------------------------------------------------------- catalogue
export interface StickerDef {
  name: string;
  code: string;
  label: string;
  keywords: string;
  pack: string;
}

export const STICKERS = catalog as StickerDef[];
const AVAILABLE = availability as Record<string, string[]>;

export const PACKS = [...new Set(STICKERS.map((s) => s.pack))];

/** URL for a sticker drawn in a given style, falling back to the nearest set we have. */
export function stickerSrc(name: string, style: ArtStyleId | undefined): string {
  const set = getArtStyle(style).set;
  if (set === "cartoon") return `/stickers/${name}.svg`;
  const have = AVAILABLE[name] ?? [];
  const order: string[] = set === "line" ? ["line", "flat", "color"] : set === "flat" ? ["flat", "color", "line"] : ["color", "flat", "line"];
  const pick = order.find((s) => have.includes(s));
  return pick ? `/stickers/${pick}/${name}.svg` : `/stickers/${name}.svg`;
}

/** Older designs stored only a path like /stickers/crocodile.svg. */
export const nameFromSrc = (src: string) => /\/stickers\/(?:[a-z]+\/)?([a-z0-9-]+)\.svg$/.exec(src)?.[1];

export function searchStickers(q: string): StickerDef[] {
  if (!q.trim()) return [];
  return rank(STICKERS, q, (s) => ({ name: `${s.label} ${s.name.replace(/-/g, " ")}`, tags: s.keywords, extra: s.pack }));
}
