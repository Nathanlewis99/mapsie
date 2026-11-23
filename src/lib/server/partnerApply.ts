// Partner self sign-up: apply → confirm email → pending partner with automatic checks → approve or deny in admin.
import { SignJWT, jwtVerify } from "jose";
import { lookup } from "node:dns/promises";
import { isIP } from "node:net";
import { nanoid } from "nanoid";
import { getKv, putKv } from "./db";
import { alertAdmin, sendEmail } from "./email";
import { listPartners, getPartner, savePartner } from "./partners";
import { publicUrl } from "./urls";
import { assessApplication, baseDomain, hostOf, PARTNER_KINDS, slugify, type ApplicationFacts, type Partner, type PartnerKind } from "../partners";
import { REGIONS, type RegionId } from "../products";

export interface ApplicationInput {
  company: string;
  contactName: string;
  email: string;
  website: string;
  kind: PartnerKind;
  region?: RegionId;
  volume?: string;
  message: string;
}

const key = () => new TextEncoder().encode(`${process.env.SESSION_SECRET ?? (process.env.NODE_ENV === "production" ? "" : "dev-only-session-secret-change-me-0123456789")}:partner-apply`);
const esc = (s: string) => s.replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]!);

/** Check and tidy the form. Returns an error message or the cleaned application. */
export function cleanApplication(b: Record<string, unknown>): ApplicationInput | string {
  const t = (k: string, max: number) => (typeof b[k] === "string" ? (b[k] as string).trim().slice(0, max) : "");
  const a: ApplicationInput = {
    company: t("company", 80),
    contactName: t("contactName", 80),
    email: t("email", 120).toLowerCase(),
    website: t("website", 200),
    kind: (PARTNER_KINDS.some((k) => k.id === t("kind", 20)) ? t("kind", 20) : "travel") as PartnerKind,
    region: REGIONS.some((r) => r.id === t("region", 4)) ? (t("region", 4) as RegionId) : undefined,
    volume: t("volume", 120) || undefined,
    message: t("message", 1500),
  };
  if (!a.company || !a.contactName) return "Please add your name and your organisation's name.";
  if (!/^\S+@\S+\.\S+$/.test(a.email)) return "Please enter a valid email address.";
  if (!hostOf(a.website) || !hostOf(a.website).includes(".")) return "Please add your website, so we can check who you are.";
  return a;
}

/** Step 1: email a link to confirm the address. Nothing is stored until it's clicked. */
export async function startApplication(a: ApplicationInput) {
  if (!process.env.SESSION_SECRET && process.env.NODE_ENV === "production") throw new Error("SESSION_SECRET is not set");
  const token = await new SignJWT({ a, aud: "partner-apply" }).setProtectedHeader({ alg: "HS256" }).setJti(nanoid(16)).setIssuedAt().setExpirationTime("24h").sign(key());
  const link = `${publicUrl()}/api/partners/verify?t=${encodeURIComponent(token)}`;
  await sendEmail({
    to: a.email,
    subject: "Confirm your Mapsie partner application",
    text: `Hi ${a.contactName},\n\nThanks for applying to partner with Mapsie. Please confirm your email address to send your application:\n\n${link}\n\nThe link lasts 24 hours. If you didn't apply, you can ignore this email.\n\nMapsie`,
    html: `<div style="font:15px/1.55 -apple-system,Segoe UI,Helvetica,Arial,sans-serif;color:#1f2430;max-width:520px"><p style="font:800 24px Georgia,serif">Mapsie<span style="color:#ff6b4a">.</span></p>
<p>Hi ${esc(a.contactName)},</p><p>Thanks for applying to partner with Mapsie. Please confirm your email address to send your application for <b>${esc(a.company)}</b>.</p>
<p><a href="${link}" style="display:inline-block;background:#ff6b4a;color:#fff;text-decoration:none;font-weight:800;padding:12px 22px;border-radius:999px">Confirm and send</a></p>
<p style="color:#8a8f99;font-size:13px">The link lasts 24 hours. If you didn't apply, you can ignore this email.</p></div>`,
  });
}

/** Step 2: from the emailed link. Creates the pending partner, runs the checks and tells us. */
export async function finishApplication(token: string): Promise<{ ok: boolean; company?: string }> {
  let a: ApplicationInput;
  let jti: string;
  try {
    const { payload } = await jwtVerify(token, key(), { algorithms: ["HS256"], audience: "partner-apply" });
    a = payload.a as ApplicationInput;
    jti = String(payload.jti);
  } catch {
    return { ok: false };
  }
  if (await getKv(`papply:${jti}`)) return { ok: true, company: a.company }; // already done: same answer
  await putKv(`papply:${jti}`, { at: new Date().toISOString() });

  const all = await listPartners();
  const facts: ApplicationFacts = {
    website: await checkWebsite(a.website, a.company),
    duplicateOf: all.find((p) => p.status !== "denied" && ((p.logins ?? []).includes(a.email) || p.contactEmail === a.email || (p.application && baseDomain(hostOf(p.application.website)) === baseDomain(hostOf(a.website)))))?.name,
  };
  const { checks, recommendation } = assessApplication(a, facts);
  let id = slugify(a.company) || `partner-${nanoid(6).toLowerCase()}`;
  if (id.length < 3) id = `${id}-partner`;
  while (await getPartner(id)) id = `${id.slice(0, 34)}-${nanoid(4).toLowerCase().replace(/[^a-z0-9]/g, "x")}`;
  const p: Partner = {
    id,
    name: a.company,
    kind: a.kind,
    active: false,
    status: "pending",
    contactEmail: a.email,
    logins: [a.email],
    commissionPct: 10,
    region: a.region,
    trips: [],
    payouts: [],
    application: { contactName: a.contactName, email: a.email, website: a.website, message: a.message, volume: a.volume, appliedAt: new Date().toISOString(), checks, recommendation },
    createdAt: new Date().toISOString(),
  };
  await savePartner(p);
  await alertAdmin(
    `Partner application: ${a.company} (${recommendation})`,
    [`${a.contactName} <${a.email}> applied for ${a.company} (${PARTNER_KINDS.find((k) => k.id === a.kind)?.label}).`, `Website: ${a.website}`, a.volume ? `Volume: ${a.volume}` : "", "", a.message, "", ...checks.map((c) => `${c.ok === true ? "✓" : c.ok === false ? "✗" : "?"} ${c.label}`), "", `Suggested: ${recommendation}`, `Approve or deny: ${publicUrl()}/admin/partners?p=${id}`].filter((x) => x !== "").join("\n"),
  );
  return { ok: true, company: a.company };
}

// ------------------------------------------------------------ looking at their website, safely
// Only public web servers: never anything on a private or internal address.
function privateAddress(ip: string) {
  if (isIP(ip) === 4) {
    const [a, b] = ip.split(".").map(Number);
    return a === 10 || a === 127 || a === 0 || (a === 169 && b === 254) || (a === 172 && b >= 16 && b <= 31) || (a === 192 && b === 168) || (a === 100 && b >= 64 && b <= 127) || a >= 224;
  }
  const v = ip.toLowerCase();
  if (v.startsWith("::ffff:")) return privateAddress(v.slice(7));
  return v === "::1" || v === "::" || v.startsWith("fc") || v.startsWith("fd") || v.startsWith("fe8") || v.startsWith("fe9") || v.startsWith("fea") || v.startsWith("feb");
}
async function publicHost(url: URL) {
  if (!["http:", "https:"].includes(url.protocol) || (url.port && !["80", "443"].includes(url.port)) || url.username || url.password) return false;
  if (isIP(url.hostname)) return false;
  try {
    const addrs = await lookup(url.hostname, { all: true });
    return addrs.length > 0 && addrs.every((x) => !privateAddress(x.address));
  } catch {
    return false;
  }
}

export async function checkWebsite(website: string, company: string): Promise<ApplicationFacts["website"]> {
  let url: URL;
  try {
    url = new URL(/^https?:\/\//i.test(website) ? website : `https://${website}`);
  } catch {
    return { reachable: false };
  }
  try {
    for (let hop = 0; hop < 4; hop++) {
      if (!(await publicHost(url))) return { reachable: false };
      const r = await fetch(url, { redirect: "manual", signal: AbortSignal.timeout(8000), headers: { "user-agent": "Mozilla/5.0 (compatible; MapsiePartnerCheck/1.0)", accept: "text/html" } });
      if (r.status >= 300 && r.status < 400 && r.headers.get("location")) {
        url = new URL(r.headers.get("location")!, url);
        continue;
      }
      if (!r.ok) return { reachable: false };
      // Read at most ~300 KB of the page.
      const reader = r.body?.getReader();
      let html = "";
      const dec = new TextDecoder();
      while (reader && html.length < 300_000) {
        const { done, value } = await reader.read();
        if (done) break;
        html += dec.decode(value, { stream: true });
      }
      await reader?.cancel().catch(() => {});
      const title = /<title[^>]*>([^<]{1,200})/i.exec(html)?.[1]?.replace(/\s+/g, " ").trim();
      const words = (s: string) => s.toLowerCase().replace(/&amp;/g, "&").replace(/\b(ltd|limited|llc|inc|plc|the|co)\b\.?/g, "").replace(/[^a-z0-9]+/g, " ").trim();
      const text = words(html.replace(/<script[\s\S]*?<\/script>|<style[\s\S]*?<\/style>/gi, " ").replace(/<[^>]+>/g, " "));
      const name = words(company);
      return { reachable: true, title, nameOnSite: !!name && text.includes(name), finalHost: url.hostname.replace(/^www\./, "") };
    }
    return { reachable: false };
  } catch {
    return { reachable: false };
  }
}

// ------------------------------------------------------------ decisions
export async function decideApplication(id: string, decision: "approved" | "denied", note?: string) {
  const p = await getPartner(id);
  if (!p?.application) throw new Error("No application for that partner");
  const application = { ...p.application, decision, decidedAt: new Date().toISOString(), ...(note ? { decisionNote: note.slice(0, 500) } : {}) };
  if (decision === "approved") {
    await savePartner({ ...p, status: "approved", active: true, application });
    await sendEmail({
      to: p.application.email,
      subject: "Welcome to Mapsie: your partner account is ready",
      text: `Hi ${p.application.contactName},\n\nGood news: ${p.name} is now a Mapsie partner.\n\nSign in to your dashboard with this email address: ${publicUrl()}/partner\nYour page for customers: ${publicUrl()}/with/${p.id}\n\nIn the dashboard you'll find your links, your sales and commission, and where to add your billing and payment details. Send us your routes (a list of stops is perfect) and we'll set them up on your page.\n\nAny questions, just reply.\n\nMapsie`,
      html: `<div style="font:15px/1.55 -apple-system,Segoe UI,Helvetica,Arial,sans-serif;color:#1f2430;max-width:520px"><p style="font:800 24px Georgia,serif">Mapsie<span style="color:#ff6b4a">.</span></p>
<p>Hi ${esc(p.application.contactName)},</p><p>Good news: <b>${esc(p.name)}</b> is now a Mapsie partner.</p>
<p><a href="${publicUrl()}/partner" style="display:inline-block;background:#ff6b4a;color:#fff;text-decoration:none;font-weight:800;padding:12px 22px;border-radius:999px">Open your dashboard</a></p>
<p>Sign in with this email address. You'll find your links, sales and commission, and where to add billing and payment details. Your page for customers is <a href="${publicUrl()}/with/${p.id}">${publicUrl().replace(/^https?:\/\//, "")}/with/${p.id}</a>.</p>
<p>Send us your routes (a list of stops is perfect) and we'll set them up on your page. Any questions, just reply.</p></div>`,
    });
  } else {
    await savePartner({ ...p, status: "denied", active: false, application });
    await sendEmail({
      to: p.application.email,
      subject: "Your Mapsie partner application",
      text: `Hi ${p.application.contactName},\n\nThank you for applying to partner with Mapsie. We're not able to set up a partner account for ${p.name} at the moment.${note ? `\n\n${note}` : ""}\n\nIf you think we've got this wrong, just reply to this email.\n\nMapsie`,
      html: `<div style="font:15px/1.55 -apple-system,Segoe UI,Helvetica,Arial,sans-serif;color:#1f2430;max-width:520px"><p>Hi ${esc(p.application.contactName)},</p><p>Thank you for applying to partner with Mapsie. We're not able to set up a partner account for ${esc(p.name)} at the moment.</p>${note ? `<p>${esc(note)}</p>` : ""}<p>If you think we've got this wrong, just reply to this email.</p><p>Mapsie</p></div>`,
    });
  }
}
