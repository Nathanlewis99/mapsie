// Server-side purchase events for the ad platforms, sent once when an order is paid,
// and only if the buyer agreed to that kind of cookie at checkout. Sending from the
// server means sales still count when the browser blocks the tags; the order id is the
// shared event id, so the platforms count the browser and server copies once.
//
//   Meta Conversions API:     META_PIXEL_ID + META_CAPI_TOKEN (System User token, from Events Manager)
//   GA4 Measurement Protocol: GA4_MEASUREMENT_ID + GA4_API_SECRET (Admin > Data streams > Measurement Protocol)
//   Pinterest Conversions API: PINTEREST_AD_ACCOUNT_ID + PINTEREST_CAPI_TOKEN (Ads Manager > Conversions > Conversion access token)
import { createHash } from "node:crypto";
import type { Order } from "./db";
import { logError } from "./log";
import { publicUrl } from "./urls";
import { CONSENT_COOKIE } from "../consentCookie";

export interface AdConsent {
  analytics: boolean;
  ads: boolean;
  fbp?: string;
  fbc?: string;
  epik?: string;
  gaClientId?: string;
  ip?: string;
  userAgent?: string;
}

const cookie = (header: string, name: string) =>
  header.split(/;\s*/).find((c) => c.startsWith(`${name}=`))?.slice(name.length + 1);

/** At checkout: what the buyer agreed to, and the ad identifiers we may use (only if they agreed). */
export function adConsentFrom(req: Request, ip: string): AdConsent | undefined {
  const header = req.headers.get("cookie") ?? "";
  let c: { analytics?: boolean; ads?: boolean } = {};
  try {
    c = JSON.parse(decodeURIComponent(cookie(header, CONSENT_COOKIE) ?? ""));
  } catch {
    return undefined;
  }
  if (!c.analytics && !c.ads) return undefined;
  // _ga looks like GA1.1.1234567890.1700000000: the client id is the last two parts.
  const ga = cookie(header, "_ga")?.split(".").slice(-2).join(".");
  return {
    analytics: !!c.analytics,
    ads: !!c.ads,
    ...(c.ads ? { fbp: cookie(header, "_fbp"), fbc: cookie(header, "_fbc"), epik: cookie(header, "_epik"), ip: ip !== "unknown" ? ip : undefined, userAgent: req.headers.get("user-agent")?.slice(0, 400) } : {}),
    ...(c.analytics && ga ? { gaClientId: ga } : {}),
  };
}

const sha256 = (s: string) => createHash("sha256").update(s.trim().toLowerCase()).digest("hex");

/** Send the sale to Meta and Google Analytics (each only if configured and agreed to). Never throws. */
export async function sendPurchaseConversions(o: Order) {
  const c = o.adConsent;
  if (!c || o.source === "etsy") return;
  const value = o.total;
  const currency = o.currency.toUpperCase();
  const jobs: Promise<unknown>[] = [];

  const pixel = process.env.META_PIXEL_ID;
  const token = process.env.META_CAPI_TOKEN;
  if (c.ads && pixel && token) {
    const version = process.env.META_GRAPH_VERSION || "v23.0";
    jobs.push(
      fetch(`https://graph.facebook.com/${version}/${pixel}/events?access_token=${encodeURIComponent(token)}`, {
        method: "POST",
        headers: { "content-type": "application/json" },
        signal: AbortSignal.timeout(10_000),
        body: JSON.stringify({
          data: [
            {
              event_name: "Purchase",
              event_time: Math.floor(Date.now() / 1000),
              event_id: o.id,
              action_source: "website",
              event_source_url: `${publicUrl()}/order/${o.id}`,
              user_data: {
                em: o.email ? [sha256(o.email)] : undefined,
                client_ip_address: c.ip,
                client_user_agent: c.userAgent,
                external_id: o.email ? [sha256(o.email)] : undefined,
                fbp: c.fbp,
                fbc: c.fbc,
              },
              custom_data: { currency, value },
            },
          ],
        }),
      }).then(async (r) => {
        if (!r.ok) throw new Error(`Meta CAPI ${r.status}: ${(await r.text()).slice(0, 300)}`);
      }),
    );
  }

  const ga4 = process.env.GA4_MEASUREMENT_ID;
  const secret = process.env.GA4_API_SECRET;
  if (c.analytics && c.gaClientId && ga4 && secret) {
    jobs.push(
      fetch(`https://www.google-analytics.com/mp/collect?measurement_id=${encodeURIComponent(ga4)}&api_secret=${encodeURIComponent(secret)}`, {
        method: "POST",
        signal: AbortSignal.timeout(10_000),
        body: JSON.stringify({ client_id: c.gaClientId, events: [{ name: "purchase", params: { transaction_id: o.id, currency, value } }] }),
      }).then((r) => {
        if (!r.ok) throw new Error(`GA4 ${r.status}`);
      }),
    );
  }

  const pinAccount = process.env.PINTEREST_AD_ACCOUNT_ID;
  const pinToken = process.env.PINTEREST_CAPI_TOKEN;
  if (c.ads && pinAccount && pinToken) {
    jobs.push(
      fetch(`https://api.pinterest.com/v5/ad_accounts/${encodeURIComponent(pinAccount)}/events`, {
        method: "POST",
        headers: { "content-type": "application/json", authorization: `Bearer ${pinToken}` },
        signal: AbortSignal.timeout(10_000),
        body: JSON.stringify({
          data: [
            {
              event_name: "checkout",
              action_source: "web",
              event_time: Math.floor(Date.now() / 1000),
              event_id: o.id,
              event_source_url: `${publicUrl()}/order/${o.id}`,
              user_data: {
                em: o.email ? [sha256(o.email)] : undefined,
                client_ip_address: c.ip,
                client_user_agent: c.userAgent,
                click_id: c.epik,
                // A stable, hashed customer id (their email) helps Pinterest match repeat buyers.
                external_id: o.email ? [sha256(o.email)] : undefined,
              },
              custom_data: { currency, value: String(value), order_id: o.id, num_items: 1 },
            },
          ],
        }),
      }).then(async (r) => {
        if (!r.ok) throw new Error(`Pinterest CAPI ${r.status}: ${(await r.text()).slice(0, 300)}`);
      }),
    );
  }

  for (const r of await Promise.allSettled(jobs)) if (r.status === "rejected") await logError("conversions", r.reason, { orderId: o.id });
}
