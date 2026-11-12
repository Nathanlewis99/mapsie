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
  /** Size of this stop's marker relative to the design's marker size. */
  markerScale?: number;
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
  hypso: boolean; // colour land by height (green lowlands to snowy peaks)
  physical: boolean; // classic atlas shaded-relief base
  details: MapDetails;
}

/** Cartographic extras that can be switched on and off. */
export interface MapDetails {
  grid: boolean; // lines of latitude and longitude
  tropics: boolean; // equator, tropics and polar circles
  currents: boolean; // major ocean currents
  lanes: boolean; // shipping lanes
  compass: boolean; // compass rose
}

export const NO_DETAILS: MapDetails = { grid: false, tropics: false, currents: false, lanes: false, compass: false };

export type RouteStyle = "auto" | "solid" | "dashed" | "dotted";
export type MarkerStyle = "number" | "dot" | "pin" | "heart";
export type Layout = "band" | "border" | "overlay";
export type Orientation = "portrait" | "landscape";
export type FrameId = "none" | "black" | "white" | "oak" | "brown" | "darkgrey" | "lightgrey" | "gold" | "silver";
export type PaperId = "ema" | "hpr" | "hge" | "lpp";
export type MountId = "none" | "white" | "offwhite" | "black";
export type GlazeId = "perspex" | "glass" | "motheye";

export interface Design {
  id: string;
  title: string;
  subtitle: string;
  font: FontId;
  layout: Layout;
  productId: string;
  orientation: Orientation;
  frame: FrameId;
  paper: PaperId; // unframed prints only; framed prints use the frame's standard paper
  mount: MountId; // framed only
  glaze: GlazeId; // framed only
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
  text: TextStyle;
  stickerStyle: ArtStyleId; // default style for new stickers
  originals: { style: OriginalStyle; palette: string }; // defaults for new Mapsie Originals
}

export type TextCase = "none" | "upper" | "lower";

/** How the title and subtitle look. `font` on the design is the title font. */
export interface TextStyle {
  titleSize: number; // multiplier, 1 = default
  titleCase: TextCase;
  titleSpacing: number; // letter spacing, % of poster width
  titleItalic: boolean;
  subtitleFont: FontId;
  subtitleSize: number;
  subtitleCase: TextCase;
  subtitleSpacing: number;
  subtitleItalic: boolean;
  showRoute: boolean; // the "A · B · C" line under the subtitle
  align: "center" | "left" | "right";
  titleOffset?: [number, number]; // dragged position, % of poster width
  subtitleOffset?: [number, number];
}

export const DEFAULT_TEXT: TextStyle = {
  titleSize: 1,
  titleCase: "none",
  titleSpacing: 0,
  titleItalic: false,
  subtitleFont: "montserrat",
  subtitleSize: 1,
  subtitleCase: "upper",
  subtitleSpacing: 0.5,
  subtitleItalic: false,
  showRoute: true,
  align: "center",
};

export type FontId = "playfair" | "caveat" | "montserrat" | "pacifico" | "bebas" | "cormorant" | "josefin" | "abril" | "courier" | "vibes";

/** Fill in fields added after a design was first saved. */
export function normalizeDesign(d: Partial<Design> & Pick<Design, "id">): Design {
  const x = d as Design;
  const r = (x.route ?? {}) as Partial<Design["route"]>;
  const m = (x.markers ?? {}) as Partial<Design["markers"]>;
  const v = (x.visited ?? {}) as Partial<Design["visited"]>;
  return {
    ...x,
    frame: x.frame ?? "none",
    paper: x.paper ?? "ema",
    mount: x.mount ?? "none",
    glaze: x.glaze ?? "perspex",
    theme: x.theme && { ...x.theme, hypso: x.theme.hypso ?? false, physical: x.theme.physical ?? false, details: { ...NO_DETAILS, ...(x.theme.details ?? {}) } },
    route: { show: r.show ?? true, style: r.style ?? "auto", curved: r.curved ?? true, width: r.width ?? 0.45, modeIcons: r.modeIcons ?? true },
    markers: { style: m.style ?? "number", showDates: m.showDates ?? false, size: m.size ?? 1, labelSize: m.labelSize ?? 1 },
    visited: { show: v.show ?? false, opacity: v.opacity ?? 0.35 },
    text: { ...DEFAULT_TEXT, ...(x.text ?? {}) },
    stickerStyle: x.stickerStyle ?? "cartoon",
    originals: x.originals ?? { style: "papercut", palette: "auto" },
    // Older designs only stored a path; recover the artwork name from it.
    stickers: (x.stickers ?? []).map((st) =>
      st.kind === "sticker" && !st.name ? { ...st, name: /\/([a-z0-9-]+)\.svg$/.exec(st.src)?.[1], art: st.art ?? "cartoon" } : st,
    ),
    stops: x.stops ?? [],
  };
}
