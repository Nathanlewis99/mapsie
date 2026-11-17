import { NextResponse } from "next/server";
import Anthropic from "@anthropic-ai/sdk";
import { AiError, aiConfigured, planToTrip, planTrip } from "@/lib/server/aiDesign";
import { getKv, putKv } from "@/lib/server/db";
import { logError } from "@/lib/server/log";

export const maxDuration = 60;

// Each request costs a few pence, so keep it to people designing maps: a handful per
// visitor in a short window, and a daily ceiling for the whole site (AI_DAILY_LIMIT).
const WINDOW_MS = 15 * 60_000;
const PER_VISITOR = 8;
const recent = new Map<string, number[]>();
const ip = (req: Request) => req.headers.get("x-forwarded-for")?.split(",")[0]?.trim() || "unknown";

function allowVisitor(who: string) {
  const now = Date.now();
  const hits = (recent.get(who) ?? []).filter((t) => now - t < WINDOW_MS);
  if (hits.length >= PER_VISITOR) return false;
  hits.push(now);
  recent.set(who, hits);
  if (recent.size > 5000) recent.clear(); // don't grow forever
  return true;
}

async function allowToday() {
  const day = new Date().toISOString().slice(0, 10);
  const key = `ai:count:${day}`;
  const n = (await getKv<number>(key))?.value ?? 0;
  if (n >= Number(process.env.AI_DAILY_LIMIT ?? 1000)) return false;
  await putKv(key, n + 1);
  return true;
}

/** POST { prompt } → { trip, reply }: a trip the editor applies like a quick-start template. */
export async function POST(req: Request) {
  if (!aiConfigured()) return NextResponse.json({ error: "Create with AI isn't switched on yet." }, { status: 503 });
  const body = (await req.json().catch(() => ({}))) as { prompt?: unknown };
  const prompt = typeof body.prompt === "string" ? body.prompt.trim() : "";
  if (prompt.length < 3) return NextResponse.json({ error: "Tell me about your trip first." }, { status: 400 });
  if (prompt.length > 2000) return NextResponse.json({ error: "That's a lot! Please keep it under 2,000 characters." }, { status: 400 });
  if (!allowVisitor(ip(req))) return NextResponse.json({ error: "You've made a few maps already. Please wait a few minutes and try again." }, { status: 429 });
  if (!(await allowToday())) return NextResponse.json({ error: "Create with AI is very busy today. Please add your stops by hand, or try again tomorrow." }, { status: 429 });

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
