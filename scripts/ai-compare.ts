// Compare the Create-with-AI models on a set of trip descriptions, printing a summary.
// Runs where ANTHROPIC_API_KEY is set (e.g. as a Render one-off job):
//   npx -y tsx@4.20.3 scripts/ai-compare.ts
// The same comparison is on /admin/ai.
import { AI_MODELS, planToTripChecked, planTripWithStats, type AiModel } from "../src/lib/server/aiDesign";

const PROMPTS = [
  "Two weeks in Sri Lanka: Colombo, then the train from Kandy to Ella, tuk-tuks down to Mirissa and Galle. March 2026 with Sam",
  "two weeks in japan",
  "Our honeymoon! Paris, then the train to Florence and Rome, and we flew home from Naples. June 2025",
  "so we started in uh Lima then went up to Cusco and did the Inca trail to Machu Picchu, then Lake Titicaca, then got the bus to La Paz and did the salt flats at Uyuni",
  "Road trip from Paris, Texas to Portland, Maine",
  "Gap year: Bangkok, Chiang Mai, the slow boat to Luang Prabang, Hanoi, Ha Long Bay, then flew to Bali and island hopped to the Gili islands",
  "Interrail summer 2024 Amsterdam Berlin Prague Vienna Budapest Ljubljana and back home to London",
  "Write me a poem about cats",
];
const MODE: Record<string, string> = { plane: "plane", car: "car", bus: "bus", train: "train", boat: "boat", walk: "walk", tuktuk: "tuktuk", moped: "moped" };

async function one(prompt: string, model: AiModel) {
  try {
    const { plan, stats } = await planTripWithStats(prompt, model);
    const checked = plan.understood && plan.stops.length ? await planToTripChecked(plan) : null;
    const route = plan.stops
      .map((s, i) => `${i ? ` -${MODE[s.arriveBy ?? ""] ?? ""}-> ` : ""}${s.name}${checked?.driftKm[i] === null ? "(?)" : ""}`)
      .join("");
    const body = plan.understood
      ? `"${plan.title}" / "${plan.subtitle}" [${plan.preset}] ${route} | stickers ${plan.stickerIdeas.join(", ")} -> ${checked?.trip.stickers.length ?? 0} matched`
      : "NOT A TRIP";
    return {
      ok: true,
      stats,
      misses: checked?.driftKm.filter((d) => d === null).length ?? 0,
      stops: plan.stops.length,
      text: `${(stats.ms / 1000).toFixed(1)}s $${stats.costUsd.toFixed(4)} out=${stats.outputTokens} | ${body} | reply: ${plan.reply}`,
    };
  } catch (e) {
    return { ok: false, text: `ERROR ${(e as Error).message}`.slice(0, 300) };
  }
}

(async () => {
  const totals: Record<string, { ms: number[]; cost: number; misses: number; stops: number; errors: number }> = {};
  for (const prompt of PROMPTS) {
    console.log(`\n=== ${prompt}`);
    const models = Object.keys(AI_MODELS) as AiModel[];
    const res = await Promise.all(models.map((m) => one(prompt, m)));
    models.forEach((m, i) => {
      const r = res[i];
      const t = (totals[m] ??= { ms: [], cost: 0, misses: 0, stops: 0, errors: 0 });
      if (r.ok && r.stats) {
        t.ms.push(r.stats.ms);
        t.cost += r.stats.costUsd;
        t.misses += r.misses ?? 0;
        t.stops += r.stops ?? 0;
      } else t.errors++;
      console.log(`  ${AI_MODELS[m].label}: ${r.text}`);
    });
  }
  console.log("\n=== SUMMARY");
  for (const [m, t] of Object.entries(totals)) {
    const sorted = [...t.ms].sort((a, b) => a - b);
    const med = (sorted[Math.floor(sorted.length / 2)] ?? 0) / 1000;
    const max = (sorted[sorted.length - 1] ?? 0) / 1000;
    console.log(`  ${AI_MODELS[m as AiModel].label}: median ${med.toFixed(1)}s, max ${max.toFixed(1)}s, total $${t.cost.toFixed(3)}, unconfirmed stops ${t.misses}/${t.stops}, errors ${t.errors}`);
  }
  console.log("=== DONE");
  process.exit(0);
})();
