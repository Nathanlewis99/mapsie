import { describe, expect, it } from "vitest";
import { commissionFor, parseStopList, partnerLink, personaliseTrip, publicPartner, slugify, tradeDiscountPct, tradePrice, type Partner, type PartnerTrip } from "@/lib/partners";
import { classifyChannel } from "@/lib/channels";
import { normalizeDesign } from "@/lib/types";

const trip: PartnerTrip = { id: "lejog", name: "LEJOG", emoji: "🚴", title: "{name}'s End to End", subtitle: "874 miles · {detail}", preset: "vintage", stickers: [], stops: [["Land's End", -5.7, 50.07], ["John o' Groats", -3.07, 58.64, "car"]], ask: { name: "Rider", detail: "Time" } };

describe("partners", () => {
  it("fills in a finisher's name and detail, and tidies when they're left blank", () => {
    expect(personaliseTrip(trip, "Sam", "9 days").title).toBe("Sam's End to End");
    expect(personaliseTrip(trip, "Sam", "9 days").subtitle).toBe("874 miles · 9 days");
    expect(personaliseTrip(trip).subtitle).toBe("874 miles");
    expect(personaliseTrip(trip, "<script>{x}").title).toBe("scriptx's End to End");
  });
  it("parses an admin stop list with travel modes", () => {
    expect(parseStopList("Edinburgh; Inverness (car)\nSkye (boat); Oban (spaceship)")).toEqual([
      { name: "Edinburgh" },
      { name: "Inverness", mode: "car" },
      { name: "Skye", mode: "boat" },
      { name: "Oban (spaceship)" },
    ]);
  });
  it("pays commission on the print, not delivery", () => {
    expect(commissionFor({ commissionPct: 10 }, 78.95, 9.95)).toBe(6.9);
    expect(commissionFor({ commissionPct: 10 }, 5, 9.95)).toBe(0);
  });
  it("prices trade codes by volume", () => {
    expect([tradeDiscountPct(1), tradeDiscountPct(10), tradeDiscountPct(50)]).toEqual([15, 20, 25]);
    expect(tradePrice(69, 20)).toBe(55.2);
  });
  it("makes slugs and links", () => {
    expect(slugify("Coast & Castles Cycling Co.")).toBe("coast-and-castles-cycling-co");
    expect(partnerLink("https://mapsie.shop", "coast", "lejog 2027")).toBe("https://mapsie.shop/with/coast?trip=lejog%202027");
  });
  it("never exposes commission, contacts or notes publicly", () => {
    const p: Partner = { id: "coast", name: "Coast", kind: "event", active: true, commissionPct: 12, contactEmail: "a@b.c", notes: "secret", trips: [trip], createdAt: "" };
    const pub = publicPartner(p) as Record<string, unknown>;
    expect(pub.commissionPct).toBeUndefined();
    expect(pub.contactEmail).toBeUndefined();
    expect(pub.notes).toBeUndefined();
  });
  it("counts partner UTM links as the partners channel", () => {
    expect(classifyChannel({ source: "coast", medium: "partner" })).toBe("partners");
  });
  it("keeps a design's partner and the single-colour countries setting", () => {
    const d = normalizeDesign({ id: "x", partnerRef: "coast", visited: { show: true, opacity: 0.3, multi: false } } as never);
    expect(d.partnerRef).toBe("coast");
    expect(d.visited.multi).toBe(false);
  });
});

import { cleanPayout, payoutSummary } from "@/lib/partners";
import { openPayout, sealPayout } from "@/lib/server/partnerAuth";

describe("partner payout details", () => {
  it("checks and tidies UK bank, IBAN and PayPal details", () => {
    expect(cleanPayout({ method: "uk_bank", accountName: "Coast Rides Ltd", sortCode: "12-34-56", accountNumber: "1234 5678" })).toEqual({ method: "uk_bank", accountName: "Coast Rides Ltd", sortCode: "123456", accountNumber: "12345678" });
    expect(cleanPayout({ method: "uk_bank", accountName: "X", sortCode: "12-34", accountNumber: "12345678" })).toBe("A sort code has 6 digits");
    expect(cleanPayout({ method: "iban", accountName: "X", iban: "gb29 nwbk 6016 1331 9268 19" })).toMatchObject({ iban: "GB29NWBK60161331926819" });
    expect(cleanPayout({ method: "iban", accountName: "X", iban: "nope" })).toBe("That doesn't look like an IBAN");
    expect(cleanPayout({ method: "paypal", email: "pay@coast.com" })).toEqual({ method: "paypal", email: "pay@coast.com" });
    expect(cleanPayout({})).toBe("Choose how you'd like to be paid");
  });
  it("only ever shows a masked summary", () => {
    expect(payoutSummary({ method: "uk_bank", accountName: "Coast", sortCode: "123456", accountNumber: "12345678" })).toBe("UK bank account ••••5678 (Coast)");
    expect(payoutSummary({ method: "paypal", email: "pay@coast.com" })).toBe("PayPal p•••@coast.com");
  });
  it("encrypts payout details at rest", () => {
    const d = { method: "uk_bank" as const, accountName: "Coast", sortCode: "123456", accountNumber: "12345678" };
    const sealed = sealPayout(d);
    expect(sealed).not.toContain("12345678");
    expect(openPayout(sealed)).toEqual(d);
    expect(openPayout(sealed.slice(0, -4) + "AAAA")).toBeNull();
  });
});

import { assessApplication, baseDomain } from "@/lib/partners";
import { checkWebsite, cleanApplication } from "@/lib/server/partnerApply";

describe("partner applications", () => {
  const live = { reachable: true, title: "Coast Rides | Cycling holidays", nameOnSite: true, finalHost: "coastrides.co.uk" };
  it("suggests approving a work email on a live website that names them", () => {
    const r = assessApplication({ company: "Coast Rides", email: "sam@coastrides.co.uk", website: "https://www.coastrides.co.uk" }, { website: live });
    expect(r.recommendation).toBe("approve");
    expect(r.checks.every((c) => c.ok)).toBe(true);
  });
  it("asks for a human look at personal emails or dead websites, and declines duplicates", () => {
    expect(assessApplication({ company: "Coast Rides", email: "sam@gmail.com", website: "coastrides.co.uk" }, { website: live }).recommendation).toBe("review");
    expect(assessApplication({ company: "Coast Rides", email: "sam@coastrides.co.uk", website: "coastrides.co.uk" }, { website: { reachable: false } }).recommendation).toBe("review");
    expect(assessApplication({ company: "Coast Rides", email: "sam@coastrides.co.uk", website: "coastrides.co.uk" }, { website: live, duplicateOf: "Coast Rides" }).recommendation).toBe("deny");
  });
  it("matches subdomains and UK domains", () => {
    expect(baseDomain("shop.coastrides.co.uk")).toBe("coastrides.co.uk");
    expect(baseDomain("mail.example.com")).toBe("example.com");
  });
  it("needs a name, a valid email and a website", () => {
    expect(cleanApplication({ company: "X", contactName: "Y", email: "nope", website: "x.com" })).toBe("Please enter a valid email address.");
    expect(cleanApplication({ company: "X", contactName: "Y", email: "a@x.com", website: "" })).toMatch(/website/);
    expect(cleanApplication({ company: " Coast ", contactName: "Sam", email: "Sam@Coast.com", website: "coast.com", kind: "shop" })).toMatchObject({ company: "Coast", email: "sam@coast.com", kind: "shop" });
  });
  it("never fetches internal addresses", async () => {
    for (const u of ["http://localhost:3000", "http://127.0.0.1", "http://169.254.169.254/latest/meta-data", "http://10.0.0.5", "https://example.com:8443", "file:///etc/passwd"]) {
      expect((await checkWebsite(u, "X")).reachable).toBe(false);
    }
  });
});
