import type { Address, Order } from "./db";
import type { Design } from "../types";
import { prodigiItem, SHIPPING } from "../products";
import { publicUrl } from "./urls";
import { callbackToken } from "./printToken";

// Prodigi print-on-demand API (v4). Uses the sandbox unless PRODIGI_ENV=live.
// Without PRODIGI_API_KEY we log the order instead of sending it.
const BASE = process.env.PRODIGI_ENV === "live" ? "https://api.prodigi.com/v4.0" : "https://api.sandbox.prodigi.com/v4.0";

export const prodigiBase = BASE;

export async function submitPrintOrder(order: Order, design: Design, address: Address, assetUrl: string) {
  const item = prodigiItem(design);
  const shipping = SHIPPING.find((s) => s.id === order.shipping) ?? SHIPPING[0];
  const body = {
    merchantReference: order.id,
    shippingMethod: shipping.prodigiMethod,
    // Prodigi tells us here when the order moves on (e.g. shipped, with tracking).
    callbackUrl: `${publicUrl()}/api/webhooks/prodigi?o=${encodeURIComponent(order.id)}&t=${callbackToken(order.id)}`,
    recipient: {
      name: address.name,
      email: order.email,
      address: {
        line1: address.line1,
        line2: address.line2 ?? "",
        postalOrZipCode: address.postcode,
        countryCode: address.country,
        townOrCity: address.city,
      },
    },
    items: [
      {
        merchantReference: design.id,
        sku: item.sku,
        copies: 1,
        sizing: "fillPrintArea",
        attributes: item.attributes,
        assets: [{ printArea: "default", url: assetUrl }],
      },
    ],
  };

  const key = process.env.PRODIGI_API_KEY;
  if (!key) {
    console.log("[prodigi:mock] would submit order", JSON.stringify(body, null, 2));
    return { id: `mock_${order.id}` };
  }
  const r = await fetch(`${BASE}/Orders`, {
    method: "POST",
    headers: { "X-API-Key": key, "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const j = await r.json();
  if (!r.ok) throw new Error(`Prodigi ${r.status}: ${JSON.stringify(j)}`);
  return { id: j.order?.id as string };
}

export interface ProdigiShipment {
  carrier?: { name?: string; service?: string };
  tracking?: { number?: string; url?: string };
  dispatchDate?: string;
  status?: string;
}

/** Look an order up at Prodigi (we never trust a callback's body on its own). */
export async function getProdigiOrder(id: string) {
  const key = process.env.PRODIGI_API_KEY;
  if (!key) return null;
  const r = await fetch(`${BASE}/Orders/${encodeURIComponent(id)}`, { headers: { "X-API-Key": key } });
  if (!r.ok) throw new Error(`Prodigi ${r.status}`);
  const j = await r.json();
  return j.order as { id: string; status: { stage: string; details?: Record<string, string> }; shipments?: ProdigiShipment[] };
}
