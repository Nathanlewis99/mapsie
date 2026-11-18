// Ad spend, imported automatically so /admin/channels can show cost per sale and
// return on ad spend without typing numbers in:
//   Meta: Marketing API insights (META_ADS_TOKEN + META_AD_ACCOUNT_ID)
//   Pinterest: Ads analytics API (PINTEREST_ADS_TOKEN + PINTEREST_AD_ACCOUNT_ID)
//   Google Ads: a Google Ads Script posts daily numbers to /api/ads/spend (see admin page)
// Refreshed at most once an hour, when the admin report is opened.
import { createHmac, timingSafeEqual } from "node:crypto";
import { getKv, putKv, saveAdSpend, type AdSpendDay } from "./db";
import { logError } from "./log";

const DAYS_BACK = 35;
const day = (d: Date) => d.toISOString().slice(0, 10);
const range = () => ({ since: day(new Date(Date.now() - DAYS_BACK * 24 * 3600_000)), until: day(new Date()) });
// Rough conversion for accounts billed in other currencies (good enough for comparing channels).
export const TO_GBP: Record<string, number> = { GBP: 1, USD: 0.79, AUD: 0.52, EUR: 0.85 };

const secret = () => process.env.SESSION_SECRET ?? "dev-only-session-secret-change-me-0123456789";
/** The key the Google Ads Script sends with its numbers (shown on the admin page). */
export const adsImportKey = () => createHmac("sha256", secret()).update("ads-spend-import").digest("base64url").slice(0, 32);
export function adsImportKeyValid(k: string | null) {
  const want = Buffer.from(adsImportKey());
  const got = Buffer.from(k ?? "");
  return got.length === want.length && timingSafeEqual(got, want);
}

type MetaAction = { action_type: string; value: string };
const pick = (list: MetaAction[] | undefined, ...types: string[]) => {
  for (const t of types) {
    const a = list?.find((x) => x.action_type === t);
    if (a) return Number(a.value);
  }
  return 0;
};

async function syncMeta(): Promise<number> {
  const token = process.env.META_ADS_TOKEN;
  const account = process.env.META_AD_ACCOUNT_ID;
  if (!token || !account) return 0;
  const v = process.env.META_GRAPH_VERSION || "v23.0";
  // Token in a header, not the URL, so it never ends up in logs.
  const auth = { authorization: `Bearer ${token}` };
  const acct = await fetch(`https://graph.facebook.com/${v}/act_${account}?fields=currency`, { headers: auth }).then((r) => r.json());
  const rate = TO_GBP[String(acct.currency ?? "GBP").toUpperCase()] ?? 1;
  const q = new URLSearchParams({
    fields: "spend,impressions,clicks,actions,action_values",
    level: "account",
    time_increment: "1",
    time_range: JSON.stringify(range()),
    limit: "100",
  });
  const res = await fetch(`https://graph.facebook.com/${v}/act_${account}/insights?${q}`, { headers: auth, signal: AbortSignal.timeout(20_000) });
  const j = (await res.json()) as { data?: { date_start: string; spend: string; impressions?: string; clicks?: string; actions?: MetaAction[]; action_values?: MetaAction[] }[]; error?: { message: string } };
  if (!res.ok || j.error) throw new Error(`Meta insights: ${j.error?.message ?? res.status}`);
  const rows: AdSpendDay[] = (j.data ?? []).map((d) => ({
    channel: "meta_ads",
    day: d.date_start,
    spend: Number(d.spend) * rate,
    impressions: Number(d.impressions ?? 0),
    clicks: Number(d.clicks ?? 0),
    platformPurchases: pick(d.actions, "purchase", "offsite_conversion.fb_pixel_purchase"),
    platformValue: pick(d.action_values, "purchase", "offsite_conversion.fb_pixel_purchase") * rate,
    source: "api",
  }));
  await saveAdSpend(rows);
  return rows.length;
}

async function syncPinterest(): Promise<number> {
  const token = process.env.PINTEREST_ADS_TOKEN;
  const account = process.env.PINTEREST_AD_ACCOUNT_ID;
  if (!token || !account) return 0;
  const { since, until } = range();
  const cols = ["SPEND_IN_MICRO_DOLLAR", "TOTAL_IMPRESSION", "TOTAL_CLICKTHROUGH", "TOTAL_CHECKOUT", "TOTAL_CHECKOUT_VALUE_IN_MICRO_DOLLAR"];
  const q = new URLSearchParams({ start_date: since, end_date: until, columns: cols.join(","), granularity: "DAY" });
  const res = await fetch(`https://api.pinterest.com/v5/ad_accounts/${account}/analytics?${q}`, { headers: { authorization: `Bearer ${token}` }, signal: AbortSignal.timeout(20_000) });
  if (!res.ok) throw new Error(`Pinterest analytics ${res.status}: ${(await res.text()).slice(0, 200)}`);
  const data = (await res.json()) as Record<string, number | string>[];
  // Pinterest reports money in "micro" units of the ad account's currency (GBP for Mapsie).
  const rows: AdSpendDay[] = data.map((d) => ({
    channel: "pinterest_ads",
    day: String(d.DATE).slice(0, 10),
    spend: Number(d.SPEND_IN_MICRO_DOLLAR ?? 0) / 1e6,
    impressions: Number(d.TOTAL_IMPRESSION ?? 0),
    clicks: Number(d.TOTAL_CLICKTHROUGH ?? 0),
    platformPurchases: Number(d.TOTAL_CHECKOUT ?? 0),
    platformValue: Number(d.TOTAL_CHECKOUT_VALUE_IN_MICRO_DOLLAR ?? 0) / 1e6,
    source: "api",
  }));
  await saveAdSpend(rows);
  return rows.length;
}

/** Pull the latest spend from the APIs, at most once an hour. Never throws. */
export async function refreshAdSpend(force = false): Promise<{ at?: string; errors: string[] }> {
  const last = await getKv<{ at: string; errors: string[] }>("adspend:sync");
  if (!force && last && Date.now() - new Date(last.value.at).getTime() < 3600_000) return last.value;
  const errors: string[] = [];
  for (const [name, fn] of [["Meta", syncMeta], ["Pinterest", syncPinterest]] as const) {
    try {
      await fn();
    } catch (e) {
      errors.push(`${name}: ${String((e as Error).message).slice(0, 200)}`);
      await logError(`adspend.${name.toLowerCase()}`, e);
    }
  }
  const state = { at: new Date().toISOString(), errors };
  await putKv("adspend:sync", state);
  return state;
}

/** Rows posted by the Google Ads Script. */
export async function importScriptRows(channel: "google_ads", rows: { day: string; cost: number; currency?: string; impressions?: number; clicks?: number; conversions?: number; value?: number }[]) {
  const ok = rows.filter((r) => /^\d{4}-\d{2}-\d{2}$/.test(r.day) && Number.isFinite(r.cost) && r.cost >= 0).slice(0, 400);
  await saveAdSpend(
    ok.map((r) => {
      const rate = TO_GBP[(r.currency ?? "GBP").toUpperCase()] ?? 1;
      return { channel, day: r.day, spend: r.cost * rate, impressions: r.impressions, clicks: r.clicks, platformPurchases: r.conversions, platformValue: (r.value ?? 0) * rate, source: "script" as const };
    }),
  );
  return ok.length;
}
