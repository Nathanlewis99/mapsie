"use client";
import { useEffect, useLayoutEffect, useRef, useState } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import FramedPoster, { frameWidth } from "@/components/FramedPoster";
import WallPreview from "@/components/WallPreview";
import { useEditor } from "@/lib/store";
import { reverseGeocode } from "@/lib/geo";
import { itemPrice, money, posterAspect } from "@/lib/products";
import { FONTS } from "@/lib/fonts";
import { ART_STYLES, stickerSrc, type ArtStyleId } from "@/lib/stickers";
import { PALETTE_NAMES, getOriginal, type OriginalStyle } from "@/lib/originals";
import { normalizeDesign, type Design } from "@/lib/types";
import { TripPanel, StylePanel, StickersPanel, TextPanel, SizePanel } from "./Panels";

const TABS = [
  { id: "trip", label: "Trip", icon: "🧭" },
  { id: "style", label: "Style", icon: "🎨" },
  { id: "stickers", label: "Stickers", icon: "🐊" },
  { id: "text", label: "Text", icon: "✍️" },
  { id: "size", label: "Size", icon: "🖼️" },
] as const;
type Tab = (typeof TABS)[number]["id"];

async function saveSnapshot(design: Design): Promise<string> {
  const r = await fetch("/api/designs", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(design) });
  if (!r.ok) throw new Error("save failed");
  return (await r.json()).id;
}

export default function Editor() {
  const store = useEditor();
  const { design, selectedSticker, fitRequest, region, past, future, savedId, dirty } = store;
  const [me, setMe] = useState<{ user: { email: string; name: string | null; picture: string | null } | null; googleEnabled: boolean } | null>(null);
  const [tab, setTab] = useState<Tab>("trip");
  const [pickMode, setPickMode] = useState(false);
  const [busy, setBusy] = useState<"" | "order" | "share" | "save">("");
  const [toast, setToast] = useState("");
  const [wall, setWall] = useState(false);
  const router = useRouter();
  const params = useSearchParams();
  const stage = useRef<HTMLDivElement>(null);
  const [box, setBox] = useState({ w: 0, h: 0 });

  useLayoutEffect(() => {
    const el = stage.current;
    if (!el) return;
    const ro = new ResizeObserver(([e]) => setBox({ w: e.contentRect.width, h: e.contentRect.height }));
    ro.observe(el);
    return () => ro.disconnect();
  }, []);

  useEffect(() => {
    fetch("/api/auth/me").then((r) => r.json()).then(setMe).catch(() => setMe({ user: null, googleEnabled: false }));
  }, []);

  /** Save to the signed-in user's account (sends them to sign in first if needed). */
  const save = async () => {
    if (!me?.user) {
      window.location.href = `/signin?next=${encodeURIComponent("/create?save=1")}`;
      return;
    }
    setBusy("save");
    try {
      const st = useEditor.getState();
      const r = await fetch("/api/me/designs", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ design: st.design, id: st.savedId ?? undefined }),
      });
      if (!r.ok) throw new Error();
      st.setSaved((await r.json()).id);
      setToast("Saved to your account ✓");
    } catch {
      setToast("Couldn't save, please try again.");
    }
    setBusy("");
  };

  // /create?saved=<id> opens a design from the account, ?new=1 starts fresh,
  // ?save=1 finishes a save that was interrupted by signing in.
  useEffect(() => {
    if (!me) return;
    const saved = params.get("saved");
    if (saved) {
      fetch(`/api/me/designs/${saved}`)
        .then((r) => (r.ok ? r.json() : Promise.reject()))
        .then((s: { id: string; design: Design }) => {
          useEditor.getState().loadSaved(s.id, s.design);
          router.replace("/create");
        })
        .catch(() => setToast("Sorry, we couldn't open that map."));
    } else if (params.get("new")) {
      useEditor.getState().reset();
      router.replace("/create");
    } else if (params.get("save") && me.user) {
      router.replace("/create");
      save();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [params, me]);

  // Open a shared design: /create?d=<id>
  useEffect(() => {
    const id = params.get("d");
    if (!id) return;
    fetch(`/api/designs/${id}`)
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then((d: Design) => {
        useEditor.getState().load(normalizeDesign(d));
        setToast("Design loaded. Make it your own!");
        router.replace("/create");
      })
      .catch(() => setToast("Sorry, we couldn't find that design."));
  }, [params, router]);

  useEffect(() => {
    if (!toast) return;
    const t = setTimeout(() => setToast(""), 3500);
    return () => clearTimeout(t);
  }, [toast]);

  // Keyboard: undo/redo, delete sticker, escape
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      const typing = ["INPUT", "TEXTAREA"].includes((e.target as HTMLElement).tagName);
      const mod = e.metaKey || e.ctrlKey;
      if (mod && e.key.toLowerCase() === "z" && !typing) {
        e.preventDefault();
        if (e.shiftKey) store.redo();
        else store.undo();
        return;
      }
      if (mod && e.key.toLowerCase() === "y" && !typing) return e.preventDefault(), store.redo();
      if (typing) return;
      if (selectedSticker && (e.key === "Delete" || e.key === "Backspace")) store.removeSticker(selectedSticker);
      if (e.key === "Escape") {
        store.select(null);
        setPickMode(false);
        setWall(false);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [selectedSticker, store]);

  const aspect = posterAspect(design.productId, design.orientation);
  const pad = box.w < 640 ? 24 : 56;
  const fitW = Math.min(box.w - pad, (box.h - pad) / aspect);
  const posterW = Math.floor(Math.max(180, fitW - frameWidth(design, fitW) * 2));
  const sel = design.stickers.find((s) => s.id === selectedSticker);
  const price = itemPrice(design.productId, design.frame, region);

  const order = async () => {
    setBusy("order");
    try {
      const id = await saveSnapshot(design);
      router.push(`/checkout/${id}`);
    } catch {
      setToast("Couldn't save your design, please try again.");
      setBusy("");
    }
  };

  const share = async () => {
    setBusy("share");
    try {
      const id = await saveSnapshot(design);
      const url = `${location.origin}/d/${id}`;
      if (navigator.share && matchMedia("(pointer: coarse)").matches) await navigator.share({ title: design.title, url }).catch(() => {});
      else await navigator.clipboard.writeText(url).catch(() => {});
      setToast("Link copied! Anyone with it can see your map.");
    } catch {
      setToast("Couldn't create a link, please try again.");
    }
    setBusy("");
  };

  const iconBtn = "w-8 h-8 sm:w-10 sm:h-10 grid place-items-center rounded-full hover:bg-ink/5 disabled:opacity-25 text-base sm:text-lg";

  return (
    <div className="h-dvh flex flex-col">
      <header className="flex items-center justify-between gap-2 px-3 sm:px-5 py-2.5 border-b border-ink/5 bg-cream">
        <Link href="/" className="font-display text-xl sm:text-2xl font-extrabold tracking-tight shrink-0">
          Mapsie<span className="text-coral">.</span>
        </Link>
        <div className="flex items-center gap-0.5 sm:gap-1">
          <button title="Undo (Ctrl+Z)" className={iconBtn} disabled={!past.length} onClick={store.undo}>↶</button>
          <button title="Redo (Ctrl+Shift+Z)" className={iconBtn} disabled={!future.length} onClick={store.redo}>↷</button>
          <span className="w-px h-6 bg-ink/10 mx-1 hidden sm:block" />
          <button title="See it on a wall" className={`${iconBtn} sm:w-auto sm:px-3 sm:text-sm sm:font-bold`} onClick={() => setWall(true)} disabled={!design.stops.length}>
            🛋️<span className="hidden sm:inline ml-1">On the wall</span>
          </button>
          <button title="Share a link" className={`${iconBtn} sm:w-auto sm:px-3 sm:text-sm sm:font-bold`} onClick={share} disabled={!!busy || !design.stops.length}>
            🔗<span className="hidden sm:inline ml-1">{busy === "share" ? "…" : "Share"}</span>
          </button>
          <button
            title={me?.user ? "Save to your account" : "Sign in to save"}
            className={`${iconBtn} sm:w-auto sm:px-3 sm:text-sm sm:font-bold`}
            onClick={save}
            disabled={busy === "save" || (!!savedId && !dirty)}
          >
            {savedId && !dirty ? "✓" : "💾"}
            <span className="hidden sm:inline ml-1">{busy === "save" ? "Saving…" : savedId && !dirty ? "Saved" : "Save"}</span>
          </button>
          <button
            onClick={() => confirm("Start a fresh map? (You can undo this.)") && store.reset()}
            className="hidden md:block text-sm font-bold text-ink/50 hover:text-ink px-2"
          >
            New
          </button>
          <button onClick={order} disabled={!!busy || design.stops.length === 0} className="ml-1 rounded-full bg-coral px-3 sm:px-5 py-2 sm:py-2.5 text-sm sm:text-base font-extrabold text-white shadow-lg shadow-coral/30 hover:bg-coral-dark disabled:opacity-40 transition whitespace-nowrap">
            {busy === "order" ? "Saving…" : <>Order<span className="hidden sm:inline"> print</span> · {money(region, price)}</>}
          </button>
          {me?.user ? (
            <Link href="/account" title="My account" className="ml-1 shrink-0">
              {me.user.picture ? (
                // eslint-disable-next-line @next/next/no-img-element
                <img src={me.user.picture} alt="My account" referrerPolicy="no-referrer" className="w-9 h-9 rounded-full" />
              ) : (
                <span className="grid place-items-center w-9 h-9 rounded-full bg-ink text-white font-extrabold">{(me.user.name ?? me.user.email)[0].toUpperCase()}</span>
              )}
            </Link>
          ) : (
            me && (
              <Link href="/signin?next=/create" className="hidden sm:block ml-1 text-sm font-bold text-ink/60 hover:text-ink px-2 whitespace-nowrap">
                Sign in
              </Link>
            )
          )}
        </div>
      </header>

      <div className="flex-1 min-h-0 flex flex-col lg:flex-row">
        {/* poster stage */}
        <div ref={stage} className="relative h-[54dvh] lg:h-auto lg:flex-1 shrink-0 grid place-items-center bg-[radial-gradient(circle_at_30%_20%,#fff_0%,#f1e8da_70%)] overflow-hidden">
          {box.w > 0 && (
            <div className={pickMode ? "[&_canvas]:!cursor-crosshair" : ""}>
              <FramedPoster
                key={`${design.productId}-${design.orientation}-${design.layout}-${design.frame}`}
                design={design}
                width={posterW}
                editable
                selectedSticker={selectedSticker}
                fitRequest={fitRequest}
                handlers={{
                  onView: (view) => store.setView(view),
                  onStopMove: (id, lng, lat) => store.updateStop(id, { lng, lat }),
                  onStickerMove: (id, lng, lat) => store.updateSticker(id, { lng, lat }),
                  onStickerChange: (id, patch) => store.updateSticker(id, patch),
                  onStickerSelect: (id) => store.select(id),
                  onDropSticker: (payload, lng, lat) => {
                    if (payload.startsWith("orig:")) {
                      const { style, palette } = design.originals;
                      store.addSticker({ kind: "original", name: payload.slice(5), origStyle: style, palette, src: "", lng, lat, size: 15, rotation: 0 });
                      return;
                    }
                    const [name, art] = payload.split("|") as [string, ArtStyleId];
                    store.addSticker({ kind: "sticker", name, art, src: stickerSrc(name, art), lng, lat, size: 9, rotation: 0 });
                  },
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
            <div className="absolute top-3 left-1/2 -translate-x-1/2 flex items-center gap-1 rounded-full bg-ink text-white px-2 py-1.5 shadow-xl text-sm font-bold max-w-[96%] overflow-x-auto">
              {sel.kind === "text" && (
                <>
                  <input
                    autoFocus
                    value={sel.text ?? ""}
                    onChange={(e) => store.updateSticker(sel.id, { text: e.target.value }, `text-${sel.id}`)}
                    className="bg-white/10 rounded-full px-3 py-1 outline-none w-40 placeholder:text-white/40"
                    placeholder="Type your note"
                  />
                  <select
                    value={sel.font ?? "caveat"}
                    onChange={(e) => store.updateSticker(sel.id, { font: e.target.value as Design["font"] })}
                    className="bg-white/10 rounded-full px-2 py-1 outline-none"
                  >
                    {FONTS.map((f) => <option key={f.id} value={f.id} className="text-ink">{f.name}</option>)}
                  </select>
                  <input type="color" value={sel.color ?? design.theme.colors.ink} onChange={(e) => store.updateSticker(sel.id, { color: e.target.value }, `color-${sel.id}`)} className="w-7 h-7 rounded-full bg-transparent border-0 p-0" />
                  <span className="w-px h-5 bg-white/20 mx-1" />
                </>
              )}
              {sel.kind === "original" && sel.name && (
                <>
                  <select
                    title="Style"
                    value={sel.origStyle ?? "papercut"}
                    onChange={(e) => store.updateSticker(sel.id, { origStyle: e.target.value as OriginalStyle, palette: "auto" })}
                    className="bg-white/10 rounded-full px-2 py-1 outline-none"
                  >
                    <option value="papercut" className="text-ink">Papercut</option>
                    <option value="line" className="text-ink">Line</option>
                  </select>
                  <select
                    title="Colours"
                    value={sel.palette ?? "auto"}
                    onChange={(e) => store.updateSticker(sel.id, { palette: e.target.value })}
                    className="bg-white/10 rounded-full px-2 py-1 outline-none"
                  >
                    <option value="auto" className="text-ink">Match map</option>
                    {(getOriginal(sel.name)?.[sel.origStyle ?? "papercut"] ?? []).map((p) => (
                      <option key={p} value={p} className="text-ink">{PALETTE_NAMES[sel.origStyle ?? "papercut"][p] ?? p}</option>
                    ))}
                  </select>
                  <span className="w-px h-5 bg-white/20 mx-1" />
                </>
              )}
              {sel.kind === "sticker" && sel.name && (
                <>
                  <select
                    title="Art style for this sticker"
                    value={sel.art ?? design.stickerStyle}
                    onChange={(e) => store.updateSticker(sel.id, { art: e.target.value as ArtStyleId, src: stickerSrc(sel.name!, e.target.value as ArtStyleId) })}
                    className="bg-white/10 rounded-full px-2 py-1 outline-none"
                  >
                    {ART_STYLES.map((a) => <option key={a.id} value={a.id} className="text-ink">{a.name}</option>)}
                  </select>
                  <span className="w-px h-5 bg-white/20 mx-1" />
                </>
              )}
              <button title="Duplicate" className="px-3 py-1 rounded-full hover:bg-white/15" onClick={() => store.addSticker({ ...sel, lng: sel.lng + 40 * (360 / (512 * 2 ** design.view.zoom)) })}>⧉</button>
              <button title="Bring to front" className="px-3 py-1 rounded-full hover:bg-white/15" onClick={() => { store.removeSticker(sel.id); store.addSticker({ ...sel }); }}>⬆</button>
              <button title="Delete" className="px-3 py-1 rounded-full hover:bg-coral" onClick={() => store.removeSticker(sel.id)}>🗑</button>
              <button className="px-3 py-1 rounded-full hover:bg-white/15 opacity-70" onClick={() => store.select(null)}>Done</button>
            </div>
          )}

          {design.stops.length === 0 && tab === "trip" && (
            <div className="absolute bottom-3 sm:bottom-5 left-1/2 -translate-x-1/2 rounded-full bg-white/95 px-4 sm:px-5 py-2 sm:py-2.5 shadow-lg text-xs sm:text-sm font-bold animate-bounce whitespace-nowrap">
              👉 Pick a trip or add your first stop
            </div>
          )}
          {toast && (
            <div className="absolute bottom-5 left-1/2 -translate-x-1/2 rounded-full bg-ink text-white px-5 py-2.5 shadow-lg text-sm font-bold whitespace-nowrap">{toast}</div>
          )}
        </div>

        {/* sidebar */}
        <aside className="flex-1 lg:flex-none lg:w-[400px] min-h-0 border-t lg:border-t-0 lg:border-l border-ink/5 bg-cream flex flex-col">
          <nav className="flex gap-1 p-2 border-b border-ink/5 bg-cream">
            {TABS.map((t) => (
              <button
                key={t.id}
                onClick={() => setTab(t.id)}
                className={`flex-1 rounded-2xl py-1.5 sm:py-2 text-xs font-extrabold transition ${tab === t.id ? "bg-white shadow-sm text-ink" : "text-ink/50 hover:text-ink"}`}
              >
                <div className="text-lg leading-none mb-0.5">{t.icon}</div>
                {t.label}
              </button>
            ))}
          </nav>
          <div className="flex-1 overflow-y-auto p-4 sm:p-5">
            {tab === "trip" && <TripPanel pickMode={pickMode} setPickMode={setPickMode} />}
            {tab === "style" && <StylePanel />}
            {tab === "stickers" && <StickersPanel />}
            {tab === "text" && <TextPanel />}
            {tab === "size" && <SizePanel />}
          </div>
        </aside>
      </div>

      {wall && (
        <div className="fixed inset-0 z-50 bg-ink/60 backdrop-blur-sm grid place-items-center p-4" onClick={() => setWall(false)}>
          <div className="w-full max-w-4xl rounded-3xl bg-cream p-4 sm:p-6 shadow-2xl" onClick={(e) => e.stopPropagation()}>
            <div className="flex items-center justify-between mb-4">
              <h2 className="font-display text-2xl font-extrabold">How it&apos;ll look at home</h2>
              <button onClick={() => setWall(false)} className="w-9 h-9 rounded-full hover:bg-ink/5 font-bold">✕</button>
            </div>
            <WallPreview design={design} />
            <div className="mt-4 flex justify-end gap-2">
              <button onClick={() => { setWall(false); setTab("size"); }} className="rounded-full border-2 border-ink/15 px-5 py-2.5 font-bold">Change size or frame</button>
              <button onClick={order} className="rounded-full bg-coral px-5 py-2.5 font-extrabold text-white">Order · {money(region, price)}</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
