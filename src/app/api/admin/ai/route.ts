import { NextResponse } from "next/server";
import { AI_MODELS, aiConfigured, planToTripChecked, planTripWithStats, type AiModel } from "@/lib/server/aiDesign";

/** Admin only (middleware): run one trip description through each model, for comparing them on /admin/ai. */
export async function POST(req: Request) {
  if (!aiConfigured()) return NextResponse.json({ error: "Set ANTHROPIC_API_KEY on the web service first." }, { status: 503 });
  const { prompt } = (await req.json().catch(() => ({}))) as { prompt?: string };
  if (!prompt?.trim()) return NextResponse.json({ error: "No prompt" }, { status: 400 });
  const results = await Promise.all(
    (Object.keys(AI_MODELS) as AiModel[]).map(async (model) => {
      try {
        const { plan, stats } = await planTripWithStats(prompt.trim().slice(0, 2000), model);
        const { trip, driftKm } = plan.understood && plan.stops.length ? await planToTripChecked(plan) : { trip: null, driftKm: [] };
        return { model, label: AI_MODELS[model].label, plan, trip, driftKm, stats };
      } catch (e) {
        return { model, label: AI_MODELS[model].label, error: String((e as Error).message ?? e).slice(0, 300) };
      }
    }),
  );
  return NextResponse.json({ results });
}
