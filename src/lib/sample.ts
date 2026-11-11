import { normalizeDesign, type Design } from "./types";
import { PRESETS, themeFromPreset } from "./themes";

export const SAMPLE: Design = normalizeDesign({
  id: "sample",
  title: "The Big Trip",
  subtitle: "Spring 2026 · 4 countries",
  font: "playfair",
  layout: "band",
  productId: "a3",
  orientation: "portrait",
  theme: themeFromPreset(PRESETS[0]),
  view: { center: [116, -2], zoom: 1.72, bearing: 0, refWidth: 400 },
  stops: [
    { id: "a", name: "Colombo", lng: 79.86, lat: 6.93, showLabel: true },
    { id: "b", name: "Kathmandu", lng: 85.32, lat: 27.72, showLabel: true, arriveBy: "plane" },
    { id: "c", name: "Singapore", lng: 103.82, lat: 1.35, showLabel: true, arriveBy: "plane" },
    { id: "d", name: "Cairns", lng: 145.77, lat: -16.92, showLabel: true, arriveBy: "plane" },
    { id: "e", name: "Sydney", lng: 151.21, lat: -33.87, showLabel: true, arriveBy: "plane" },
  ],
  route: { show: true, style: "auto", curved: true, width: 0.5, modeIcons: false },
  visited: { show: true, opacity: 0.25 },
  stickers: [
    { id: "s1", kind: "sticker", src: "/stickers/elephant.svg", lng: 82, lat: 12, size: 9, rotation: -8 },
    { id: "s2", kind: "sticker", src: "/stickers/snowy-mountain.svg", lng: 90.5, lat: 33, size: 10, rotation: 0 },
    { id: "s3", kind: "sticker", src: "/stickers/diving-mask.svg", lng: 150, lat: -12, size: 9, rotation: 10 },
    { id: "s4", kind: "sticker", src: "/stickers/crocodile.svg", lng: 136, lat: -20, size: 11, rotation: -6 },
    { id: "s5", kind: "text", src: "", text: "best trip ever!", font: "caveat", lng: 127, lat: 21, size: 5, rotation: -8 },
  ],
});
