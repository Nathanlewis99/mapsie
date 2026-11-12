import { describe, expect, it } from "vitest";
import { rank, scoreMatch } from "@/lib/search";
import { searchOriginals } from "@/lib/originals";
import { searchStickers } from "@/lib/stickers";

describe("sticker search", () => {
  it("matches whole words, not letters inside other words", () => {
    expect(scoreMatch("car", { name: "Scarlet macaw", extra: "Caribbean parrot" })).toBe(0);
    expect(scoreMatch("car", { name: "Car" })).toBeGreaterThan(scoreMatch("car", { name: "Carousel horse" }));
  });
  it("ranks the name above synonyms above descriptions", () => {
    const items = [
      { name: "Ferry crossing", tags: "boat" },
      { name: "Boat", tags: "" },
      { name: "Island hopping", extra: "boat sea" },
    ];
    expect(rank(items, "boat", (x) => x).map((x) => x.name)).toEqual(["Boat", "Ferry crossing", "Island hopping"]);
  });
  it("understands simple plurals", () => {
    expect(scoreMatch("beaches", { name: "Beach" })).toBeGreaterThan(0);
    expect(scoreMatch("cars", { name: "Car" })).toBeGreaterThan(0);
  });
  it("never puts a parrot first for 'car'", () => {
    expect(searchOriginals("car")[0]?.title ?? "").not.toMatch(/macaw|parrot/i);
    expect(searchStickers("car")[0]?.label).toMatch(/car/i);
  });
  it("finds snakes by type", () => {
    expect(searchOriginals("snake").length).toBeGreaterThan(5);
  });
});
