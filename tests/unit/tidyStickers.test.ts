import { describe, expect, it } from "vitest";
import { crowdedStickers, stickerBox, tidyStickers } from "../../src/lib/legibility";
import { normalizeDesign } from "../../src/lib/types";

const base = () =>
  normalizeDesign({
    id: "t", title: "T", subtitle: "", productId: "a3", orientation: "portrait", frame: "none", paper: "ema", mount: "none", glaze: "perspex",
    view: { center: [0, 0], zoom: 4, bearing: 0, refWidth: 400 },
    stops: [{ id: "s1", name: "Somewhere", lng: 0, lat: 0, showLabel: true }],
    stickers: [],
  } as never);

const st = (id: string, lng: number, lat: number, size = 10, kind = "sticker") => ({ id, kind, src: "", name: "tent", lng, lat, size, rotation: 0 }) as never;

describe("tidying stickers, photos and notes", () => {
  it("moves a sticker off a stop, nearby, without shrinking if there's room", () => {
    const d = { ...base(), stickers: [st("a", 0, 0)] };
    expect(crowdedStickers(d)).toEqual(["a"]);
    const p = tidyStickers(d);
    const moved = { ...d, stickers: [{ ...d.stickers[0], ...p.a }] };
    expect(crowdedStickers(moved)).toEqual([]);
    expect(p.a.size).toBe(10);
    expect(Math.hypot(p.a.lng!, p.a.lat!)).toBeLessThan(8); // stays near its place
  });
  it("brings a sticker hanging off the edge back onto the map", () => {
    const d = { ...base(), stickers: [st("b", 8.6, 0)] }; // half off the right edge
    expect(crowdedStickers(d)).toEqual(["b"]);
    const p = tidyStickers(d);
    expect(crowdedStickers({ ...d, stickers: [{ ...d.stickers[0], ...p.b }] })).toEqual([]);
  });
  it("separates two stacked items and leaves clear ones alone", () => {
    const d = { ...base(), stickers: [st("c", -3, 3), st("d", -3, 3, 8, "photo"), st("e", 3, -3)] };
    const p = tidyStickers(d);
    expect(p.e).toBeUndefined();
    const after = { ...d, stickers: d.stickers.map((x: { id: string }) => ({ ...x, ...(p[x.id] ?? {}) })) };
    expect(crowdedStickers(after)).toEqual([]);
  });
  it("sizes notes by their text", () => {
    const box = stickerBox({ kind: "text", text: "swam with turtles!", size: 3 } as never, { x: 0, y: 0 });
    expect(box.r - box.l).toBeGreaterThan(20);
  });
});
