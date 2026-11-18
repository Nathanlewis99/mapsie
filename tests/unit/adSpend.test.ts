import { describe, expect, it } from "vitest";
import { adsImportKey, adsImportKeyValid, importScriptRows } from "../../src/lib/server/adSpend";
import { listAdSpend } from "../../src/lib/server/db";

describe("ad spend import", () => {
  it("checks the script's key", () => {
    expect(adsImportKeyValid(adsImportKey())).toBe(true);
    expect(adsImportKeyValid("nope")).toBe(false);
    expect(adsImportKeyValid(null)).toBe(false);
  });
  it("saves Google Ads rows, converting currency and replacing repeats", async () => {
    await importScriptRows("google_ads", [{ day: "2026-12-01", cost: 10, currency: "GBP", conversions: 1, value: 89 }, { day: "bad", cost: 5 }]);
    await importScriptRows("google_ads", [{ day: "2026-12-01", cost: 12, currency: "USD" }]);
    const rows = await listAdSpend("2026-12-01");
    expect(rows).toHaveLength(1);
    expect(rows[0].spend).toBeCloseTo(12 * 0.79);
  });
});
