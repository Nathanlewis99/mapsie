// "Create with AI": the customer describes a trip (typed or spoken) and Claude plans
// the map: the stops in order with how they travelled between them, a map style, a
// title and some sticker ideas. We then pin each stop with our own geocoder and pick
// real Mapsie Originals for the stickers. The editor applies the result like one of
// its quick-start trips (sticker placement, road routes and framing happen there).
//
// Needs ANTHROPIC_API_KEY on the web service.
import Anthropic from "@anthropic-ai/sdk";
import { betaZodOutputFormat } from "@anthropic-ai/sdk/helpers/beta/zod";
import { z } from "zod";
import { PRESETS } from "../themes";
import { searchOriginals } from "../originals";
import type { TripTemplate } from "../templates";
import type { TravelMode } from "../types";
import { searchPlaces } from "./geocode";

export const aiConfigured = () => !!process.env.ANTHROPIC_API_KEY;

const MODES = ["plane", "car", "bus", "train", "boat", "walk", "tuktuk", "moped"] as const satisfies readonly TravelMode[];

const Plan = z.object({
  understood: z.boolean().describe("false if the request isn't about a trip or a map (then leave stops empty)"),
  reply: z.string().describe("One short, friendly sentence for the customer about the map you made, or why you couldn't."),
  title: z.string().describe("Poster title, at most 28 characters, e.g. 'Sri Lanka 2026' or 'Our Honeymoon'"),
  subtitle: z.string().describe("Short line under the title, at most 45 characters, e.g. 'By tuk-tuk, train & car · March 2026'"),
  preset: z.enum(PRESETS.map((p) => p.id) as [string, ...string[]]),
  stops: z.array(
    z.object({
      name: z.string().describe("Label for the map: the place's short common name, e.g. 'Kandy'"),
      search: z.string().describe("Geocoder query that finds exactly this place, e.g. 'Kandy, Sri Lanka'"),
      lng: z.number(),
      lat: z.number(),
      arriveBy: z.enum(MODES).nullable().describe("How they got here from the previous stop; null for the first stop"),
    }),
  ),
  stickerIdeas: z.array(z.string()).describe("2 to 5 short sticker ideas tied to the trip, e.g. 'elephant', 'surfing', 'tea plantation'"),
});
export type AiPlan = z.infer<typeof Plan>;

const SYSTEM = `You plan custom travel-map posters for Mapsie. The customer describes a trip, and you turn it into the stops on their map.

Stops:
- List the places in the order they were visited, as the customer described. Include every place they mention; if they only name a country or region, choose 4 to 8 well-known stops that make a sensible route.
- Use at most 25 stops. A place visited twice (e.g. a round trip home) can appear again at the end.
- Give accurate coordinates and a geocoder query with the country so the place can be found exactly.
- arriveBy is how they travelled from the previous stop: plane for long or overseas hops, train, car, bus, boat, walk, tuktuk or moped when they say so or it's clearly how people go. Default to car for road trips. The first stop's arriveBy is null.

Style (preset), pick the one that suits the trip:
${PRESETS.map((p) => `- ${p.id}: ${p.name}${p.tag ? ` (${p.tag})` : ""}`).join("\n")}
Terrain for mountains and hiking, Tropical for beaches and islands, Nautical for sailing and coasts, Vintage or Explorer for big adventures and backpacking, Blush for honeymoons and romance, Midnight for cities at night, Minimal or Ink for clean modern looks, Atlas for whole-continent trips. Use the style the customer asks for if they name one.

Title and subtitle: warm and personal, using names, dates or the occasion if given. Never invent personal names.

If the request isn't about a trip, places or a map, set understood to false, leave stops empty and say briefly what you can help with.`;

let client: Anthropic | null = null;

/** The models we compare on /admin/ai, with list prices per million tokens (input, output). */
export const AI_MODELS = {
  "claude-opus-5-5": { label: "Opus 5.5", price: [4, 20] },
  "claude-sonnet-5-5": { label: "Sonnet 5.5", price: [2, 10] },
} as const;
export type AiModel = keyof typeof AI_MODELS;
/** The model customers get: AI_MODEL on Render, else Opus 5.5. */
export const liveModel = (): AiModel => (process.env.AI_MODEL && process.env.AI_MODEL in AI_MODELS ? (process.env.AI_MODEL as AiModel) : "claude-opus-5-5");

export interface PlanStats { model: string; ms: number; inputTokens: number; outputTokens: number; costUsd: number }

/** Ask Claude for a plan. */
export async function planTrip(prompt: string, model: AiModel = liveModel()): Promise<AiPlan> {
  return (await planTripWithStats(prompt, model)).plan;
}

export async function planTripWithStats(prompt: string, model: AiModel = liveModel()): Promise<{ plan: AiPlan; stats: PlanStats }> {
  client ??= new Anthropic();
  const t0 = Date.now();
  const res = await client.beta.messages.parse({
    model,
    max_tokens: 8000,
    // A quick, well-formed plan matters more here than deep deliberation.
    output_config: { effort: "low", format: betaZodOutputFormat(Plan) },
    // If the request is ever declined by a safety classifier, retry on a fallback model.
    betas: ["server-side-fallback-2026-07-01"],
    fallbacks: "default",
    system: SYSTEM,
    messages: [{ role: "user", content: prompt }],
  });
  if (res.stop_reason === "refusal" || !res.parsed_output) throw new AiError("Sorry, I couldn't plan that map. Try describing the places you went.");
  const [pin, pout] = AI_MODELS[model].price;
  const { input_tokens: inputTokens, output_tokens: outputTokens } = res.usage;
  return {
    plan: res.parsed_output,
    stats: { model: res.model, ms: Date.now() - t0, inputTokens, outputTokens, costUsd: (inputTokens * pin + outputTokens * pout) / 1e6 },
  };
}

export class AiError extends Error {}

const km = (a: { lng: number; lat: number }, b: { lng: number; lat: number }) => {
  const r = Math.PI / 180;
  const h = Math.sin(((b.lat - a.lat) * r) / 2) ** 2 + Math.cos(a.lat * r) * Math.cos(b.lat * r) * Math.sin(((b.lng - a.lng) * r) / 2) ** 2;
  return 12742 * Math.asin(Math.sqrt(h));
};

/**
 * Turn the plan into a quick-start trip: each stop is pinned with our geocoder (when
 * it agrees with Claude's rough position, to avoid a same-named town elsewhere), and
 * sticker ideas become Mapsie Originals.
 */
export async function planToTrip(plan: AiPlan): Promise<TripTemplate> {
  return (await planToTripChecked(plan)).trip;
}

/** As planToTrip, plus how far each stop's position from Claude was from the geocoder's (km; null = no match). */
export async function planToTripChecked(plan: AiPlan): Promise<{ trip: TripTemplate; driftKm: (number | null)[] }> {
  const driftKm: (number | null)[] = [];
  const stops = await Promise.all(
    plan.stops.slice(0, 25).map(async (s, i): Promise<TripTemplate["stops"][number]> => {
      const guess = { lng: s.lng, lat: s.lat };
      let at = guess;
      driftKm[i] = null;
      try {
        const hit = (await searchPlaces(s.search || s.name)).find((p) => km(p, guess) < 150);
        if (hit) {
          at = { lng: hit.lng, lat: hit.lat };
          driftKm[i] = +km(hit, guess).toFixed(1);
        }
      } catch {
        /* keep Claude's position */
      }
      const lng = Math.max(-180, Math.min(180, at.lng));
      const lat = Math.max(-85, Math.min(85, at.lat));
      return [s.name.slice(0, 40), +lng.toFixed(5), +lat.toFixed(5), i === 0 ? undefined : (s.arriveBy ?? "car")];
    }),
  );
  const stickers = [...new Set(plan.stickerIdeas.map((idea) => searchOriginals(idea)[0]?.id).filter((x): x is string => !!x))].slice(0, 5);
  const trip: TripTemplate = {
    id: "ai",
    name: "Your trip",
    emoji: "✨",
    title: plan.title.slice(0, 40),
    subtitle: plan.subtitle.slice(0, 60),
    preset: PRESETS.some((p) => p.id === plan.preset) ? plan.preset : PRESETS[0].id,
    stickers,
    stops,
  };
  return { trip, driftKm };
}
