import { describe, expect, it } from "vitest";
import { DEFAULT_TEXT, normalizeDesign, type Design } from "@/lib/types";
import { crowding, recommendedProduct, smallestText, tidyCrowded } from "@/lib/legibility";

const stop = (id: string, name: string, lng: number, lat: number) => ({ id, name, lng, lat, showLabel: true });
const design = (stops: ReturnType<typeof stop>[], view: Partial<Design["view"]> = {}) =>
  normalizeDesign({ id: "t", productId: "a3", orientation: "portrait", view: { center: [100, 0], zoom: 3, bearing: 0, refWidth: 550, ...view }, stops } as never);

describe("normalizeDesign", () => {
  it("fills in fields added after a design was saved", () => {
    const d = normalizeDesign({ id: "old" } as never);
    expect(d.text).toEqual(DEFAULT_TEXT);
    expect(d.markers).toMatchObject({ size: 1, labelSize: 1 });
    expect(d.paper).toBe("ema");
  });
  it("falls back to options Prodigi sells", () => {
    const d = normalizeDesign({ id: "x", mount: "black", glaze: "motheye" } as never);
    expect(d.mount).toBe("white");
    expect(d.glaze).toBe("perspex");
  });
});

describe("legibility", () => {
  // Six stops on a small island with the trip continuing to Australia: too tight at this zoom.
  const sriLanka = [stop("a", "Colombo", 79.86, 6.93), stop("b", "Kandy", 80.64, 7.29), stop("c", "Ella", 81.05, 6.87), stop("d", "Sigiriya", 80.76, 7.96), stop("e", "Mirissa", 80.46, 5.95), stop("f", "Galle", 80.22, 6.03)];
  const onward = [stop("g", "Singapore", 103.82, 1.35), stop("h", "Sydney", 151.21, -33.87)];
  const crowded = design([...sriLanka, ...onward], { center: [116, -12], zoom: 2.3 });

  it("spots overlapping stops", () => {
    expect(crowding(crowded).length).toBeGreaterThan(0);
  });
  it("untangles them, only touching the crowded ones", () => {
    const patch = tidyCrowded(crowded);
    const after = { ...crowded, stops: crowded.stops.map((s) => ({ ...s, ...patch[s.id] })) };
    expect(crowding(after)).toEqual([]);
    expect(patch.g).toBeUndefined();
    expect(patch.h).toBeUndefined();
  });
  it("prints bigger text on bigger paper and recommends a size", () => {
    const d = { ...design(onward), markers: { ...design(onward).markers, labelSize: 0.3 } };
    expect(smallestText(d, "a1").pt).toBeGreaterThan(smallestText(d, "a4").pt * 2.5);
    expect(recommendedProduct(d)?.id).toBeDefined();
  });
});
