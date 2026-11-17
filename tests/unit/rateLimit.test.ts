import { describe, expect, it } from "vitest";
import { clientIp, limit, sameOrigin } from "../../src/lib/server/rateLimit";

const req = (headers: Record<string, string>, url = "https://mapsie.shop/api/ai/design") => new Request(url, { headers });

describe("rate limiting", () => {
  it("allows up to the limit in the window, per key", () => {
    for (let i = 0; i < 3; i++) expect(limit("t", "a", 3, 60_000)).toBe(true);
    expect(limit("t", "a", 3, 60_000)).toBe(false);
    expect(limit("t", "b", 3, 60_000)).toBe(true);
  });
  it("prefers Cloudflare's address over a forgeable X-Forwarded-For", () => {
    expect(clientIp(req({ "cf-connecting-ip": "1.2.3.4", "x-forwarded-for": "9.9.9.9, 1.2.3.4" }))).toBe("1.2.3.4");
    expect(clientIp(req({ "x-forwarded-for": "5.6.7.8, 10.0.0.1" }))).toBe("5.6.7.8");
    expect(clientIp(req({}))).toBe("unknown");
  });
  it("only accepts requests from our own pages", () => {
    expect(sameOrigin(req({ origin: "https://mapsie.shop" }), "https://mapsie.shop")).toBe(true);
    expect(sameOrigin(req({ referer: "https://mapsie.shop/create" }), "https://mapsie.shop")).toBe(true);
    expect(sameOrigin(req({ origin: "https://evil.example" }), "https://mapsie.shop")).toBe(false);
    expect(sameOrigin(req({}), "https://mapsie.shop")).toBe(false);
  });
});
