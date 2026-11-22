import { NextResponse } from "next/server";
import { clientIp, limit, sameOrigin, tooMany } from "@/lib/server/rateLimit";
import { sendEmail } from "@/lib/server/email";
import { publicUrl } from "@/lib/server/urls";
import { logError } from "@/lib/server/log";
import { COMPANY } from "@/lib/company";

const esc = (s: string) => s.replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]!);

// A business enquiry from /partners: emailed to the sales inbox. Nothing is sent to the address given.
export async function POST(req: Request) {
  if (!sameOrigin(req, publicUrl())) return NextResponse.json({ error: "Bad request" }, { status: 400 });
  if (!limit("partner-enquiry", clientIp(req), 3, 60 * 60_000)) return tooMany("Thanks, we've got your message. Please wait a while before sending another.", 3600);
  const b = (await req.json().catch(() => ({}))) as Record<string, unknown>;
  const get = (k: string, max: number) => (typeof b[k] === "string" ? (b[k] as string).trim().slice(0, max) : "");
  if (get("company_url", 10)) return NextResponse.json({ ok: true }); // honeypot
  const e = { name: get("name", 80), email: get("email", 120), org: get("org", 120), website: get("website", 200), kind: get("kind", 20), message: get("message", 2000) };
  if (!e.name || !e.org || !/^\S+@\S+\.\S+$/.test(e.email)) return NextResponse.json({ error: "Please add your name, organisation and email." }, { status: 400 });
  const text = [`New partner enquiry`, "", `Name: ${e.name}`, `Email: ${e.email}`, `Organisation: ${e.org}`, `Website: ${e.website || "-"}`, `Type: ${e.kind}`, "", e.message || "(no message)", "", `Set them up: ${publicUrl()}/admin/partners`].join("\n");
  try {
    await sendEmail({
      to: process.env.SALES_EMAIL ?? process.env.ALERT_EMAIL ?? COMPANY.supportEmail,
      subject: `[Mapsie] Partner enquiry: ${e.org}`,
      text,
      html: `<pre style="font:14px/1.5 -apple-system,Segoe UI,sans-serif;white-space:pre-wrap">${esc(text)}</pre>`,
    });
  } catch (err) {
    await logError("partner.enquiry", err, { org: e.org });
    return NextResponse.json({ error: `Sorry, that didn't send. Please email ${COMPANY.helloEmail}.` }, { status: 502 });
  }
  return NextResponse.json({ ok: true });
}
