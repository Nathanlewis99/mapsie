import { feature } from "topojson-client";
import type { Topology, GeometryCollection } from "topojson-specification";
import type { Stop } from "./types";

// Country outlines (Natural Earth 1:50m via world-atlas), loaded on demand.
let cache: Promise<GeoJSON.FeatureCollection> | null = null;
export function loadCountries() {
  cache ??= fetch("/geo/countries-50m.json")
    .then((r) => r.json())
    .then((topo: Topology) => feature(topo, topo.objects.countries as GeometryCollection) as unknown as GeoJSON.FeatureCollection);
  return cache;
}

type Ring = number[][];
function inRing([x, y]: number[], ring: Ring) {
  let inside = false;
  for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) {
    const [xi, yi] = ring[i];
    const [xj, yj] = ring[j];
    if (yi > y !== yj > y && x < ((xj - xi) * (y - yi)) / (yj - yi) + xi) inside = !inside;
  }
  return inside;
}
function inPolygon(p: number[], poly: Ring[]) {
  return inRing(p, poly[0]) && !poly.slice(1).some((hole) => inRing(p, hole));
}
function contains(f: GeoJSON.Feature, p: number[]) {
  const g = f.geometry;
  if (g.type === "Polygon") return inPolygon(p, g.coordinates);
  if (g.type === "MultiPolygon") return g.coordinates.some((poly) => inPolygon(p, poly));
  return false;
}

/** Countries that contain at least one stop. */
export function visitedCountries(all: GeoJSON.FeatureCollection, stops: Stop[]): GeoJSON.FeatureCollection {
  const hit = all.features.filter((f) => stops.some((s) => contains(f, [s.lng, s.lat])));
  return { type: "FeatureCollection", features: hit };
}
