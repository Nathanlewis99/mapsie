"use client";
import Poster from "@/components/Poster";
import type { Design } from "@/lib/types";

/**
 * Chrome draws large SVG images in tiles at print density, and SVG filters
 * (the papercut shadows) get lost at tile edges. So before capture, each SVG
 * sticker without a CSS effect is drawn once, whole, into a canvas at full
 * device resolution and swapped in as a bitmap.
 */
async function flattenSvgStickers() {
  const dpr = window.devicePixelRatio || 1;
  const imgs = [...document.querySelectorAll<HTMLImageElement>(".mapsie-sticker img")].filter(
    (i) => /\.svg($|\?)/.test(i.src) && !i.style.filter,
  );
  await Promise.all(
    imgs.map(async (img) => {
      try {
        await img.decode();
        const w = Math.max(1, Math.round(img.clientWidth * dpr));
        const h = Math.max(1, Math.round(img.clientHeight * dpr));
        const src = new Image(w, h);
        src.src = img.src;
        await src.decode();
        const canvas = document.createElement("canvas");
        canvas.width = w;
        canvas.height = h;
        canvas.getContext("2d")!.drawImage(src, 0, 0, w, h);
        img.src = canvas.toDataURL("image/png");
        await img.decode();
      } catch {
        // keep the original SVG if anything goes wrong
      }
    }),
  );
}

export default function PrintView({ design }: { design: Design }) {
  return (
    <div style={{ margin: 0, padding: 0, width: design.view.refWidth }}>
      <Poster
        design={design}
        width={design.view.refWidth}
        print
        onReady={async () => {
          // let stickers/photos finish decoding before we say we're ready
          await Promise.all([...document.images].map((i) => (i.complete ? null : i.decode().catch(() => null))));
          await flattenSvgStickers();
          requestAnimationFrame(() => (window.__MAPSIE_READY = true));
        }}
      />
    </div>
  );
}
