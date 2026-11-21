import { describe, expect, it } from "vitest";
import { createPasswordUser, getSavedDesign, listSavedDesigns, upsertSavedDesign } from "../../src/lib/server/db";
import { SAMPLE } from "../../src/lib/sample";

describe("duplicating a saved map", () => {
  it("keeps everything in place, with its own id and an account label, leaving the original alone", async () => {
    const user = (await createPasswordUser({ email: `dup-${Date.now()}@example.com`, passwordHash: "x" })).id;
    const design = { ...SAMPLE, title: "Our honeymoon", stickers: [{ id: "s1", kind: "sticker" as const, name: "beer", src: "", lng: 1, lat: 2, size: 9, rotation: 15 }] };
    const original = await upsertSavedDesign(user, design);
    const src = (await getSavedDesign(user, original))!;
    const copy = await upsertSavedDesign(user, { ...src.design, id: "new-design-id" }, undefined, `${src.title} (copy)`);
    expect(copy).not.toBe(original);
    const c = (await getSavedDesign(user, copy))!;
    expect(c.title).toBe("Our honeymoon (copy)");
    expect(c.design.title).toBe("Our honeymoon"); // the printed title is unchanged
    expect(c.design.stickers).toEqual(design.stickers); // same place, size and angle
    expect((await getSavedDesign(user, original))!.title).toBe("Our honeymoon");
    expect((await listSavedDesigns(user)).length).toBe(2);
  });
});
