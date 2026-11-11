"use client";
import { create } from "zustand";
import { persist } from "zustand/middleware";
import { nanoid } from "nanoid";
import { normalizeDesign, type Design, type Stop, type Sticker } from "./types";
import { PRESETS, themeFromPreset } from "./themes";
import { fetchRoad, guessMode, legKey } from "./geo";
import { guessRegion, type RegionId } from "./products";
import { templateStops, type TripTemplate } from "./templates";

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
  });
}


type Snapshot = Omit<Design, "view">;
const snap = ({ view: _v, ...rest }: Design): Snapshot => rest; // eslint-disable-line @typescript-eslint/no-unused-vars

interface EditorState {
  design: Design;
  region: RegionId;
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
  load: (d: Design) => void;
  applyTemplate: (t: TripTemplate) => void;
  setRegion: (r: RegionId) => void;
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

        reset: () => commit(() => newDesign(), "edit", { selectedSticker: null }),
        load: (d) => {
          commit(() => normalizeDesign({ ...d, id: nanoid(10) }), "edit", { selectedSticker: null, fitRequest: 0 });
        },
        applyTemplate: (t) => {
          const preset = PRESETS.find((p) => p.id === t.preset) ?? PRESETS[0];
          const stops = templateStops(t).map((s) => ({ ...s, id: nanoid(8) }));
          // Spread the template's stickers along the trip, alternating sides of the route.
          const lngs = stops.map((s) => s.lng);
          const lats = stops.map((s) => s.lat);
          const span = Math.max(Math.max(...lngs) - Math.min(...lngs), Math.max(...lats) - Math.min(...lats), 2);
          const stickers: Sticker[] = t.stickers.map((name, i) => {
            const at = stops[Math.round((i / Math.max(1, t.stickers.length - 1)) * (stops.length - 1))];
            const side = i % 2 ? 1 : -1;
            return { id: nanoid(8), kind: "sticker", src: `/stickers/${name}.svg`, lng: at.lng + side * span * 0.16, lat: at.lat + span * 0.05, size: 9, rotation: side * 8 };
          });
          commit(
            (d) => ({ ...d, title: t.title, subtitle: t.subtitle, theme: themeFromPreset(preset), stops, stickers }),
            "edit",
            { fitRequest: get().fitRequest + 1, selectedSticker: null },
          );
          afterStopsChange();
        },
        setRegion: (region) => set({ region }),

        /** Fetch road geometry for any car/bus leg that doesn't have it yet. */
        ensureRoads: async () => {
          const stops = get().design.stops;
          const todo = stops
            .map((b, i) => ({ a: stops[i - 1], b }))
            .filter(({ a, b }) => a && (b.arriveBy === "car" || b.arriveBy === "bus") && b.pathFor !== legKey(a, b));
          if (!todo.length) return;
          set((s) => ({ roadsLoading: s.roadsLoading + todo.length }));
          await Promise.all(
            todo.map(async ({ a, b }) => {
              const key = legKey(a, b);
              const path = await fetchRoad(a, b);
              set((s) => ({
                roadsLoading: s.roadsLoading - 1,
                // Write straight into the design (not an undo step) if the leg hasn't changed meanwhile.
                design: {
                  ...s.design,
                  stops: s.design.stops.map((x, i, arr) =>
                    x.id === b.id && arr[i - 1] && legKey(arr[i - 1], x) === key && path !== undefined ? { ...x, path: path ?? undefined, pathFor: key } : x,
                  ),
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
      partialize: (s) => ({ design: s.design, region: s.region }),
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
