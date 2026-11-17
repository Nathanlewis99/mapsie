"use client";
import { CONSENT_COOKIE } from "./consentCookie";
export { CONSENT_COOKIE };
// The visitor's cookie choices, for the optional analytics (Google Analytics) and
// advertising (Meta Pixel, Google Ads) tags. Stored in a first-party cookie so the
// server can see it at checkout (for sending the sale to the ad platforms only when
// the visitor agreed). Nothing optional loads until the visitor chooses.
export interface Consent {
  analytics: boolean;
  ads: boolean;
  at: string;
}

const MAX_AGE = 180 * 24 * 3600; // ask again after 6 months, as the ICO recommends

export function readConsent(): Consent | null {
  if (typeof document === "undefined") return null;
  const raw = document.cookie.split("; ").find((c) => c.startsWith(`${CONSENT_COOKIE}=`))?.slice(CONSENT_COOKIE.length + 1);
  if (!raw) return null;
  try {
    const c = JSON.parse(decodeURIComponent(raw)) as Consent;
    return typeof c.analytics === "boolean" && typeof c.ads === "boolean" ? c : null;
  } catch {
    return null;
  }
}

export function saveConsent(analytics: boolean, ads: boolean): Consent {
  const c: Consent = { analytics, ads, at: new Date().toISOString() };
  const secure = location.protocol === "https:" ? "; Secure" : "";
  document.cookie = `${CONSENT_COOKIE}=${encodeURIComponent(JSON.stringify(c))}; Max-Age=${MAX_AGE}; Path=/; SameSite=Lax${secure}`;
  window.dispatchEvent(new CustomEvent("mapsie:consent", { detail: c }));
  return c;
}

/** Open the cookie settings (from the footer link). */
export const openCookieSettings = () => window.dispatchEvent(new Event("mapsie:consent-open"));
