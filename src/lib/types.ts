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
}

export interface Sticker {
  id: string;
  kind: "sticker" | "photo" | "text";
  src: string; // /stickers/x.svg, a data: URL for photos, "" for text
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
  markers: { style: MarkerStyle; showDates: boolean };
  visited: { show: boolean; opacity: number };
  stickers: Sticker[];
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
    markers: { style: m.style ?? "number", showDates: m.showDates ?? false },
    visited: { show: v.show ?? false, opacity: v.opacity ?? 0.35 },
    stickers: x.stickers ?? [],
    stops: x.stops ?? [],
  };
}
