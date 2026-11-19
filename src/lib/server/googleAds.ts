// Google Ads API: read campaign and ad status, and make changes the owner has approved.
//
// On Render (service "mapsie"):
//   GOOGLE_ADS_CLIENT_ID, GOOGLE_ADS_CLIENT_SECRET  OAuth client (Google Cloud → APIs & Services → Credentials)
//   GOOGLE_ADS_DEVELOPER_TOKEN                      Manager account → Admin → API Center
//   GOOGLE_ADS_CUSTOMER_ID                          the Mapsie ads account, e.g. 123-456-7890
//   GOOGLE_ADS_LOGIN_CUSTOMER_ID                    the manager account's id (when access is through it)
// The long-lived refresh token comes from "Connect Google Ads" in /admin/channels and is
// stored encrypted in the database, never in an environment variable or a log.
import { createCipheriv, createDecipheriv, createHash, randomBytes } from "node:crypto";
import { getKv, putKv } from "./db";
import { publicUrl } from "./urls";

export const GADS_SCOPE = "https://www.googleapis.com/auth/adwords";
const KV = "gads:refresh";
const version = () => process.env.GOOGLE_ADS_API_VERSION || "v26";
const digits = (s?: string) => (s ?? "").replace(/\D/g, "");

export const gadsRedirectUri = () => `${publicUrl()}/api/admin/google-ads/callback`;

export function gadsConfig() {
  return {
    clientId: process.env.GOOGLE_ADS_CLIENT_ID ?? "",
    clientSecret: process.env.GOOGLE_ADS_CLIENT_SECRET ?? "",
    developerToken: process.env.GOOGLE_ADS_DEVELOPER_TOKEN ?? "",
    customerId: digits(process.env.GOOGLE_ADS_CUSTOMER_ID),
    loginCustomerId: digits(process.env.GOOGLE_ADS_LOGIN_CUSTOMER_ID),
  };
}

/** What's still missing before the API can be used (names only, never values). */
export function gadsMissing(): string[] {
  const c = gadsConfig();
  return [
    !c.clientId && "GOOGLE_ADS_CLIENT_ID",
    !c.clientSecret && "GOOGLE_ADS_CLIENT_SECRET",
    !c.developerToken && "GOOGLE_ADS_DEVELOPER_TOKEN",
    !c.customerId && "GOOGLE_ADS_CUSTOMER_ID",
  ].filter(Boolean) as string[];
}

// ------------------------------------------------------------ refresh token, encrypted at rest
const key = () => createHash("sha256").update(`${process.env.SESSION_SECRET ?? "dev-only-session-secret-change-me-0123456789"}:google-ads`).digest();

export function sealToken(token: string): string {
  const iv = randomBytes(12);
  const c = createCipheriv("aes-256-gcm", key(), iv);
  const body = Buffer.concat([c.update(token, "utf8"), c.final()]);
  return [iv, c.getAuthTag(), body].map((b) => b.toString("base64url")).join(".");
}

export function openToken(sealed: string): string {
  const [iv, tag, body] = sealed.split(".").map((p) => Buffer.from(p, "base64url"));
  const d = createDecipheriv("aes-256-gcm", key(), iv);
  d.setAuthTag(tag);
  return Buffer.concat([d.update(body), d.final()]).toString("utf8");
}

export async function gadsConnection(): Promise<{ connected: boolean; at?: string; email?: string }> {
  const kv = await getKv<{ sealed: string; email?: string }>(KV);
  return kv ? { connected: true, at: kv.updatedAt, email: kv.value.email } : { connected: false };
}

// ------------------------------------------------------------ OAuth
export function gadsAuthUrl(state: string) {
  const q = new URLSearchParams({
    client_id: gadsConfig().clientId,
    redirect_uri: gadsRedirectUri(),
    response_type: "code",
    scope: `${GADS_SCOPE} openid email`,
    access_type: "offline",
    prompt: "consent", // always return a refresh token
    include_granted_scopes: "true",
    state,
  });
  return `https://accounts.google.com/o/oauth2/v2/auth?${q}`;
}

/** After the owner approves on Google's screen: swap the code for a refresh token and store it. */
export async function gadsFinishConnect(code: string) {
  const c = gadsConfig();
  const r = await fetch("https://oauth2.googleapis.com/token", {
    method: "POST",
    headers: { "content-type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({ code, client_id: c.clientId, client_secret: c.clientSecret, redirect_uri: gadsRedirectUri(), grant_type: "authorization_code" }),
    signal: AbortSignal.timeout(15_000),
  });
  const j = (await r.json()) as { refresh_token?: string; id_token?: string; error?: string; error_description?: string };
  if (!r.ok || !j.refresh_token) throw new Error(`Google sign-in failed: ${j.error_description ?? j.error ?? r.status}${r.ok ? " (no refresh token returned)" : ""}`);
  let email: string | undefined;
  try {
    email = JSON.parse(Buffer.from(String(j.id_token).split(".")[1], "base64url").toString()).email;
  } catch {
    /* email is only for display */
  }
  await putKv(KV, { sealed: sealToken(j.refresh_token), email });
  cached = null;
}

let cached: { token: string; until: number } | null = null;

async function accessToken(): Promise<string> {
  if (cached && cached.until > Date.now() + 60_000) return cached.token;
  const kv = await getKv<{ sealed: string }>(KV);
  if (!kv) throw new Error("Google Ads isn't connected yet: use Connect Google Ads in /admin/channels");
  const c = gadsConfig();
  const r = await fetch("https://oauth2.googleapis.com/token", {
    method: "POST",
    headers: { "content-type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({ refresh_token: openToken(kv.value.sealed), client_id: c.clientId, client_secret: c.clientSecret, grant_type: "refresh_token" }),
    signal: AbortSignal.timeout(15_000),
  });
  const j = (await r.json()) as { access_token?: string; expires_in?: number; error?: string; error_description?: string };
  if (!r.ok || !j.access_token) throw new Error(`Google token refresh failed: ${j.error_description ?? j.error ?? r.status}`);
  cached = { token: j.access_token, until: Date.now() + (j.expires_in ?? 3600) * 1000 };
  return cached.token;
}

// ------------------------------------------------------------ API calls
async function call<T>(path: string, body: unknown): Promise<T> {
  const missing = gadsMissing();
  if (missing.length) throw new Error(`Google Ads not configured on Render: missing ${missing.join(", ")}`);
  const c = gadsConfig();
  const r = await fetch(`https://googleads.googleapis.com/${version()}/customers/${c.customerId}/${path}`, {
    method: "POST",
    headers: {
      authorization: `Bearer ${await accessToken()}`,
      "developer-token": c.developerToken,
      ...(c.loginCustomerId ? { "login-customer-id": c.loginCustomerId } : {}),
      "content-type": "application/json",
    },
    body: JSON.stringify(body),
    signal: AbortSignal.timeout(30_000),
  });
  const text = await r.text();
  if (!r.ok) {
    let msg = text.slice(0, 600);
    try {
      const e = JSON.parse(text).error;
      const details = (e?.details ?? []).flatMap((d: { errors?: { message: string }[] }) => d.errors ?? []).map((x: { message: string }) => x.message);
      msg = [e?.message, ...details].filter(Boolean).join(" | ");
    } catch {
      /* keep the raw text */
    }
    throw new Error(`Google Ads API ${r.status}: ${msg}`);
  }
  return JSON.parse(text) as T;
}

/** Run a GAQL query and return every row. */
export async function gadsSearch<T = Record<string, unknown>>(query: string): Promise<T[]> {
  const rows: T[] = [];
  let pageToken: string | undefined;
  do {
    const j = await call<{ results?: T[]; nextPageToken?: string }>("googleAds:search", { query, ...(pageToken ? { pageToken } : {}) });
    rows.push(...(j.results ?? []));
    pageToken = j.nextPageToken;
  } while (pageToken && rows.length < 50_000);
  return rows;
}

/** Apply changes, e.g. gadsMutate("campaigns", [{ update: {...}, updateMask: "status" }]). */
export async function gadsMutate(resource: string, operations: unknown[], validateOnly = false) {
  if (!/^[a-zA-Z]+$/.test(resource)) throw new Error("bad resource name");
  return call<{ results?: { resourceName: string }[] }>(`${resource}:mutate`, { operations, validateOnly });
}

/** Campaigns, budgets and every ad's review status, for a quick check. */
export async function gadsStatus() {
  // No date segment here: a campaign with no impressions yet would otherwise be left out.
  const campaigns = await gadsSearch(
    "SELECT campaign.id, campaign.name, campaign.status, campaign.serving_status, campaign.primary_status, campaign.primary_status_reasons, campaign_budget.amount_micros FROM campaign WHERE campaign.status != 'REMOVED'",
  );
  const ads = await gadsSearch(
    "SELECT campaign.name, ad_group.name, ad_group_ad.ad.id, ad_group_ad.status, ad_group_ad.policy_summary.approval_status, ad_group_ad.policy_summary.review_status, ad_group_ad.policy_summary.policy_topic_entries FROM ad_group_ad WHERE ad_group_ad.status != 'REMOVED'",
  );
  return { campaigns, ads };
}
