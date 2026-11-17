import { describe, expect, it } from "vitest";
import { christmasState } from "../../src/lib/christmas";

const at = (iso: string) => new Date(`${iso}T12:00:00Z`);
describe("Christmas order-by dates", () => {
  it("moves from standard to express to digital, per country", () => {
    expect(christmasState("GB", at("2026-10-20")).kind).toBe("none");
    expect(christmasState("GB", at("2026-11-17"))).toMatchObject({ kind: "standard", date: "2026-12-16" });
    expect(christmasState("GB", at("2026-12-16")).kind).toBe("standard");
    expect(christmasState("GB", at("2026-12-17")).kind).toBe("digital");
    expect(christmasState("US", at("2026-12-14"))).toMatchObject({ kind: "express", date: "2026-12-16" });
    expect(christmasState("US", at("2026-12-17")).kind).toBe("digital");
    expect(christmasState("AU", at("2026-12-25")).kind).toBe("none");
  });
});
