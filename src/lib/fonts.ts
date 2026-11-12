import type { FontId } from "./types";

// Fonts are bundled with the app (Fontsource, open licences), so builds and
// print renders never depend on Google Fonts. The CSS variables are defined in
// globals.css and the font files are imported in app/layout.tsx.
// `bold` is the weight used for titles (single-weight fonts use their only weight).
export const FONTS: { id: FontId; name: string; css: string; bold: number }[] = [
  { id: "playfair", name: "Classic", css: "var(--f-playfair), serif", bold: 700 },
  { id: "cormorant", name: "Elegant", css: "var(--f-cormorant), serif", bold: 600 },
  { id: "abril", name: "Display", css: "var(--f-abril), serif", bold: 400 },
  { id: "montserrat", name: "Modern", css: "var(--f-montserrat), sans-serif", bold: 700 },
  { id: "josefin", name: "Geometric", css: "var(--f-josefin), sans-serif", bold: 600 },
  { id: "bebas", name: "Bold", css: "var(--f-bebas), sans-serif", bold: 400 },
  { id: "caveat", name: "Handwritten", css: "var(--f-caveat), cursive", bold: 700 },
  { id: "vibes", name: "Script", css: "var(--f-vibes), cursive", bold: 400 },
  { id: "pacifico", name: "Retro", css: "var(--f-pacifico), cursive", bold: 400 },
  { id: "courier", name: "Typewriter", css: "var(--f-courier), monospace", bold: 700 },
  { id: "marker", name: "Marker", css: "var(--f-marker), cursive", bold: 400 },
  { id: "amatic", name: "Amatic", css: "var(--f-amatic), cursive", bold: 700 },
  { id: "indie", name: "Doodle", css: "var(--f-indie), cursive", bold: 400 },
  { id: "patrick", name: "Notebook", css: "var(--f-patrick), cursive", bold: 400 },
  { id: "kalam", name: "Pen", css: "var(--f-kalam), cursive", bold: 700 },
  { id: "dancing", name: "Dancing", css: "var(--f-dancing), cursive", bold: 700 },
  { id: "satisfy", name: "Satisfy", css: "var(--f-satisfy), cursive", bold: 400 },
  { id: "lobster", name: "Lobster", css: "var(--f-lobster), cursive", bold: 400 },
  { id: "righteous", name: "Righteous", css: "var(--f-righteous), sans-serif", bold: 400 },
  { id: "fredoka", name: "Rounded", css: "var(--f-fredoka), sans-serif", bold: 600 },
  { id: "elite", name: "Typewriter 2", css: "var(--f-elite), monospace", bold: 400 },
  { id: "rocksalt", name: "Scrawl", css: "var(--f-rocksalt), cursive", bold: 400 },
];

export const fontCss = (id: FontId) => FONTS.find((f) => f.id === id)?.css ?? FONTS[0].css;
export const fontBold = (id: FontId) => FONTS.find((f) => f.id === id)?.bold ?? 700;
