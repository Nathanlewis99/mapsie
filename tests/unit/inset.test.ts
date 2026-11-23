import { describe, expect, it } from "vitest";
import { insetExtent, merc, pathFor, viewBox } from "@/lib/inset";

const square = (x0: number, y0: number, x1: number, y1: number): GeoJSON.Feature => ({ type: "Feature", properties: {}, geometry: { type: "Polygon", coordinates: [[[x0, y0], [x1, y0], [x1, y1], [x0, y1], [x0, y0]]] } });
const world: GeoJSON.FeatureCollection = { type: "FeatureCollection", features: [square(113, -39, 154, -11), square(145, -44, 149, -40.5)] };

describe("overview map", () => {
  it("frames the whole land mass the trip is on, not just the stops", () => {
    const e = insetExtent(world, [{ lng: 151.2, lat: -33.9 }, { lng: 145.8, lat: -16.9 }])!;
    const [wx] = merc([113, 0]);
    expect(e.x0).toBeLessThan(wx);
    // and reaches far enough south for Tasmania
    expect(e.y1).toBeGreaterThan(merc([0, -42])[1]);
  });
  it("has nothing to show for a trip entirely at sea", () => {
    expect(insetExtent(world, [{ lng: 0, lat: 0 }])).toBeNull();
  });
  it("the main map's box shrinks as it zooms in", () => {
    const a = viewBox([150, -25], 4, 800, 1000);
    const b = viewBox([150, -25], 5, 800, 1000);
    expect(b.x1 - b.x0).toBeCloseTo((a.x1 - a.x0) / 2);
  });
  it("lifts the pen instead of drawing across the world at the date line", () => {
    const ext = { x0: 0, y0: 0, x1: 1, y1: 1 };
    const d = pathFor([[[[179, -17], [-179, -17], [-179, -18], [179, -18]]]], ext, 100, 100);
    expect(d.match(/M/g)!.length).toBeGreaterThan(1);
  });
});
