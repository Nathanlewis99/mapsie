"use client";
// Sea depth drawn as vector contour lines. The seabed elevation data is coarse, so
// shading it blurs at print size; lines traced from it are vector and print crisp at
// any size. maplibre-contour traces them in a web worker from the same terrain tiles.
import maplibregl from "maplibre-gl";
import mlcontour from "maplibre-contour";

let tiles: string | null = null;

/** The contour tile URL, registering the generator with MapLibre the first time. */
export function seaContourTiles() {
  if (tiles) return tiles;
  const dem = new mlcontour.DemSource({
    url: "https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png",
    encoding: "terrarium",
    maxzoom: 11,
    // The worker is built from the library's own source text, which Next's dev-mode
    // hot reload alters (it breaks with "$RefreshSig$ is not defined"). Production is fine.
    worker: process.env.NODE_ENV === "production",
  });
  dem.setupMaplibre(maplibregl);
  tiles = dem.contourProtocolUrl({
    // Metres between lines, [minor, major], by zoom: wider apart when zoomed out.
    thresholds: { 1: [2000, 4000], 4: [1000, 2000], 6: [500, 2000], 8: [200, 1000], 10: [100, 500], 11: [50, 250] },
    elevationKey: "ele",
    levelKey: "level",
    contourLayer: "contours",
    // Trace on a finer grid when zoomed in, so curves stay smooth rather than stepped.
    subsampleBelow: 512,
  });
  return tiles;
}
