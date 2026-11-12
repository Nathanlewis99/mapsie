import type { StyleSpecification, LayerSpecification } from "maplibre-gl";
import { NO_DETAILS, type MapDetails, type Theme, type ThemeColors } from "./types";
import { currents, graticule, shippingLanes, specialLatitudes } from "./mapDetails";

// Base cartography: OpenFreeMap (free, no API key, commercial use allowed).
// We recolour every layer from the user's theme, so one base style gives us
// unlimited looks.
export const BASE_STYLE_URL = "https://tiles.openfreemap.org/styles/positron";

export interface Preset {
  id: string;
  name: string;
  colors: ThemeColors;
  relief: boolean;
  texture: boolean;
  hypso?: boolean;
  physical?: boolean;
  details?: Partial<MapDetails>;
  /** Shown as a small tag on the style card. */
  tag?: string;
}

export const PRESETS: Preset[] = [
  {
    id: "vintage",
    name: "Vintage",
    relief: true,
    texture: true,
    colors: { land: "#efe2c4", water: "#a7c3bd", park: "#dcd2a6", roads: "#cfae80", borders: "#8a6a4a", labels: "#5b4636", accent: "#b5452b", paper: "#f4ead2", ink: "#3d2e22" },
  },
  {
    id: "minimal",
    name: "Minimal",
    relief: false,
    texture: false,
    colors: { land: "#f4f2ee", water: "#d3dce4", park: "#e7eae0", roads: "#ffffff", borders: "#b9b9b9", labels: "#6b6b6b", accent: "#ff5a5f", paper: "#ffffff", ink: "#1d1d1f" },
  },
  {
    id: "topo",
    name: "Topographic",
    relief: true,
    texture: false,
    colors: { land: "#eef0e2", water: "#9cc3d8", park: "#cfe0b4", roads: "#d8b98a", borders: "#8f8f7c", labels: "#4a4a3a", accent: "#e4572e", paper: "#f7f6ef", ink: "#2a2a22" },
  },
  {
    id: "tropical",
    name: "Tropical",
    relief: false,
    texture: false,
    colors: { land: "#fff1d0", water: "#58c4c6", park: "#bfe5a9", roads: "#ffd59a", borders: "#e3a06f", labels: "#25605f", accent: "#ff6b6b", paper: "#fffaf0", ink: "#124645" },
  },
  {
    id: "midnight",
    name: "Midnight",
    relief: true,
    texture: false,
    colors: { land: "#1c2739", water: "#0d1522", park: "#203244", roads: "#3a4a63", borders: "#56688a", labels: "#a5b6d0", accent: "#ffcf5c", paper: "#0f1724", ink: "#f3e9d2" },
  },
  {
    id: "blush",
    name: "Blush",
    relief: false,
    texture: true,
    colors: { land: "#fbe9e4", water: "#c9d8ef", park: "#f2d8cf", roads: "#ffffff", borders: "#d9a5a0", labels: "#8a5b63", accent: "#d0507a", paper: "#fff5f2", ink: "#5a2e3a" },
  },
  {
    id: "terrain",
    name: "Terrain",
    tag: "Mountains",
    relief: true,
    texture: false,
    hypso: true,
    colors: { land: "#e9ecd9", water: "#9fc4d9", park: "#b9d3a0", roads: "#c9a77c", borders: "#7d7462", labels: "#3d3a2e", accent: "#d1452f", paper: "#f6f3ea", ink: "#2b2a22" },
  },
  {
    id: "atlas",
    name: "Atlas",
    tag: "Physical",
    relief: false,
    texture: false,
    physical: true,
    details: { grid: true },
    colors: { land: "#e8e4c9", water: "#a6cbe3", park: "#cfdcae", roads: "#b58b5a", borders: "#a0405a", labels: "#2f2a24", accent: "#d1302f", paper: "#fbf8ef", ink: "#1f2a3a" },
  },
  {
    id: "nautical",
    name: "Nautical",
    tag: "Sea chart",
    relief: false,
    texture: true,
    details: { grid: true, lanes: true, compass: true },
    colors: { land: "#f1e6c8", water: "#cfe3e6", park: "#e4dab4", roads: "#d6c39b", borders: "#8c6f4e", labels: "#2c4a5a", accent: "#b23a2e", paper: "#f7efda", ink: "#1e3a4c" },
  },
  {
    id: "explorer",
    name: "Explorer",
    tag: "Currents",
    relief: true,
    texture: true,
    details: { grid: true, tropics: true, currents: true, compass: true },
    colors: { land: "#e8d5aa", water: "#a9bdb0", park: "#d5c08e", roads: "#b89566", borders: "#7a5634", labels: "#4a3420", accent: "#9c2f1c", paper: "#efe0bd", ink: "#3a2716" },
  },
  {
    id: "blueprint",
    name: "Blueprint",
    relief: false,
    texture: false,
    details: { grid: true },
    colors: { land: "#2c5d9c", water: "#1d4479", park: "#2c5d9c", roads: "#a9c4e8", borders: "#dbe7f7", labels: "#eef4fc", accent: "#ffd166", paper: "#1d4479", ink: "#f2f6fc" },
  },
  {
    id: "ink",
    name: "Ink",
    relief: false,
    texture: false,
    colors: { land: "#ffffff", water: "#e9e9e9", park: "#f3f3f3", roads: "#c8c8c8", borders: "#4a4a4a", labels: "#1a1a1a", accent: "#111111", paper: "#ffffff", ink: "#111111" },
  },
];

export function themeFromPreset(p: Preset): Theme {
  return {
    presetId: p.id,
    colors: { ...p.colors },
    labels: true,
    relief: p.relief,
    texture: p.texture,
    hypso: p.hypso ?? false,
    physical: p.physical ?? false,
    details: { ...NO_DETAILS, ...p.details },
  };
}

let baseStylePromise: Promise<StyleSpecification> | null = null;
export function loadBaseStyle() {
  baseStylePromise ??= fetch(BASE_STYLE_URL).then((r) => r.json());
  return baseStylePromise;
}

type AnyLayer = LayerSpecification & { paint?: Record<string, unknown>; layout?: Record<string, unknown> };

const hide = (l: AnyLayer) => {
  l.layout = { ...(l.layout ?? {}), visibility: "none" };
};

export function buildStyle(base: StyleSpecification, theme: Theme): StyleSpecification {
  const c = theme.colors;
  const style: StyleSpecification = JSON.parse(JSON.stringify(base));
  const out: AnyLayer[] = [];

  for (const layer of style.layers as AnyLayer[]) {
    const id = layer.id;
    const paint = (layer.paint ??= {});

    if (id === "background") paint["background-color"] = c.land;
    else if (id === "water") paint["fill-color"] = c.water;
    else if (id === "waterway") paint["line-color"] = c.water;
    else if (id === "park" || id === "landcover_wood") {
      paint["fill-color"] = c.park;
      paint["fill-opacity"] = 0.7;
    } else if (id.startsWith("landcover_ice") || id === "landcover_glacier") {
      paint["fill-color"] = c.land;
    } else if (id === "landuse_residential") paint["fill-color"] = c.land;
    else if (id === "building" || id.startsWith("aeroway") || id.includes("casing") || id.includes("pier") || id.startsWith("tunnel")) {
      hide(layer);
    } else if (id.startsWith("highway") && layer.type === "line") {
      paint["line-color"] = c.roads;
    } else if (id.startsWith("railway")) {
      paint["line-color"] = c.roads;
      paint["line-opacity"] = 0.6;
    } else if (id.startsWith("boundary")) {
      paint["line-color"] = c.borders;
    } else if (layer.type === "symbol") {
      const isPlaceOrWater = id.startsWith("label_") || id.startsWith("water_name");
      if (!theme.labels || !isPlaceOrWater || id === "label_other") hide(layer);
      else {
        // English names read best on a poster; fall back to the local name.
        layer.layout = { ...(layer.layout ?? {}), "text-field": ["coalesce", ["get", "name:en"], ["get", "name_en"], ["get", "name:latin"], ["get", "name"]] };
        paint["text-color"] = c.labels;
        paint["text-halo-color"] = c.land;
        paint["text-halo-width"] = 1.2;
      }
    }

    if (id === "park" && theme.hypso) paint["fill-opacity"] = 0.3;
    if (id === "landcover_wood" && theme.hypso) paint["fill-opacity"] = 0.25;

    // The classic atlas base (Natural Earth shaded relief) sits on the land, under
    // our own sea colour, and fades out as you zoom into a city.
    if (id === "water" && theme.physical) {
      out.push({
        id: "mapsie-physical",
        type: "raster",
        source: "ne2_shaded",
        paint: { "raster-opacity": ["interpolate", ["linear"], ["zoom"], 5, 0.9, 8, 0], "raster-saturation": 0.1, "raster-contrast": 0.08 },
      } as AnyLayer);
    }

    // Elevation colours go straight on top of the paper, under parks and water.
    if (id === "park" && theme.hypso) out.push(hypsoLayer(c.land));

    out.push(layer);

    // Cartographic extras go just below the place names.
    if (id === "boundary_disputed") out.push(...detailLayers(theme.details ?? NO_DETAILS, c));

    // Terrain shading sits just above land cover and below water.
    if (id === "landuse_residential" && theme.relief) {
      out.push({
        id: "mapsy-relief",
        type: "hillshade",
        source: "mapsy-dem",
        paint: {
          "hillshade-exaggeration": theme.hypso ? 0.6 : 0.45,
          "hillshade-shadow-color": c.labels,
          "hillshade-highlight-color": c.land,
          "hillshade-accent-color": c.borders,
        },
      } as AnyLayer);
    }
  }

  style.layers = out;
  const d = theme.details ?? NO_DETAILS;
  const geo = (data: unknown) => ({ type: "geojson", data }) as StyleSpecification["sources"][string];
  if (d.grid) style.sources["mapsie-grid"] = geo(graticule);
  if (d.tropics) style.sources["mapsie-tropics"] = geo(specialLatitudes);
  if (d.currents) style.sources["mapsie-currents"] = geo(currents);
  if (d.lanes) style.sources["mapsie-lanes"] = geo(shippingLanes);
  if (theme.relief || theme.hypso) {
    style.sources["mapsy-dem"] = {
      type: "raster-dem",
      tiles: ["https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png"],
      encoding: "terrarium",
      tileSize: 256,
      maxzoom: 12,
      attribution: "Terrain: Mapzen / AWS Open Data",
    };
  }
  return style;
}

// Height bands, roughly in the tradition of school atlases. Sea level and below
// are under the water layer, so they never show.
function hypsoLayer(land: string): AnyLayer {
  return {
    id: "mapsie-hypso",
    type: "color-relief",
    source: "mapsy-dem",
    paint: {
      "color-relief-opacity": 0.85,
      "color-relief-color": [
        "interpolate", ["linear"], ["elevation"],
        -10, land,
        0, "#a8c98f",
        200, "#c5d99a",
        500, "#e3dfa2",
        1000, "#e6c98d",
        1800, "#d2a376",
        2800, "#b5876a",
        4000, "#d9d2cb",
        5200, "#ffffff",
      ],
    },
  } as AnyLayer;
}

const WARM = "#c8553d";
const COLD = "#3b78b0";

function detailLayers(d: MapDetails, c: ThemeColors): AnyLayer[] {
  const layers: AnyLayer[] = [];
  const font = ["Noto Sans Italic"];
  if (d.grid) {
    layers.push({
      id: "mapsie-grid",
      type: "line",
      source: "mapsie-grid",
      paint: { "line-color": c.labels, "line-opacity": 0.2, "line-width": 0.7 },
    } as AnyLayer);
  }
  if (d.tropics) {
    layers.push(
      {
        id: "mapsie-tropics",
        type: "line",
        source: "mapsie-tropics",
        paint: { "line-color": c.labels, "line-opacity": 0.55, "line-width": ["match", ["get", "name"], "Equator", 1.4, 1], "line-dasharray": [6, 4] },
      } as AnyLayer,
      {
        id: "mapsie-tropics-label",
        type: "symbol",
        source: "mapsie-tropics",
        layout: {
          "symbol-placement": "line",
          "symbol-spacing": 600,
          "text-field": ["upcase", ["get", "name"]],
          "text-font": font,
          "text-size": 10,
          "text-letter-spacing": 0.25,
          "text-offset": [0, -0.8],
        },
        paint: { "text-color": c.labels, "text-opacity": 0.8, "text-halo-color": c.water, "text-halo-width": 1 },
      } as AnyLayer,
    );
  }
  if (d.lanes) {
    layers.push(
      {
        id: "mapsie-lanes",
        type: "line",
        source: "mapsie-lanes",
        layout: { "line-cap": "round", "line-join": "round" },
        paint: { "line-color": c.labels, "line-opacity": 0.45, "line-width": 1.1, "line-dasharray": [1, 2.5] },
      } as AnyLayer,
      {
        id: "mapsie-lanes-ship",
        type: "symbol",
        source: "mapsie-lanes",
        layout: { "symbol-placement": "line", "symbol-spacing": 260, "icon-image": "mapsie-ship", "icon-size": 0.5, "icon-rotation-alignment": "viewport", "icon-allow-overlap": true },
        paint: { "icon-color": c.labels, "icon-opacity": 0.65 },
      } as AnyLayer,
    );
  }
  if (d.currents) {
    const color: unknown = ["match", ["get", "kind"], "warm", WARM, COLD];
    layers.push(
      {
        id: "mapsie-currents",
        type: "line",
        source: "mapsie-currents",
        layout: { "line-cap": "round", "line-join": "round" },
        paint: { "line-color": color, "line-opacity": 0.7, "line-width": ["interpolate", ["linear"], ["zoom"], 1, 1.4, 5, 2.6] },
      } as AnyLayer,
      {
        id: "mapsie-currents-arrow",
        type: "symbol",
        source: "mapsie-currents",
        layout: { "symbol-placement": "line", "symbol-spacing": 90, "icon-image": "mapsie-arrow", "icon-size": 0.55, "icon-allow-overlap": true, "icon-ignore-placement": true },
        paint: { "icon-color": color, "icon-opacity": 0.85 },
      } as AnyLayer,
      {
        id: "mapsie-currents-label",
        type: "symbol",
        source: "mapsie-currents",
        minzoom: 1.5,
        layout: { "symbol-placement": "line", "symbol-spacing": 500, "text-field": ["get", "name"], "text-font": font, "text-size": 10.5, "text-offset": [0, -0.9], "text-max-angle": 30 },
        paint: { "text-color": color, "text-halo-color": c.water, "text-halo-width": 1.2 },
      } as AnyLayer,
    );
  }
  return layers;
}
