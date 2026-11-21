// Builds public/geo/countries-wash.json for the Antique style: every country with a
// colour index `c` (0-4) so that neighbours never share a colour, like the hand-coloured
// maps. Run: npx tsx scripts/build/countries-wash.ts
import { readFileSync, writeFileSync } from "node:fs";
import { feature, neighbors } from "topojson-client";
import type { Topology, GeometryCollection } from "topojson-specification";

const topo = JSON.parse(readFileSync("public/geo/countries-50m.json", "utf8")) as Topology;
const obj = topo.objects.countries as GeometryCollection;
const nb = neighbors(obj.geometries as never);
const colours = 5;
const c: number[] = new Array(obj.geometries.length).fill(-1);
// Colour the most-connected countries first (greedy), which needs few colours on maps.
const order = [...c.keys()].sort((a, b) => nb[b].length - nb[a].length);
for (const i of order) {
  const used = new Set(nb[i].map((j) => c[j]));
  // Prefer a colour by id so similar maps look varied, but never a neighbour's.
  const start = Number(obj.geometries[i].id ?? i) % colours;
  for (let k = 0; k < colours; k++) {
    const col = (start + k) % colours;
    if (!used.has(col)) {
      c[i] = col;
      break;
    }
  }
  if (c[i] < 0) c[i] = start;
}
const fc = feature(topo, obj) as unknown as GeoJSON.FeatureCollection;
// Round coordinates to ~100 m to keep the file small.
const round = (x: unknown): unknown => (Array.isArray(x) ? x.map(round) : typeof x === "number" ? Math.round(x * 1000) / 1000 : x);
fc.features = fc.features.map((f, i) => ({ type: "Feature", properties: { c: c[i] }, geometry: { ...f.geometry, coordinates: round((f.geometry as GeoJSON.Polygon).coordinates) } as GeoJSON.Geometry }));
writeFileSync("public/geo/countries-wash.json", JSON.stringify(fc));
console.log(fc.features.length, "countries,", Math.round(JSON.stringify(fc).length / 1024), "KB");
