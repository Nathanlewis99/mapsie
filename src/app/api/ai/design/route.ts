import { NextResponse } from "next/server";
import Anthropic from "@anthropic-ai/sdk";
import { AiError, aiConfigured, planToTrip, planTrip } from "@/lib/server/aiDesign";
import { getKv, putKv } from "@/lib/server/db";
import { logError } from "@/lib/server/log";
import { clientIp, limit, sameOrigin, tooMany } from "@/lib/server/rateLimit";
import { publicUrl } from "@/lib/server/urls";

export const maxDuration = 60;

// Each request costs money, so several layers:
//  1. Only from our own pages (Origin check).
//  2. A bot check (Cloudflare Turnstile) when TURNSTILE_SECRET_KEY and
//     TURNSTILE_SITE_KEY are set on Render.
//  3. Per visitor: 6 in 10 minutes, 25 a day.
//  4. Site-wide: AI_HOURLY_LIMIT (default 60) and AI_DAILY_LIMIT (default 300).
//  5. Set a monthly spend limit in the Anthropic Console as the final backstop.
const turnstileSiteKey = () => process.env.TURNSTILE_SITE_KEY || "";

/** What the editor needs to show the box: whether it's on, and the bot-check site key. */
export async function GET() {
  return NextResponse.json({ enabled: aiConfigured(), turnstileSiteKey: turnstileSiteKey() || null }, { headers: { "cache-control": "no-store" } });
}

async function humanCheck(token: unknown, ip: string): Promise<boolean> {
  const secret = process.env.TURNSTILE_SECRET_KEY;
  if (!secret || !turnstileSiteKey()) return true; // not set up: rely on the limits
  if (typeof token !== "string" || !token || token.length > 4096) return false;
  try {
    const r = await fetch("https://challenges.cloudflare.com/turnstile/v0/siteverify", {
      method: "POST",
      body: new URLSearchParams({ secret, response: token, ...(ip !== "unknown" ? { remoteip: ip } : {}) }),
      signal: AbortSignal.timeout(8000),
    });
    return ((await r.json()) as { success?: boolean }).success === true;
  } catch (e) {
    await logError("ai.turnstile", e);
    return true; // Cloudflare unreachable: don't lock everyone out; the limits still apply
  }
}

/** Site-wide counters in the database (shared by every web instance). */
async function underSiteCaps() {
  const nowIso = new Date().toISOString();
  const caps = [
    { key: `ai:count:${nowIso.slice(0, 10)}`, max: Number(process.env.AI_DAILY_LIMIT ?? 300) },
    { key: `ai:hour:${nowIso.slice(0, 13)}`, max: Number(process.env.AI_HOURLY_LIMIT ?? 60) },
  ];
  const counts = await Promise.all(caps.map(async (c) => (await getKv<number>(c.key))?.value ?? 0));
  if (caps.some((c, i) => counts[i] >= c.max)) return false;
  await Promise.all(caps.map((c, i) => putKv(c.key, counts[i] + 1)));
  return true;
}

/** POST { prompt, turnstileToken? } → { trip, reply }: a trip the editor applies like a quick-start template. */
export async function POST(req: Request) {
  if (!aiConfigured()) return NextResponse.json({ error: "Create with AI isn't switched on yet." }, { status: 503 });
  if (!sameOrigin(req, publicUrl())) return NextResponse.json({ error: "Not allowed" }, { status: 403 });
  const ip = clientIp(req);
  const body = (await req.json().catch(() => ({}))) as { prompt?: unknown; turnstileToken?: unknown };
  const prompt = typeof body.prompt === "string" ? body.prompt.trim() : "";
  if (prompt.length < 3) return NextResponse.json({ error: "Tell me about your trip first." }, { status: 400 });
  if (prompt.length > 2000) return NextResponse.json({ error: "That's a lot! Please keep it under 2,000 characters." }, { status: 400 });
  if (!limit("ai-burst", ip, 6, 10 * 60_000)) return tooMany("You've made a few maps already. Please wait a few minutes and try again.", 600);
  if (!limit("ai-day", ip, 25, 24 * 3600_000)) return tooMany("That's today's limit for AI maps. You can still add stops by hand, or try again tomorrow.", 3600);
  if (!(await humanCheck(body.turnstileToken, ip))) return NextResponse.json({ error: "Please complete the quick check and try again.", retryCheck: true }, { status: 403 });
  if (!(await underSiteCaps())) return tooMany("Create with AI is very busy right now. Please add your stops by hand, or try again later.", 3600);

  try {
    const plan = await planTrip(prompt);
    if (!plan.understood || !plan.stops.length) return NextResponse.json({ reply: plan.reply || "Tell me where you went and I'll map it.", trip: null });
    return NextResponse.json({ reply: plan.reply, trip: await planToTrip(plan) });
  } catch (e) {
    if (e instanceof AiError) return NextResponse.json({ error: e.message }, { status: 422 });
    if (e instanceof Anthropic.RateLimitError) return NextResponse.json({ error: "Create with AI is busy right now. Please try again in a minute." }, { status: 503 });
    await logError("ai.design", e, { promptLength: prompt.length });
    return NextResponse.json({ error: "Something went wrong making your map. Please try again." }, { status: 500 });
  }
}
