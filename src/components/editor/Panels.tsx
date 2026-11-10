"use client";
import { useEffect, useRef, useState } from "react";
import { useEditor } from "@/lib/store";
import { searchPlaces, type PlaceResult } from "@/lib/geo";
import { PRESETS, themeFromPreset } from "@/lib/themes";
import { STICKER_PACKS } from "@/lib/stickers";
import { FONTS } from "@/lib/fonts";
import { PRODUCTS } from "@/lib/products";
import type { ThemeColors, Layout } from "@/lib/types";

const Label = ({ children }: { children: React.ReactNode }) => (
  <div className="text-xs font-bold uppercase tracking-wider text-ink/50 mb-2">{children}</div>
);

function Toggle({ on, onChange, label }: { on: boolean; onChange: (v: boolean) => void; label: string }) {
  return (
    <button onClick={() => onChange(!on)} className="flex items-center justify-between w-full py-1.5 text-sm font-semibold">
      {label}
      <span className={`w-10 h-6 rounded-full p-0.5 transition ${on ? "bg-coral" : "bg-ink/15"}`}>
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

// ---------------------------------------------------------------- Trip
export function TripPanel({ pickMode, setPickMode }: { pickMode: boolean; setPickMode: (v: boolean) => void }) {
  const { design, addStop, updateStop, removeStop, moveStop, set, requestFit } = useEditor();
  const [q, setQ] = useState("");
  const [results, setResults] = useState<PlaceResult[]>([]);
  const [active, setActive] = useState(0);
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

  return (
    <div className="space-y-5">
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
        <button
          onClick={() => setPickMode(!pickMode)}
          className={`mt-2 w-full rounded-2xl px-4 py-2.5 text-sm font-bold border-2 border-dashed transition ${pickMode ? "border-coral bg-coral/10 text-coral-dark" : "border-ink/15 text-ink/60 hover:border-ink/30"}`}
        >
          {pickMode ? "✓ Tap the map to drop stops — click to finish" : "📍 Or tap on the map to add stops"}
        </button>
      </div>

      <div>
        <div className="flex items-center justify-between">
          <Label>Your journey ({design.stops.length})</Label>
          {design.stops.length > 0 && (
            <button onClick={requestFit} className="text-xs font-bold text-coral mb-2">Fit map to trip</button>
          )}
        </div>
        {design.stops.length === 0 && (
          <div className="rounded-2xl bg-sand/60 p-4 text-sm text-ink/60">
            Add the places you went, in order. We&apos;ll draw the route between them.
          </div>
        )}
        <ol className="space-y-2">
          {design.stops.map((s, i) => (
            <li
              key={s.id}
              draggable
              onDragStart={() => (dragFrom.current = i)}
              onDragOver={(e) => e.preventDefault()}
              onDrop={() => {
                if (dragFrom.current !== null && dragFrom.current !== i) moveStop(dragFrom.current, i);
                dragFrom.current = null;
              }}
              className="group flex items-center gap-2 rounded-2xl bg-white border border-ink/5 px-2 py-2 shadow-sm"
            >
              <span className="cursor-grab text-ink/30 px-1" title="Drag to reorder">⠿</span>
              <span className="grid place-items-center w-7 h-7 rounded-full text-xs font-extrabold text-white shrink-0" style={{ background: design.theme.colors.accent }}>
                {i + 1}
              </span>
              <input
                value={s.name}
                onChange={(e) => updateStop(s.id, { name: e.target.value })}
                className="flex-1 min-w-0 bg-transparent font-bold outline-none"
              />
              <button title={s.showLabel ? "Hide label" : "Show label"} onClick={() => updateStop(s.id, { showLabel: !s.showLabel })} className={`text-sm px-1 ${s.showLabel ? "" : "opacity-30"}`}>
                🏷️
              </button>
              <button title="Remove" onClick={() => removeStop(s.id)} className="text-ink/30 hover:text-coral px-1 font-bold">✕</button>
            </li>
          ))}
        </ol>
      </div>

      {design.stops.length > 1 && (
        <div className="space-y-3">
          <Label>Route</Label>
          <Toggle on={design.route.show} onChange={(v) => set({ route: { ...design.route, show: v } })} label="Draw route line" />
          <Toggle on={design.route.curved} onChange={(v) => set({ route: { ...design.route, curved: v } })} label="Curvy flight-path lines" />
          <Chips
            value={design.route.style}
            options={[{ id: "dashed", label: "- - Dashed" }, { id: "dotted", label: "··· Dotted" }, { id: "solid", label: "— Solid" }]}
            onChange={(v) => set({ route: { ...design.route, style: v } })}
          />
          <input type="range" min={0.15} max={1.2} step={0.05} value={design.route.width} onChange={(e) => set({ route: { ...design.route, width: +e.target.value } })} className="w-full accent-coral" />
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
        <Label>Details</Label>
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
  const place = (src: string, kind: "sticker" | "photo" = "sticker") =>
    addSticker({ src, kind, lng: cx + jitter(), lat: cy + jitter() * 0.7, size: kind === "photo" ? 16 : 9, rotation: kind === "photo" ? -4 : 0 });

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
        Tap a sticker to add it, or drag it straight onto the map. Then drag it where you want.
      </div>
      <button onClick={() => fileRef.current?.click()} className="w-full rounded-2xl border-2 border-dashed border-ink/15 px-4 py-3 font-bold text-ink/70 hover:border-coral hover:text-coral">
        📸 Add your own photo
      </button>
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
        <input value={design.title} maxLength={48} onChange={(e) => set({ title: e.target.value })} className="w-full rounded-2xl border-2 border-ink/10 bg-white px-4 py-3 font-bold outline-none focus:border-coral" />
      </div>
      <div>
        <Label>Subtitle</Label>
        <input value={design.subtitle} maxLength={60} onChange={(e) => set({ subtitle: e.target.value })} placeholder="e.g. Spring 2026 · 4 countries · 1 big adventure" className="w-full rounded-2xl border-2 border-ink/10 bg-white px-4 py-3 font-semibold outline-none focus:border-coral" />
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
  const { design, set } = useEditor();
  return (
    <div className="space-y-5">
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
              <span className="font-extrabold">£{p.priceGbp}</span>
            </button>
          ))}
        </div>
        <p className="mt-3 text-xs text-ink/50">Museum-quality matte art paper. Free UK delivery, or next-day express.</p>
      </div>
    </div>
  );
}
