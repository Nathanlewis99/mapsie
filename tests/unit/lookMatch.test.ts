import { describe, expect, it } from "vitest";
import { applyPreset, visitedPalette } from "../../src/lib/lookMatch";
import { PRESETS, WASH_COLOURS } from "../../src/lib/themes";
import { SAMPLE } from "../../src/lib/sample";

const preset = (id: string) => PRESETS.find((p) => p.id === id)!;

describe("matching the design to the map style", () => {
  it("gives a vintage map engraved stickers, a dashed route and town-symbol pins", () => {
    const d = { ...SAMPLE, stickers: [{ id: "s1", kind: "sticker" as const, name: "beer", src: "", lng: 0, lat: 0, size: 10, rotation: 0 }, { id: "o1", kind: "original" as const, name: "safari-giraffe", origStyle: "papercut" as const, src: "", lng: 0, lat: 0, size: 10, rotation: 0 }] };
    const out = applyPreset(d, preset("heritage"));
    expect(out.stickerStyle).toBe("engraved");
    expect(out.route?.style).toBe("dashed");
    expect(out.route?.iconArt).toBe("engraved");
    expect(out.markers?.style).toBe("dot");
    expect(out.stickers?.[0].art).toBe("engraved");
    expect(out.stickers?.[1].origStyle).toBe("engraved");
    // and back again to a modern style
    const back = applyPreset({ ...d, ...out } as typeof d, preset("minimal"));
    expect(back.stickers?.[1].origStyle).toBe("line");
    expect(back.route?.style).toBe("auto");
  });
  it("keeps a sticker style the customer chose themselves", () => {
    const d = { ...SAMPLE, stickers: [{ id: "s1", kind: "sticker" as const, name: "beer", art: "neon" as const, src: "", lng: 0, lat: 0, size: 10, rotation: 0 }] };
    expect(applyPreset(d, preset("antique")).stickers?.[0].art).toBe("neon");
  });
  it("colours visited countries differently, to suit the map", () => {
    expect(visitedPalette("#d9442b", "antique", WASH_COLOURS)).toEqual(WASH_COLOURS);
    const p = visitedPalette("#d9442b", undefined, WASH_COLOURS);
    expect(new Set(p).size).toBe(5);
  });
});
