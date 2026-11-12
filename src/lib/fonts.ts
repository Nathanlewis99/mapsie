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
];

export const fontCss = (id: FontId) => FONTS.find((f) => f.id === id)?.css ?? FONTS[0].css;
export const fontBold = (id: FontId) => FONTS.find((f) => f.id === id)?.bold ?? 700;
