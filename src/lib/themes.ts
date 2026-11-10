import type { StyleSpecification, LayerSpecification } from "maplibre-gl";
import type { Theme, ThemeColors } from "./types";

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
];

export function themeFromPreset(p: Preset): Theme {
  return { presetId: p.id, colors: { ...p.colors }, labels: true, relief: p.relief, texture: p.texture };
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

    out.push(layer);

    // Terrain shading sits just above land cover and below water.
    if (id === "landuse_residential" && theme.relief) {
      out.push({
        id: "mapsy-relief",
        type: "hillshade",
        source: "mapsy-dem",
        paint: {
          "hillshade-exaggeration": 0.45,
          "hillshade-shadow-color": c.labels,
          "hillshade-highlight-color": c.land,
          "hillshade-accent-color": c.borders,
        },
      } as AnyLayer);
    }
  }

  style.layers = out;
  if (theme.relief) {
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
