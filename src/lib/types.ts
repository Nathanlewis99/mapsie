import type { ArtStyleId } from "./stickers";
import type { OriginalStyle } from "./originals";

// The whole poster is described by one JSON "design". The editor and the
// print renderer both draw from it, so what you see is what gets printed.

export type LngLat = [number, number];

export type TravelMode = "plane" | "car" | "bus" | "train" | "boat" | "walk";

export interface Stop {
  id: string;
  name: string;
  lng: number;
  lat: number;
  showLabel: boolean;
  date?: string; // free text, e.g. "12–18 March"
  // How they travelled TO this stop (ignored for the first stop).
  arriveBy?: TravelMode;
  // Road geometry for car/bus legs, fetched once and stored so prints never re-fetch.
  path?: LngLat[];
  pathFor?: string; // which leg the path was fetched for, so moved stops refetch
  /** Where the label sits relative to its default spot, in % of poster width. */
  labelOffset?: [number, number];
  /** Size of this stop's label relative to the design's label size. */
  labelScale?: number;
}

export interface Sticker {
  id: string;
  kind: "sticker" | "photo" | "text" | "original";
  src: string; // a data: URL for photos; for stickers, derived from name + art
  name?: string; // sticker artwork name, e.g. "crocodile"
  art?: ArtStyleId; // sticker art style
  origStyle?: OriginalStyle; // Mapsie Originals: papercut or line
  palette?: string; // Mapsie Originals: palette name, or "auto" to follow the map style
  lng: number;
  lat: number;
  size: number; // % of poster width (for text: font size)
  rotation: number; // degrees
  text?: string;
  font?: FontId;
  color?: string;
}

export interface ThemeColors {
  land: string;
  water: string;
  park: string;
  roads: string;
  borders: string;
  labels: string;
  accent: string; // route, stop markers
  paper: string; // poster background / title band
  ink: string; // title text
}

export interface Theme {
  presetId: string;
  colors: ThemeColors;
  labels: boolean;
  relief: boolean; // hillshade terrain
  texture: boolean; // paper grain overlay
}

export type RouteStyle = "auto" | "solid" | "dashed" | "dotted";
export type MarkerStyle = "number" | "dot" | "pin" | "heart";
export type Layout = "band" | "border" | "overlay";
export type Orientation = "portrait" | "landscape";
export type FrameId = "none" | "black" | "white" | "oak";

export interface Design {
  id: string;
  title: string;
  subtitle: string;
  font: FontId;
  layout: Layout;
  productId: string;
  orientation: Orientation;
  frame: FrameId;
  theme: Theme;
  // refWidth = poster width in CSS px when the view was saved. The print
  // renderer lays the poster out at this width and just raises the pixel
  // density, so the framing and label sizes match the editor exactly.
  view: { center: LngLat; zoom: number; bearing: number; refWidth: number };
  stops: Stop[];
  route: { show: boolean; style: RouteStyle; curved: boolean; width: number; modeIcons: boolean };
  markers: { style: MarkerStyle; showDates: boolean; size: number; labelSize: number };
  visited: { show: boolean; opacity: number };
  stickers: Sticker[];
  stickerStyle: ArtStyleId; // default style for new stickers
  originals: { style: OriginalStyle; palette: string }; // defaults for new Mapsie Originals
}

export type FontId = "playfair" | "caveat" | "montserrat" | "pacifico" | "bebas";

/** Fill in fields added after a design was first saved. */
export function normalizeDesign(d: Partial<Design> & Pick<Design, "id">): Design {
  const x = d as Design;
  const r = (x.route ?? {}) as Partial<Design["route"]>;
  const m = (x.markers ?? {}) as Partial<Design["markers"]>;
  const v = (x.visited ?? {}) as Partial<Design["visited"]>;
  return {
    ...x,
    frame: x.frame ?? "none",
    route: { show: r.show ?? true, style: r.style ?? "auto", curved: r.curved ?? true, width: r.width ?? 0.45, modeIcons: r.modeIcons ?? true },
    markers: { style: m.style ?? "number", showDates: m.showDates ?? false, size: m.size ?? 1, labelSize: m.labelSize ?? 1 },
    visited: { show: v.show ?? false, opacity: v.opacity ?? 0.35 },
    stickerStyle: x.stickerStyle ?? "cartoon",
    originals: x.originals ?? { style: "papercut", palette: "auto" },
    // Older designs only stored a path; recover the artwork name from it.
    stickers: (x.stickers ?? []).map((st) =>
      st.kind === "sticker" && !st.name ? { ...st, name: /\/([a-z0-9-]+)\.svg$/.exec(st.src)?.[1], art: st.art ?? "cartoon" } : st,
    ),
    stops: x.stops ?? [],
  };
}
