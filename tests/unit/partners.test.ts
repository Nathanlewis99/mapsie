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
