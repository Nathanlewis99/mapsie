// The whole poster is described by one JSON "design". The editor and the
// print renderer both draw from it, so what you see is what gets printed.

export type LngLat = [number, number];

export interface Stop {
  id: string;
  name: string;
  lng: number;
  lat: number;
  showLabel: boolean;
}

export interface Sticker {
  id: string;
  kind: "sticker" | "photo";
  src: string; // /stickers/x.svg or a data: URL for uploaded photos
  lng: number;
  lat: number;
  size: number; // % of poster width
  rotation: number; // degrees
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

export type RouteStyle = "solid" | "dashed" | "dotted";
export type Layout = "band" | "border" | "overlay";
export type Orientation = "portrait" | "landscape";

export interface Design {
  id: string;
  title: string;
  subtitle: string;
  font: FontId;
  layout: Layout;
  productId: string;
  orientation: Orientation;
  theme: Theme;
  // refWidth = poster width in CSS px when the view was saved. The print
  // renderer lays the poster out at this width and just raises the pixel
  // density, so the framing and label sizes match the editor exactly.
  view: { center: LngLat; zoom: number; bearing: number; refWidth: number };
  stops: Stop[];
  route: { show: boolean; style: RouteStyle; curved: boolean; width: number };
  stickers: Sticker[];
}

export type FontId = "playfair" | "caveat" | "montserrat" | "pacifico" | "bebas";
