// Partner dashboard sign-in: no passwords. A partner types their email at /partner/signin; if it's
// one of a partner's login addresses we email a one-time link (valid 30 minutes), which sets a
// partner session cookie for 30 days. Separate from customer and admin sessions.
import { SignJWT, jwtVerify } from "jose";
import { cookies } from "next/headers";
import { createCipheriv, createDecipheriv, createHash, randomBytes } from "node:crypto";
import { nanoid } from "nanoid";
import { getKv, putKv } from "./db";
import { listPartners, getPartner } from "./partners";
import { sendEmail } from "./email";
import { publicUrl } from "./urls";
import type { Partner, PayoutMethod } from "../partners";

export const PARTNER_COOKIE = "mapsie_partner";
const DAYS = 30;
const secret = () => {
  const s = process.env.SESSION_SECRET;
  if (!s && process.env.NODE_ENV === "production") throw new Error("SESSION_SECRET is not set");
  return s ?? "dev-only-session-secret-change-me-0123456789";
};
const jwtKey = () => new TextEncoder().encode(`${secret()}:partner`);

const norm = (e: string) => e.trim().toLowerCase();
export async function partnersForEmail(email: string): Promise<Partner[]> {
  const e = norm(email);
  return (await listPartners()).filter((p) => p.active && (p.logins ?? []).some((l) => norm(l) === e));
}

/** Email a sign-in link if the address belongs to a partner. Says nothing either way (no account fishing). */
export async function sendPartnerSignInLink(email: string) {
  const list = await partnersForEmail(email);
  if (!list.length) return;
  const token = await new SignJWT({ email: norm(email), aud: "partner-link" })
    .setProtectedHeader({ alg: "HS256" })
    .setJti(nanoid(16))
    .setIssuedAt()
    .setExpirationTime("30m")
    .sign(jwtKey());
  const link = `${publicUrl()}/api/partner/auth?t=${encodeURIComponent(token)}`;
  const names = list.map((p) => p.name).join(", ");
  await sendEmail({
    to: email.trim(),
    subject: "Sign in to your Mapsie partner dashboard",
    text: `Hi,\n\nHere's your link to sign in to the Mapsie partner dashboard for ${names}:\n\n${link}\n\nIt works once and expires in 30 minutes. If you didn't ask for it, you can ignore this email.\n\nMapsie`,
    html: `<div style="font:15px/1.55 -apple-system,Segoe UI,Helvetica,Arial,sans-serif;color:#1f2430;max-width:520px">
<p style="font:800 24px Georgia,serif">Mapsie<span style="color:#ff6b4a">.</span></p>
<p>Here's your link to sign in to the Mapsie partner dashboard for <b>${names.replace(/[<>&"]/g, "")}</b>.</p>
<p><a href="${link}" style="display:inline-block;background:#ff6b4a;color:#fff;text-decoration:none;font-weight:800;padding:12px 22px;border-radius:999px">Sign in</a></p>
<p style="color:#8a8f99;font-size:13px">It works once and expires in 30 minutes. If you didn't ask for it, you can ignore this email.</p></div>`,
  });
}

/** From the emailed link: check it, use it up, and start a partner session. Returns false if it's no good. */
export async function finishPartnerSignIn(token: string): Promise<boolean> {
  let email: string;
  let jti: string;
  try {
    const { payload } = await jwtVerify(token, jwtKey(), { algorithms: ["HS256"], audience: "partner-link" });
    email = String(payload.email);
    jti = String(payload.jti);
  } catch {
    return false;
  }
  if (await getKv(`plink:${jti}`)) return false; // already used
  await putKv(`plink:${jti}`, { at: new Date().toISOString() });
  if (!(await partnersForEmail(email)).length) return false;
  const session = await new SignJWT({ email, aud: "partner" }).setProtectedHeader({ alg: "HS256" }).setIssuedAt().setExpirationTime(`${DAYS}d`).sign(jwtKey());
  (await cookies()).set(PARTNER_COOKIE, session, { httpOnly: true, sameSite: "lax", secure: process.env.NODE_ENV === "production", path: "/", maxAge: DAYS * 24 * 3600 });
  return true;
}

export async function partnerSignOut() {
  (await cookies()).delete(PARTNER_COOKIE);
}

/** The signed-in partner login, and the partners it may see (checked against the live list every time). */
export async function currentPartnerLogin(): Promise<{ email: string; partners: Partner[] } | null> {
  const t = (await cookies()).get(PARTNER_COOKIE)?.value;
  if (!t) return null;
  try {
    const { payload } = await jwtVerify(t, jwtKey(), { algorithms: ["HS256"], audience: "partner" });
    const email = String(payload.email);
    const partners = await partnersForEmail(email);
    return partners.length ? { email, partners } : null;
  } catch {
    return null;
  }
}

/** A partner this login may act for (the one asked for, or their first). */
export async function currentPartner(id?: string | null): Promise<{ email: string; partner: Partner; all: Partner[] } | null> {
  const s = await currentPartnerLogin();
  if (!s) return null;
  const p = (id && s.partners.find((x) => x.id === id)) || s.partners[0];
  const fresh = await getPartner(p.id);
  return fresh ? { email: s.email, partner: fresh, all: s.partners } : null;
}

// ------------------------------------------------------------ payout details, encrypted at rest
const payoutKey = () => createHash("sha256").update(`${secret()}:partner-payout`).digest();
export function sealPayout(p: PayoutMethod): string {
  const iv = randomBytes(12);
  const c = createCipheriv("aes-256-gcm", payoutKey(), iv);
  const body = Buffer.concat([c.update(JSON.stringify(p), "utf8"), c.final()]);
  return [iv, c.getAuthTag(), body].map((b) => b.toString("base64url")).join(".");
}
export function openPayout(sealed: string): PayoutMethod | null {
  try {
    const [iv, tag, body] = sealed.split(".").map((x) => Buffer.from(x, "base64url"));
    const d = createDecipheriv("aes-256-gcm", payoutKey(), iv);
    d.setAuthTag(tag);
    return JSON.parse(Buffer.concat([d.update(body), d.final()]).toString("utf8")) as PayoutMethod;
  } catch {
    return null;
  }
}
