import { describe, expect, it } from "vitest";
import { classifyChannel } from "../../src/lib/channels";

describe("sales channel", () => {
  it("credits ad clicks to the right network", () => {
    expect(classifyChannel({ click: "gclid" })).toBe("google_ads");
    expect(classifyChannel({ click: "epik", source: "pinterest" })).toBe("pinterest_ads");
    expect(classifyChannel({ click: "fbclid", source: "instagram", medium: "paid" })).toBe("meta_ads");
    expect(classifyChannel({ source: "facebook", medium: "cpc", campaign: "xmas" })).toBe("meta_ads");
  });
  it("tells organic from paid", () => {
    // fbclid is added to ordinary shared links too, so on its own it's social, not an ad.
    expect(classifyChannel({ click: "fbclid", referrer: "l.instagram.com" })).toBe("organic_social");
    expect(classifyChannel({ referrer: "google.com" })).toBe("organic_search");
    expect(classifyChannel({ referrer: "pinterest.co.uk" })).toBe("organic_social");
    expect(classifyChannel({ source: "newsletter", medium: "email" })).toBe("email");
    expect(classifyChannel({ referrer: "someblog.com" })).toBe("referral");
    expect(classifyChannel({ landing: "/" })).toBe("direct");
    expect(classifyChannel(undefined)).toBe("direct");
  });
});
