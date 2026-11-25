// This week's promotions (shared by browser and server).
//  - Black Friday: 10% off everything with BLACKFRIDAY10, shown in the banner, until the end of Monday 30 Nov (UK).
//  - Save your map: after someone shows intent in the designer we offer to email them their map, with a
//    personal code for SAVE_OFFER_PCT% off that expires an hour later (a trial for this week).
export const BLACK_FRIDAY = { code: "BLACKFRIDAY10", pct: 10, ends: "2026-12-01T00:00:00Z" } as const;
export const SAVE_OFFER = { pct: 15, minutes: 60, ends: "2026-12-01T00:00:00Z" } as const;

export const blackFridayOn = (now = Date.now()) => now < Date.parse(BLACK_FRIDAY.ends);
export const saveOfferOn = (now = Date.now()) => now < Date.parse(SAVE_OFFER.ends);

/** A personal code the visitor got from "Save your map", kept in their browser until it expires. */
export interface MyOffer { code: string; pct: number; expiresAt: string }
const KEY = "mapsie-offer";
export function myOffer(): MyOffer | null {
  try {
    const o = JSON.parse(localStorage.getItem(KEY) ?? "null") as MyOffer | null;
    return o && Date.parse(o.expiresAt) > Date.now() ? o : null;
  } catch {
    return null;
  }
}
export function rememberOffer(o: MyOffer) {
  try {
    localStorage.setItem(KEY, JSON.stringify(o));
  } catch {}
}
export const minutesLeft = (o: MyOffer, now = Date.now()) => Math.max(0, Math.ceil((Date.parse(o.expiresAt) - now) / 60_000));
export const countdown = (o: MyOffer, now = Date.now()) => {
  const s = Math.max(0, Math.floor((Date.parse(o.expiresAt) - now) / 1000));
  return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`;
};
