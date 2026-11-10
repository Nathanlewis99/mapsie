"use client";
import Poster from "@/components/Poster";
import type { Design } from "@/lib/types";

declare global {
  interface Window { __MAPSIE_READY?: boolean }
}

export default function PrintView({ design }: { design: Design }) {
  return (
    <div style={{ margin: 0, padding: 0, width: design.view.refWidth }}>
      <Poster
        design={design}
        width={design.view.refWidth}
        print
        onReady={() => {
          // let stickers/photos finish decoding before we say we're ready
          Promise.all([...document.images].map((i) => (i.complete ? null : i.decode().catch(() => null)))).then(() => {
            requestAnimationFrame(() => (window.__MAPSIE_READY = true));
          });
        }}
      />
    </div>
  );
}
