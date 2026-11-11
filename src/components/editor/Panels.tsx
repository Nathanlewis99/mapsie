"use client";
import { useEffect, useRef, useState } from "react";
import { useEditor } from "@/lib/store";
import { searchPlaces, MODES, type PlaceResult } from "@/lib/geo";
import { PRESETS, themeFromPreset } from "@/lib/themes";
import { STICKER_PACKS } from "@/lib/stickers";
import { FONTS } from "@/lib/fonts";
import { PRODUCTS, FRAMES, money, getRegion, REGIONS } from "@/lib/products";
import { TEMPLATES } from "@/lib/templates";
import type { ThemeColors, Layout, TravelMode, MarkerStyle, RouteStyle } from "@/lib/types";

export const Label = ({ children }: { children: React.ReactNode }) => (
  <div className="text-xs font-bold uppercase tracking-wider text-ink/50 mb-2">{children}</div>
);

function Toggle({ on, onChange, label }: { on: boolean; onChange: (v: boolean) => void; label: string }) {
  return (
    <button onClick={() => onChange(!on)} className="flex items-center justify-between w-full py-1.5 text-sm font-semibold">
      {label}
      <span className={`w-10 h-6 rounded-full p-0.5 transition shrink-0 ${on ? "bg-coral" : "bg-ink/15"}`}>
        <span className={`block w-5 h-5 rounded-full bg-white shadow transition ${on ? "translate-x-4" : ""}`} />
      </span>
    </button>
  );
}

function Chips<T extends string>({ value, options, onChange }: { value: T; options: { id: T; label: string }[]; onChange: (v: T) => void }) {
  return (
    <div className="flex flex-wrap gap-2">
      {options.map((o) => (
        <button
          key={o.id}
          onClick={() => onChange(o.id)}
          className={`px-3 py-1.5 rounded-full text-sm font-bold border-2 transition ${value === o.id ? "border-coral bg-coral text-white" : "border-ink/10 bg-white hover:border-ink/30"}`}
        >
          {o.label}
        </button>
      ))}
    </div>
  );
}

function Slider({ value, min, max, step, onChange, label }: { value: number; min: number; max: number; step: number; onChange: (v: number) => void; label: string }) {
  return (
    <label className="flex items-center gap-3 py-1.5 text-sm font-semibold">
      <span className="w-24 shrink-0">{label}</span>
      <input type="range" min={min} max={max} step={step} value={value} onChange={(e) => onChange(+e.target.value)} className="flex-1 accent-coral" />
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
  const [active, setActive] = useState(0);
  const [pasteOpen, setPasteOpen] = useState(false);
  const [paste, setPaste] = useState("");
  const [pasting, setPasting] = useState<string | null>(null);
  const [openStop, setOpenStop] = useState<string | null>(null);
  const dragFrom = useRef<number | null>(null);

  useEffect(() => {
    if (q.trim().length < 2) return setResults([]);
    const ctl = new AbortController();
    const t = setTimeout(() => searchPlaces(q, ctl.signal).then((r) => (setResults(r), setActive(0))).catch(() => {}), 220);
    return () => (clearTimeout(t), ctl.abort());
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
              if (e.key === "Enter" && results[active]) pick(results[active]);
            }}
            placeholder="Search a city, island, park…"
            className="w-full rounded-2xl border-2 border-ink/10 bg-white px-4 py-3 font-semibold outline-none focus:border-coral"
          />
          {results.length > 0 && (
            <div className="absolute z-20 mt-2 w-full rounded-2xl bg-white shadow-xl border border-ink/5 overflow-hidden">
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
          <Toggle on={design.route.show} onChange={(v) => set({ route: { ...design.route, show: v } })} label="Draw the route" />
          <Toggle on={design.route.modeIcons} onChange={(v) => set({ route: { ...design.route, modeIcons: v } })} label="Show ✈️ 🚗 🚆 icons on legs" />
          <Toggle on={design.route.curved} onChange={(v) => set({ route: { ...design.route, curved: v } })} label="Curvy flight paths" />
          <div className="pt-2">
            <Chips<RouteStyle>
              value={design.route.style}
              options={[{ id: "auto", label: "✨ Auto" }, { id: "dashed", label: "Dashed" }, { id: "dotted", label: "Dotted" }, { id: "solid", label: "Solid" }]}
              onChange={(v) => set({ route: { ...design.route, style: v } })}
            />
          </div>
          <Slider label="Thickness" min={0.15} max={1.2} step={0.05} value={design.route.width} onChange={(v) => set({ route: { ...design.route, width: v } }, "route-width")} />
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
              <div className="h-14 rounded-xl relative overflow-hidden" style={{ background: p.colors.land }}>
                <div className="absolute -right-3 -bottom-4 w-16 h-12 rounded-full" style={{ background: p.colors.water }} />
                <div className="absolute left-2 top-3 w-10 h-5 rounded-full opacity-80" style={{ background: p.colors.park }} />
                <svg className="absolute inset-0" viewBox="0 0 60 40"><path d="M6 32 Q 25 4 52 14" fill="none" stroke={p.colors.accent} strokeWidth="2.5" strokeDasharray="4 3" strokeLinecap="round" /></svg>
              </div>
              <div className="text-xs font-bold mt-1">{p.name}</div>
            </button>
          ))}
        </div>
      </div>

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
          options={[{ id: "number", label: "① Numbers" }, { id: "pin", label: "📍 Pins" }, { id: "heart", label: "♥ Hearts" }, { id: "dot", label: "• Dots" }]}
          onChange={(v) => set({ markers: { ...design.markers, style: v } })}
        />
        <div className="mt-2">
          <Toggle on={design.markers.showDates} onChange={(v) => set({ markers: { ...design.markers, showDates: v } })} label="📅 Show dates under stop names" />
        </div>
      </div>

      <div>
        <Label>Details</Label>
        <Toggle on={design.visited.show} onChange={(v) => set({ visited: { ...design.visited, show: v } })} label="🌍 Highlight countries I visited" />
        {design.visited.show && (
          <Slider label="Highlight" min={0.1} max={0.8} step={0.05} value={design.visited.opacity} onChange={(v) => set({ visited: { ...design.visited, opacity: v } }, "visited-opacity")} />
        )}
        <Toggle on={t.relief} onChange={(v) => setTheme({ relief: v })} label="⛰️ Terrain shading" />
        <Toggle on={t.labels} onChange={(v) => setTheme({ labels: v })} label="🔤 Place names" />
        <Toggle on={t.texture} onChange={(v) => setTheme({ texture: v })} label="📜 Aged paper texture" />
      </div>
    </div>
  );
}

// ---------------------------------------------------------------- Stickers
export function StickersPanel() {
  const { design, addSticker } = useEditor();
  const fileRef = useRef<HTMLInputElement>(null);
  const [cx, cy] = design.view.center;
  // Scatter new stickers around the middle of the map so they don't stack up.
  const degPerPx = 360 / (512 * 2 ** design.view.zoom);
  const jitter = () => (Math.random() - 0.5) * 220 * degPerPx;
  const at = () => ({ lng: cx + jitter(), lat: cy + jitter() * 0.7 });
  const place = (src: string, kind: "sticker" | "photo" = "sticker") =>
    addSticker({ src, kind, ...at(), size: kind === "photo" ? 16 : 9, rotation: kind === "photo" ? -4 : 0 });

  const onFile = async (f: File) => {
    const img = await createImageBitmap(f);
    const scale = Math.min(1, 1600 / Math.max(img.width, img.height));
    const c = document.createElement("canvas");
    c.width = Math.round(img.width * scale);
    c.height = Math.round(img.height * scale);
    c.getContext("2d")!.drawImage(img, 0, 0, c.width, c.height);
    place(c.toDataURL("image/jpeg", 0.88), "photo");
  };

  return (
    <div className="space-y-5">
      <div className="rounded-2xl bg-sand/60 p-3 text-sm text-ink/70">
        Tap a sticker to add it, or drag it onto the map. Drag the corner handle to resize, the top one to rotate.
      </div>
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
      </div>
      <input ref={fileRef} type="file" accept="image/*" hidden onChange={(e) => e.target.files?.[0] && onFile(e.target.files[0])} />
      {STICKER_PACKS.map((pack) => (
        <div key={pack.name}>
          <Label>{pack.name}</Label>
          <div className="grid grid-cols-6 gap-1.5">
            {pack.items.map((src) => (
              <button
                key={src}
                draggable
                onDragStart={(e) => e.dataTransfer.setData("text/mapsie-sticker", src)}
                onClick={() => place(src)}
                className="aspect-square rounded-xl bg-white border border-ink/5 p-1.5 hover:scale-110 hover:-rotate-6 transition"
              >
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img src={src} alt="" className="w-full h-full pointer-events-none" />
              </button>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

// ---------------------------------------------------------------- Text
export function TextPanel() {
  const { design, set } = useEditor();
  return (
    <div className="space-y-5">
      <div>
        <Label>Title</Label>
        <input value={design.title} maxLength={48} onChange={(e) => set({ title: e.target.value }, "title")} className="w-full rounded-2xl border-2 border-ink/10 bg-white px-4 py-3 font-bold outline-none focus:border-coral" />
      </div>
      <div>
        <Label>Subtitle</Label>
        <input value={design.subtitle} maxLength={60} onChange={(e) => set({ subtitle: e.target.value }, "subtitle")} placeholder="e.g. Spring 2026 · 4 countries · 1 big adventure" className="w-full rounded-2xl border-2 border-ink/10 bg-white px-4 py-3 font-semibold outline-none focus:border-coral" />
      </div>
      <div>
        <Label>Font</Label>
        <div className="grid grid-cols-2 gap-2">
          {FONTS.map((f) => (
            <button key={f.id} onClick={() => set({ font: f.id })} className={`rounded-2xl border-2 px-3 py-3 text-xl transition ${design.font === f.id ? "border-coral bg-white" : "border-ink/10 bg-white hover:border-ink/30"}`} style={{ fontFamily: f.css }}>
              {f.name}
            </button>
          ))}
        </div>
      </div>
      <div>
        <Label>Layout</Label>
        <Chips<Layout>
          value={design.layout}
          options={[{ id: "band", label: "Title below" }, { id: "border", label: "Framed border" }, { id: "overlay", label: "Full bleed" }]}
          onChange={(v) => set({ layout: v })}
        />
      </div>
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
      <div>
        <Label>Print size</Label>
        <div className="space-y-2">
          {PRODUCTS.map((p) => (
            <button key={p.id} onClick={() => set({ productId: p.id })} className={`flex w-full items-center justify-between rounded-2xl border-2 px-4 py-3 transition ${design.productId === p.id ? "border-coral bg-white" : "border-ink/10 bg-white hover:border-ink/30"}`}>
              <span className="font-bold">{p.label}</span>
              <span className="text-sm text-ink/50">{p.widthCm} × {p.heightCm} cm</span>
              <span className="font-extrabold">{money(region, p.price[region])}</span>
            </button>
          ))}
        </div>
      </div>
      <div>
        <Label>Frame</Label>
        <div className="grid grid-cols-4 gap-2">
          {FRAMES.map((f) => {
            const p = PRODUCTS.find((x) => x.id === design.productId)!;
            return (
              <button key={f.id} onClick={() => set({ frame: f.id })} className={`rounded-2xl border-2 p-2 text-center transition bg-white ${design.frame === f.id ? "border-coral" : "border-ink/10 hover:border-ink/30"}`}>
                <div className="mx-auto w-9 h-11 rounded-sm bg-sand" style={{ boxShadow: f.id === "none" ? "inset 0 0 0 1px #0002" : `inset 0 0 0 5px ${f.color}` }} />
                <div className="text-[11px] font-bold mt-1 leading-tight">{f.label}</div>
                <div className="text-[11px] text-ink/50">{f.id === "none" ? "—" : `+${money(region, p.framePrice[region])}`}</div>
              </button>
            );
          })}
        </div>
      </div>
      <p className="text-xs text-ink/50">
        Museum-quality matte art paper. Free delivery to {getRegion(region).label}, or express.
      </p>
    </div>
  );
}
