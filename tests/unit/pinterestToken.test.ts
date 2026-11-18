import { afterEach, describe, expect, it, vi } from "vitest";
import { pinterestTokenStatus } from "../../src/lib/server/adSpend";

afterEach(() => {
  vi.useRealTimers();
  delete process.env.PINTEREST_ADS_TOKEN;
});

describe("Pinterest token expiry", () => {
  it("counts 30 days from when a token first appears, and restarts for a new token", async () => {
    expect((await pinterestTokenStatus()).level).toBe("none");
    vi.useFakeTimers({ toFake: ["Date"] });
    vi.setSystemTime(new Date("2026-12-01T09:00:00Z"));
    process.env.PINTEREST_ADS_TOKEN = "token-one";
    expect(await pinterestTokenStatus()).toMatchObject({ level: "ok", daysLeft: 30, expiresOn: "2026-12-31" });
    vi.setSystemTime(new Date("2026-12-27T09:00:00Z"));
    expect(await pinterestTokenStatus()).toMatchObject({ level: "soon", daysLeft: 4 });
    vi.setSystemTime(new Date("2027-01-02T09:00:00Z"));
    expect((await pinterestTokenStatus()).level).toBe("expired");
    process.env.PINTEREST_ADS_TOKEN = "token-two";
    expect(await pinterestTokenStatus()).toMatchObject({ level: "ok", daysLeft: 30 });
  });
});
