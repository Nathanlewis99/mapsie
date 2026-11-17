import { describe, expect, it } from "vitest";
import { adConsentFrom } from "../../src/lib/server/conversions";

const req = (cookie: string) => new Request("https://mapsie.shop/api/checkout", { headers: { cookie, "user-agent": "UA" } });
const consent = (analytics: boolean, ads: boolean) => `mapsie_consent=${encodeURIComponent(JSON.stringify({ analytics, ads, at: "x" }))}`;

describe("ad consent at checkout", () => {
  it("records nothing without consent", () => {
    expect(adConsentFrom(req("_fbp=fb.1.2.3; _ga=GA1.1.111.222"), "1.2.3.4")).toBeUndefined();
    expect(adConsentFrom(req(`${consent(false, false)}; _fbp=fb.1.2.3`), "1.2.3.4")).toBeUndefined();
  });
  it("keeps only what each choice allows", () => {
    const analyticsOnly = adConsentFrom(req(`${consent(true, false)}; _fbp=fb.1.2.3; _ga=GA1.1.111.222`), "1.2.3.4");
    expect(analyticsOnly).toEqual({ analytics: true, ads: false, gaClientId: "111.222" });
    const all = adConsentFrom(req(`${consent(true, true)}; _fbp=fb.1.2.3; _ga=GA1.1.111.222`), "1.2.3.4");
    expect(all).toMatchObject({ ads: true, fbp: "fb.1.2.3", ip: "1.2.3.4", userAgent: "UA", gaClientId: "111.222" });
  });
});
