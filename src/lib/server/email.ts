import { createHmac, timingSafeEqual } from "node:crypto";
import { getDesign, getOrder, updateOrder, type DesignEmail, type Order } from "./db";
import { publicUrl } from "./urls";
import { COMPANY } from "../company";
import { describeOptions, getRegion, money, SHIPPING, type RegionId } from "../products";
import { normalizeDesign } from "../types";

// Order emails. Sent through whichever is configured:
//   RESEND_API_KEY                         Resend (recommended: built for this, free up to 3,000 a month)
//   SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS   any SMTP server, e.g. Google Workspace (smtp.gmail.com, 465, app password)
// With neither, emails are written to the log instead (development).
// EMAIL_FROM sets the sender, e.g. "Mapsie <orders@mapsie.shop>".

const FROM = () => process.env.EMAIL_FROM ?? `Mapsie <${COMPANY.helloEmail}>`;

export interface Email {
  to: string;
  subject: string;
  html: string;
  text: string;
}

export async function sendEmail(m: Email) {
  if (process.env.RESEND_API_KEY) {
    const r = await fetch("https://api.resend.com/emails", {
      method: "POST",
      headers: { Authorization: `Bearer ${process.env.RESEND_API_KEY}`, "Content-Type": "application/json" },
      body: JSON.stringify({ from: FROM(), to: [m.to], reply_to: COMPANY.supportEmail, subject: m.subject, html: m.html, text: m.text }),
    });
    if (!r.ok) throw new Error(`Resend ${r.status}: ${(await r.text()).slice(0, 300)}`);
    return;
  }
  if (process.env.SMTP_HOST) {
    const nodemailer = await import("nodemailer");
    const port = Number(process.env.SMTP_PORT ?? 465);
    const t = nodemailer.createTransport({
      host: process.env.SMTP_HOST,
      port,
      secure: port === 465,
      auth: process.env.SMTP_USER ? { user: process.env.SMTP_USER, pass: process.env.SMTP_PASS } : undefined,
    });
    await t.sendMail({ from: FROM(), replyTo: COMPANY.supportEmail, to: m.to, subject: m.subject, html: m.html, text: m.text });
    return;
  }
  console.log(JSON.stringify({ level: "info", scope: "email", message: `(not sent: no email provider) ${m.subject} -> ${m.to}`, text: m.text }));
}

/** Send an order email once only (callbacks and retries can repeat). Never throws. */
export async function sendOrderEmail(orderId: string, kind: "confirmed" | "shipped" | "cancelled" | "delivered") {
  try {
    const o = await getOrder(orderId);
    if (!o || o.emailsSent?.includes(kind)) return;
    const m = await build(o, kind);
    await sendEmail(m);
    await updateOrder(orderId, { emailsSent: [...((await getOrder(orderId))?.emailsSent ?? []), kind] });
  } catch (e) {
    const { logError } = await import("./log");
    await logError("email.order", e, { orderId, kind });
  }
}

/** Etsy buyers: the link to design their map ("invite"), and reminders. Each sent once. Never throws. */
export async function sendEtsyDesignEmail(o: Order, kind: "invite" | "remind1" | "remind2", force = false) {
  const key = `etsy-${kind}`;
  try {
    const fresh = await getOrder(o.id);
    if (!fresh || !fresh.email || fresh.status !== "awaiting_design" || (!force && fresh.emailsSent?.includes(key))) return;
    // A reminder only after the invite went out, and never two at once.
    if (kind === "remind1" && !fresh.emailsSent?.includes("etsy-invite")) return;
    if (kind === "remind2" && !fresh.emailsSent?.includes("etsy-remind1")) return;
    const { etsyDesignUrl } = await import("./etsy");
    const name = fresh.address?.name?.split(" ")[0];
    const { etsyPrintLabel } = await import("../etsyOptions");
    const what = fresh.print ? etsyPrintLabel(fresh.print) : "map print";
    const several = fresh.etsy && fresh.etsy.of > 1 ? ` (print ${fresh.etsy.unit} of ${fresh.etsy.of})` : "";
    const lines = {
      invite: [
        name ? `Hi ${name},` : "Hi,",
        `Thank you for your Etsy order! Now for the fun part: designing your map${several}.`,
        "Add the places you went, pick a style, add stickers and a title. It takes about five minutes, and you'll see exactly how it will look before it's printed.",
        `Your print: ${what}.`,
        `Etsy order ${fresh.etsy?.receiptId}`,
      ],
      remind1: [
        name ? `Hi ${name},` : "Hi,",
        `Your map${several} is waiting for you! We can't print it until you've designed it.`,
        `Your print: ${what}.`,
        `Etsy order ${fresh.etsy?.receiptId}`,
      ],
      remind2: [
        name ? `Hi ${name},` : "Hi,",
        `Just checking in: your map${several} still needs designing before we can print and send it.`,
        "Stuck or have a question? Reply to this email and we'll help.",
        `Etsy order ${fresh.etsy?.receiptId}`,
      ],
    }[kind];
    const subject = { invite: "Design your Mapsie map", remind1: "Your map is waiting to be designed", remind2: "Don't forget to design your map" }[kind];
    const heading = { invite: "Let's design your map 🗺️", remind1: "Your map is waiting", remind2: "Still there?" }[kind];
    await sendEmail(page(fresh.email, subject, heading, lines, { label: "Design my map", href: etsyDesignUrl(fresh.id) }));
    const sent = (await getOrder(o.id))?.emailsSent ?? [];
    if (!sent.includes(key)) await updateOrder(o.id, { emailsSent: [...sent, key] });
  } catch (e) {
    const { logError } = await import("./log");
    await logError("email.etsy", e, { orderId: o.id, kind });
  }
}

/**
 * A sale! Emailed to SALES_EMAIL (or the alert address) once per order, when it's paid
 * (or, for Etsy, when the buyer sends their design to print). Never throws.
 */
export async function sendSaleAlert(orderId: string) {
  try {
    const o = await getOrder(orderId);
    if (!o || o.emailsSent?.includes("sale-alert")) return;
    const raw = o.designId ? await getDesign(o.designId) : null;
    const d = raw ? normalizeDesign(raw) : null;
    const where = [o.address?.city, o.address?.country].filter(Boolean).join(", ");
    const what = d ? describeOptions(d) : "map print";
    const etsy = o.etsy ? ` (Etsy order ${o.etsy.receiptId})` : "";
    const to = process.env.SALES_EMAIL ?? process.env.ALERT_EMAIL ?? COMPANY.supportEmail;
    const lines = [
      `${money(o.region, o.total)}${etsy}: ${what}`,
      d ? `“${d.title}”, ${d.stops.length} stops` : "",
      where ? `Going to ${where}` : "",
      `Order ${o.id}`,
      `${publicUrl()}/admin`,
    ].filter(Boolean);
    await sendEmail({
      to,
      subject: `🎉 New Mapsie sale: ${money(o.region, o.total)}${etsy}`,
      text: lines.join("\n"),
      html: `<div style="font:15px/1.6 -apple-system,Segoe UI,sans-serif">${lines.map((l) => `<div>${esc(l)}</div>`).join("")}</div>`,
    });
    await updateOrder(orderId, { emailsSent: [...((await getOrder(orderId))?.emailsSent ?? []), "sale-alert"] });
  } catch (e) {
    console.error(JSON.stringify({ level: "error", scope: "email.sale", message: String(e) }));
  }
}

/** Tell us when something needs a human (failed renders, printer problems). Never throws. */
export async function alertAdmin(subject: string, text: string) {
  try {
    const to = process.env.ALERT_EMAIL ?? COMPANY.supportEmail;
    await sendEmail({ to, subject: `[Mapsie] ${subject}`, text, html: `<pre style="font:14px/1.5 monospace;white-space:pre-wrap">${esc(text)}</pre>` });
  } catch (e) {
    console.error(JSON.stringify({ level: "error", scope: "email.alert", message: String(e) }));
  }
}

// ---------------------------------------------------------------- templates
const esc = (s: string) => s.replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]!);

const TZ: Record<RegionId, { tz: string; label: string }> = {
  GB: { tz: "Europe/London", label: "UK time" },
  US: { tz: "America/New_York", label: "Eastern time" },
  AU: { tz: "Australia/Sydney", label: "Sydney time" },
};
const clock = (iso: string, region: RegionId) =>
  `${new Date(iso).toLocaleTimeString("en-GB", { hour: "2-digit", minute: "2-digit", timeZone: TZ[region].tz })} ${TZ[region].label}`;

async function build(o: Order, kind: "confirmed" | "shipped" | "cancelled" | "delivered"): Promise<Email> {
  const raw = await getDesign(o.designId);
  const d = raw ? normalizeDesign(raw) : null;
  const what = d ? `“${d.title}”, ${describeOptions(d)}` : "your map print";
  const link = `${publicUrl()}/order/${o.id}`;
  const name = o.address?.name?.split(" ")[0];
  const hi = name ? `Hi ${name},` : "Hi,";
  const total = money(o.region, o.total);
  const ship = SHIPPING.find((s) => s.id === o.shipping) ?? SHIPPING[0];

  if (kind === "delivered") {
    const lines = [
      hi,
      `Your map is ready: ${what}.`,
      "Download it from your order page. It's a full-resolution 300 dpi PNG, ready to print at any good print shop or online printer, at the size you chose or smaller.",
      `Order ${o.id}`,
    ];
    return page(o.email, "Your Mapsie map is ready to download", "Your map is ready ⬇️", lines, { label: "Download your map", href: link });
  }
  if (kind === "confirmed" && o.digital) {
    const lines = [
      hi,
      `Thank you! We're making the full-resolution file of ${what}.`,
      "We'll email your download link in a few minutes, as soon as the file is ready.",
      o.etsy ? `Etsy order ${o.etsy.receiptId}` : `Order ${o.id} · ${total}`,
    ].filter(Boolean);
    return page(o.email, `Your Mapsie order ${o.id}`, "Thank you! 🎉", lines, { label: "View your order", href: link });
  }
  if (kind === "confirmed" && o.source === "etsy") {
    const until = o.holdUntil ? clock(o.holdUntil, o.region) : null;
    const lines = [
      hi,
      `Thank you! Your design is in, and we're getting ${what} ready to print.`,
      until ? `Want to change something? You can reopen your design until ${until}, on your order page. After that it goes to print.` : "",
      `We'll email you when it's on its way, and Etsy will show the tracking too.`,
      `Etsy order ${o.etsy?.receiptId}`,
    ].filter(Boolean);
    return page(o.email, `Your map is going to print`, "Design received 🎉", lines, { label: "View your order", href: link });
  }
  if (kind === "confirmed") {
    const until = o.holdUntil ? clock(o.holdUntil, o.region) : null;
    const lines = [
      hi,
      `Thank you for your order! We're getting ${what} ready.`,
      until ? `Spotted a mistake? You can cancel for a full refund until ${until}, on your order page. After that it goes to print.` : "",
      `Delivery: ${ship.label.toLowerCase()} (${ship.detail}) to ${getRegion(o.region).label}. We'll email you when it's on its way.`,
      `Order ${o.id} · ${total}`,
    ].filter(Boolean);
    return page(o.email, `Your Mapsie order ${o.id}`, "Thank you! 🎉", lines, { label: "View your order", href: link });
  }
  if (kind === "shipped") {
    const s = o.shipments?.[0];
    const lines = [
      hi,
      `Good news: ${what} is on its way.`,
      s?.carrier || s?.trackingNumber ? `Courier: ${[s?.carrier, s?.trackingNumber].filter(Boolean).join(", tracking number ")}` : "",
      `Order ${o.id}`,
    ].filter(Boolean);
    return page(o.email, `Your Mapsie print is on its way`, "It's on its way 📦", lines, { label: s?.trackingUrl ? "Track your parcel" : "View your order", href: s?.trackingUrl ?? link });
  }
  const lines = [
    hi,
    `Your order ${o.id} has been cancelled and won't be printed.`,
    o.refunded ? `We've refunded ${total} to your card. Refunds usually arrive within 5 to 10 working days.` : "You haven't been charged for it.",
    "Your design is still there if you'd like to make changes and order again.",
  ];
  return page(o.email, `Your Mapsie order ${o.id} is cancelled`, "Order cancelled", lines, { label: "Back to Mapsie", href: `${publicUrl()}/create` });
}

function page(to: string, subject: string, heading: string, lines: string[], cta: { label: string; href: string }, unsubscribe?: string): Email {
  const footer =
    `Questions? Just reply to this email or write to ${COMPANY.supportEmail}.\n${COMPANY.brand} is run by ${COMPANY.legalName}, ${COMPANY.address}. Company no. ${COMPANY.number}.` +
    (unsubscribe ? `\nDon't want reminders? Unsubscribe: ${unsubscribe}` : "");
  const text = [heading, "", ...lines, "", `${cta.label}: ${cta.href}`, "", footer].join("\n");
  const html = `<!doctype html><html><body style="margin:0;background:#fbf6ee;font-family:-apple-system,Segoe UI,Helvetica,Arial,sans-serif;color:#1f2430">
<table width="100%" cellpadding="0" cellspacing="0"><tr><td align="center" style="padding:32px 16px">
<table width="100%" cellpadding="0" cellspacing="0" style="max-width:520px;background:#ffffff;border-radius:20px;padding:32px">
<tr><td style="font:800 26px Georgia,serif;padding-bottom:4px">Mapsie<span style="color:#ff6b4a">.</span></td></tr>
<tr><td style="font:800 22px Georgia,serif;padding:16px 0 8px">${esc(heading)}</td></tr>
${lines.map((l) => `<tr><td style="font-size:15px;line-height:1.55;padding:6px 0">${esc(l)}</td></tr>`).join("")}
<tr><td style="padding:22px 0 8px"><a href="${esc(cta.href)}" style="display:inline-block;background:#ff6b4a;color:#ffffff;text-decoration:none;font-weight:800;padding:12px 22px;border-radius:999px">${esc(cta.label)}</a></td></tr>
<tr><td style="font-size:12px;line-height:1.5;color:#8a8f99;padding-top:20px;white-space:pre-line">${esc(footer)}</td></tr>
</table></td></tr></table></body></html>`;
  return { to, subject, html, text };
}

// ---------------------------------------------------------------- "Email me my design"
const linkSecret = () => process.env.SESSION_SECRET ?? "dev-only-session-secret-change-me-0123456789";
export const unsubscribeToken = (email: string) => createHmac("sha256", linkSecret()).update(`unsub:${email.trim().toLowerCase()}`).digest("base64url").slice(0, 22);
export function unsubscribeTokenValid(email: string, token: string | null | undefined) {
  const want = Buffer.from(unsubscribeToken(email));
  const got = Buffer.from(token ?? "");
  return got.length === want.length && timingSafeEqual(got, want);
}
export const unsubscribeUrl = (email: string) => `${publicUrl()}/unsubscribe?e=${encodeURIComponent(email)}&t=${unsubscribeToken(email)}`;
const designLink = (designId: string) => `${publicUrl()}/create?d=${designId}`;

/** The link to their design, which they asked for. */
export async function sendDesignLinkEmail(row: DesignEmail, title: string) {
  const lines = [
    "Here's the link to the map you were designing. Open it on any device to pick up where you left off.",
    title ? `Your map: “${title}”.` : "",
    row.remind ? "As you asked, we'll send you one reminder tomorrow if you haven't ordered it yet." : "",
  ].filter(Boolean);
  await sendEmail(page(row.email, "Your Mapsie map design", "Your map is saved 🗺️", lines, { label: "Open my map", href: designLink(row.designId) }, row.remind ? unsubscribeUrl(row.email) : undefined));
}

/** The one reminder they opted in to, a day later. */
export async function sendDesignReminderEmail(row: DesignEmail, title: string) {
  const code = process.env.LAUNCH_CODE;
  const lines = [
    "Your map is still waiting for you, just as you left it.",
    title ? `Your map: “${title}”.` : "",
    "Every print is made to order, framed if you like, and delivered in a few days.",
    code ? `To say thanks for trying Mapsie, use code ${code} at checkout for ${process.env.LAUNCH_CODE_TEXT ?? "money off"}.` : "",
    "This is the only reminder we'll send.",
  ].filter(Boolean);
  await sendEmail(page(row.email, "Your map is still waiting", "Still dreaming about that trip?", lines, { label: "Finish my map", href: designLink(row.designId) }, unsubscribeUrl(row.email)));
}
