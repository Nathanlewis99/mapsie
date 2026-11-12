"use client";
import type { TrackEvent } from "./funnel";

// Anonymous analytics that store nothing on the device: no cookies, no local or
// session storage. A random id lives only in this page's memory, so a "visit" is
// one page load and the client-side navigation after it (home -> editor ->
// checkout). Each step is sent once per visit. Nothing personal is collected,
// and browsers that ask not to be tracked (Global Privacy Control / Do Not Track) are skipped.

let id: string | null = null;
const sent = new Set<string>();

function optedOut() {
  const n = navigator as Navigator & { globalPrivacyControl?: boolean };
  return n.globalPrivacyControl === true || n.doNotTrack === "1";
}

export function visitId(): string | null {
  if (typeof window === "undefined" || optedOut()) return null;
  return (id ??= Math.random().toString(36).slice(2) + Date.now().toString(36));
}

export function track(name: TrackEvent, props?: Record<string, string | number | boolean>) {
  const v = visitId();
  if (!v || sent.has(name)) return;
  sent.add(name);
  const body = JSON.stringify({ v, name, props });
  if (!navigator.sendBeacon?.("/api/events", new Blob([body], { type: "application/json" })))
    fetch("/api/events", { method: "POST", body, headers: { "content-type": "application/json" }, keepalive: true }).catch(() => {});
}

/** First event of a visit: where they came from and on what. */
export function trackVisit() {
  const p = new URLSearchParams(location.search);
  let ref = "";
  try {
    ref = document.referrer ? new URL(document.referrer).hostname.replace(/^www\./, "") : "";
  } catch {}
  if (ref === location.hostname.replace(/^www\./, "")) ref = "";
  track("visit", {
    source: p.get("utm_source") ?? (ref || "direct"),
    ...(p.get("utm_campaign") ? { campaign: p.get("utm_campaign")! } : {}),
    landing: location.pathname.split("/").slice(0, 2).join("/") || "/",
    device: matchMedia("(pointer: coarse)").matches ? "mobile" : "desktop",
  });
}
