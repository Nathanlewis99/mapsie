"use client";
import { useEffect, useLayoutEffect, useRef, useState } from "react";
import Logo from "@/components/Logo";
import Icon from "@/components/Icon";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import FramedPoster, { frameWidth } from "@/components/FramedPoster";
import WallPreview from "@/components/WallPreview";
import { useEditor } from "@/lib/store";
import { reverseGeocode } from "@/lib/geo";
import { itemPrice, money, posterAspect, REGIONS } from "@/lib/products";
import { FONTS, fontBold, fontCss } from "@/lib/fonts";
import { ART_STYLES, stickerSrc, type ArtStyleId } from "@/lib/stickers";
import { PALETTE_NAMES, getOriginal, type OriginalStyle } from "@/lib/originals";
import { normalizeDesign, type Design } from "@/lib/types";
import { TripPanel, StylePanel, StickersPanel, TextPanel, SizePanel } from "./Panels";
import { track } from "@/lib/track";

const TABS = [
  { id: "trip", label: "Trip", icon: "route" },
  { id: "style", label: "Style", icon: "palette" },
  { id: "stickers", label: "Stickers", icon: "sticker" },
  { id: "text", label: "Text", icon: "type" },
  { id: "size", label: "Size", icon: "frame" },
] as const;
type Tab = (typeof TABS)[number]["id"];

async function saveSnapshot(design: Design): Promise<string> {
  const r = await fetch("/api/designs", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(design) });
  if (!r.ok) throw new Error("save failed");
  return (await r.json()).id;
}

export default function Editor() {
  const store = useEditor();
  const { design, selectedSticker, selectedLabel, fitRequest, region, past, future, savedId, dirty, roadsLoading } = store;
  const labelStop = design.stops.find((s) => s.id === selectedLabel);
  const [me, setMe] = useState<{ user: { email: string; name: string | null; picture: string | null } | null; googleEnabled: boolean } | null>(null);
  const [tab, setTab] = useState<Tab>("trip");
  const [pickMode, setPickMode] = useState(false);
  const [busy, setBusy] = useState<"" | "order" | "share" | "save">("");
  const [toast, setToast] = useState("");
  const [wall, setWall] = useState(false);
  const [fontMenu, setFontMenu] = useState(false);
  useEffect(() => setFontMenu(false), [selectedSticker]);
  // "Lock framing": the map stays put and the poster itself can be zoomed and panned,
  // so labels and stickers are easy to rearrange on a phone.
  const [locked, setLocked] = useState(false);
  const [zoom, setZoom] = useState({ k: 1, x: 0, y: 0 });
  const zoomRef = useRef(zoom);
  zoomRef.current = zoom;
  const lockedRef = useRef(locked);
  lockedRef.current = locked;
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
      track("saved_design");
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
        store.selectLabel(null);
        setPickMode(false);
        setWall(false);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [selectedSticker, store]);

  useEffect(() => {
    const el = stage.current;
    if (!el) return;
    const clampK = (k: number) => Math.min(5, Math.max(1, k));
    // Zoom about a point (client coords) so what's under the finger/cursor stays put.
    const zoomAt = (k2: number, cx: number, cy: number) => {
      const r = el.getBoundingClientRect();
      const { k, x, y } = zoomRef.current;
      const nk = clampK(k2);
      const px = cx - r.left - r.width / 2, py = cy - r.top - r.height / 2;
      const nx = nk === 1 ? 0 : px - ((px - x) * nk) / k;
      const ny = nk === 1 ? 0 : py - ((py - y) * nk) / k;
      setZoom({ k: nk, x: nx, y: ny });
    };
    const onWheel = (e: WheelEvent) => {
      if (!lockedRef.current) return;
      e.preventDefault();
      e.stopPropagation();
      zoomAt(zoomRef.current.k * Math.exp(-e.deltaY * (e.ctrlKey ? 0.01 : 0.0025)), e.clientX, e.clientY);
    };
    const pts = new Map<number, { x: number; y: number }>();
    let pinch: { d: number; k: number; mx: number; my: number; x: number; y: number } | null = null;
    let pan: { sx: number; sy: number; k: number; x: number; y: number } | null = null;
    const onDown = (e: PointerEvent) => {
      if (!lockedRef.current) return;
      pts.set(e.pointerId, { x: e.clientX, y: e.clientY });
      if (pts.size === 2) {
        const [a, b] = [...pts.values()];
        const { k, x, y } = zoomRef.current;
        pinch = { d: Math.hypot(a.x - b.x, a.y - b.y) || 1, k, mx: (a.x + b.x) / 2, my: (a.y + b.y) / 2, x, y };
        pan = null;
        e.stopPropagation();
      } else if (pts.size === 1) {
        // One finger on empty map (not a pin, label or sticker) pans the zoomed poster.
        const t = e.target as HTMLElement;
        if (t.closest(".maplibregl-canvas") || t === el) pan = { sx: e.clientX, sy: e.clientY, ...zoomRef.current };
      }
    };
    const onMove = (e: PointerEvent) => {
      if (!pts.has(e.pointerId)) return;
      pts.set(e.pointerId, { x: e.clientX, y: e.clientY });
      if (pinch && pts.size >= 2) {
        const [a, b] = [...pts.values()];
        const d = Math.hypot(a.x - b.x, a.y - b.y);
        const mx = (a.x + b.x) / 2, my = (a.y + b.y) / 2;
        const r = el.getBoundingClientRect();
        const nk = clampK((pinch.k * d) / pinch.d);
        const px = pinch.mx - r.left - r.width / 2, py = pinch.my - r.top - r.height / 2;
        setZoom({ k: nk, x: px - ((px - pinch.x) * nk) / pinch.k + (mx - pinch.mx), y: py - ((py - pinch.y) * nk) / pinch.k + (my - pinch.my) });
      } else if (pan && zoomRef.current.k > 1) {
        setZoom({ k: pan.k, x: pan.x + e.clientX - pan.sx, y: pan.y + e.clientY - pan.sy });
      }
    };
    const onUp = (e: PointerEvent) => {
      pts.delete(e.pointerId);
      if (pts.size < 2) pinch = null;
      if (pts.size === 0) pan = null;
    };
    el.addEventListener("wheel", onWheel, { passive: false, capture: true });
    el.addEventListener("pointerdown", onDown, true);
    window.addEventListener("pointermove", onMove);
    window.addEventListener("pointerup", onUp);
    window.addEventListener("pointercancel", onUp);
    return () => {
      el.removeEventListener("wheel", onWheel, true);
      el.removeEventListener("pointerdown", onDown, true);
      window.removeEventListener("pointermove", onMove);
      window.removeEventListener("pointerup", onUp);
      window.removeEventListener("pointercancel", onUp);
    };
  }, []);
  useEffect(() => {
    if (!locked) setZoom({ k: 1, x: 0, y: 0 });
  }, [locked]);

  // Funnel analytics (anonymous): opened the editor, added a stop, made it their own.
  const firstLook = useRef<string | null>(null);
  const stopCount = useRef<number | null>(null);
  useEffect(() => track("editor_open"), []);
  useEffect(() => {
    if (stopCount.current !== null && design.stops.length > stopCount.current) track("stop_added");
    stopCount.current = design.stops.length;
  }, [design.stops.length]);
  const lookKey = JSON.stringify([design.theme, design.text, design.title, design.subtitle, design.stickers.length, design.markers, design.font]);
  useEffect(() => {
    if (firstLook.current !== null && firstLook.current !== lookKey) track("customised");
    firstLook.current = lookKey;
  }, [lookKey]);
  useEffect(() => {
    if (wall) track("wall_preview");
  }, [wall]);
  useEffect(() => {
    if (locked) track("lock_framing");
  }, [locked]);

  const aspect = posterAspect(design.productId, design.orientation);
  const pad = box.w < 640 ? 24 : 56;
  const fitW = Math.min(box.w - pad, (box.h - pad) / aspect);
  const posterW = Math.floor(Math.max(180, fitW - frameWidth(design, fitW) * 2));
  const sel = design.stickers.find((s) => s.id === selectedSticker);
  const price = itemPrice(design, region);

  const order = async () => {
    track("order_click");
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
      track("shared");
      setToast("Link copied! Anyone with it can see your map.");
    } catch {
      setToast("Couldn't create a link, please try again.");
    }
    setBusy("");
  };

  const iconBtn = "w-9 h-9 grid place-items-center rounded-full text-ink/70 hover:text-ink hover:bg-ink/5 disabled:opacity-25 disabled:hover:bg-transparent transition";
  const textBtn = "inline-flex items-center gap-2 h-9 px-2 lg:px-3 rounded-full text-sm font-semibold text-ink/70 hover:text-ink hover:bg-ink/5 disabled:opacity-30 disabled:hover:bg-transparent transition";

  return (
    <div className="h-dvh flex flex-col">
      <header className="flex items-center justify-between gap-3 px-3 sm:px-6 h-14 sm:h-16 border-b border-ink/10 bg-cream">
        <Link href="/" className="font-display text-xl sm:text-2xl font-extrabold tracking-tight shrink-0">
          <Logo />
        </Link>
        <div className="flex items-center gap-1 sm:gap-2 min-w-0">
          <div className="flex items-center">
            <button title="Undo (Ctrl+Z)" aria-label="Undo" className={iconBtn} disabled={!past.length} onClick={store.undo}>
              <Icon name="undo" />
            </button>
            <button title="Redo (Ctrl+Shift+Z)" aria-label="Redo" className={iconBtn} disabled={!future.length} onClick={store.redo}>
              <Icon name="redo" />
            </button>
          </div>
          <span className="w-px h-6 bg-ink/10 mx-1 sm:mx-2 hidden sm:block" />
          <div className="flex items-center sm:gap-1">
            <button title="See it on a wall" className={textBtn} onClick={() => setWall(true)} disabled={!design.stops.length}>
              <Icon name="wall" />
              <span className="hidden lg:inline">On the wall</span>
            </button>
            <button title="Share a link" className={textBtn} onClick={share} disabled={!!busy || !design.stops.length}>
              <Icon name="share" />
              <span className="hidden lg:inline">{busy === "share" ? "Sharing…" : "Share"}</span>
            </button>
            <button title={me?.user ? "Save to your account" : "Sign in to save"} className={textBtn} onClick={save} disabled={busy === "save" || (!!savedId && !dirty)}>
              <Icon name={savedId && !dirty ? "check" : "save"} />
              <span className="hidden lg:inline">{busy === "save" ? "Saving…" : savedId && !dirty ? "Saved" : "Save"}</span>
            </button>
            <button title="Start a new map" onClick={() => confirm("Start a fresh map? (You can undo this.)") && store.reset()} className={`${textBtn} hidden md:inline-flex`}>
              <Icon name="plus" />
              <span className="hidden lg:inline">New</span>
            </button>
          </div>
          <span className="w-px h-6 bg-ink/10 mx-1 sm:mx-2 hidden sm:block" />
          <label className="hidden sm:flex items-center gap-1.5 rounded-full border border-ink/15 pl-3 pr-1 h-9 text-sm font-semibold text-ink/70 hover:border-ink/30 cursor-pointer" title="Where should we ship it? Prices and printing are local to each country.">
            <Icon name="globe" size={16} />
            <select value={region} onChange={(e) => store.setRegion(e.target.value as typeof region)} aria-label="Ship to" className="bg-transparent outline-none cursor-pointer pr-1">
              {REGIONS.map((r) => (
                <option key={r.id} value={r.id}>{r.id === "GB" ? "UK" : r.id}</option>
              ))}
            </select>
          </label>
          <button
            onClick={order}
            disabled={!!busy || design.stops.length === 0}
            className="ml-1 sm:ml-2 h-9 sm:h-10 rounded-full bg-coral px-4 sm:px-5 text-sm sm:text-[15px] font-bold text-white shadow-sm hover:bg-coral-dark disabled:opacity-40 transition whitespace-nowrap"
          >
            {busy === "order" ? "Saving…" : <>Order<span className="hidden sm:inline"> print</span> · {money(region, price)}</>}
          </button>
          {me?.user ? (
            <Link href="/account" title="My account" className="ml-1 sm:ml-2 shrink-0">
              {me.user.picture ? (
                // eslint-disable-next-line @next/next/no-img-element
                <img src={me.user.picture} alt="My account" referrerPolicy="no-referrer" className="w-9 h-9 rounded-full ring-1 ring-ink/10" />
              ) : (
                <span className="grid place-items-center w-9 h-9 rounded-full bg-ink text-white font-semibold">{(me.user.name ?? me.user.email)[0].toUpperCase()}</span>
              )}
            </Link>
          ) : (
            me && (
              <Link href="/signin?next=/create" className="hidden sm:block ml-1 sm:ml-2 text-sm font-semibold text-ink/60 hover:text-ink px-2 whitespace-nowrap">
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
            <div
              className={`${pickMode ? "[&_canvas]:!cursor-crosshair" : ""} ${locked ? "touch-none [&_canvas]:!cursor-default" : ""}`}
              style={{ transform: `translate(${zoom.x}px, ${zoom.y}px) scale(${zoom.k})`, transformOrigin: "center", transition: "transform 60ms linear" }}
            >
              <FramedPoster
                frozen={locked}
                key={`${design.productId}-${design.orientation}-${design.layout}-${design.frame}`}
                design={design}
                width={posterW}
                editable
                selectedSticker={selectedSticker}
                selectedLabel={selectedLabel}
                fitRequest={fitRequest}
                handlers={{
                  onView: (view) => store.setView(view),
                  onStopMove: (id, lng, lat) => store.updateStop(id, { lng, lat }),
                  onStickerMove: (id, lng, lat) => store.updateSticker(id, { lng, lat }),
                  onStickerChange: (id, patch) => store.updateSticker(id, patch),
                  onStickerSelect: (id) => store.select(id),
                  onLabelSelect: (id) => store.selectLabel(id),
                  onLabelChange: (id, patch) => store.updateStop(id, patch),
                  onTextMove: (which, o) => store.set({ text: { ...useEditor.getState().design.text, [which === "title" ? "titleOffset" : "subtitleOffset"]: o } }),
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
                    if (!pickMode) {
                      if (tab === "trip") setToast("To add a stop by tapping, press “📍 Tap on the map” first");
                      return;
                    }
                    // Drop the pin straight away; fill in the place name when the lookup returns.
                    const st = useEditor.getState();
                    const id = st.addStopAt(lng, lat, "Finding place…");
                    const name = await reverseGeocode(lng, lat);
                    st.nameStopQuietly(id, name ?? "New stop");
                    if (!name) setToast("No town there. Rename the stop in the list if you like.");
                  },
                }}
              />
            </div>
          )}

          <div className="absolute right-3 bottom-3 z-20 flex flex-col items-end gap-2">
            {locked && (
              <div className="flex flex-col rounded-2xl bg-white shadow-lg overflow-hidden text-lg font-extrabold">
                <button title="Zoom in" aria-label="Zoom in" className="w-10 h-10 hover:bg-ink/5" onClick={() => setZoom((z) => ({ k: Math.min(5, z.k * 1.4), x: z.x * 1.4, y: z.y * 1.4 }))}>+</button>
                <button title="Zoom out" aria-label="Zoom out" className="w-10 h-10 hover:bg-ink/5 border-t border-ink/10" onClick={() => setZoom((z) => (z.k / 1.4 <= 1.01 ? { k: 1, x: 0, y: 0 } : { k: z.k / 1.4, x: z.x / 1.4, y: z.y / 1.4 }))}>−</button>
                <button title="Fit the poster" aria-label="Fit the poster" className="w-10 h-10 hover:bg-ink/5 border-t border-ink/10 text-sm" onClick={() => setZoom({ k: 1, x: 0, y: 0 })}>⤢</button>
              </div>
            )}
            <button
              onClick={() => {
                setLocked((v) => !v);
                if (!locked) setToast("Framing locked. Pinch or use + to zoom in and rearrange labels and stickers.");
              }}
              title={locked ? "Unlock to move and zoom the map again" : "Lock the map's framing, then zoom in to edit"}
              className={`rounded-full px-4 py-2.5 text-sm font-extrabold shadow-lg transition ${locked ? "bg-ink text-white" : "bg-white text-ink hover:bg-cream"}`}
            >
              {locked ? "🔒 Framing locked" : "🔓 Lock framing"}
            </button>
          </div>

          {roadsLoading > 0 && (
            <div className="absolute inset-0 z-10 grid place-items-center bg-cream/40 backdrop-blur-[1px] pointer-events-none" role="status" aria-live="polite">
              <div className="flex items-center gap-3 rounded-full bg-white px-5 py-3 shadow-xl font-extrabold text-sm">
                <span className="w-5 h-5 rounded-full border-2 border-coral/30 border-t-coral animate-spin" aria-hidden />
                🚗 Plotting the roads ({roadsLoading} {roadsLoading === 1 ? "drive" : "drives"})…
              </div>
            </div>
          )}

          {labelStop && (
            <div className="absolute top-3 left-1/2 -translate-x-1/2 z-20 flex items-center gap-1 rounded-full bg-ink text-white px-2 py-1.5 shadow-xl text-sm font-bold max-w-[96%] overflow-x-auto">
              <span className="px-2 opacity-60 whitespace-nowrap max-w-32 truncate">“{labelStop.name}”</span>
              {design.markers.style === "sticker" && (
                <button className="px-3 py-1 rounded-full bg-coral hover:bg-coral-dark whitespace-nowrap" onClick={() => setTab("stickers")}>🎨 {labelStop.marker ? "Change sticker" : "Choose sticker"}</button>
              )}
              <span className="text-[11px] uppercase tracking-wider opacity-50 pl-1">{design.markers.style === "sticker" ? "Size" : "Pin"}</span>
              <button title="Smaller pin" className="px-2.5 py-1 rounded-full hover:bg-white/15" onClick={() => store.updateStop(labelStop.id, { markerScale: Math.max(0.25, (labelStop.markerScale ?? 1) / 1.2) }, `msize-${labelStop.id}`)}>−</button>
              <button title="Bigger pin" className="px-2.5 py-1 rounded-full hover:bg-white/15" onClick={() => store.updateStop(labelStop.id, { markerScale: Math.min(3, (labelStop.markerScale ?? 1) * 1.2) }, `msize-${labelStop.id}`)}>+</button>
              <span className="w-px h-5 bg-white/20 mx-1" />
              {labelStop.showLabel ? (
                <>
                  <span className="text-[11px] uppercase tracking-wider opacity-50 pl-1">Name</span>
                  <button title="Smaller name" className="px-2.5 py-1 rounded-full hover:bg-white/15" onClick={() => store.updateStop(labelStop.id, { labelScale: Math.max(0.25, (labelStop.labelScale ?? 1) / 1.15) }, `lsize-${labelStop.id}`)}>A−</button>
                  <button title="Bigger name" className="px-2.5 py-1 rounded-full hover:bg-white/15 text-base" onClick={() => store.updateStop(labelStop.id, { labelScale: Math.min(4, (labelStop.labelScale ?? 1) * 1.15) }, `lsize-${labelStop.id}`)}>A+</button>
                  <button title="Hide this name" className="px-2.5 py-1 rounded-full hover:bg-white/15 whitespace-nowrap" onClick={() => store.updateStop(labelStop.id, { showLabel: false })}>Hide</button>
                </>
              ) : (
                <button className="px-3 py-1 rounded-full hover:bg-white/15 whitespace-nowrap" onClick={() => store.updateStop(labelStop.id, { showLabel: true })}>Show name</button>
              )}
              <span className="w-px h-5 bg-white/20 mx-1" />
              <button title="Back to the standard size and position" className="px-2.5 py-1 rounded-full hover:bg-white/15 whitespace-nowrap" onClick={() => store.updateStop(labelStop.id, { labelOffset: undefined, labelScale: undefined, markerScale: undefined })}>↺ Reset</button>
              <button className="px-3 py-1 rounded-full hover:bg-white/15 opacity-70" onClick={() => store.selectLabel(null)}>Done</button>
            </div>
          )}

          {sel?.kind === "text" && fontMenu && (
            <div className="absolute top-16 left-1/2 -translate-x-1/2 z-30 w-[min(30rem,94%)] max-h-[60%] overflow-y-auto rounded-3xl bg-white shadow-2xl p-3 grid grid-cols-2 sm:grid-cols-3 gap-2" role="listbox" aria-label="Fonts">
              {FONTS.map((f) => (
                <button
                  key={f.id}
                  role="option"
                  aria-selected={(sel.font ?? "caveat") === f.id}
                  onClick={() => {
                    store.updateSticker(sel.id, { font: f.id });
                    setFontMenu(false);
                  }}
                  className={`rounded-2xl border-2 px-3 py-2 text-left transition ${(sel.font ?? "caveat") === f.id ? "border-coral bg-coral/5" : "border-ink/10 hover:border-ink/30"}`}
                >
                  <span className="block text-lg leading-tight truncate" style={{ fontFamily: f.css, fontWeight: f.bold }}>{sel.text?.trim() || "Best day ever!"}</span>
                  <span className="block text-[11px] font-bold text-ink/50">{f.name}</span>
                </button>
              ))}
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
                  <span className="relative">
                    <button
                      onClick={() => setFontMenu((v) => !v)}
                      className="bg-white/10 rounded-full px-3 py-1 whitespace-nowrap"
                      style={{ fontFamily: fontCss(sel.font ?? "caveat"), fontWeight: fontBold(sel.font ?? "caveat") }}
                      aria-haspopup="listbox"
                      aria-expanded={fontMenu}
                    >
                      {FONTS.find((f) => f.id === (sel.font ?? "caveat"))?.name ?? "Font"} ▾
                    </button>
                  </span>
                  <input type="color" value={sel.color ?? design.theme.colors.ink} onChange={(e) => store.updateSticker(sel.id, { color: e.target.value }, `color-${sel.id}`)} className="w-7 h-7 rounded-full bg-transparent border-0 p-0" />
                  <label className="flex items-center gap-1.5 bg-white/10 rounded-full pl-2.5 pr-3 py-1 whitespace-nowrap" title="Curve the text">
                    <span aria-hidden>{(sel.curve ?? 0) < 0 ? "◡" : "◠"}</span>
                    <input
                      type="range"
                      min={-100}
                      max={100}
                      step={5}
                      value={sel.curve ?? 0}
                      onChange={(e) => store.updateSticker(sel.id, { curve: Number(e.target.value) || undefined }, `curve-${sel.id}`)}
                      onDoubleClick={() => store.updateSticker(sel.id, { curve: undefined })}
                      aria-label="Curve"
                      className="w-20 accent-coral"
                    />
                  </label>
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
                className={`flex-1 rounded-xl py-2 text-xs font-semibold tracking-wide transition ${tab === t.id ? "bg-white shadow-sm text-ink" : "text-ink/45 hover:text-ink"}`}
              >
                <Icon name={t.icon} size={19} className="mx-auto mb-1" />
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
