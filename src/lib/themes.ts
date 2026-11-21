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
  engraved?: boolean;
  look?: Look;
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
    // After the Ordnance Survey town plans of the 1880s and 90s: one sepia ink on cream,
    // engraved buildings, stippled parks, contour lines and a gilt route.
    id: "heritage",
    name: "Heritage",
    tag: "Victorian",
    relief: true,
    texture: true,
    engraved: true,
    colors: { land: "#f2e8d0", water: "#d8ccad", park: "#ebe0c4", roads: "#f7efdc", borders: "#5b4630", labels: "#3a2a19", accent: "#c08b2c", paper: "#efe4c9", ink: "#3a2a19" },
  },
  {
    // After Bartholomew's half-inch and the Ordnance Survey's 1920s Popular Edition:
    // red main roads, yellow lanes, green woods, brown contours, blue water.
    id: "touring",
    name: "Touring",
    tag: "1920s",
    relief: true,
    texture: true,
    look: "touring",
    colors: { land: "#f3ead3", water: "#b9d2d8", park: "#bccb9b", roads: "#c4473a", borders: "#4b3a2a", labels: "#2f2418", accent: "#2b4f86", paper: "#f3ead3", ink: "#2f2418" },
  },
  {
    // Hand-coloured maps of the 1600s and 1700s: a watercolour wash along every
    // border, engraved lettering, and the sea lined along the coast.
    id: "antique",
    name: "Antique",
    tag: "1700s",
    relief: true,
    texture: true,
    look: "antique",
    details: { compass: true, compassStyle: "vintage", neatline: true },
    colors: { land: "#f1e3c2", water: "#ece0c2", park: "#e4d6b0", roads: "#f6ecd6", borders: "#4a3622", labels: "#3a2a18", accent: "#a2342a", paper: "#efe0bd", ink: "#3a2a18" },
  },
  {
    // Mid-century railway and travel posters: a few strong flat colours.
    id: "poster",
    name: "Railway poster",
    tag: "1930s",
    relief: false,
    texture: false,
    look: "poster",
    colors: { land: "#f0d9a8", water: "#24628f", park: "#8db26c", roads: "#fff4dc", borders: "#2d3a46", labels: "#1f2a35", accent: "#d9442b", paper: "#f6e7c4", ink: "#1f2a35" },
  },
  {
    // Soft painted washes on white paper, with a hand-lettered feel.
    id: "watercolour",
    name: "Watercolour",
    relief: true,
    texture: false,
    look: "watercolour",
    colors: { land: "#fbf8f1", water: "#9fc8db", park: "#b7d3a0", roads: "#d9cfc2", borders: "#6b5b4b", labels: "#4a4038", accent: "#d46a6a", paper: "#fbf8f1", ink: "#4a4038" },
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
    ...(p.engraved ? { engraved: true } : {}),
    ...(p.look ? { look: p.look } : {}),
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

/** Sea depth is on by default for the styles that show relief. */
export const showSeaDepth = (t: Theme) => t.seaDepth ?? t.relief;

/** `seaTiles`: the sea-depth contour tile URL (from lib/seaDepth), when running in a browser. */
export function buildStyle(base: StyleSpecification, theme: Theme, opts: { seaTiles?: string; origin?: string } = {}): StyleSpecification {
  const sea = showSeaDepth(theme) && !!opts.seaTiles;
  const c = theme.colors;
  const style: StyleSpecification = JSON.parse(JSON.stringify(base));
  const out: AnyLayer[] = [];
  const look = lookOf(theme);
  if (look && OWN_FONTS.includes(look)) style.glyphs = `${opts.origin ?? ""}/api/glyphs/{fontstack}/{range}.pbf`;
  const waterlines = theme.details?.waterlines ?? look === "antique";

  for (const layer of style.layers as AnyLayer[]) {
    const id = layer.id;
    const paint = (layer.paint ??= {});

    if (look) {
      const res = restyle(look, layer, theme, sea);
      if (res) {
        out.push(...res);
        if (id === "water" && waterlines) out.push(...waterLines(c.water, c.borders));
        if (id === "boundary_disputed") out.push(...detailLayers(theme.details ?? NO_DETAILS, c));
        continue;
      }
    }

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
      const minorPlace = id.startsWith("label_") && !id.startsWith("label_country");
      if (!theme.labels || !isPlaceOrWater || id === "label_other" || (theme.countriesOnly && minorPlace)) hide(layer);
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

    // Terrain shading goes under the sea. The seabed data is coarse (1-2 km a
    // pixel), so shading it turns into soft smudges at print size; the water
    // layer covers them and keeps the coast crisp.
    if (id === "water" && theme.relief) {
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

    out.push(layer);

    // Sea depth goes straight on top of the sea: a soft deep-water tint, and fine
    // contour lines (vector, so they stay crisp at any print size).
    if (id === "water" && sea) out.push(...seaLayers(c.water, c.labels));
    if (id === "water" && waterlines) out.push(...waterLines(c.water, c.borders));

    // Cartographic extras go just below the place names.
    if (id === "boundary_disputed") out.push(...detailLayers(theme.details ?? NO_DETAILS, c));

  }

  style.layers = out;
  const d = theme.details ?? NO_DETAILS;
  const geo = (data: unknown) => ({ type: "geojson", data }) as StyleSpecification["sources"][string];
  if (d.grid) style.sources["mapsie-grid"] = geo(graticule);
  if (d.tropics) style.sources["mapsie-tropics"] = geo(specialLatitudes);
  if (d.currents) style.sources["mapsie-currents"] = geo(currents);
  if (d.lanes) style.sources["mapsie-lanes"] = geo(shippingLanes);
  if (look === "antique") style.sources["mapsie-wash"] = geo(`${opts.origin ?? ""}/geo/countries-wash.json`);
  if (sea) style.sources["mapsie-sea"] = { type: "vector", tiles: [opts.seaTiles!], maxzoom: 11 } as StyleSpecification["sources"][string];
  if (theme.relief || theme.hypso || sea) {
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

// ---------------------------------------------------------------- vintage looks
// Heritage (engraved), Touring, Antique, Railway poster and Watercolour each restyle the
// base layers in their own way. Each returns the layers to draw in place of one base
// layer, or null to fall back to the normal handling.
export type Look = "engraved" | "touring" | "antique" | "poster" | "watercolour";
export const lookOf = (t: Theme): Look | undefined => t.look ?? (t.engraved ? "engraved" : undefined);
/** Looks that use our own label fonts (served from /api/glyphs). */
const OWN_FONTS: Look[] = ["engraved", "touring", "antique", "watercolour"];

const SERIF = { regular: ["Old Standard Regular"], italic: ["Old Standard Italic"], bold: ["Old Standard Bold"] };
const HAND = { regular: ["Patrick Hand Regular"], italic: ["Patrick Hand Regular"], bold: ["Patrick Hand Regular"] };
const SANS = { regular: ["Noto Sans Regular"], italic: ["Noto Sans Italic"], bold: ["Noto Sans Bold"] };
// Road widths: a fine ink casing either side of a coloured road.
const roadWidth = (k: number, extra = 0): unknown => ["interpolate", ["exponential", 1.6], ["zoom"], 10, 0.4 * k + extra, 13, 1.6 * k + extra, 15, 5 * k + extra, 17, 14 * k + extra];
// Touring maps (Bartholomew, OS Popular Edition): red main roads, yellow minor roads.
const TOURING_MINOR = "#ecc86a";
// Antique hand-colouring: one muted watercolour per country (see public/geo/countries-wash.json).
export const WASH_COLOURS = ["#cf8a72", "#9fb487", "#dcbc6e", "#b99ab8", "#93b0c0"];

const setPaint = (l: AnyLayer, p: Record<string, unknown>) => ((l as { paint?: Record<string, unknown> }).paint = p);
const setLayout = (l: AnyLayer, p: Record<string, unknown>) => ((l as { layout?: Record<string, unknown> }).layout = p);

function restyle(look: Look, layer: AnyLayer, theme: Theme, sea: boolean): AnyLayer[] | null {
  const id = layer.id;
  const c = theme.colors;
  const ink = c.borders;
  const paint = (layer.paint ??= {});
  const show = () => setLayout(layer, { ...(layer.layout ?? {}), visibility: "visible" });
  const from = layer as unknown as { source: string; "source-layer"?: string; filter?: unknown };
  const like = (extra: Record<string, unknown>) => {
    const l: Record<string, unknown> = { type: "line", source: from.source, "source-layer": from["source-layer"], filter: from.filter, ...extra };
    for (const k of Object.keys(l)) if (l[k] === undefined) delete l[k];
    return l as unknown as AnyLayer;
  };
  const fonts = look === "watercolour" ? HAND : look === "poster" ? SANS : SERIF;

  if (id === "water") {
    paint["fill-color"] = c.water;
    const out: AnyLayer[] = [];
    if (look === "antique") out.push(...washLayers());
    const relief = { engraved: 0.25, touring: 0.35, antique: 0.4, poster: 0, watercolour: 0.2 }[look];
    if (theme.relief && relief) out.push(reliefLayer(theme, relief));
    out.push(layer);
    if (look === "watercolour") {
      // Pigment pools at the edge of a wash, so the coast is a soft, darker line.
      out.push({ ...layer, id: "mapsie-water-texture", paint: { "fill-pattern": "mapsie-wash", "fill-opacity": 0.35 } } as AnyLayer);
      out.push(like({ id: "mapsie-water-edge", paint: { "line-color": mix(c.water, ink, 0.3), "line-width": ["interpolate", ["linear"], ["zoom"], 4, 3, 10, 7], "line-blur": ["interpolate", ["linear"], ["zoom"], 4, 3, 10, 7], "line-opacity": 0.6 } }));
    } else if (look !== "poster") {
      out.push(like({ id: "mapsie-water-edge", paint: { "line-color": ink, "line-width": ["interpolate", ["linear"], ["zoom"], 8, 0.4, 15, 1.1], "line-opacity": 0.8 } }));
    }
    // Old hand-coloured maps show no sea depth; their sea is lined along the coast instead.
    if (sea && (look === "engraved" || look === "touring")) out.push(...seaLayers(c.water, c.labels));
    // Land contours (in brown on touring maps, as on Bartholomew's).
    if (sea && (look === "engraved" || look === "touring")) {
      out.push({
        id: "mapsie-land-contours",
        type: "line",
        source: "mapsie-sea",
        "source-layer": "contours",
        filter: [">", ["get", "ele"], 0],
        layout: { "line-join": "round", "line-cap": "round" },
        paint: { "line-color": look === "touring" ? "#a87a4e" : ink, "line-opacity": ["match", ["get", "level"], 1, 0.5, 0.3], "line-width": ["match", ["get", "level"], 1, 0.8, 0.5] },
      } as AnyLayer);
    }
    return out;
  }
  if (id === "park" || id === "landcover_wood") {
    // Real parks and woods only: the park data also holds protected areas, such as
    // Edinburgh's World Heritage Site, which cover whole city centres.
    if (id === "park") (layer as { filter?: unknown }).filter = ["all", from.filter as never, ["!", ["in", ["get", "class"], ["literal", ["protected_area", "national_park", "aboriginal_lands"]]]]] as never;
    paint["fill-color"] = c.park;
    paint["fill-opacity"] = look === "watercolour" ? 0.75 : 1;
    if (look === "engraved" || look === "antique") return [layer, { ...layer, id: `${id}-stipple`, paint: { "fill-pattern": "mapsie-stipple", "fill-opacity": 0.9 } } as AnyLayer];
    if (look === "watercolour") return [layer, { ...layer, id: `${id}-texture`, paint: { "fill-pattern": "mapsie-wash", "fill-opacity": 0.5 } } as AnyLayer, like({ id: `${id}-edge`, paint: { "line-color": mix(c.park, ink, 0.3), "line-width": 2, "line-blur": 2, "line-opacity": 0.45 } })];
    if (look === "touring") return [layer, like({ id: `${id}-edge`, paint: { "line-color": mix(c.park, ink, 0.4), "line-width": 0.5, "line-opacity": 0.6 } })];
    return [layer];
  }
  if (id === "building") {
    if (look === "poster") return (hide(layer), [layer]);
    show();
    if (look === "watercolour") {
      setPaint(layer, { "fill-color": mix(c.land, ink, 0.18), "fill-opacity": ["interpolate", ["linear"], ["zoom"], 13, 0, 14, 0.6] });
      return [layer];
    }
    if (look === "touring") {
      setPaint(layer, { "fill-color": "#c9a08a", "fill-opacity": ["interpolate", ["linear"], ["zoom"], 13, 0.4, 14, 0.9] });
      return [layer, like({ id: "building-outline", filter: undefined, minzoom: 14, paint: { "line-color": ink, "line-width": 0.4, "line-opacity": 0.6 } })];
    }
    setPaint(layer, { "fill-pattern": "mapsie-hatch", "fill-opacity": ["interpolate", ["linear"], ["zoom"], 12, 0.4, 14, 1] });
    return [layer, like({ id: "building-outline", filter: undefined, minzoom: 13, paint: { "line-color": ink, "line-width": ["interpolate", ["linear"], ["zoom"], 13, 0.3, 17, 1], "line-opacity": 0.85 } })];
  }
  if (id.startsWith("highway") && layer.type === "line" && !id.includes("casing") && !id.includes("subtle") && !id.includes("bridge")) {
    const major = id.includes("motorway") || id.includes("major");
    const k = id.includes("motorway") ? 1.6 : id.includes("major") ? 1.3 : id.includes("path") ? 0.35 : 1;
    if (id.includes("path")) {
      if (look === "poster") return (hide(layer), [layer]);
      setPaint(layer, { "line-color": ink, "line-width": 0.6, "line-dasharray": [2, 2], "line-opacity": look === "watercolour" ? 0.3 : 0.6 });
      return [layer];
    }
    show();
    if (look === "poster") {
      // Only the main roads, as simple pale lines.
      if (!major) return (hide(layer), [layer]);
      setPaint(layer, { "line-color": c.roads, "line-width": roadWidth(k * 0.7), "line-opacity": 0.9 });
      return [layer];
    }
    if (look === "watercolour") {
      setPaint(layer, { "line-color": mix(c.land, ink, 0.35), "line-width": roadWidth(k * 0.6), "line-opacity": 0.55 });
      return [layer];
    }
    const fill = look === "touring" ? (major ? c.roads : TOURING_MINOR) : c.roads;
    const casing = { ...layer, id: `${id}-engraved-case`, paint: { "line-color": ink, "line-width": roadWidth(k, look === "touring" ? 0.9 : 1.2), "line-opacity": 0.9 } } as unknown as AnyLayer;
    setPaint(layer, { "line-color": fill, "line-width": roadWidth(k) });
    return [casing, layer];
  }
  if (look === "touring" && id.startsWith("highway") && id.includes("subtle")) {
    // The main roads at region scale, in touring-map red.
    setPaint(layer, { "line-color": c.roads, "line-width": ["interpolate", ["linear"], ["zoom"], 5, 0.8, 10, 2.2], "line-opacity": ["interpolate", ["linear"], ["zoom"], 10, 1, 11, 0] });
    show();
    return [layer];
  }
  if (id.startsWith("highway") && layer.type === "line") return (hide(layer), [layer]);
  if (id.startsWith("railway")) {
    // Fine single lines, as engraved; the base style's dashed overlays would thicken them.
    if (id.includes("dashline") || look === "poster" || look === "watercolour") hide(layer);
    else setPaint(layer, { "line-color": ink, "line-opacity": 0.8, "line-width": ["interpolate", ["linear"], ["zoom"], 12, 0.5, 16, 1.4] });
    return [layer];
  }
  if (id.startsWith("boundary")) {
    if (look === "poster") setPaint(layer, { "line-color": ink, "line-opacity": 0.5, "line-width": id === "boundary_2" ? 1.2 : 0.6 });
    else if (look === "watercolour") setPaint(layer, { "line-color": ink, "line-opacity": 0.3, "line-width": 1, "line-dasharray": [3, 2] });
    // Fine dotted county lines, as on the old maps; national borders a little heavier.
    else setPaint(layer, { "line-color": ink, "line-opacity": look === "antique" ? 0.6 : 0.45, "line-width": id === "boundary_2" ? 0.9 : 0.6, "line-dasharray": [1, 2] });
    return [layer];
  }
  if (layer.type === "symbol") {
    const isPlaceOrWater = id.startsWith("label_") || id.startsWith("water_name");
    const minorPlace = id.startsWith("label_") && !id.startsWith("label_country");
    const big = id.startsWith("label_country") || id.startsWith("label_state") || id === "label_city_capital" || id === "label_city";
    const water = id.startsWith("water_name");
    // Railway posters only name the big places.
    const posterSkip = look === "poster" && !big;
    if (!theme.labels || !isPlaceOrWater || id === "label_other" || (theme.countriesOnly && minorPlace) || posterSkip) return (hide(layer), [layer]);
    const name = ["coalesce", ["get", "name:en"], ["get", "name_en"], ["get", "name:latin"], ["get", "name"]];
    const upper = big && look !== "watercolour";
    setLayout(layer, {
      ...(layer.layout ?? {}),
      "text-field": upper ? ["upcase", name] : name,
      "text-font": water ? fonts.italic : big ? (look === "antique" ? fonts.italic : fonts.bold) : fonts.regular,
      "text-letter-spacing": upper ? 0.25 : water ? 0.12 : 0.04,
    });
    paint["text-color"] = c.labels;
    paint["text-halo-color"] = c.land;
    paint["text-halo-width"] = look === "poster" ? 0 : 1.4;
    return [layer];
  }
  return null;
}

/** Antique hand-colouring: each country edged in its own watercolour, fading out as you zoom into a town. */
function washLayers(): AnyLayer[] {
  const colour = ["match", ["get", "c"], ...WASH_COLOURS.flatMap((col, i) => [i, col]), WASH_COLOURS[0]];
  const fade = (v: number) => ["interpolate", ["linear"], ["zoom"], 6, v, 9, 0];
  return [
    { id: "mapsie-wash-fill", type: "fill", source: "mapsie-wash", paint: { "fill-color": colour, "fill-opacity": fade(0.24) } } as unknown as AnyLayer,
    { id: "mapsie-wash-edge", type: "line", source: "mapsie-wash", layout: { "line-join": "round" }, paint: { "line-color": colour, "line-width": ["interpolate", ["linear"], ["zoom"], 1, 3, 5, 9], "line-blur": ["interpolate", ["linear"], ["zoom"], 1, 2, 5, 6], "line-opacity": fade(0.9) } } as unknown as AnyLayer,
  ];
}

/** Water-lining: fine lines following the coast out to sea, the old engravers' trademark. */
function waterLines(water: string, ink: string): AnyLayer[] {
  const offsets = [2.5, 6, 11];
  return offsets.map((o, i) => ({
    id: `mapsie-waterline-${i}`,
    type: "line",
    source: "openmaptiles",
    "source-layer": "water",
    filter: ["match", ["geometry-type"], ["MultiPolygon", "Polygon"], true, false],
    layout: { "line-join": "round" },
    paint: { "line-color": mix(water, ink, 0.5), "line-width": 0.55, "line-offset": o, "line-opacity": 0.5 - i * 0.14 },
  }) as unknown as AnyLayer);
}

function reliefLayer(theme: Theme, exaggeration: number): AnyLayer {
  const c = theme.colors;
  return { id: "mapsy-relief", type: "hillshade", source: "mapsy-dem", paint: { "hillshade-exaggeration": exaggeration, "hillshade-shadow-color": c.labels, "hillshade-highlight-color": c.land, "hillshade-accent-color": c.borders } } as AnyLayer;
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

// Deep water a little darker, shallow water untouched, land not at all. The tint
// fades in gradually from the coast, so the coarse seabed data never shows a hard edge.
function seaLayers(water: string, ink: string): AnyLayer[] {
  const rgb = (hex: string, a: number) => {
    const n = parseInt(hex.replace("#", ""), 16);
    return `rgba(${(n >> 16) & 255}, ${(n >> 8) & 255}, ${n & 255}, ${a})`;
  };
  const deep = mix(water, ink, 0.35);
  return [
    {
      id: "mapsie-sea-tint",
      type: "color-relief",
      source: "mapsy-dem",
      paint: {
        "color-relief-opacity": 1,
        "color-relief-color": ["interpolate", ["linear"], ["elevation"], -6000, rgb(deep, 0.55), -2000, rgb(deep, 0.38), -200, rgb(deep, 0.12), -20, rgb(deep, 0), 0, rgb(deep, 0)],
      },
    } as AnyLayer,
    {
      id: "mapsie-sea-depth",
      type: "line",
      source: "mapsie-sea",
      "source-layer": "contours",
      filter: ["<", ["get", "ele"], 0],
      layout: { "line-join": "round", "line-cap": "round" },
      paint: {
        "line-color": mix(water, ink, 0.45),
        "line-opacity": ["match", ["get", "level"], 1, 0.55, 0.32],
        "line-width": ["match", ["get", "level"], 1, 0.7, 0.45],
      },
    } as AnyLayer,
  ];
}

/** Blend two #rrggbb colours: t=0 gives a, t=1 gives b. */
function mix(a: string, b: string, t: number) {
  const pa = parseInt(a.slice(1), 16), pb = parseInt(b.slice(1), 16);
  const ch = (s: number) => Math.round(((pa >> s) & 255) * (1 - t) + ((pb >> s) & 255) * t);
  return `#${[16, 8, 0].map((s) => ch(s).toString(16).padStart(2, "0")).join("")}`;
}
