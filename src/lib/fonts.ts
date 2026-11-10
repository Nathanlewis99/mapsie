import { Playfair_Display, Caveat, Montserrat, Pacifico, Bebas_Neue } from "next/font/google";
import type { FontId } from "./types";

const playfair = Playfair_Display({ subsets: ["latin"], weight: ["600", "800"], variable: "--f-playfair" });
const caveat = Caveat({ subsets: ["latin"], weight: ["600", "700"], variable: "--f-caveat" });
const montserrat = Montserrat({ subsets: ["latin"], weight: ["500", "700"], variable: "--f-montserrat" });
const pacifico = Pacifico({ subsets: ["latin"], weight: "400", variable: "--f-pacifico" });
const bebas = Bebas_Neue({ subsets: ["latin"], weight: "400", variable: "--f-bebas" });

export const fontVariables = [playfair, caveat, montserrat, pacifico, bebas].map((f) => f.variable).join(" ");

export const FONTS: { id: FontId; name: string; css: string }[] = [
  { id: "playfair", name: "Classic", css: "var(--f-playfair), serif" },
  { id: "caveat", name: "Handwritten", css: "var(--f-caveat), cursive" },
  { id: "montserrat", name: "Modern", css: "var(--f-montserrat), sans-serif" },
  { id: "pacifico", name: "Retro", css: "var(--f-pacifico), cursive" },
  { id: "bebas", name: "Bold", css: "var(--f-bebas), sans-serif" },
];

export const fontCss = (id: FontId) => FONTS.find((f) => f.id === id)?.css ?? FONTS[0].css;
