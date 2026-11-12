"use client";
import { useEffect, useRef, useState } from "react";
import { useEditor } from "@/lib/store";
import { searchPlaces, MODES, type PlaceResult } from "@/lib/geo";
import { PRESETS, themeFromPreset } from "@/lib/themes";
import { ART_STYLES, PACKS, STICKERS, getArtStyle, searchStickers, stickerSrc, suggestedStyleFor, type ArtStyleId } from "@/lib/stickers";
import StickerFilters, { filterId } from "@/components/StickerFilters";
import {
  ORIGINALS,
  PAINTED,
  ORIGINAL_CATEGORIES,
  PALETTE_NAMES,
  PALETTE_SWATCH,
  matchedPalette,
  originalSrc,
  resolvePalette,
  searchOriginals,
  type OriginalDef,
  LANDMARK_REGIONS,
  landmarksNear,
  type OriginalStyle,
} from "@/lib/originals";
import { FONTS } from "@/lib/fonts";
import { getRegion, REGIONS } from "@/lib/products";
import PrintOptionsPicker from "@/components/PrintOptionsPicker";
import { Compass } from "@/components/Poster";
import { trackSearch } from "@/lib/track";
import SafeImg from "@/components/SafeImg";
import { crowding, MIN_STOP_SCALE, readability, recommendedProduct, sizeNote, smallestText, tidyCrowded } from "@/lib/legibility";
import { getProduct } from "@/lib/products";
import { TEMPLATES } from "@/lib/templates";
import type { CompassStyle, ThemeColors, Layout, TravelMode, MarkerStyle, RouteStyle, TextStyle, TextCase, FontId } from "@/lib/types";

export const Label = ({ children }: { children: React.ReactNode }) => (
  <div className="text-xs font-bold uppercase tracking-wider text-ink/50 mb-2">{children}</div>
);

/** On/off switch. `disabled` greys it out (with `hint` saying why) when another setting makes it irrelevant. */
function Toggle({ on, onChange, label, disabled, hint }: { on: boolean; onChange: (v: boolean) => void; label: string; disabled?: boolean; hint?: string }) {
  return (
    <button
      onClick={() => onChange(!on)}
      disabled={disabled}
      title={disabled ? hint : undefined}
      className="flex items-center justify-between w-full py-1.5 text-sm font-semibold text-left disabled:opacity-40 disabled:cursor-not-allowed"
    >
      <span>
        {label}
        {disabled && hint && <span className="block text-[11px] font-semibold text-ink/60">{hint}</span>}
      </span>
      <span className={`w-10 h-6 rounded-full p-0.5 transition shrink-0 ${on ? "bg-coral" : "bg-ink/15"}`}>
        <span className={`block w-5 h-5 rounded-full bg-white shadow transition ${on ? "translate-x-4" : ""}`} />
      </span>
    </button>
  );
}

function Chips<T extends string>({ value, options, onChange, disabled }: { value: T; options: { id: T; label: string }[]; onChange: (v: T) => void; disabled?: boolean }) {
  return (
    <div className={`flex flex-wrap gap-2 ${disabled ? "opacity-40 pointer-events-none" : ""}`} aria-disabled={disabled}>
      {options.map((o) => (
        <button
          key={o.id}
          disabled={disabled}
          onClick={() => onChange(o.id)}
          className={`px-3 py-1.5 rounded-full text-sm font-bold border-2 transition ${value === o.id ? "border-coral bg-coral text-white" : "border-ink/10 bg-white hover:border-ink/30"}`}
        >
          {o.label}
        </button>
      ))}
    </div>
  );
}

function Slider({ value, min, max, step, onChange, label, disabled }: { value: number; min: number; max: number; step: number; onChange: (v: number) => void; label: string; disabled?: boolean }) {
  return (
    <label className={`flex items-center gap-3 py-1.5 text-sm font-semibold ${disabled ? "opacity-40" : ""}`}>
      <span className="w-24 shrink-0">{label}</span>
      <input type="range" min={min} max={max} step={step} value={value} disabled={disabled} onChange={(e) => onChange(+e.target.value)} className="flex-1 accent-coral disabled:cursor-not-allowed" />
    </label>
  );
}

// ---------------------------------------------------------------- Trip
function ModePicker({ value, onChange }: { value: TravelMode; onChange: (m: TravelMode) => void }) {
  return (
    <div className="flex items-center gap-1 pl-10 py-1">
      <span className="w-px h-4 bg-ink/15 mr-2" />
      {MODES.map((m) => (
        <button
          key={m.id}
          title={m.label}
          onClick={() => onChange(m.id)}
          className={`w-8 h-8 rounded-full grid place-items-center transition ${value === m.id ? "bg-coral/15 ring-2 ring-coral" : "opacity-40 hover:opacity-100"}`}
        >
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src={m.icon} alt={m.label} className="w-5 h-5" />
        </button>
      ))}
    </div>
  );
}

export function TripPanel({ pickMode, setPickMode }: { pickMode: boolean; setPickMode: (v: boolean) => void }) {
  const { design, addStop, addStops, updateStop, removeStop, moveStop, set, requestFit, applyTemplate, roadsLoading } = useEditor();
  const [q, setQ] = useState("");
  const [results, setResults] = useState<PlaceResult[]>([]);
  const [searchState, setSearchState] = useState<"idle" | "searching" | "done" | "error">("idle");
  const [active, setActive] = useState(0);
  const [pasteOpen, setPasteOpen] = useState(false);
  const [paste, setPaste] = useState("");
  const [pasting, setPasting] = useState<string | null>(null);
  const [openStop, setOpenStop] = useState<string | null>(null);
  const dragFrom = useRef<number | null>(null);

  const runSearch = (query: string, full: boolean, signal?: AbortSignal) => {
    setSearchState("searching");
    return searchPlaces(query, signal, full)
      .then((r) => {
        setResults(r);
        setActive(0);
        setSearchState("done");
      })
      .catch((e) => {
        if ((e as Error).name !== "AbortError") setSearchState("error");
      });
  };

  useEffect(() => {
    if (q.trim().length < 2) {
      setResults([]);
      setSearchState("idle");
      return;
    }
    const ctl = new AbortController();
    setSearchState("searching");
    const t = setTimeout(() => runSearch(q, false, ctl.signal), 250);
    return () => {
      clearTimeout(t);
      ctl.abort();
    };
  }, [q]);

  const pick = (r: PlaceResult) => {
    addStop({ name: r.name, lng: r.lng, lat: r.lat });
    setQ("");
    setResults([]);
  };

  const importList = async () => {
    const names = paste.split(/\n|,|→|->|;/).map((s) => s.trim()).filter(Boolean).slice(0, 30);
    const found: PlaceResult[] = [];
    const missed: string[] = [];
    for (const n of names) {
      setPasting(n);
      const r = (await searchPlaces(n).catch(() => []))[0];
      if (r) found.push({ ...r, name: n.replace(/,.*$/, "") });
      else missed.push(n);
    }
    setPasting(null);
    if (found.length) addStops(found);
    setPaste(missed.length ? `Couldn't find:\n${missed.join("\n")}` : "");
    if (!missed.length) setPasteOpen(false);
  };

  const routeOn = design.route.show;
  const hasFlights = design.stops.slice(1).some((x) => (x.arriveBy ?? "plane") === "plane");
  return (
    <div className="space-y-5">
      {design.stops.length === 0 && (
        <div>
          <Label>Start from a trip</Label>
          <div className="grid grid-cols-2 gap-2">
            {TEMPLATES.map((t) => (
              <button key={t.id} onClick={() => applyTemplate(t)} className="rounded-2xl bg-white border border-ink/5 p-3 text-left hover:border-coral hover:-translate-y-0.5 transition shadow-sm">
                <div className="text-2xl">{t.emoji}</div>
                <div className="text-sm font-extrabold leading-tight mt-1">{t.name}</div>
              </button>
            ))}
          </div>
          <div className="text-center text-xs font-bold text-ink/40 mt-4">or build your own ↓</div>
        </div>
      )}

      <div>
        <Label>Add a stop</Label>
        <div className="relative">
          <input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "ArrowDown") setActive((a) => Math.min(a + 1, results.length - 1));
              if (e.key === "ArrowUp") setActive((a) => Math.max(a - 1, 0));
              if (e.key === "Enter") {
                if (results[active]) pick(results[active]);
                else if (q.trim().length >= 2) runSearch(q, true);
              }
              if (e.key === "Escape") setQ("");
            }}
            placeholder="Search a city, island, park…"
            className="w-full rounded-2xl border-2 border-ink/10 bg-white px-4 py-3 font-semibold outline-none focus:border-coral"
          />
          {searchState === "searching" && (
            <span className="absolute right-4 top-1/2 -translate-y-1/2 w-5 h-5 rounded-full border-2 border-coral/30 border-t-coral animate-spin" aria-label="Searching" />
          )}
          {q.trim().length >= 2 && searchState !== "idle" && (
            <div className="absolute z-20 mt-2 w-full rounded-2xl bg-white shadow-xl border border-ink/5 overflow-hidden">
              {searchState === "searching" && results.length === 0 && <div className="px-4 py-3 text-sm text-ink/50">Searching…</div>}
              {searchState === "error" && <div className="px-4 py-3 text-sm text-coral-dark font-bold">Search isn&apos;t responding. Try again in a moment.</div>}
              {searchState === "done" && results.length === 0 && (
                <div className="px-4 py-3 text-sm text-ink/60">No places found for “{q.trim()}”.</div>
              )}
              {results.map((r, i) => (
                <button
                  key={`${r.lng},${r.lat},${i}`}
                  onMouseEnter={() => setActive(i)}
                  onClick={() => pick(r)}
                  className={`block w-full text-left px-4 py-2.5 ${i === active ? "bg-coral/10" : ""}`}
                >
                  <div className="font-bold">{r.name}</div>
                  <div className="text-xs text-ink/50">{r.detail}</div>
                </button>
              ))}
              {searchState === "done" && (
                <button onClick={() => runSearch(q, true)} className="block w-full text-left px-4 py-2.5 text-sm font-bold text-coral border-t border-ink/5">
                  🔍 Not here? Search more places
                </button>
              )}
            </div>
          )}
        </div>
        <div className="mt-2 grid grid-cols-2 gap-2">
          <button
            onClick={() => setPickMode(!pickMode)}
            className={`rounded-2xl px-3 py-2.5 text-sm font-bold border-2 border-dashed transition ${pickMode ? "border-coral bg-coral/10 text-coral-dark" : "border-ink/15 text-ink/60 hover:border-ink/30"}`}
          >
            {pickMode ? "✓ Tap map… (done)" : "📍 Tap on the map"}
          </button>
          <button onClick={() => setPasteOpen(!pasteOpen)} className="rounded-2xl px-3 py-2.5 text-sm font-bold border-2 border-dashed border-ink/15 text-ink/60 hover:border-ink/30">
            📋 Paste a list
          </button>
        </div>
        {pasteOpen && (
          <div className="mt-2 space-y-2">
            <textarea
              value={paste}
              onChange={(e) => setPaste(e.target.value)}
              rows={4}
              placeholder={"One place per line, or comma separated:\nColombo, Kathmandu, Singapore, Cairns"}
              className="w-full rounded-2xl border-2 border-ink/10 bg-white px-4 py-3 text-sm font-semibold outline-none focus:border-coral"
            />
            <button onClick={importList} disabled={!!pasting || !paste.trim()} className="w-full rounded-full bg-ink text-white py-2.5 text-sm font-extrabold disabled:opacity-50">
              {pasting ? `Finding ${pasting}…` : "Add these stops"}
            </button>
          </div>
        )}
      </div>

      <div>
        <div className="flex items-center justify-between">
          <Label>Your journey ({design.stops.length})</Label>
          {design.stops.length > 0 && (
            <button onClick={requestFit} className="text-xs font-bold text-coral mb-2">Fit map to trip</button>
          )}
        </div>
        {roadsLoading > 0 && <div className="text-xs font-bold text-sea mb-2 animate-pulse">🚗 Finding the roads…</div>}
        <ol>
          {design.stops.map((s, i) => (
            <li key={s.id}>
              {i > 0 && <ModePicker value={s.arriveBy ?? "plane"} onChange={(m) => updateStop(s.id, { arriveBy: m })} />}
              <div
                draggable
                onDragStart={() => (dragFrom.current = i)}
                onDragOver={(e) => e.preventDefault()}
                onDrop={() => {
                  if (dragFrom.current !== null && dragFrom.current !== i) moveStop(dragFrom.current, i);
                  dragFrom.current = null;
                }}
                className="rounded-2xl bg-white border border-ink/5 shadow-sm"
              >
                <div className="flex items-center gap-2 px-2 py-2">
                  <span className="cursor-grab text-ink/30 px-1" title="Drag to reorder">⠿</span>
                  <span className="grid place-items-center w-7 h-7 rounded-full text-xs font-extrabold text-white shrink-0" style={{ background: design.theme.colors.accent }}>
                    {i + 1}
                  </span>
                  <input value={s.name} onChange={(e) => updateStop(s.id, { name: e.target.value }, `name-${s.id}`)} className="flex-1 min-w-0 bg-transparent font-bold outline-none" />
                  <button title="More" onClick={() => setOpenStop(openStop === s.id ? null : s.id)} className="text-ink/40 hover:text-ink px-1 font-bold">
                    {openStop === s.id ? "▴" : "▾"}
                  </button>
                  <button title="Remove" onClick={() => removeStop(s.id)} className="text-ink/30 hover:text-coral px-1 font-bold">✕</button>
                </div>
                {openStop === s.id && (
                  <div className="px-3 pb-3 space-y-1 border-t border-ink/5 pt-2">
                    <input
                      value={s.date ?? ""}
                      onChange={(e) => updateStop(s.id, { date: e.target.value }, `date-${s.id}`)}
                      placeholder="Dates, e.g. 3–9 March"
                      className="w-full rounded-xl border border-ink/10 px-3 py-2 text-sm font-semibold outline-none focus:border-coral"
                    />
                    <Toggle on={s.showLabel} onChange={(v) => updateStop(s.id, { showLabel: v })} label="Show name on map" />
                  </div>
                )}
              </div>
            </li>
          ))}
        </ol>
        {design.stops.length === 0 && (
          <div className="rounded-2xl bg-sand/60 p-4 text-sm text-ink/60">Add the places you went, in order. We&apos;ll draw the route between them.</div>
        )}
      </div>

      {design.stops.length > 1 && (
        <div className="space-y-1">
          <Label>Route</Label>
          {/* (settings below grey out when the route is hidden or has no flights) */}
          <Toggle on={design.route.show} onChange={(v) => set({ route: { ...design.route, show: v } })} label="Draw the route" />
          <Toggle disabled={!routeOn} hint="Turn on “Draw the route” first" on={design.route.modeIcons} onChange={(v) => set({ route: { ...design.route, modeIcons: v } })} label="Show ✈️ 🚗 🚆 icons on legs" />
          <Toggle
            disabled={!routeOn || !hasFlights}
            hint={!routeOn ? "Turn on “Draw the route” first" : "No flights on this trip (set a leg to ✈️ in your stops)"}
            on={design.route.curved}
            onChange={(v) => set({ route: { ...design.route, curved: v } })}
            label="Curvy flight paths"
          />
          <div className="pt-2">
            <Chips<RouteStyle>
              disabled={!routeOn}
              value={design.route.style}
              options={[{ id: "auto", label: "✨ Auto" }, { id: "dashed", label: "Dashed" }, { id: "dotted", label: "Dotted" }, { id: "solid", label: "Solid" }]}
              onChange={(v) => set({ route: { ...design.route, style: v } })}
            />
          </div>
          <Slider disabled={!routeOn} label="Thickness" min={0.15} max={1.2} step={0.05} value={design.route.width} onChange={(v) => set({ route: { ...design.route, width: v } }, "route-width")} />
        </div>
      )}
    </div>
  );
}

// ---------------------------------------------------------------- Style
const COLOR_FIELDS: { key: keyof ThemeColors; label: string }[] = [
  { key: "land", label: "Land" },
  { key: "water", label: "Water" },
  { key: "park", label: "Parks" },
  { key: "roads", label: "Roads" },
  { key: "borders", label: "Borders" },
  { key: "labels", label: "Labels" },
  { key: "accent", label: "Route" },
  { key: "paper", label: "Paper" },
  { key: "ink", label: "Title" },
];

export function StylePanel() {
  const { design, set, setTheme, setColors } = useEditor();
  const t = design.theme;
  const anyLabels = design.stops.some((x) => x.showLabel);
  const anyDates = design.stops.some((x) => x.date?.trim());
  return (
    <div className="space-y-6">
      <div>
        <Label>Map style</Label>
        <div className="grid grid-cols-3 gap-2">
          {PRESETS.map((p) => (
            <button
              key={p.id}
              onClick={() => set({ theme: { ...themeFromPreset(p), labels: t.labels } })}
              className={`rounded-2xl p-1.5 border-2 transition ${t.presetId === p.id ? "border-coral" : "border-transparent hover:border-ink/15"}`}
            >
              <div
                className="h-14 rounded-xl relative overflow-hidden"
                style={{ background: p.hypso ? `linear-gradient(160deg, #f4f1ea 0%, #c9a07a 28%, #e3dfa2 55%, #a8c98f 80%)` : p.physical ? `linear-gradient(150deg, #d9c99b, #b7cf9a 45%, #e8e4c9)` : p.colors.land }}
              >
                {p.details?.grid && (
                  <div className="absolute inset-0 opacity-40" style={{ backgroundImage: `linear-gradient(${p.colors.borders} 1px, transparent 1px), linear-gradient(90deg, ${p.colors.borders} 1px, transparent 1px)`, backgroundSize: "14px 14px" }} />
                )}
                <div className="absolute -right-3 -bottom-4 w-16 h-12 rounded-full" style={{ background: p.colors.water }} />
                <div className="absolute left-2 top-3 w-10 h-5 rounded-full opacity-80" style={{ background: p.colors.park }} />
                <svg className="absolute inset-0" viewBox="0 0 60 40"><path d="M6 32 Q 25 4 52 14" fill="none" stroke={p.colors.accent} strokeWidth="2.5" strokeDasharray="4 3" strokeLinecap="round" /></svg>
              </div>
              <div className="text-xs font-bold mt-1">{p.name}</div>
              {p.tag && <div className="text-[10px] font-bold text-ink/45 -mt-0.5">{p.tag}</div>}
            </button>
          ))}
        </div>
      </div>

      <SuggestionCard />

      <div>
        <Label>Make it yours</Label>
        <div className="grid grid-cols-3 gap-2">
          {COLOR_FIELDS.map((f) => (
            <label key={f.key} className="flex items-center gap-2 rounded-xl bg-white border border-ink/5 px-2 py-1.5 cursor-pointer">
              <input type="color" value={t.colors[f.key]} onChange={(e) => setColors({ [f.key]: e.target.value })} className="w-6 h-6 rounded-md cursor-pointer border-0 p-0 bg-transparent" />
              <span className="text-xs font-bold">{f.label}</span>
            </label>
          ))}
        </div>
      </div>

      <div>
        <Label>Stop markers</Label>
        <Chips<MarkerStyle>
          value={design.markers.style}
          options={[{ id: "number", label: "① Numbers" }, { id: "pin", label: "📍 Pins" }, { id: "heart", label: "♥ Hearts" }, { id: "dot", label: "• Dots" }, { id: "sticker", label: "🦘 Stickers" }]}
          onChange={(v) => set({ markers: { ...design.markers, style: v } })}
        />
        {design.markers.style === "sticker" && (
          <p className="text-xs text-ink/60 font-semibold mt-2">Tap a stop on the map, then choose its sticker in the Stickers tab. Stops without one show a pin.</p>
        )}
        <div className="mt-2">
          <Toggle
            disabled={!anyLabels || !anyDates}
            hint={!anyLabels ? "All stop names are hidden" : "Add dates to your stops in the Trip tab"}
            on={design.markers.showDates}
            onChange={(v) => set({ markers: { ...design.markers, showDates: v } })}
            label="📅 Show dates under stop names"
          />
        </div>
        <Slider label="Marker size" min={0.25} max={2.2} step={0.05} value={design.markers.size} onChange={(v) => set({ markers: { ...design.markers, size: v } }, "marker-size")} />
        <Slider disabled={!anyLabels} label="Label size" min={0.25} max={2.5} step={0.05} value={design.markers.labelSize} onChange={(v) => set({ markers: { ...design.markers, labelSize: v } }, "label-size")} />
        <p className="text-xs text-ink/50">Tip: tap a pin or place name on the map to resize just that stop, or drag the name somewhere else. Drag the pin to move the stop itself.</p>
        <div className="mt-3"><StopsCheck /></div>
      </div>

      <div>
        <Label>Details</Label>
        <Toggle on={design.visited.show} onChange={(v) => set({ visited: { ...design.visited, show: v } })} label="🌍 Highlight countries I visited" />
        {design.visited.show && (
          <Slider label="Highlight" min={0.1} max={0.8} step={0.05} value={design.visited.opacity} onChange={(v) => set({ visited: { ...design.visited, opacity: v } }, "visited-opacity")} />
        )}
        <Toggle on={t.relief} onChange={(v) => setTheme({ relief: v })} label="⛰️ Terrain shading" />
        <Toggle on={t.hypso} onChange={(v) => setTheme({ hypso: v })} label="🏔️ Colour land by height" />
        <Toggle on={t.physical} onChange={(v) => setTheme({ physical: v })} label="🗺️ Classic atlas relief" />
      </div>

      <div>
        <Label>Map extras</Label>
        <Toggle on={t.details.currents} onChange={(v) => setTheme({ details: { ...t.details, currents: v } })} label="🌊 Ocean currents" />
        <Toggle on={t.details.lanes} onChange={(v) => setTheme({ details: { ...t.details, lanes: v } })} label="🚢 Shipping lanes" />
        <Toggle on={t.details.grid} onChange={(v) => setTheme({ details: { ...t.details, grid: v } })} label="🌐 Latitude & longitude grid" />
        <Toggle on={t.details.tropics} onChange={(v) => setTheme({ details: { ...t.details, tropics: v } })} label="☀️ Equator & tropics" />
        <Toggle on={t.details.compass} onChange={(v) => setTheme({ details: { ...t.details, compass: v } })} label="🧭 Compass rose" />
        {t.details.compass && (
          <div className="pb-2">
            <div className="grid grid-cols-4 gap-2">
              {(["classic", "nautical", "minimal", "vintage"] as CompassStyle[]).map((v) => (
                <button
                  key={v}
                  title={v}
                  onClick={() => setTheme({ details: { ...t.details, compassStyle: v } })}
                  className={`rounded-xl border-2 p-1 ${(t.details.compassStyle ?? "classic") === v ? "border-coral" : "border-ink/10"}`}
                  style={{ background: t.colors.land }}
                >
                  <div className="aspect-square"><Compass inline u={1} ink={t.colors.ink} accent={t.colors.accent} paper={t.colors.paper} variant={v} /></div>
                  <div className="text-[10px] font-bold capitalize">{v}</div>
                </button>
              ))}
            </div>
            <div className="flex gap-1 mt-2 text-xs font-bold">
              {([["tl", "↖"], ["tr", "↗"], ["bl", "↙"], ["br", "↘"]] as const).map(([c, icon]) => (
                <button
                  key={c}
                  onClick={() => setTheme({ details: { ...t.details, compassCorner: c } })}
                  className={`rounded-full border-2 px-2.5 py-0.5 ${(t.details.compassCorner ?? "br") === c ? "border-coral bg-white" : "border-ink/10"}`}
                >
                  {icon}
                </button>
              ))}
              <span className="self-center text-ink/50 ml-1">corner</span>
            </div>
          </div>
        )}
        <Toggle on={t.labels} onChange={(v) => setTheme({ labels: v })} label="🔤 Place names" />
        <Toggle on={t.texture} onChange={(v) => setTheme({ texture: v })} label="📜 Aged paper texture" />
      </div>
    </div>
  );
}

// ---------------------------------------------------------------- Stops check
/** Overlapping stops and how readable the smallest name will be when printed. */
export function StopsCheck() {
  const { design, set } = useEditor();
  if (design.stops.length < 1) return null;
  const pairs = crowding(design);
  const crowded = new Set(pairs.flat()).size;
  const p = getProduct(design.productId);
  const small = smallestText(design);
  const status = readability(small.pt);
  const rec = recommendedProduct(design);
  const bigger = rec && rec.widthCm > p.widthCm ? rec : null;
  const tidy = () => {
    const patch = tidyCrowded(design);
    set({ stops: design.stops.map((s) => (patch[s.id] ? { ...s, ...patch[s.id] } : s)) });
  };
  const what = small.number < small.label ? "pin numbers" : `“${small.labelStop}”`;
  const crowdedIds = new Set(pairs.flat());
  const canShrink = design.stops.some((s) => crowdedIds.has(s.id) && ((s.markerScale ?? 1) > MIN_STOP_SCALE + 0.01 || (s.labelScale ?? 1) > MIN_STOP_SCALE + 0.01));
  return (
    <div className="space-y-2">
      {crowded > 0 && (
        <div className="rounded-2xl bg-coral/10 p-3 text-sm">
          <div className="font-extrabold">⚠️ {crowded} stops overlap at this zoom</div>
          {canShrink ? (
            <>
              <p className="text-ink/60 text-xs mt-0.5">Shrink just the crowded ones (the rest stay as they are), or tap a pin to size it yourself.</p>
              <button onClick={tidy} className="mt-2 rounded-full bg-coral px-4 py-1.5 text-sm font-extrabold text-white hover:bg-coral-dark">✨ Shrink crowded stops</button>
            </>
          ) : (
            <p className="text-ink/60 text-xs mt-0.5">
              They&apos;re as small as they go and still too close at this zoom. Tap a pin and choose Hide for some names, drag names apart (a line links them back to their pin), or zoom the map in a little.
            </p>
          )}
        </div>
      )}
      {Number.isFinite(small.pt) && (
        <div className={`rounded-2xl p-3 text-sm ${status === "good" ? "bg-sea/10" : status === "small" ? "bg-amber-100" : "bg-coral/10"}`}>
          <div className="font-extrabold">
            {status === "good" ? "✅ Easy to read" : status === "small" ? "👓 Small but readable" : "🔍 Too small to read"} on {p.label}
          </div>
          <p className="text-ink/60 text-xs mt-0.5">
            Smallest text: {what} prints at about {small.pt.toFixed(1)}pt ({((small.pt / 72) * 25.4 * 0.7).toFixed(1)} mm tall letters).
            {status !== "good" && (bigger ? ` On ${bigger.label} it would be ${smallestText(design, bigger.id).pt.toFixed(1)}pt.` : " Try bigger names, or hide a few.")}
          </p>
          {status !== "good" && bigger && (
            <button onClick={() => set({ productId: bigger.id })} className="mt-2 rounded-full bg-ink px-4 py-1.5 text-sm font-extrabold text-white">Switch to {bigger.label}</button>
          )}
          <p className="text-ink/40 text-[11px] mt-1.5">Prints are always sharp (300 dpi), so small names stay crisp. This is about reading them from a step away.</p>
        </div>
      )}
    </div>
  );
}

// ---------------------------------------------------------------- Stickers
/** A sticker drawn in a given art style (uses the panel's own filter defs). */
export function StickerThumb({ name, style, className = "" }: { name: string; style: ArtStyleId; className?: string }) {
  const art = getArtStyle(style);
  return (
    <SafeImg
      src={stickerSrc(name, style)}
      className={`w-full h-full pointer-events-none ${className}`}
      style={{ filter: art.finish !== "none" ? `url(#${filterId(PANEL_FILTERS, art.finish)})` : undefined, mixBlendMode: art.blend }}
    />
  );
}
const PANEL_FILTERS = "mapsie-panel";

/** Drag payload for dropping a sticker onto the map: "name|style". */
export const stickerDragType = "text/mapsie-sticker";

function SuggestionCard() {
  const { design, setStickerStyle } = useEditor();
  const suggested = suggestedStyleFor(design.theme.presetId);
  const preset = PRESETS.find((p) => p.id === design.theme.presetId);
  if (!preset || design.stickerStyle === suggested) return null;
  const count = design.stickers.filter((s) => s.kind === "sticker").length;
  return (
    <div className="rounded-2xl border-2 border-coral/30 bg-coral/5 p-3 flex items-center gap-3">
      <div className="w-12 h-12 shrink-0 rounded-xl p-1.5" style={{ background: design.theme.colors.land }}>
        <StickerThumb name="elephant" style={suggested} />
      </div>
      <div className="flex-1 text-sm">
        <div className="font-extrabold">✨ Suggested: {getArtStyle(suggested).name}</div>
        <div className="text-ink/60">Made to match your {preset.name} map.</div>
      </div>
      <button onClick={() => setStickerStyle(suggested, true)} className="rounded-full bg-coral text-white px-3 py-1.5 text-sm font-extrabold shrink-0">
        {count ? "Use it" : "Use"}
      </button>
    </div>
  );
}

/** With sticker stop markers: the selected stop, whose marker the next sticker tap sets. */
function useMarkerTarget() {
  const { design, selectedLabel } = useEditor();
  return design.markers.style === "sticker" && selectedLabel ? design.stops.find((s) => s.id === selectedLabel) : undefined;
}

function EmojiStickers({ q }: { q: string }) {
  const { design, addSticker, setStickerStyle } = useEditor();
  const at = useDropPoint();
  const [showAllStyles, setShowAllStyles] = useState(false);
  const style = design.stickerStyle;
  const suggested = suggestedStyleFor(design.theme.presetId);
  const results = searchStickers(q);
  const bg = design.theme.colors.land;
  const placed = design.stickers.filter((s) => s.kind === "sticker");
  const mixed = placed.some((s) => s.art !== style);

  const target = useMarkerTarget();
  const { updateStop } = useEditor();
  const place = (name: string, art: ArtStyleId = style) =>
    target
      ? updateStop(target.id, { marker: { kind: "sticker", name, art } })
      : addSticker({ kind: "sticker", name, art, src: stickerSrc(name, art), ...at(), size: 9, rotation: 0 });

  const tile = (name: string, art: ArtStyleId, title?: string) => (
    <button
      key={`${name}-${art}`}
      title={title}
      draggable
      onDragStart={(e) => e.dataTransfer.setData(stickerDragType, `${name}|${art}`)}
      onClick={() => place(name, art)}
      className="aspect-square rounded-xl border border-ink/5 p-1.5 hover:scale-110 hover:-rotate-6 transition"
      style={{ background: bg }}
    >
      <StickerThumb name={name} style={art} />
    </button>
  );

  const styles = showAllStyles ? ART_STYLES : ART_STYLES.slice(0, 6);

  return (
    <div className="space-y-5">
      <StickerFilters prefix={PANEL_FILTERS} colors={design.theme.colors} />

      {!q && (
      <div>
        <Label>Sticker style</Label>
        <div className="grid grid-cols-3 gap-2">
          {styles.map((a) => (
            <button
              key={a.id}
              onClick={() => setStickerStyle(a.id, true)}
              title={a.blurb}
              className={`relative rounded-2xl border-2 p-1.5 transition text-left ${style === a.id ? "border-coral bg-white" : "border-transparent bg-white/60 hover:border-ink/15"}`}
            >
              {a.id === suggested && <span className="absolute -top-2 -right-1 rounded-full bg-coral text-white text-[10px] font-extrabold px-1.5 py-0.5 z-10">✨ Match</span>}
              <div className="aspect-[4/3] rounded-xl grid grid-cols-2 gap-1 p-1.5" style={{ background: bg }}>
                <StickerThumb name="crocodile" style={a.id} />
                <StickerThumb name="palm-tree" style={a.id} />
              </div>
              <div className="text-xs font-extrabold mt-1 leading-tight">{a.name}</div>
            </button>
          ))}
        </div>
        <button onClick={() => setShowAllStyles(!showAllStyles)} className="mt-2 text-xs font-bold text-coral">
          {showAllStyles ? "Fewer styles" : `More styles (${ART_STYLES.length - 6})`}
        </button>
        <p className="text-xs text-ink/50 mt-1">{getArtStyle(style).blurb}. Changing style updates the stickers already on your map.</p>
        {mixed && placed.length > 0 && (
          <button onClick={() => setStickerStyle(style, true)} className="mt-2 text-xs font-bold text-ink/60 underline">
            Make all {placed.length} stickers {getArtStyle(style).name}
          </button>
        )}
      </div>
      )}

      {!q && <SuggestionCard />}

      {q ? (
        <div className="space-y-4">
          {results.length === 0 && <div className="text-sm text-ink/50">No stickers match “{q}” yet. Try a broader word like “animal” or “beach”.</div>}
          {results.slice(0, 12).map((s) => (
            <div key={s.name}>
              <div className="text-sm font-extrabold mb-1.5">{s.label} <span className="text-ink/40 font-semibold">· tap any style</span></div>
              <div className="grid grid-cols-5 gap-1.5">
                {ART_STYLES.map((a) => tile(s.name, a.id, a.name))}
              </div>
            </div>
          ))}
        </div>
      ) : (
        PACKS.map((pack) => (
          <div key={pack}>
            <Label>{pack}</Label>
            <div className="grid grid-cols-6 gap-1.5">{STICKERS.filter((s) => s.pack === pack).map((s) => tile(s.name, style, s.label))}</div>
          </div>
        ))
      )}
      <p className="text-[11px] text-ink/40">Artwork: Microsoft Fluent Emoji (MIT) and Twemoji (CC-BY 4.0).</p>
    </div>
  );
}

/** Where to drop a new sticker: scattered around the middle of the current view so they don't stack up. */
function useDropPoint() {
  const { design } = useEditor();
  const [cx, cy] = design.view.center;
  const degPerPx = 360 / (512 * 2 ** design.view.zoom);
  const jitter = () => (Math.random() - 0.5) * 220 * degPerPx;
  return () => ({ lng: cx + jitter(), lat: cy + jitter() * 0.7 });
}

function ExtrasRow() {
  const { addSticker } = useEditor();
  const at = useDropPoint();
  const fileRef = useRef<HTMLInputElement>(null);
  const onFile = async (f: File) => {
    const img = await createImageBitmap(f);
    const scale = Math.min(1, 1600 / Math.max(img.width, img.height));
    const c = document.createElement("canvas");
    c.width = Math.round(img.width * scale);
    c.height = Math.round(img.height * scale);
    c.getContext("2d")!.drawImage(img, 0, 0, c.width, c.height);
    addSticker({ kind: "photo", src: c.toDataURL("image/jpeg", 0.88), ...at(), size: 16, rotation: -4 });
  };
  return (
    <div className="grid grid-cols-2 gap-2">
      <button onClick={() => fileRef.current?.click()} className="rounded-2xl border-2 border-dashed border-ink/15 px-3 py-3 font-bold text-ink/70 hover:border-coral hover:text-coral">
        📸 Your photo
      </button>
      <button
        onClick={() => addSticker({ kind: "text", src: "", text: "Best day ever!", font: "caveat", ...at(), size: 4, rotation: -6 })}
        className="rounded-2xl border-2 border-dashed border-ink/15 px-3 py-3 font-bold text-ink/70 hover:border-coral hover:text-coral"
      >
        ✍️ Text note
      </button>
      <input ref={fileRef} type="file" accept="image/*" hidden onChange={(e) => e.target.files?.[0] && onFile(e.target.files[0])} />
    </div>
  );
}

function Swatch({ name }: { name: string }) {
  const [a, b, c] = PALETTE_SWATCH[name] ?? ["#eee", "#ccc", "#999"];
  return (
    <span className="inline-flex w-6 h-6 rounded-full overflow-hidden border border-ink/10 shrink-0" aria-hidden>
      <span className="flex-1" style={{ background: a }} />
      <span className="flex-1" style={{ background: b }} />
      <span className="flex-1" style={{ background: c }} />
    </span>
  );
}

/** Landmarks go where they really are; anything else where the user is looking. */
function landmarkPoint(id: string, fallback: () => { lng: number; lat: number }) {
  const o = ORIGINALS.find((x) => x.id === id);
  return o?.lat !== undefined && o.lng !== undefined ? { lng: o.lng, lat: o.lat } : fallback();
}

function OriginalsPanel({ q }: { q: string }) {
  const { design, addSticker, setOriginals } = useEditor();
  const at = useDropPoint();
  const { style, palette } = design.originals;
  const preset = design.theme.presetId;
  const matched = matchedPalette(preset, style);
  const resolved = resolvePalette(palette, preset, style);
  const results = searchOriginals(q);
  const byActivity = new Map<string, OriginalDef[]>();
  for (const o of results) byActivity.set(o.activity, [...(byActivity.get(o.activity) ?? []), o]);
  const categories = ORIGINAL_CATEGORIES.filter((c) => results.some((o) => o.category === c));
  const presetName = PRESETS.find((p) => p.id === preset)?.name ?? "your";
  const placed = design.stickers.filter((s) => s.kind === "original").length;

  const target = useMarkerTarget();
  const { updateStop } = useEditor();
  const place = (id: string) =>
    target
      ? updateStop(target.id, { marker: { kind: "original", name: id, origStyle: style, palette } })
      : addSticker({ kind: "original", name: id, origStyle: style, palette, src: "", ...landmarkPoint(id, at), size: 15, rotation: 0 });
  // Animals are listed by region (the catalogue is sorted by label, so sort by region first).
  const regionOf = (o?: OriginalDef) => (o?.keywords ?? "").replace(/ wildlife animal$/, "");
  const prevAnimal = { current: null as OriginalDef | null };
  const animalOrder = (a: [string, OriginalDef[]], b: [string, OriginalDef[]]) =>
    a[1][0].category === "Animals" && b[1][0].category === "Animals" ? regionOf(a[1][0]).localeCompare(regionOf(b[1][0])) : 0;

  const origTile = (o: OriginalDef) => (
    <button
      key={o.id}
      title={o.title}
      draggable
      onDragStart={(e) => e.dataTransfer.setData(stickerDragType, `orig:${o.id}`)}
      onClick={() => place(o.id)}
      className="rounded-2xl p-1.5 hover:scale-105 hover:-rotate-3 transition"
      style={{ background: style === "line" && resolved === "night" ? "#1F2A44" : "transparent" }}
    >
      <SafeImg src={originalSrc(o.id, style, resolved)} className="w-full aspect-square pointer-events-none" />
      <div className="text-[11px] font-bold text-ink/60 leading-tight mt-0.5 truncate">{o.title}</div>
    </button>
  );
  const near = q ? [] : landmarksNear(design.stops);
  // Landmarks and city skylines are listed by region rather than by activity.
  const PLACE_CATEGORIES = ["City skylines", "Landmarks"];
  const placeSections = PLACE_CATEGORIES.map((cat) => ({
    cat,
    groups: Object.entries(LANDMARK_REGIONS)
      .map(([g, name]) => [name, results.filter((o) => o.category === cat && o.group === g)] as const)
      .filter(([, list]) => list.length),
  })).filter((x) => x.groups.length);

  return (
    <div className="space-y-5">
      {!q && (<>
      <div className="rounded-2xl bg-sand/60 p-3 text-sm text-ink/70">
        Our own artwork, drawn for Mapsie. {ORIGINALS.length} designs across {new Set(ORIGINALS.map((o) => o.activity)).size} activities. Tap to add, or drag onto the map.
      </div>

      <div>
        <Label>Style</Label>
        <div className={`grid gap-2 ${PAINTED.size ? "grid-cols-3" : "grid-cols-2"}`}>
          {((PAINTED.size ? ["papercut", "line", "painted"] : ["papercut", "line"]) as OriginalStyle[]).map((st) => (
            <button
              key={st}
              onClick={() => setOriginals({ style: st, palette: "auto" })}
              className={`rounded-2xl border-2 p-2 flex items-center gap-2 transition ${style === st ? "border-coral bg-white" : "border-transparent bg-white/60 hover:border-ink/15"}`}
            >
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img src={originalSrc(st === "painted" ? [...PAINTED][0] : "safari-giraffe", st, matchedPalette(preset, st))} alt="" className="w-12 h-12" />
              <span className="font-extrabold text-sm">{st === "papercut" ? "Papercut" : st === "line" ? "Line" : "Painted"}</span>
            </button>
          ))}
        </div>
      </div>

      <div>
        <Label>Colours</Label>
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => setOriginals({ palette: "auto" })}
            className={`flex items-center gap-1.5 rounded-full border-2 pl-1 pr-3 py-1 text-sm font-bold ${palette === "auto" ? "border-coral bg-white" : "border-ink/10 bg-white"}`}
          >
            <Swatch name={matched} /> ✨ Match {presetName} map
          </button>
          {Object.entries(PALETTE_NAMES[style]).map(([id, name]) => (
            <button
              key={id}
              onClick={() => setOriginals({ palette: id })}
              className={`flex items-center gap-1.5 rounded-full border-2 pl-1 pr-3 py-1 text-sm font-bold ${palette === id ? "border-coral bg-white" : "border-ink/10 bg-white"}`}
            >
              <Swatch name={id} /> {name}
            </button>
          ))}
        </div>
        {placed > 0 && <p className="text-xs text-ink/50 mt-2">Applies to the {placed} Mapsie Original{placed > 1 ? "s" : ""} on your map too.</p>}
      </div>

      <ExtrasRow />

      </>)}

      {results.length === 0 && <div className="text-sm text-ink/50">No Mapsie Originals match “{q}” yet. Try the Emoji stickers, or a simpler word like “boat” or “mountain”.</div>}
      {near.length > 0 && (
        <div>
          <Label>📍 On your trip</Label>
          <div className="grid grid-cols-3 gap-2">{near.map(origTile)}</div>
        </div>
      )}
      {q ? (
        <div className="grid grid-cols-3 gap-2">{results.map(origTile)}</div>
      ) : (
        <>
      {placeSections.map(({ cat, groups }) => (
        <div key={cat}>
          <Label>{cat}</Label>
          {groups.map(([name, list]) => (
            <div key={name}>
              <div className="text-xs font-extrabold text-coral mt-3 mb-1">{name}</div>
              <div className="grid grid-cols-3 gap-2">{list.map(origTile)}</div>
            </div>
          ))}
        </div>
      ))}
      {categories.filter((c) => !PLACE_CATEGORIES.includes(c)).map((cat) => (
        <div key={cat}>
          <Label>{cat}</Label>
          <div className="space-y-3">
            {[...byActivity.entries()]
              .filter(([, list]) => list[0].category === cat)
              .sort(animalOrder)
              .map(([activity, list]) => (
                <div key={activity}>
                  {cat === "Animals" && regionOf(list[0]) !== regionOf(prevAnimal.current ?? undefined) && (
                    <div className="text-xs font-extrabold text-coral mt-4 mb-1">{regionOf((prevAnimal.current = list[0]))}</div>
                  )}
                  <div className="text-sm font-extrabold mb-1">{list[0].label}</div>
                  <div className="grid grid-cols-3 gap-2">{list.map(origTile)}</div>
                </div>
              ))}
          </div>
        </div>
      ))}
        </>
      )}
    </div>
  );
}

export function StickersPanel() {
  const [collection, setCollection] = useState<"originals" | "emoji">("originals");
  const [q, setQ] = useState("");
  const counts = q.trim() ? { originals: searchOriginals(q).length, emoji: searchStickers(q).length } : null;
  // Note what people look for (anonymously), once they pause typing.
  useEffect(() => {
    if (!counts) return;
    const t = setTimeout(() => trackSearch(q, counts.originals + counts.emoji), 1200);
    return () => clearTimeout(t);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [q]);
  const target = useMarkerTarget();
  const { design, selectLabel, updateStop } = useEditor();
  const stickerMarkers = design.markers.style === "sticker";
  return (
    <div className="space-y-5">
      {target ? (
        <div className="rounded-2xl bg-coral text-white p-3 text-sm font-bold flex items-center gap-2">
          <span className="flex-1">📍 Tap a sticker to use it as the marker for “{target.name}”</span>
          {target.marker && (
            <button onClick={() => updateStop(target.id, { marker: undefined })} className="rounded-full bg-white/20 px-3 py-1 text-xs">Use a pin</button>
          )}
          <button onClick={() => selectLabel(null)} className="rounded-full bg-white/20 px-3 py-1 text-xs">Done</button>
        </div>
      ) : stickerMarkers ? (
        <div className="rounded-2xl bg-sand/70 p-3 text-xs font-bold text-ink/60">
          Sticker markers are on: tap a stop on the map, then pick its sticker here. Stickers added without a stop selected go on the map as usual.
        </div>
      ) : null}
      <div className="relative sticky top-0 z-10">
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          onKeyDown={(e) => e.key === "Escape" && setQ("")}
          placeholder="🔍 Search stickers: car, beach, temple, snake…"
          className="w-full rounded-2xl border-2 border-ink/10 bg-white px-4 py-3 font-semibold outline-none focus:border-coral shadow-sm"
        />
        {q && <button onClick={() => setQ("")} aria-label="Clear search" className="absolute right-3 top-1/2 -translate-y-1/2 text-ink/40 font-bold px-2">✕</button>}
      </div>
      <div className="grid grid-cols-2 gap-1 rounded-full bg-sand/70 p-1">
        {([["originals", "✨ Mapsie Originals"], ["emoji", "😀 Emoji stickers"]] as const).map(([id, label]) => (
          <button key={id} onClick={() => setCollection(id)} className={`rounded-full py-2 text-sm font-extrabold transition ${collection === id ? "bg-white shadow-sm" : "text-ink/50"}`}>
            {label}
            {counts && <span className="ml-1 text-ink/40">· {counts[id]}</span>}
          </button>
        ))}
      </div>
      {collection === "originals" ? <OriginalsPanel q={q} /> : (<>{!q && <ExtrasRow />}<EmojiStickers q={q} /></>)}
    </div>
  );
}

// ---------------------------------------------------------------- Text
function FontPicker({ value, onChange }: { value: FontId; onChange: (f: FontId) => void }) {
  return (
    <div className="grid grid-cols-2 gap-2">
      {FONTS.map((f) => (
        <button
          key={f.id}
          onClick={() => onChange(f.id)}
          className={`rounded-2xl border-2 px-3 py-2 text-lg leading-tight transition truncate ${value === f.id ? "border-coral bg-white" : "border-ink/10 bg-white hover:border-ink/30"}`}
          style={{ fontFamily: f.css, fontWeight: f.bold }}
        >
          {f.name}
        </button>
      ))}
    </div>
  );
}

function TextFormat(p: {
  size: number;
  onSize: (v: number) => void;
  spacing: number;
  onSpacing: (v: number) => void;
  textCase: TextCase;
  onCase: (v: TextCase) => void;
  italic: boolean;
  onItalic: (v: boolean) => void;
  maxSize: number;
}) {
  const btn = (on: boolean) => `rounded-full border-2 px-3 py-1 text-sm font-bold ${on ? "border-coral bg-white" : "border-ink/10 bg-white hover:border-ink/30"}`;
  return (
    <div className="mt-2">
      <Slider label="Size" min={0.5} max={p.maxSize} step={0.05} value={p.size} onChange={p.onSize} />
      <Slider label="Spacing" min={-0.2} max={1.5} step={0.05} value={p.spacing} onChange={p.onSpacing} />
      <div className="flex flex-wrap gap-2 pt-1">
        <button className={btn(p.textCase === "none")} onClick={() => p.onCase("none")}>Aa</button>
        <button className={btn(p.textCase === "upper")} onClick={() => p.onCase("upper")}>AA</button>
        <button className={btn(p.textCase === "lower")} onClick={() => p.onCase("lower")}>aa</button>
        <button className={`${btn(p.italic)} italic`} onClick={() => p.onItalic(!p.italic)}>Italic</button>
      </div>
    </div>
  );
}

export function TextPanel() {
  const { design, set } = useEditor();
  const tx = design.text;
  const setText = (patch: Partial<TextStyle>, key?: string) => set({ text: { ...useEditor.getState().design.text, ...patch } }, key);
  return (
    <div className="space-y-5">
      <div>
        <Label>Layout</Label>
        <Chips<Layout>
          value={design.layout}
          options={[{ id: "band", label: "Title below" }, { id: "border", label: "Framed border" }, { id: "overlay", label: "Full bleed" }, { id: "none", label: "🗺️ Map only, no text" }]}
          onChange={(v) => set({ layout: v })}
        />
        {design.layout === "none" && <p className="text-xs text-ink/60 font-semibold mt-2">The whole print is map. Pick another layout to bring the title back.</p>}
      </div>
      <fieldset disabled={design.layout === "none"} className={`space-y-5 ${design.layout === "none" ? "opacity-40" : ""}`} title={design.layout === "none" ? "Map only layout: no title or subtitle" : undefined}>
      <div>
        <Label>Title</Label>
        <input value={design.title} maxLength={48} onChange={(e) => set({ title: e.target.value }, "title")} className="w-full rounded-2xl border-2 border-ink/10 bg-white px-4 py-3 font-bold outline-none focus:border-coral" />
      </div>
      <div>
        <Label>Subtitle</Label>
        <input value={design.subtitle} maxLength={60} onChange={(e) => set({ subtitle: e.target.value }, "subtitle")} placeholder="e.g. Spring 2026 · 4 countries · 1 big adventure" className="w-full rounded-2xl border-2 border-ink/10 bg-white px-4 py-3 font-semibold outline-none focus:border-coral" />
      </div>
      <div>
        <Label>Title font</Label>
        <FontPicker value={design.font} onChange={(f) => set({ font: f })} />
        <TextFormat
          size={tx.titleSize}
          onSize={(v) => setText({ titleSize: v }, "title-size")}
          spacing={tx.titleSpacing}
          onSpacing={(v) => setText({ titleSpacing: v }, "title-spacing")}
          textCase={tx.titleCase}
          onCase={(v) => setText({ titleCase: v })}
          italic={tx.titleItalic}
          onItalic={(v) => setText({ titleItalic: v })}
          maxSize={2.2}
        />
      </div>
      <div>
        <Label>Subtitle font</Label>
        <FontPicker value={tx.subtitleFont} onChange={(f) => setText({ subtitleFont: f })} />
        <TextFormat
          size={tx.subtitleSize}
          onSize={(v) => setText({ subtitleSize: v }, "subtitle-size")}
          spacing={tx.subtitleSpacing}
          onSpacing={(v) => setText({ subtitleSpacing: v }, "subtitle-spacing")}
          textCase={tx.subtitleCase}
          onCase={(v) => setText({ subtitleCase: v })}
          italic={tx.subtitleItalic}
          onItalic={(v) => setText({ subtitleItalic: v })}
          maxSize={2.5}
        />
      </div>
      </fieldset>
      <fieldset disabled={!design.stops.some((x) => x.showLabel)} className={design.stops.some((x) => x.showLabel) ? "" : "opacity-40"}>
      <div>
        <Label>Place name font</Label>
        <p className="text-xs text-ink/50 -mt-1 mb-2">The stop names on the map.</p>
        <button
          onClick={() => setText({ labelFont: "title" })}
          className={`w-full mb-2 rounded-2xl border-2 px-3 py-2 text-sm font-bold ${tx.labelFont === "title" ? "border-coral bg-white" : "border-ink/10 bg-white hover:border-ink/30"}`}
        >
          Same as the title
        </button>
        <FontPicker value={tx.labelFont === "title" ? ("" as FontId) : tx.labelFont} onChange={(f) => setText({ labelFont: f })} />
        <div className="flex flex-wrap gap-2 pt-2">
          {(["none", "upper", "lower"] as TextCase[]).map((c) => (
            <button
              key={c}
              onClick={() => setText({ labelCase: c })}
              className={`rounded-full border-2 px-3 py-1 text-sm font-bold ${tx.labelCase === c ? "border-coral bg-white" : "border-ink/10 bg-white hover:border-ink/30"}`}
            >
              {c === "none" ? "Aa" : c === "upper" ? "AA" : "aa"}
            </button>
          ))}
          <button
            onClick={() => setText({ labelItalic: !tx.labelItalic })}
            className={`rounded-full border-2 px-3 py-1 text-sm font-bold italic ${tx.labelItalic ? "border-coral bg-white" : "border-ink/10 bg-white hover:border-ink/30"}`}
          >
            Italic
          </button>
        </div>
        <p className="text-xs text-ink/50 mt-2">Size: the Label size slider in Style, or tap a name on the map.</p>
      </div>
      </fieldset>
      <fieldset disabled={design.layout === "none"} className={`space-y-5 ${design.layout === "none" ? "opacity-40" : ""}`} title={design.layout === "none" ? "Map only layout: no title or subtitle" : undefined}>
      <div>
        <Label>Alignment</Label>
        <Chips<TextStyle["align"]>
          value={tx.align}
          options={[{ id: "left", label: "⟸ Left" }, { id: "center", label: "Centre" }, { id: "right", label: "Right ⟹" }]}
          onChange={(v) => setText({ align: v })}
        />
        <div className="mt-2">
          <Toggle on={tx.showRoute} onChange={(v) => setText({ showRoute: v })} label="Show the list of stops under the title" />
        </div>
        <p className="text-xs text-ink/50 mt-1">Tip: drag the title or subtitle on the poster to move them anywhere.</p>
        {(tx.titleOffset || tx.subtitleOffset) && (
          <button onClick={() => setText({ titleOffset: undefined, subtitleOffset: undefined })} className="mt-2 text-sm font-bold text-coral-dark">
            ↺ Put the text back in place
          </button>
        )}
      </div>
      </fieldset>
    </div>
  );
}

// ---------------------------------------------------------------- Size

export function SizePanel() {
  const { design, set, region, setRegion } = useEditor();
  return (
    <div className="space-y-5">
      <div>
        <Label>Ship to</Label>
        <Chips value={region} options={REGIONS.map((r) => ({ id: r.id, label: `${r.flag} ${r.label}` }))} onChange={setRegion} />
      </div>
      <div>
        <Label>Orientation</Label>
        <Chips value={design.orientation} options={[{ id: "portrait", label: "▯ Portrait" }, { id: "landscape", label: "▭ Landscape" }]} onChange={(v) => set({ orientation: v })} />
      </div>
      <PrintOptionsPicker value={design} onChange={(patch) => set(patch)} region={region} sizeNote={(id) => sizeNote(design, id)} />
      <StopsCheck />
      <p className="text-xs text-ink/50">
        Printed and shipped by our print partner in {getRegion(region).label}. Free delivery, or express.
      </p>
    </div>
  );
}
