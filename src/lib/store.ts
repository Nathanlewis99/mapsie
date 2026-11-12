"use client";
import { create } from "zustand";
import { persist } from "zustand/middleware";
import { nanoid } from "nanoid";
import { normalizeDesign, type Design, type Stop, type Sticker } from "./types";
import { PRESETS, themeFromPreset } from "./themes";
import { fetchRoads, guessMode, legKey } from "./geo";
import { guessRegion, type RegionId } from "./products";
import { templateStops, type TripTemplate } from "./templates";
import { suggestedStyleFor, stickerSrc, type ArtStyleId } from "./stickers";

export function newDesign(): Design {
  return normalizeDesign({
    id: nanoid(10),
    title: "Our Big Adventure",
    subtitle: "2026",
    font: "playfair",
    layout: "band",
    productId: "a3",
    orientation: "portrait",
    frame: "none",
    theme: themeFromPreset(PRESETS[0]),
    view: { center: [100, 5], zoom: 2.2, bearing: 0, refWidth: 600 },
    stops: [],
    stickers: [],
    stickerStyle: suggestedStyleFor(PRESETS[0].id),
  });
}


type Snapshot = Omit<Design, "view">;
const snap = ({ view: _v, ...rest }: Design): Snapshot => rest; // eslint-disable-line @typescript-eslint/no-unused-vars

interface EditorState {
  design: Design;
  region: RegionId;
  /** Id of this design in the signed-in user's account, once saved. */
  savedId: string | null;
  /** Changes since the last save to the account. */
  dirty: boolean;
  setSaved: (id: string | null) => void;
  past: Snapshot[];
  future: Snapshot[];
  lastCommit: { key: string; at: number };
  selectedSticker: string | null;
  fitRequest: number; // bump to ask the map to frame all stops
  roadsLoading: number;

  set: (patch: Partial<Design>, key?: string) => void;
  setTheme: (patch: Partial<Design["theme"]>) => void;
  setColors: (patch: Partial<Design["theme"]["colors"]>) => void;
  setView: (view: Design["view"]) => void;
  addStop: (s: Pick<Stop, "name" | "lng" | "lat">) => void;
  addStops: (s: Pick<Stop, "name" | "lng" | "lat">[]) => void;
  /** Tap-to-add: drops a stop at once (without moving the map) and returns its id. */
  addStopAt: (lng: number, lat: number, name: string) => string;
  /** Set a stop's name without making an undo step (e.g. when the place lookup returns). */
  nameStopQuietly: (id: string, name: string) => void;
  updateStop: (id: string, patch: Partial<Stop>, key?: string) => void;
  removeStop: (id: string) => void;
  moveStop: (from: number, to: number) => void;
  addSticker: (s: Omit<Sticker, "id">) => void;
  updateSticker: (id: string, patch: Partial<Sticker>, key?: string) => void;
  removeSticker: (id: string) => void;
  select: (id: string | null) => void;
  requestFit: () => void;
  undo: () => void;
  redo: () => void;
  reset: () => void;
  /** Open a design from the user's account. */
  loadSaved: (id: string, d: Design) => void;
  load: (d: Design) => void;
  applyTemplate: (t: TripTemplate) => void;
  setRegion: (r: RegionId) => void;
  /** Change the default sticker style; optionally restyle every sticker already placed. */
  setStickerStyle: (style: ArtStyleId, applyToAll: boolean) => void;
  /** Change the default style/palette for Mapsie Originals and apply it to those already placed. */
  setOriginals: (patch: Partial<Design["originals"]>) => void;
  ensureRoads: () => Promise<void>;
}

export const useEditor = create<EditorState>()(
  persist(
    (set, get) => {
      /** Apply a change and record it for undo. Rapid edits with the same key (e.g. a slider) merge into one step. */
      const commit = (fn: (d: Design) => Design, key = "edit", extra: Partial<EditorState> = {}) => {
        const s = get();
        const next = fn(s.design);
        const now = Date.now();
        const merge = key !== "edit" && s.lastCommit.key === key && now - s.lastCommit.at < 800;
        set({
          design: next,
          past: merge ? s.past : [...s.past.slice(-79), snap(s.design)],
          future: [],
          lastCommit: { key, at: now },
          dirty: true,
          ...extra,
        });
      };
      const afterStopsChange = () => setTimeout(() => get().ensureRoads(), 0);

      return {
        design: newDesign(),
        region: "GB",
        past: [],
        future: [],
        lastCommit: { key: "", at: 0 },
        selectedSticker: null,
        fitRequest: 0,
        roadsLoading: 0,

        set: (patch, key) => commit((d) => ({ ...d, ...patch }), key),
        setTheme: (patch) => commit((d) => ({ ...d, theme: { ...d.theme, ...patch } })),
        setColors: (patch) =>
          commit((d) => ({ ...d, theme: { ...d.theme, presetId: "custom", colors: { ...d.theme.colors, ...patch } } }), "colors"),
        // Panning/zooming isn't an undo step.
        setView: (view) => set((s) => ({ design: { ...s.design, view } })),

        addStop: (stop) => get().addStops([stop]),
        addStops: (list) => {
          commit(
            (d) => {
              const stops = [...d.stops];
              for (const st of list) {
                const prev = stops[stops.length - 1];
                stops.push({ ...st, id: nanoid(8), showLabel: true, arriveBy: prev ? guessMode(prev, st) : undefined });
              }
              return { ...d, stops };
            },
            "edit",
            { fitRequest: get().fitRequest + 1 },
          );
          afterStopsChange();
        },
        addStopAt: (lng, lat, name) => {
          const id = nanoid(8);
          commit((d) => {
            const prev = d.stops[d.stops.length - 1];
            const stop = { id, name, lng, lat, showLabel: true, arriveBy: prev ? guessMode(prev, { lng, lat }) : undefined };
            return { ...d, stops: [...d.stops, stop] };
          });
          afterStopsChange();
          return id;
        },
        nameStopQuietly: (id, name) =>
          set((s) => ({ design: { ...s.design, stops: s.design.stops.map((x) => (x.id === id ? { ...x, name } : x)) } })),
        updateStop: (id, patch, key) => {
          commit((d) => ({ ...d, stops: d.stops.map((x) => (x.id === id ? { ...x, ...patch } : x)) }), key);
          if ("lng" in patch || "arriveBy" in patch) afterStopsChange();
        },
        removeStop: (id) => {
          commit((d) => ({ ...d, stops: d.stops.filter((x) => x.id !== id) }));
          afterStopsChange();
        },
        moveStop: (from, to) => {
          commit((d) => {
            const stops = [...d.stops];
            const [m] = stops.splice(from, 1);
            stops.splice(to, 0, m);
            return { ...d, stops };
          });
          afterStopsChange();
        },
        addSticker: (st) => {
          const id = nanoid(8);
          commit((d) => ({ ...d, stickers: [...d.stickers, { ...st, id }] }), "edit", { selectedSticker: id });
        },
        updateSticker: (id, patch, key) =>
          commit((d) => ({ ...d, stickers: d.stickers.map((x) => (x.id === id ? { ...x, ...patch } : x)) }), key),
        removeSticker: (id) =>
          commit((d) => ({ ...d, stickers: d.stickers.filter((x) => x.id !== id) }), "edit", {
            selectedSticker: get().selectedSticker === id ? null : get().selectedSticker,
          }),
        select: (id) => set({ selectedSticker: id }),
        requestFit: () => set((s) => ({ fitRequest: s.fitRequest + 1 })),

        undo: () => {
          const { past, future, design } = get();
          const prev = past[past.length - 1];
          if (!prev) return;
          set({ design: { ...prev, view: design.view }, past: past.slice(0, -1), future: [snap(design), ...future], lastCommit: { key: "", at: 0 } });
        },
        redo: () => {
          const { past, future, design } = get();
          const next = future[0];
          if (!next) return;
          set({ design: { ...next, view: design.view }, past: [...past, snap(design)], future: future.slice(1), lastCommit: { key: "", at: 0 } });
        },

        reset: () => commit(() => newDesign(), "edit", { selectedSticker: null, savedId: null }),
        savedId: null,
        dirty: true,
        setSaved: (id) => set({ savedId: id, dirty: false }),
        loadSaved: (id, d) => {
          set({ design: normalizeDesign(d), past: [], future: [], selectedSticker: null, fitRequest: 0, savedId: id, dirty: false, lastCommit: { key: "", at: 0 } });
        },
        load: (d) => {
          commit(() => normalizeDesign({ ...d, id: nanoid(10) }), "edit", { selectedSticker: null, fitRequest: 0, savedId: null });
        },
        applyTemplate: (t) => {
          const preset = PRESETS.find((p) => p.id === t.preset) ?? PRESETS[0];
          const stops = templateStops(t).map((s) => ({ ...s, id: nanoid(8) }));
          // Spread the template's stickers along the trip, alternating sides of the route.
          const lngs = stops.map((s) => s.lng);
          const lats = stops.map((s) => s.lat);
          const span = Math.max(Math.max(...lngs) - Math.min(...lngs), Math.max(...lats) - Math.min(...lats), 2);
          const art = suggestedStyleFor(preset.id);
          const stickers: Sticker[] = t.stickers.map((name, i) => {
            const at = stops[Math.round((i / Math.max(1, t.stickers.length - 1)) * (stops.length - 1))];
            const side = i % 2 ? 1 : -1;
            return { id: nanoid(8), kind: "original", name, origStyle: "papercut", palette: "auto", src: "", lng: at.lng + side * span * 0.16, lat: at.lat + span * 0.05, size: 14, rotation: side * 5 };
          });
          commit(
            (d) => ({ ...d, title: t.title, subtitle: t.subtitle, theme: themeFromPreset(preset), stops, stickers, stickerStyle: art }),
            "edit",
            { fitRequest: get().fitRequest + 1, selectedSticker: null },
          );
          afterStopsChange();
        },
        setRegion: (region) => set({ region }),
        setOriginals: (patch) =>
          commit((d) => {
            const originals = { ...d.originals, ...patch };
            return {
              ...d,
              originals,
              stickers: d.stickers.map((x) => (x.kind === "original" ? { ...x, origStyle: originals.style, palette: originals.palette } : x)),
            };
          }),
        setStickerStyle: (style, applyToAll) =>
          commit((d) => ({
            ...d,
            stickerStyle: style,
            stickers: applyToAll
              ? d.stickers.map((x) => (x.kind === "sticker" && x.name ? { ...x, art: style, src: stickerSrc(x.name, style) } : x))
              : d.stickers,
          })),

        /** Fetch road geometry for any car/bus leg that doesn't have it yet. */
        ensureRoads: async () => {
          const stops = get().design.stops;
          const needs = (i: number) =>
            i > 0 && (stops[i].arriveBy === "car" || stops[i].arriveBy === "bus") && stops[i].pathFor !== legKey(stops[i - 1], stops[i]);
          // Group consecutive drives into runs: each run is one request.
          const runs: number[][] = [];
          for (let i = 1; i < stops.length; i++) {
            if (!needs(i)) continue;
            const last = runs[runs.length - 1];
            if (last && last[last.length - 1] === i - 1) last.push(i);
            else runs.push([i]);
          }
          if (!runs.length) return;
          const total = runs.reduce((n, r) => n + r.length, 0);
          set((s) => ({ roadsLoading: s.roadsLoading + total }));
          await Promise.all(
            runs.map(async (run) => {
              const pts = [stops[run[0] - 1], ...run.map((i) => stops[i])];
              const paths = await fetchRoads(pts);
              set((s) => ({
                roadsLoading: s.roadsLoading - run.length,
                // Write straight into the design (not an undo step) if the leg hasn't changed meanwhile.
                design: {
                  ...s.design,
                  stops: s.design.stops.map((x, i, arr) => {
                    const k = run.findIndex((idx) => stops[idx].id === x.id);
                    if (k < 0 || !arr[i - 1]) return x;
                    const key = legKey(pts[k], pts[k + 1]);
                    const path = paths[k];
                    return legKey(arr[i - 1], x) === key && path !== undefined ? { ...x, path: path ?? undefined, pathFor: key } : x;
                  }),
                },
              }));
            }),
          );
        },
      };
    },
    {
      name: "mapsie-design",
      version: 2,
      partialize: (s) => ({ design: s.design, region: s.region, savedId: s.savedId }),
      migrate: (persisted) => {
        const p = persisted as { design?: Design; region?: RegionId };
        return { ...p, design: p.design ? normalizeDesign(p.design) : newDesign(), region: p.region ?? guessRegion() };
      },
      onRehydrateStorage: () => (state) => {
        if (state) state.design = normalizeDesign(state.design);
      },
    },
  ),
);
