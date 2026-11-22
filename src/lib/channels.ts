// Which marketing channel brought an order, from the visit's UTM tags, ad click id
// and referrer. Used for sales-by-channel (return on ad spend) in admin.
export interface AttributionIn { source?: string; medium?: string; campaign?: string; click?: string; referrer?: string; landing?: string }

export const CHANNELS = [
  { id: "meta_ads", label: "Meta ads (Instagram/Facebook)" },
  { id: "google_ads", label: "Google ads" },
  { id: "pinterest_ads", label: "Pinterest ads" },
  { id: "tiktok_ads", label: "TikTok ads" },
  { id: "microsoft_ads", label: "Microsoft (Bing) ads" },
  { id: "other_paid", label: "Other paid" },
  { id: "organic_search", label: "Organic search" },
  { id: "organic_social", label: "Organic social (incl. Pinterest pins)" },
  { id: "email", label: "Email" },
  { id: "etsy", label: "Etsy" },
  { id: "partners", label: "Partners (tour operators, events…)" },
  { id: "referral", label: "Other websites" },
  { id: "direct", label: "Direct / unknown" },
] as const;
export type ChannelId = (typeof CHANNELS)[number]["id"];

const has = (s: string | undefined, ...words: string[]) => !!s && words.some((w) => s.toLowerCase().includes(w));

export function classifyChannel(a: AttributionIn | undefined): ChannelId {
  if (!a) return "direct";
  const src = a.source?.toLowerCase();
  const paid = has(a.medium, "cpc", "ppc", "paid", "ads", "cpm", "display", "shopping") || !!a.click;
  // Ad click ids are the most reliable signal.
  if (a.click === "fbclid" && paid && (has(src, "facebook", "instagram", "meta", "fb", "ig") || has(a.medium, "paid", "cpc", "ads"))) return "meta_ads";
  if (["gclid", "gbraid", "wbraid"].includes(a.click ?? "")) return "google_ads";
  if (a.click === "epik") return "pinterest_ads";
  if (a.click === "ttclid") return "tiktok_ads";
  if (a.click === "msclkid") return "microsoft_ads";
  if (a.medium?.toLowerCase() === "partner") return "partners";
  if (has(a.medium, "email", "newsletter")) return "email";
  if (paid && src) {
    if (has(src, "facebook", "instagram", "meta", "fb", "ig")) return "meta_ads";
    if (has(src, "google", "youtube")) return "google_ads";
    if (has(src, "pinterest")) return "pinterest_ads";
    if (has(src, "tiktok")) return "tiktok_ads";
    if (has(src, "bing", "microsoft")) return "microsoft_ads";
    return "other_paid";
  }
  const from = `${src ?? ""} ${a.referrer ?? ""}`;
  if (has(from, "etsy")) return "etsy";
  if (has(from, "google", "bing", "duckduckgo", "yahoo", "ecosia", "brave", "yandex")) return "organic_search";
  if (has(from, "facebook", "instagram", "pinterest", "tiktok", "t.co", "twitter", "x.com", "reddit", "youtube", "linkedin", "threads", "whatsapp")) return "organic_social";
  if (src || a.referrer) return "referral";
  return "direct";
}

/** Keep only short, known fields from the browser. */
export function cleanAttribution(v: unknown): AttributionIn | undefined {
  if (!v || typeof v !== "object") return undefined;
  const o = v as Record<string, unknown>;
  const out: AttributionIn = {};
  for (const k of ["source", "medium", "campaign", "click", "referrer", "landing"] as const) {
    if (typeof o[k] === "string" && o[k]) out[k] = (o[k] as string).slice(0, 80);
  }
  return Object.keys(out).length ? out : undefined;
}
