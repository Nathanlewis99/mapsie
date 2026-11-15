import { createHmac, randomBytes, timingSafeEqual } from "node:crypto";
import { nanoid } from "nanoid";
import Stripe from "stripe";
import {
  getDesign, getOrder, getTicket, listOrdersByEtsyReceipt, saveOrder, saveSupportFile, saveTicket, updateOrder,
  type Order, type Ticket, type TicketMessage, type TicketStatus,
} from "./db";
import { alertAdmin, sendEmail } from "./email";
import { processPaidOrders, ROLE } from "./fulfil";
import { logError } from "./log";
import { publicUrl } from "./urls";
import { COMPANY } from "../company";
import { describeOptions, money, SHIPPING } from "../products";
import { normalizeDesign } from "../types";
import { MAX_PHOTOS, PHOTO_MAX_CHARS, reasonFor, type SupportReason } from "../support";

// ---------------------------------------------------------------- ids and links
const ALPHABET = "23456789ABCDEFGHJKMNPQRSTUVWXYZ"; // no 0/O, 1/I/L: easy to read out
export const newTicketId = () => "MS-" + Array.from(randomBytes(6), (b) => ALPHABET[b % ALPHABET.length]).join("");
const secret = () => process.env.SESSION_SECRET ?? "dev-only-session-secret-change-me-0123456789";
export const ticketToken = (id: string) => createHmac("sha256", secret()).update(`ticket:${id}`).digest("base64url").slice(0, 24);
export function ticketTokenValid(id: string, token: string | null | undefined) {
  if (!token) return false;
  const a = Buffer.from(ticketToken(id));
  const b = Buffer.from(token);
  return a.length === b.length && timingSafeEqual(a, b);
}
export const ticketUrl = (id: string) => `${publicUrl()}/support/t/${id}?k=${ticketToken(id)}`;

// ---------------------------------------------------------------- finding the order
const sameEmail = (a: string, b: string) => !!a && !!b && a.trim().toLowerCase() === b.trim().toLowerCase();

/**
 * The order a customer means, if the number they typed (a Mapsie order number or an Etsy
 * order number) belongs to an order placed with the email they gave. Otherwise null, and we
 * show them nothing about it.
 */
export async function findOrderFor(ref: string, email: string): Promise<Order | null> {
  const r = ref.trim();
  if (/^ord_[A-Za-z0-9_-]{6,40}$/.test(r)) {
    const o = await getOrder(r);
    return o && sameEmail(o.email, email) ? o : null;
  }
  const digits = r.replace(/[^\d]/g, "");
  if (digits.length >= 6) {
    const etsy = await listOrdersByEtsyReceipt(digits);
    return etsy.find((o) => sameEmail(o.email, email)) ?? null;
  }
  return null;
}

/** What we can safely show a verified customer about their order on the form. */
export async function orderSummary(o: Order) {
  const raw = o.designId ? await getDesign(o.designId) : null;
  const d = raw ? normalizeDesign(raw) : null;
  const ship = SHIPPING.find((s) => s.id === o.shipping) ?? SHIPPING[0];
  return {
    id: o.id,
    status: o.status,
    title: d?.title ?? null,
    what: d ? describeOptions(d) : null,
    placed: o.paidAt ?? o.createdAt,
    delivery: `${ship.label} (${ship.detail})`,
    shipments: o.shipments ?? [],
    holdUntil: o.holdUntil ?? null,
    etsy: !!o.etsy,
  };
}

// ---------------------------------------------------------------- photos
/** Store uploaded photos (data URLs from the browser, already shrunk). Returns their ids. */
async function storePhotos(ticketId: string, photos: unknown): Promise<string[]> {
  if (!Array.isArray(photos)) return [];
  const ids: string[] = [];
  for (const p of photos.slice(0, MAX_PHOTOS)) {
    const m = typeof p === "string" ? /^data:(image\/(?:jpeg|png|webp));base64,([A-Za-z0-9+/=]+)$/.exec(p) : null;
    if (!m || m[2].length > PHOTO_MAX_CHARS) continue;
    const id = `f_${nanoid(16)}`;
    await saveSupportFile({ id, ticketId, mime: m[1], data: m[2] });
    ids.push(id);
  }
  return ids;
}

// ---------------------------------------------------------------- tickets
export async function createTicket(p: { email: string; name?: string; orderRef: string; reason: SupportReason; message: string; photos?: unknown }) {
  const order = p.orderRef ? await findOrderFor(p.orderRef, p.email) : null;
  const id = newTicketId();
  const at = new Date().toISOString();
  const files = await storePhotos(id, p.photos);
  const t: Ticket = {
    id,
    email: p.email.trim(),
    name: p.name?.trim() || order?.address?.name || undefined,
    orderRef: p.orderRef.trim(),
    orderId: order?.id,
    reason: p.reason,
    status: "open",
    messages: [{ from: "customer", text: p.message.trim(), at, files }],
    createdAt: at,
    updatedAt: at,
  };
  await saveTicket(t);
  await emailCustomer(t, "received");
  await alertAdmin(
    `Support ${t.id}: ${reasonFor(t.reason).label}`,
    [
      `From: ${t.name ? `${t.name} <${t.email}>` : t.email}`,
      `Order: ${t.orderId ?? `${t.orderRef || "none given"} (not matched to this email)`}`,
      `Photos: ${files.length}`,
      "",
      t.messages[0].text,
      "",
      `Open it: ${publicUrl()}/admin/support/${t.id}`,
    ].join("\n"),
  );
  return t;
}

/** The customer adds to their ticket from its page. */
export async function customerReply(id: string, text: string, photos?: unknown) {
  const t = await getTicket(id);
  if (!t) throw new Error("not found");
  const files = await storePhotos(id, photos);
  const at = new Date().toISOString();
  const next: Ticket = { ...t, status: "open", messages: [...t.messages, { from: "customer", text: text.trim(), at, files }], updatedAt: at };
  await saveTicket(next);
  await alertAdmin(`Support ${id}: new reply from the customer`, `${text.trim()}\n\nPhotos: ${files.length}\n\nOpen it: ${publicUrl()}/admin/support/${id}`);
  return next;
}

/** We reply (from the admin page): saved on the ticket and emailed to the customer. */
export async function staffReply(id: string, text: string, status: TicketStatus) {
  const t = await getTicket(id);
  if (!t) throw new Error("not found");
  const at = new Date().toISOString();
  const msg: TicketMessage = { from: "mapsie", text: text.trim(), at };
  const next: Ticket = { ...t, status, messages: text.trim() ? [...t.messages, msg] : t.messages, updatedAt: at };
  await saveTicket(next);
  if (text.trim()) await emailCustomer(next, "reply");
  return next;
}

export async function setTicketStatus(id: string, status: TicketStatus) {
  const t = await getTicket(id);
  if (!t) throw new Error("not found");
  await saveTicket({ ...t, status, updatedAt: new Date().toISOString() });
}

async function noteAction(id: string, action: string) {
  const t = await getTicket(id);
  if (!t) return;
  await saveTicket({ ...t, actions: [...(t.actions ?? []), `${new Date().toISOString().slice(0, 10)} ${action}`], updatedAt: new Date().toISOString() });
}

// ---------------------------------------------------------------- putting it right
/**
 * A free reprint: a new order with the same design and address, sent straight to the
 * normal render and print queue (no payment, no cancellation hold).
 */
export async function reprint(ticketId: string) {
  const t = await getTicket(ticketId);
  const o = t?.orderId ? await getOrder(t.orderId) : null;
  if (!t || !o || !o.address || !o.designId) throw new Error("This ticket isn't linked to an order with a design and address.");
  const now = new Date().toISOString();
  const copy: Order = {
    id: `ord_${nanoid(10)}`,
    designId: o.designId,
    userId: o.userId,
    email: o.email,
    shipping: o.shipping,
    region: o.region,
    currency: o.currency,
    total: 0,
    status: "paid",
    address: o.address,
    paidAt: now,
    holdUntil: now,
    source: o.source,
    reprintOf: o.id,
    supportTicket: t.id,
    emailsSent: ["confirmed"], // the support reply tells them; no "thanks for your order" email
    createdAt: now,
  };
  await saveOrder(copy);
  await noteAction(ticketId, `Free reprint ${copy.id} (of ${o.id})`);
  if (ROLE !== "web") void processPaidOrders();
  return copy.id;
}

/** Full refund through Stripe (Etsy orders are refunded on Etsy instead). */
export async function refund(ticketId: string) {
  const t = await getTicket(ticketId);
  const o = t?.orderId ? await getOrder(t.orderId) : null;
  if (!t || !o) throw new Error("This ticket isn't linked to an order.");
  if (o.refunded) throw new Error("This order has already been refunded.");
  if (o.etsy) throw new Error("Etsy orders are refunded on Etsy: open the order in Shop Manager and choose Refund.");
  if (!process.env.STRIPE_SECRET_KEY || !o.stripePaymentIntent) throw new Error("No Stripe payment found for this order (was it a test order?).");
  try {
    await new Stripe(process.env.STRIPE_SECRET_KEY).refunds.create({ payment_intent: o.stripePaymentIntent });
  } catch (e) {
    await logError("support.refund", e, { orderId: o.id, ticketId });
    throw new Error(`Stripe didn't accept the refund: ${String(e).slice(0, 200)}`);
  }
  await updateOrder(o.id, { refunded: true });
  await noteAction(ticketId, `Refunded ${money(o.region, o.total)} (${o.id})`);
}

// ---------------------------------------------------------------- emails
const esc = (s: string) => s.replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]!);

async function emailCustomer(t: Ticket, kind: "received" | "reply") {
  try {
    const hi = t.name ? `Hi ${t.name.split(" ")[0]},` : "Hi,";
    const last = t.messages[t.messages.length - 1];
    const lines =
      kind === "received"
        ? [hi, `Thanks for getting in touch. We've got your message about “${reasonFor(t.reason).label.toLowerCase()}” and we'll reply within one working day.`, `Your reference is ${t.id}. You can add photos or more details on your support page.`]
        : [hi, "We've replied to your message:", last.text, "You can reply on your support page, or just reply to this email."];
    const link = ticketUrl(t.id);
    const subject = kind === "received" ? `We've got your message (${t.id})` : `Re: your Mapsie support request (${t.id})`;
    await sendEmail({
      to: t.email,
      subject,
      text: `${lines.join("\n\n")}\n\nYour support page: ${link}\n\nMapsie · ${COMPANY.supportEmail}`,
      html: `<div style="font:15px/1.6 -apple-system,Segoe UI,sans-serif;color:#1f2430;max-width:560px">${lines
        .map((l) => `<p style="white-space:pre-wrap">${esc(l)}</p>`)
        .join("")}<p><a href="${link}" style="display:inline-block;background:#ff6b4a;color:#fff;padding:10px 20px;border-radius:999px;text-decoration:none;font-weight:700">Your support page</a></p><p style="color:#888;font-size:13px">Mapsie · ${COMPANY.supportEmail}</p></div>`,
    });
  } catch (e) {
    await logError("support.email", e, { ticketId: t.id, kind });
  }
}
