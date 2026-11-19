import { describe, expect, it } from "vitest";
import { gadsAuthUrl, openToken, sealToken } from "../../src/lib/server/googleAds";

describe("Google Ads connection", () => {
  it("stores the refresh token encrypted, and only it can be opened", () => {
    const sealed = sealToken("1//refresh-token-example");
    expect(sealed).not.toContain("refresh");
    expect(openToken(sealed)).toBe("1//refresh-token-example");
    const [iv, tag, body] = sealed.split(".");
    expect(() => openToken([iv, tag, body.slice(0, -2) + "AA"].join("."))).toThrow();
  });
  it("asks Google for offline access to Ads", () => {
    const u = new URL(gadsAuthUrl("st4te"));
    expect(u.searchParams.get("scope")).toContain("https://www.googleapis.com/auth/adwords");
    expect(u.searchParams.get("access_type")).toBe("offline");
    expect(u.searchParams.get("state")).toBe("st4te");
    expect(u.searchParams.get("redirect_uri")).toMatch(/\/api\/admin\/google-ads\/callback$/);
  });
});
