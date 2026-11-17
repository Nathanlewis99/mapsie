"use client";
// Conversion events for the ad platforms. Each call does nothing unless the visitor
// agreed to that kind of cookie and the tag has loaded (see ConsentManager).
type Gtag = (...args: unknown[]) => void;
type Fbq = ((...args: unknown[]) => void) & { loaded?: boolean };
declare global {
  interface Window {
    gtag?: Gtag;
    fbq?: Fbq;
    __mapsieAds?: { googleAds?: string; adsPurchaseLabel?: string };
  }
}

export type AdEvent =
  | { name: "view_design" }
  | { name: "begin_checkout"; value: number; currency: string }
  | { name: "purchase"; orderId: string; value: number; currency: string };

export function adEvent(e: AdEvent) {
  const { gtag, fbq } = window;
  if (e.name === "view_design") {
    gtag?.("event", "view_item", { items: [{ item_id: "custom-map", item_name: "Custom map print" }] });
    fbq?.("track", "ViewContent", { content_name: "Map designer" });
  } else if (e.name === "begin_checkout") {
    const currency = e.currency.toUpperCase();
    gtag?.("event", "begin_checkout", { currency, value: e.value });
    fbq?.("track", "InitiateCheckout", { currency, value: e.value });
  } else if (e.name === "purchase") {
    const currency = e.currency.toUpperCase();
    // The same order is also sent from our server (in case the browser blocks tags),
    // with the order id as the shared event id so each platform counts it once.
    gtag?.("event", "purchase", { transaction_id: e.orderId, currency, value: e.value });
    const ads = window.__mapsieAds;
    if (ads?.googleAds && ads.adsPurchaseLabel) gtag?.("event", "conversion", { send_to: `${ads.googleAds}/${ads.adsPurchaseLabel}`, transaction_id: e.orderId, currency, value: e.value });
    fbq?.("track", "Purchase", { currency, value: e.value }, { eventID: e.orderId });
  }
}
