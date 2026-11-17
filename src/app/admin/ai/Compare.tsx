"use client";
import { useState } from "react";

// Real customer-style descriptions: detailed, vague, spoken (rambling), ambiguous
// place names, long routes, and one that isn't a trip at all.
const DEFAULT_PROMPTS = [
  "Two weeks in Sri Lanka: Colombo, then the train from Kandy to Ella, tuk-tuks down to Mirissa and Galle. March 2026 with Sam",
  "two weeks in japan",
  "Our honeymoon! Paris, then the train to Florence and Rome, and we flew home from Naples. June 2025",
  "so we started in uh Lima then went up to Cusco and did the Inca trail to Machu Picchu, then Lake Titicaca, then got the bus to La Paz and did the salt flats at Uyuni",
  "Road trip from Paris, Texas to Portland, Maine",
  "Gap year: Bangkok, Chiang Mai, the slow boat to Luang Prabang, Hanoi, Ha Long Bay, then flew to Bali and island hopped to the Gili islands",
  "Interrail summer 2024 Amsterdam Berlin Prague Vienna Budapest Ljubljana and back home to London",
  "Write me a poem about cats",
];

type Result = {
  model: string;
  label: string;
  error?: string;
  plan?: { understood: boolean; reply: string; title: string; subtitle: string; preset: string; stops: { name: string; arriveBy: string | null }[]; stickerIdeas: string[] };
  trip?: { stickers: string[] } | null;
  driftKm?: (number | null)[];
  stats?: { model: string; ms: number; inputTokens: number; outputTokens: number; costUsd: number };
};
type Row = { prompt: string; results?: Result[]; error?: string };

const MODE: Record<string, string> = { plane: "✈️", car: "🚗", bus: "🚌", train: "🚆", boat: "⛴️", walk: "🚶", tuktuk: "🛺", moped: "🛵" };

export default function Compare() {
  const [text, setText] = useState(DEFAULT_PROMPTS.join("\n"));
  const [rows, setRows] = useState<Row[]>([]);
  const [busy, setBusy] = useState(false);

  const run = async () => {
    const prompts = text.split("\n").map((x) => x.trim()).filter(Boolean).slice(0, 20);
    setBusy(true);
    setRows(prompts.map((prompt) => ({ prompt })));
    // Two at a time: quick, without tripping rate limits.
    let next = 0;
    const worker = async () => {
      while (next < prompts.length) {
        const i = next++;
        try {
          const r = await fetch("/api/admin/ai", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ prompt: prompts[i] }) });
          const j = await r.json();
          setRows((rs) => rs.map((x, k) => (k === i ? (r.ok ? { ...x, results: j.results } : { ...x, error: j.error }) : x)));
        } catch (e) {
          setRows((rs) => rs.map((x, k) => (k === i ? { ...x, error: String(e) } : x)));
        }
      }
    };
    await Promise.all([worker(), worker()]);
    setBusy(false);
  };

  // Totals per model across finished rows.
  const totals = new Map<string, { label: string; n: number; ms: number[]; cost: number; misses: number; stops: number }>();
  for (const r of rows)
    for (const x of r.results ?? []) {
      if (!x.stats) continue;
      const t = totals.get(x.model) ?? { label: x.label, n: 0, ms: [], cost: 0, misses: 0, stops: 0 };
      t.n++;
      t.ms.push(x.stats.ms);
      t.cost += x.stats.costUsd;
      t.stops += x.driftKm?.length ?? 0;
      t.misses += (x.driftKm ?? []).filter((d) => d === null).length;
      totals.set(x.model, t);
    }
  const median = (a: number[]) => [...a].sort((p, q) => p - q)[Math.floor(a.length / 2)] ?? 0;

  return (
    <div className="space-y-5">
      <div className="rounded-3xl bg-white p-5 shadow-sm space-y-3">
        <div className="text-sm font-bold">Trip descriptions, one per line (each runs on both models; about 5p a line in total)</div>
        <textarea value={text} onChange={(e) => setText(e.target.value)} rows={8} className="w-full rounded-xl border-2 border-ink/10 px-3 py-2 text-sm font-mono" />
        <button onClick={run} disabled={busy} className="rounded-full bg-coral px-5 py-2.5 font-extrabold text-white disabled:opacity-50">{busy ? "Running…" : "Run comparison"}</button>
      </div>

      {totals.size > 0 && (
        <div className="grid sm:grid-cols-2 gap-3">
          {[...totals.values()].map((t) => (
            <div key={t.label} className="rounded-3xl bg-white p-5 shadow-sm text-sm">
              <div className="font-extrabold text-lg">{t.label}</div>
              <div>Median time: <b>{(median(t.ms) / 1000).toFixed(1)}s</b> · slowest {(Math.max(...t.ms) / 1000).toFixed(1)}s</div>
              <div>Cost: <b>${t.cost.toFixed(3)}</b> for {t.n} maps (≈ ${(t.cost / t.n).toFixed(3)} each)</div>
              <div>Stops the geocoder couldn&apos;t confirm: <b>{t.misses}</b> of {t.stops}</div>
            </div>
          ))}
        </div>
      )}

      {rows.map((r, i) => (
        <div key={i} className="rounded-3xl bg-white p-5 shadow-sm space-y-3">
          <div className="text-sm font-bold">“{r.prompt}”</div>
          {r.error && <div className="text-coral-dark font-bold text-sm">{r.error}</div>}
          {!r.results && !r.error && <div className="text-sm text-ink/40">Running…</div>}
          <div className="grid md:grid-cols-2 gap-4">
            {r.results?.map((x) => (
              <div key={x.model} className="rounded-2xl bg-sand/50 p-4 text-sm space-y-1.5">
                <div className="flex justify-between font-extrabold">
                  <span>{x.label}</span>
                  {x.stats && <span className="text-ink/50 font-bold">{(x.stats.ms / 1000).toFixed(1)}s · ${x.stats.costUsd.toFixed(3)} · {x.stats.outputTokens} tok</span>}
                </div>
                {x.error && <div className="text-coral-dark">{x.error}</div>}
                {x.plan && (
                  <>
                    <div className="italic text-ink/70">{x.plan.reply}</div>
                    {x.plan.understood && (
                      <>
                        <div><b>{x.plan.title}</b> · {x.plan.subtitle} · <span className="text-ink/50">{x.plan.preset}</span></div>
                        <div className="leading-relaxed">
                          {x.plan.stops.map((s, k) => (
                            <span key={k}>
                              {k > 0 && <span className="text-ink/50"> {MODE[s.arriveBy ?? ""] ?? "→"} </span>}
                              <span className={x.driftKm?.[k] === null ? "text-coral-dark font-bold" : x.driftKm?.[k] != null && x.driftKm[k]! > 30 ? "text-amber-700" : ""} title={x.driftKm?.[k] == null ? "Geocoder found no match within 150 km: Claude's position used" : `${x.driftKm[k]} km from the geocoder`}>{s.name}</span>
                            </span>
                          ))}
                        </div>
                        <div className="text-ink/60">Stickers: {x.plan.stickerIdeas.join(", ")} → <b>{x.trip?.stickers.length ?? 0} matched</b></div>
                      </>
                    )}
                  </>
                )}
              </div>
            ))}
          </div>
        </div>
      ))}
      <p className="text-xs text-ink/40">Red stop = the geocoder couldn&apos;t confirm it (Claude&apos;s own position is used); amber = more than 30 km from the geocoder&apos;s spot. Hover a stop for the distance.</p>
    </div>
  );
}
