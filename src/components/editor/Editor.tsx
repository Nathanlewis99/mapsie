"use client";
import { useEffect, useLayoutEffect, useRef, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import Poster from "@/components/Poster";
import { useEditor } from "@/lib/store";
import { reverseGeocode } from "@/lib/geo";
import { getProduct, posterAspect } from "@/lib/products";
import { TripPanel, StylePanel, StickersPanel, TextPanel, SizePanel } from "./Panels";

const TABS = [
  { id: "trip", label: "Trip", icon: "🧭" },
  { id: "style", label: "Style", icon: "🎨" },
  { id: "stickers", label: "Stickers", icon: "🐊" },
  { id: "text", label: "Text", icon: "✍️" },
  { id: "size", label: "Size", icon: "📐" },
] as const;
type Tab = (typeof TABS)[number]["id"];

export default function Editor() {
  const store = useEditor();
  const { design, selectedSticker, fitRequest } = store;
  const [tab, setTab] = useState<Tab>("trip");
  const [pickMode, setPickMode] = useState(false);
  const [saving, setSaving] = useState(false);
  const router = useRouter();
  const stage = useRef<HTMLDivElement>(null);
  const [box, setBox] = useState({ w: 0, h: 0 });

  useLayoutEffect(() => {
    const el = stage.current;
    if (!el) return;
    const ro = new ResizeObserver(([e]) => setBox({ w: e.contentRect.width, h: e.contentRect.height }));
    ro.observe(el);
    return () => ro.disconnect();
  }, []);

  // Delete / Backspace removes the selected sticker
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (!selectedSticker || (e.target as HTMLElement).tagName === "INPUT") return;
      if (e.key === "Delete" || e.key === "Backspace") store.removeSticker(selectedSticker);
      if (e.key === "Escape") store.select(null);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [selectedSticker, store]);

  const aspect = posterAspect(design.productId, design.orientation);
  const posterW = Math.floor(Math.max(200, Math.min(box.w - 48, (box.h - 48) / aspect)));
  const sel = design.stickers.find((s) => s.id === selectedSticker);
  const product = getProduct(design.productId);

  const order = async () => {
    setSaving(true);
    const r = await fetch("/api/designs", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(design) });
    const { id } = await r.json();
    router.push(`/checkout/${id}`);
  };

  return (
    <div className="h-dvh flex flex-col">
      <header className="flex items-center justify-between px-5 py-3 border-b border-ink/5 bg-cream">
        <Link href="/" className="font-display text-2xl font-extrabold tracking-tight">
          Mapsie<span className="text-coral">.</span>
        </Link>
        <div className="flex items-center gap-3">
          <button onClick={() => confirm("Start a fresh map? This clears your current design.") && store.reset()} className="hidden sm:block text-sm font-bold text-ink/50 hover:text-ink">
            Start over
          </button>
          <button onClick={order} disabled={saving || design.stops.length === 0} className="rounded-full bg-coral px-5 py-2.5 font-extrabold text-white shadow-lg shadow-coral/30 hover:bg-coral-dark disabled:opacity-40 transition">
            {saving ? "Saving…" : `Order print · £${product.priceGbp}`}
          </button>
        </div>
      </header>

      <div className="flex-1 min-h-0 flex flex-col lg:flex-row">
        {/* poster stage */}
        <div ref={stage} className="relative flex-1 min-h-[60vh] lg:min-h-0 grid place-items-center bg-[radial-gradient(circle_at_30%_20%,#fff_0%,#f1e8da_70%)]">
          {box.w > 0 && (
            <div className={`shadow-[0_30px_60px_-15px_rgba(31,36,48,0.35)] ${pickMode ? "cursor-crosshair [&_canvas]:cursor-crosshair" : ""}`}>
              <Poster
                key={`${design.productId}-${design.orientation}-${design.layout}`}
                design={design}
                width={posterW}
                editable
                selectedSticker={selectedSticker}
                fitRequest={fitRequest}
                handlers={{
                  onView: (view) => store.set({ view }),
                  onStopMove: (id, lng, lat) => store.updateStop(id, { lng, lat }),
                  onStickerMove: (id, lng, lat) => store.updateSticker(id, { lng, lat }),
                  onStickerSelect: (id) => store.select(id),
                  onDropSticker: (src, lng, lat) => store.addSticker({ src, kind: "sticker", lng, lat, size: 9, rotation: 0 }),
                  onMapClick: async (lng, lat) => {
                    if (!pickMode) return;
                    const name = await reverseGeocode(lng, lat);
                    useEditor.getState().addStop({ name, lng, lat });
                  },
                }}
              />
            </div>
          )}

          {sel && (
            <div className="absolute top-4 left-1/2 -translate-x-1/2 flex items-center gap-1 rounded-full bg-ink text-white px-2 py-1.5 shadow-xl text-sm font-bold">
              <button className="px-3 py-1 rounded-full hover:bg-white/15" onClick={() => store.updateSticker(sel.id, { size: Math.max(3, sel.size / 1.15) })}>➖</button>
              <span className="px-1 opacity-60">size</span>
              <button className="px-3 py-1 rounded-full hover:bg-white/15" onClick={() => store.updateSticker(sel.id, { size: Math.min(45, sel.size * 1.15) })}>➕</button>
              <span className="w-px h-5 bg-white/20 mx-1" />
              <button className="px-3 py-1 rounded-full hover:bg-white/15" onClick={() => store.updateSticker(sel.id, { rotation: sel.rotation - 15 })}>⟲</button>
              <button className="px-3 py-1 rounded-full hover:bg-white/15" onClick={() => store.updateSticker(sel.id, { rotation: sel.rotation + 15 })}>⟳</button>
              <span className="w-px h-5 bg-white/20 mx-1" />
              <button className="px-3 py-1 rounded-full hover:bg-white/15" onClick={() => store.addSticker({ ...sel, lng: sel.lng + 0.5 * 2 ** -(design.view.zoom - 2), lat: sel.lat })}>⧉</button>
              <button className="px-3 py-1 rounded-full hover:bg-coral" onClick={() => store.removeSticker(sel.id)}>🗑</button>
              <button className="px-3 py-1 rounded-full hover:bg-white/15 opacity-60" onClick={() => store.select(null)}>Done</button>
            </div>
          )}

          {design.stops.length === 0 && tab === "trip" && (
            <div className="absolute bottom-6 left-1/2 -translate-x-1/2 rounded-full bg-white/95 px-5 py-2.5 shadow-lg text-sm font-bold animate-bounce">
              👉 Start by adding your first stop
            </div>
          )}
        </div>

        {/* sidebar */}
        <aside className="lg:w-[400px] shrink-0 border-t lg:border-t-0 lg:border-l border-ink/5 bg-cream flex flex-col min-h-0">
          <nav className="flex gap-1 p-2 border-b border-ink/5 sticky top-0 bg-cream z-10">
            {TABS.map((t) => (
              <button
                key={t.id}
                onClick={() => setTab(t.id)}
                className={`flex-1 rounded-2xl py-2 text-xs font-extrabold transition ${tab === t.id ? "bg-white shadow-sm text-ink" : "text-ink/50 hover:text-ink"}`}
              >
                <div className="text-lg leading-none mb-0.5">{t.icon}</div>
                {t.label}
              </button>
            ))}
          </nav>
          <div className="flex-1 overflow-y-auto p-5">
            {tab === "trip" && <TripPanel pickMode={pickMode} setPickMode={setPickMode} />}
            {tab === "style" && <StylePanel />}
            {tab === "stickers" && <StickersPanel />}
            {tab === "text" && <TextPanel />}
            {tab === "size" && <SizePanel />}
          </div>
        </aside>
      </div>
    </div>
  );
}
