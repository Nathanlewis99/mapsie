// Simple abuse protection for public endpoints.
//
// clientIp: the visitor's address. Render runs behind Cloudflare, which sets
// CF-Connecting-IP itself (a visitor can't fake it). X-Forwarded-For is only a fallback:
// its first entry can be written by the visitor.
//
// limit(): a sliding window per key, kept in this server's memory. With several web
// instances each keeps its own count, which is fine for slowing abuse; anything that
// costs money also has a site-wide cap in the database (see the AI route).
export function clientIp(req: Request): string {
  const h = req.headers;
  return (
    h.get("cf-connecting-ip")?.trim() ||
    h.get("true-client-ip")?.trim() ||
    h.get("x-real-ip")?.trim() ||
    h.get("x-forwarded-for")?.split(",")[0]?.trim() ||
    "unknown"
  );
}

const buckets = new Map<string, Map<string, number[]>>();

/** True if this request is allowed: at most `max` per `windowMs` for this key in this bucket. */
export function limit(bucket: string, key: string, max: number, windowMs: number): boolean {
  const now = Date.now();
  let b = buckets.get(bucket);
  if (!b) buckets.set(bucket, (b = new Map()));
  const hits = (b.get(key) ?? []).filter((t) => now - t < windowMs);
  if (hits.length >= max) {
    b.set(key, hits);
    return false;
  }
  hits.push(now);
  b.set(key, hits);
  // Forget idle visitors now and then, so memory stays small.
  if (b.size > 10_000) for (const [k, v] of b) if (!v.some((t) => now - t < windowMs)) b.delete(k);
  return true;
}

/** A 429 with a friendly message and Retry-After. */
export const tooMany = (message = "Too many requests. Please wait a minute and try again.", retryAfterSec = 60) =>
  Response.json({ error: message }, { status: 429, headers: { "retry-after": String(retryAfterSec) } });

/**
 * Requests from our own pages only: the browser's Origin (or Referer) must be this
 * site. Scripts can fake it, but it stops other websites using our endpoints from
 * their visitors' browsers, and casual scripting.
 */
export function sameOrigin(req: Request, site: string): boolean {
  const from = req.headers.get("origin") ?? req.headers.get("referer");
  if (!from) return false;
  try {
    const host = new URL(from).host;
    return host === new URL(site).host || host === new URL(req.url).host || /^(localhost|127\.0\.0\.1)(:\d+)?$/.test(host);
  } catch {
    return false;
  }
}
