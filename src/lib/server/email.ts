import { getDesign, getOrder, updateOrder, type Order } from "./db";
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
export async function sendOrderEmail(orderId: string, kind: "confirmed" | "shipped" | "cancelled") {
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

async function build(o: Order, kind: "confirmed" | "shipped" | "cancelled"): Promise<Email> {
  const raw = await getDesign(o.designId);
  const d = raw ? normalizeDesign(raw) : null;
  const what = d ? `“${d.title}”, ${describeOptions(d)}` : "your map print";
  const link = `${publicUrl()}/order/${o.id}`;
  const name = o.address?.name?.split(" ")[0];
  const hi = name ? `Hi ${name},` : "Hi,";
  const total = money(o.region, o.total);
  const ship = SHIPPING.find((s) => s.id === o.shipping) ?? SHIPPING[0];

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

function page(to: string, subject: string, heading: string, lines: string[], cta: { label: string; href: string }): Email {
  const footer = `Questions? Just reply to this email or write to ${COMPANY.supportEmail}.\n${COMPANY.brand} is run by ${COMPANY.legalName}, ${COMPANY.address}. Company no. ${COMPANY.number}.`;
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
