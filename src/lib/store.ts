"use client";
import { create } from "zustand";
import { persist } from "zustand/middleware";
import { nanoid } from "nanoid";
import type { Design, Stop, Sticker } from "./types";
import { PRESETS, themeFromPreset } from "./themes";

export function newDesign(): Design {
  return {
    id: nanoid(10),
    title: "Our Big Adventure",
    subtitle: "2026",
    font: "playfair",
    layout: "band",
    productId: "a3",
    orientation: "portrait",
    theme: themeFromPreset(PRESETS[0]),
    view: { center: [100, 5], zoom: 2.2, bearing: 0, refWidth: 600 },
    stops: [],
    route: { show: true, style: "dashed", curved: true, width: 0.45 },
    stickers: [],
  };
}

interface EditorState {
  design: Design;
  selectedSticker: string | null;
  fitRequest: number; // bump to ask the map to frame all stops
  set: (patch: Partial<Design>) => void;
  setTheme: (patch: Partial<Design["theme"]>) => void;
  setColors: (patch: Partial<Design["theme"]["colors"]>) => void;
  addStop: (s: Omit<Stop, "id" | "showLabel">) => void;
  updateStop: (id: string, patch: Partial<Stop>) => void;
  removeStop: (id: string) => void;
  moveStop: (from: number, to: number) => void;
  addSticker: (s: Omit<Sticker, "id">) => void;
  updateSticker: (id: string, patch: Partial<Sticker>) => void;
  removeSticker: (id: string) => void;
  select: (id: string | null) => void;
  requestFit: () => void;
  reset: () => void;
}

export const useEditor = create<EditorState>()(
  persist(
    (set) => ({
      design: newDesign(),
      selectedSticker: null,
      fitRequest: 0,
      set: (patch) => set((s) => ({ design: { ...s.design, ...patch } })),
      setTheme: (patch) => set((s) => ({ design: { ...s.design, theme: { ...s.design.theme, ...patch } } })),
      setColors: (patch) =>
        set((s) => ({
          design: { ...s.design, theme: { ...s.design.theme, presetId: "custom", colors: { ...s.design.theme.colors, ...patch } } },
        })),
      addStop: (stop) =>
        set((s) => ({
          design: { ...s.design, stops: [...s.design.stops, { ...stop, id: nanoid(8), showLabel: true }] },
          fitRequest: s.fitRequest + 1,
        })),
      updateStop: (id, patch) =>
        set((s) => ({ design: { ...s.design, stops: s.design.stops.map((x) => (x.id === id ? { ...x, ...patch } : x)) } })),
      removeStop: (id) => set((s) => ({ design: { ...s.design, stops: s.design.stops.filter((x) => x.id !== id) } })),
      moveStop: (from, to) =>
        set((s) => {
          const stops = [...s.design.stops];
          const [m] = stops.splice(from, 1);
          stops.splice(to, 0, m);
          return { design: { ...s.design, stops } };
        }),
      addSticker: (st) => {
        const id = nanoid(8);
        set((s) => ({ design: { ...s.design, stickers: [...s.design.stickers, { ...st, id }] }, selectedSticker: id }));
      },
      updateSticker: (id, patch) =>
        set((s) => ({ design: { ...s.design, stickers: s.design.stickers.map((x) => (x.id === id ? { ...x, ...patch } : x)) } })),
      removeSticker: (id) =>
        set((s) => ({
          design: { ...s.design, stickers: s.design.stickers.filter((x) => x.id !== id) },
          selectedSticker: s.selectedSticker === id ? null : s.selectedSticker,
        })),
      select: (id) => set({ selectedSticker: id }),
      requestFit: () => set((s) => ({ fitRequest: s.fitRequest + 1 })),
      reset: () => set({ design: newDesign(), selectedSticker: null }),
    }),
    { name: "mapsie-design", partialize: (s) => ({ design: s.design }) },
  ),
);
