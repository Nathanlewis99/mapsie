import type { FontId } from "./types";

// Fonts are bundled with the app (Fontsource, open licences), so builds and
// print renders never depend on Google Fonts. The CSS variables are defined in
// globals.css and the font files are imported in app/layout.tsx.
export const FONTS: { id: FontId; name: string; css: string }[] = [
  { id: "playfair", name: "Classic", css: "var(--f-playfair), serif" },
  { id: "caveat", name: "Handwritten", css: "var(--f-caveat), cursive" },
  { id: "montserrat", name: "Modern", css: "var(--f-montserrat), sans-serif" },
  { id: "pacifico", name: "Retro", css: "var(--f-pacifico), cursive" },
  { id: "bebas", name: "Bold", css: "var(--f-bebas), sans-serif" },
];

export const fontCss = (id: FontId) => FONTS.find((f) => f.id === id)?.css ?? FONTS[0].css;
