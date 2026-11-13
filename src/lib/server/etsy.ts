import { createHash, createHmac, randomBytes, timingSafeEqual } from "node:crypto";
import { getKv, getOrder, listOrdersByStatus, putKv, saveOrder, updateOrder, type Address, type Order } from "./db";
import { FRAMES, PRODUCTS, type RegionId } from "../products";
import { publicUrl } from "./urls";
import { logError } from "./log";
import { alertAdmin, sendEtsyDesignEmail } from "./email";

// Etsy: customers buy a "custom travel map" listing on Etsy, then design the map on
// Mapsie. Every few minutes the worker fetches new paid Etsy orders and makes a
// Mapsie order for each print, waiting for its design. When the buyer presses
// "Send to print" it goes through the same render and Prodigi steps as any order,
// and the tracking number is sent back to Etsy when it ships.
//
// Set on Render (both services):  ETSY_API_KEY (the app's keystring) and ETSY_SHARED_SECRET.
// Then connect the shop once from /admin/etsy.

const API = "https://api.etsy.com/v3/application";
const SCOPES = "shops_r transactions_r transactions_w listings_r";
export const etsyConfigured = () => !!(process.env.ETSY_API_KEY && process.env.ETSY_SHARED_SECRET);
export const etsyRedirectUri = () => `${publicUrl()}/api/etsy/callback`;
const apiKeyHeader = () => `${process.env.ETSY_API_KEY}:${process.env.ETSY_SHARED_SECRET}`;

interface EtsyAuth {
  access: string;
  refresh: string;
  expiresAt: number; // epoch ms
  userId: string;
  shopId: string;
  shopName: string;
  connectedAt: string;
}
const AUTH_KEY = "etsy:auth";
export const etsyConnection = async () => (await getKv<EtsyAuth>(AUTH_KEY))?.value ?? null;
export const disconnectEtsy = () => putKv(AUTH_KEY, null);

// ---------------------------------------------------------------- connecting the shop (OAuth with PKCE)
export function startConnect() {
  const verifier = randomBytes(32).toString("base64url");
  const state = randomBytes(16).toString("base64url");
  const challenge = createHash("sha256").update(verifier).digest("base64url");
  const url = new URL("https://www.etsy.com/oauth/connect");
  url.search = new URLSearchParams({
    response_type: "code",
    client_id: process.env.ETSY_API_KEY!,
    redirect_uri: etsyRedirectUri(),
    scope: SCOPES,
    state,
    code_challenge: challenge,
    code_challenge_method: "S256",
  }).toString();
  return { url: url.toString(), state, verifier };
}

async function tokenRequest(body: Record<string, string>) {
  const r = await fetch("https://api.etsy.com/v3/public/oauth/token", {
    method: "POST",
    headers: { "content-type": "application/x-www-form-urlencoded", "x-api-key": apiKeyHeader() },
    body: new URLSearchParams({ client_id: process.env.ETSY_API_KEY!, ...body }),
  });
  if (!r.ok) throw new Error(`Etsy token ${r.status}: ${(await r.text()).slice(0, 300)}`);
  return (await r.json()) as { access_token: string; refresh_token: string; expires_in: number };
}

export async function finishConnect(code: string, verifier: string) {
  const t = await tokenRequest({ grant_type: "authorization_code", code, code_verifier: verifier, redirect_uri: etsyRedirectUri() });
  const userId = t.access_token.split(".")[0];
  const auth: EtsyAuth = {
    access: t.access_token, refresh: t.refresh_token, expiresAt: Date.now() + (t.expires_in - 60) * 1000,
    userId, shopId: "", shopName: "", connectedAt: new Date().toISOString(),
  };
  await putKv(AUTH_KEY, auth);
  const me = await etsy<{ user_id: number; shop_id?: number }>("GET", "/users/me");
  if (!me.shop_id) throw new Error("This Etsy account doesn't have a shop.");
  const shop = await etsy<{ shop_name: string }>("GET", `/shops/${me.shop_id}`);
  await putKv(AUTH_KEY, { ...auth, shopId: String(me.shop_id), shopName: shop.shop_name });
  return shop.shop_name;
}

async function accessToken(): Promise<string> {
  const a = await etsyConnection();
  if (!a) throw new Error("Etsy isn't connected");
  if (Date.now() < a.expiresAt) return a.access;
  const t = await tokenRequest({ grant_type: "refresh_token", refresh_token: a.refresh });
  await putKv(AUTH_KEY, { ...a, access: t.access_token, refresh: t.refresh_token, expiresAt: Date.now() + (t.expires_in - 60) * 1000 });
  return t.access_token;
}

async function etsy<T>(method: "GET" | "POST", path: string, body?: unknown): Promise<T> {
  const r = await fetch(`${API}${path}`, {
    method,
    headers: {
      "x-api-key": apiKeyHeader(),
      authorization: `Bearer ${await accessToken()}`,
      ...(body ? { "content-type": "application/json" } : {}),
    },
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!r.ok) throw new Error(`Etsy ${method} ${path} ${r.status}: ${(await r.text()).slice(0, 300)}`);
  return r.json() as Promise<T>;
}

// ---------------------------------------------------------------- what was bought
/** SKUs to give each listing variation: MAPSIE-<size>-<frame>, e.g. MAPSIE-A3-NONE or MAPSIE-A3-BLACK. */
export const etsySku = (productId: string, frame: string) => `MAPSIE-${productId.toUpperCase()}-${frame.toUpperCase()}`;
export const ALL_SKUS = PRODUCTS.flatMap((p) => FRAMES.map((f) => ({ sku: etsySku(p.id, f.id), product: p.label, frame: f.label })));

type Variation = { formatted_name?: string; formatted_value?: string };
/**
 * Size and frame from the SKU, or failing that from the variation names the buyer chose
 * ("Size: A3", "Frame: Black"). Returns matched=false if we had to guess.
 */
export function matchPrint(sku: string | null | undefined, variations: Variation[] = []) {
  const m = /^MAPSIE-([A-Z0-9]+)-([A-Z]+)$/i.exec((sku ?? "").trim());
  if (m) {
    const p = PRODUCTS.find((x) => x.id.toUpperCase() === m[1].toUpperCase());
    const f = FRAMES.find((x) => x.id.toUpperCase() === m[2].toUpperCase());
    if (p && f) return { productId: p.id, frame: f.id, matched: true };
  }
  const text = variations.map((v) => `${v.formatted_name ?? ""}: ${v.formatted_value ?? ""}`).join(" | ").toLowerCase();
  const size = PRODUCTS.find((p) =>
    p.id === "50x70" ? /50\s*[x×]\s*70/.test(text) : new RegExp(`\\b${p.id}\\b`).test(text),
  );
  const frame =
    /unframed|no frame|print only|poster only/.test(text) ? FRAMES[0]
    : FRAMES.slice(1).find((f) => text.includes(f.label.toLowerCase()) || text.includes(f.id) || (f.id === "oak" && /oak|natural|wood/.test(text)));
  return { productId: size?.id ?? "a3", frame: frame?.id ?? "none", matched: !!size && !!frame };
}

const REGION_FOR: Record<string, RegionId> = { GB: "GB", US: "US", AU: "AU" };

// ---------------------------------------------------------------- buyer links
const secret = () => process.env.SESSION_SECRET ?? "dev-only-session-secret-change-me-0123456789";
/** The secret part of an Etsy buyer's design link. */
export const etsyToken = (orderId: string) => createHmac("sha256", secret()).update(`etsy:${orderId}`).digest("base64url").slice(0, 24);
export function etsyTokenValid(orderId: string, token: string | null | undefined) {
  if (!token) return false;
  const a = Buffer.from(etsyToken(orderId));
  const b = Buffer.from(token);
  return a.length === b.length && timingSafeEqual(a, b);
}
export const etsyDesignUrl = (orderId: string) => `${publicUrl()}/etsy/${orderId}?k=${etsyToken(orderId)}`;
/** Postcodes compared without spaces or case: "SW1A 1AA" = "sw1a1aa". */
export const samePostcode = (a: string, b: string) => a.replace(/\s+/g, "").toLowerCase() === b.replace(/\s+/g, "").toLowerCase();

// ---------------------------------------------------------------- syncing orders
type Money = { amount: number; divisor: number; currency_code: string };
export interface Receipt {
  receipt_id: number; buyer_email?: string | null; name: string; first_line: string; second_line?: string | null; city: string;
  state?: string | null; zip: string; country_iso: string; is_paid: boolean; created_timestamp: number; grandtotal?: Money;
  transactions: { transaction_id: number; title?: string; quantity: number; sku?: string | null; variations?: Variation[]; price?: Money; shipping_upgrade?: string | null }[];
}

/** Fetch paid Etsy orders since the last check and make a Mapsie order for each print. */
export async function syncEtsyOrders(): Promise<number> {
  if (!etsyConfigured()) return 0;
  const conn = await etsyConnection();
  if (!conn?.shopId) return 0;
  const since = (await getKv<number>("etsy:synced"))?.value ?? Math.floor(Date.now() / 1000) - 7 * 24 * 3600;
  const startedAt = Math.floor(Date.now() / 1000);
  let made = 0;
  for (let offset = 0; offset < 1000; offset += 100) {
    const page = await etsy<{ count: number; results: Receipt[] }>(
      "GET",
      `/shops/${conn.shopId}/receipts?was_paid=true&min_created=${since - 3600}&limit=100&offset=${offset}&sort_on=created&sort_order=asc`,
    );
    for (const r of page.results) made += await importReceipt(r);
    if (page.results.length < 100) break;
  }
  await putKv("etsy:synced", startedAt);
  return made;
}

export async function importReceipt(r: Receipt): Promise<number> {
  const address: Address = {
    name: r.name, line1: r.first_line, line2: r.second_line || undefined, city: r.city,
    state: r.state || undefined, postcode: r.zip, country: (r.country_iso || "GB").toUpperCase(),
  };
  let made = 0;
  for (const t of r.transactions) {
    for (let unit = 1; unit <= Math.max(1, t.quantity); unit++) {
      // The same Etsy print always gets the same id (so it's imported once), but the id
      // can't be guessed from Etsy's sequential order numbers.
      const id = `ord_etsy_${createHmac("sha256", secret()).update(`etsy-order:${r.receipt_id}:${t.transaction_id}:${unit}`).digest("base64url").replace(/[-_]/g, "").slice(0, 14)}`;
      if (await getOrder(id)) continue; // already imported
      const print = matchPrint(t.sku, t.variations);
      const price = t.price ? t.price.amount / t.price.divisor : 0;
      const order: Order = {
        id,
        designId: "",
        email: r.buyer_email ?? "",
        shipping: /express|priority|next.?day/i.test(t.shipping_upgrade ?? "") ? "express" : "standard",
        region: REGION_FOR[address.country] ?? "GB",
        currency: (t.price?.currency_code ?? r.grandtotal?.currency_code ?? "GBP").toLowerCase(),
        total: price,
        status: "awaiting_design",
        address,
        source: "etsy",
        print: { productId: print.productId, frame: print.frame },
        etsy: {
          receiptId: String(r.receipt_id), transactionId: String(t.transaction_id), unit, of: t.quantity,
          title: t.title?.slice(0, 120), matched: print.matched,
          choices: (t.variations ?? []).map((v) => `${v.formatted_name}: ${v.formatted_value}`).join(", ").slice(0, 300),
        },
        createdAt: new Date(r.created_timestamp * 1000).toISOString(),
      };
      await saveOrder(order);
      made++;
      if (!print.matched)
        await alertAdmin(
          `Etsy order ${r.receipt_id}: check the size and frame`,
          `We couldn't tell the size and frame of Etsy order ${r.receipt_id} from its SKU (${t.sku || "none"}) or options (${order.etsy!.choices || "none"}), so it's set to ${print.productId.toUpperCase()}, ${print.frame}. Fix the listing's SKUs (see /admin/etsy) and check this order before the buyer designs it.`,
        );
      if (order.email) await sendEtsyDesignEmail(order, "invite");
    }
  }
  return made;
}

/** Remind buyers who haven't designed their map yet: after 3 days and again after 7. */
export async function remindEtsyBuyers() {
  const day = 24 * 3600_000;
  for (const o of await listOrdersByStatus("awaiting_design")) {
    if (o.source !== "etsy" || !o.email) continue;
    const age = Date.now() - new Date(o.createdAt).getTime();
    if (age > 7 * day) await sendEtsyDesignEmail(o, "remind2");
    else if (age > 3 * day) await sendEtsyDesignEmail(o, "remind1");
  }
}

/** Mark the Etsy order dispatched, with tracking, once Prodigi has shipped it. */
export async function sendEtsyTracking(orderId: string) {
  const o = await getOrder(orderId);
  if (!o?.etsy || o.etsy.trackingSent) return;
  const s = o.shipments?.find((x) => x.trackingNumber);
  if (!s?.trackingNumber) return;
  const conn = await etsyConnection();
  if (!conn?.shopId) return;
  try {
    await etsy("POST", `/shops/${conn.shopId}/receipts/${o.etsy.receiptId}/tracking`, {
      tracking_code: s.trackingNumber,
      carrier_name: s.carrier || "other",
      send_bcc: false,
    });
    await updateOrder(orderId, { etsy: { ...o.etsy, trackingSent: true } });
  } catch (e) {
    await logError("etsy.tracking", e, { orderId });
  }
}

/** One worker job: new orders, reminders. Never throws. */
export async function etsyJob() {
  try {
    await syncEtsyOrders();
    await remindEtsyBuyers();
  } catch (e) {
    await logError("etsy.sync", e);
  }
}
