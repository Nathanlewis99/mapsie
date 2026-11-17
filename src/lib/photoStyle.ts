// How a customer's own photo looks on the map: its shape, border and colour style.
// Shared by the editor toolbar and the map (and so the print file).
import type { Sticker } from "./types";

export type PhotoShape = "original" | "square" | "landscape" | "portrait" | "circle" | "rounded" | "heart" | "stamp";
export type PhotoBorder = "none" | "thin" | "classic" | "thick" | "polaroid" | "tape";
export type PhotoFilter = "none" | "bw" | "sepia" | "vintage" | "warm" | "cool" | "faded";

export const PHOTO_SHAPES: { id: PhotoShape; label: string }[] = [
  { id: "original", label: "Original" },
  { id: "square", label: "Square" },
  { id: "landscape", label: "Landscape" },
  { id: "portrait", label: "Portrait" },
  { id: "circle", label: "Circle" },
  { id: "rounded", label: "Rounded" },
  { id: "heart", label: "Heart" },
  { id: "stamp", label: "Postage stamp" },
];
export const PHOTO_BORDERS: { id: PhotoBorder; label: string }[] = [
  { id: "none", label: "No border" },
  { id: "thin", label: "Thin" },
  { id: "classic", label: "Classic" },
  { id: "thick", label: "Thick" },
  { id: "polaroid", label: "Polaroid" },
  { id: "tape", label: "Taped" },
];
export const PHOTO_FILTERS: { id: PhotoFilter; label: string; css: string }[] = [
  { id: "none", label: "Colour", css: "" },
  { id: "bw", label: "Black & white", css: "grayscale(1) contrast(1.06)" },
  { id: "sepia", label: "Sepia", css: "sepia(0.75) contrast(0.95) brightness(1.03)" },
  { id: "vintage", label: "Vintage", css: "sepia(0.35) saturate(0.8) contrast(0.9) brightness(1.05)" },
  { id: "warm", label: "Warm", css: "sepia(0.18) saturate(1.25) hue-rotate(-8deg)" },
  { id: "cool", label: "Cool", css: "saturate(1.05) hue-rotate(10deg) brightness(1.02)" },
  { id: "faded", label: "Faded", css: "contrast(0.8) brightness(1.1) saturate(0.7)" },
];
/** Border colours offered for photos (the map's own ink and accent are added by the editor). */
export const PHOTO_BORDER_COLOURS = [
  { id: "#ffffff", label: "White" },
  { id: "#f6efe0", label: "Cream" },
  { id: "#c8a97e", label: "Kraft" },
  { id: "#1f2430", label: "Black" },
];

const HEART = "polygon(50% 92%, 39% 82%, 22% 67%, 9% 53%, 3% 41%, 3% 27%, 9% 15%, 19% 8%, 31% 7%, 42% 12%, 50% 21%, 58% 12%, 69% 7%, 81% 8%, 91% 15%, 97% 27%, 97% 41%, 91% 53%, 78% 67%, 61% 82%)";

/** Shape and border with defaults: photos added before these options look as they always did. */
export function photoLook(st: Sticker) {
  const shape: PhotoShape = st.photoShape ?? (st.photoAspect ? "original" : "square");
  let border: PhotoBorder = st.photoBorder ?? "classic";
  // A polaroid's deep bottom edge only makes sense on a rectangle.
  if (border === "polaroid" && (shape === "circle" || shape === "heart" || shape === "stamp")) border = "classic";
  if (shape === "stamp" && border === "none") border = "classic";
  return { shape, border, colour: st.photoBorderColor ?? "#ffffff", filter: PHOTO_FILTERS.find((f) => f.id === st.photoFilter)?.css ?? "" };
}

/**
 * Builds the photo's element for the map. `px` is the photo's width (the sticker size).
 * Returns the element and its full height, so the marker can be sized to fit.
 */
export function buildPhoto(st: Sticker, px: number): { el: HTMLElement; height: number } {
  const { shape, border, colour, filter } = photoLook(st);
  const aspect = shape === "square" || shape === "circle" || shape === "heart" ? 1 : shape === "landscape" ? 0.75 : shape === "portrait" ? 4 / 3 : shape === "stamp" ? (st.photoAspect ?? 1.2) : (st.photoAspect ?? 1);
  const t = { none: 0, thin: 0.025, classic: 0.05, thick: 0.09, polaroid: 0.055, tape: 0.035 }[border] * px;
  const b = border === "polaroid" ? px * 0.22 : t;
  const w = px - 2 * t;
  const h = w * aspect;
  const height = t + h + b;

  const frame = document.createElement("div");
  frame.className = "mapsie-photo";
  frame.style.cssText = `position:relative;width:${px}px;height:${height}px;padding:${t}px ${t}px ${b}px;background:${border === "none" ? "transparent" : colour};box-sizing:border-box;`;
  const img = document.createElement("img");
  img.src = st.src;
  img.alt = "";
  img.draggable = false;
  img.style.cssText = `display:block;width:${w}px;height:${h}px;object-fit:cover;${filter ? `filter:${filter};` : "filter:none;"}`;

  if (shape === "circle") {
    frame.style.borderRadius = "50%";
    img.style.borderRadius = "50%";
  } else if (shape === "rounded") {
    frame.style.borderRadius = `${px * 0.12}px`;
    img.style.borderRadius = `${Math.max(0, px * 0.12 - t)}px`;
  } else if (shape === "heart") {
    frame.style.clipPath = HEART;
    img.style.clipPath = HEART;
  } else if (shape === "stamp") {
    // Perforated edge: holes along the border, the picture area left whole.
    const r = Math.max(1, t * 0.6);
    const mask = `radial-gradient(circle at center, transparent ${r}px, #000 ${r + 0.5}px) ${-r}px ${-r}px / ${r * 3}px ${r * 3}px repeat, linear-gradient(#000 0 0) content-box`;
    frame.style.setProperty("-webkit-mask", mask);
    frame.style.setProperty("mask", mask);
  } else if (border !== "none") {
    frame.style.borderRadius = `${Math.max(1, px * 0.008)}px`;
  }
  frame.appendChild(img);

  if (border === "tape") {
    // Two strips of washi tape across the top corners.
    for (const side of [-1, 1]) {
      const tape = document.createElement("div");
      tape.style.cssText = `position:absolute;top:${-px * 0.035}px;${side < 0 ? "left" : "right"}:${-px * 0.06}px;width:${px * 0.34}px;height:${px * 0.1}px;background:rgba(244,232,200,0.82);transform:rotate(${side * 38}deg);box-shadow:0 1px 1px rgba(0,0,0,0.08);`;
      frame.appendChild(tape);
    }
  }
  return { el: frame, height };
}
