"use client";
import { useEffect, useState } from "react";
import FramedPoster, { frameWidth } from "@/components/FramedPoster";
import { posterAspect } from "@/lib/products";
import type { Design } from "@/lib/types";

/** The whole print, as big as the screen allows (not editable). × or Escape goes back to the editor. */
export default function FullScreenPreview({ design, onClose }: { design: Design; onClose: () => void }) {
  const [vp, setVp] = useState({ w: 0, h: 0 });
  useEffect(() => {
    // The visible screen (on phones the page's layout width can be wider than what's shown).
    const size = () => setVp({ w: window.visualViewport?.width ?? document.documentElement.clientWidth, h: window.visualViewport?.height ?? window.innerHeight });
    size();
    window.addEventListener("resize", size);
    window.visualViewport?.addEventListener("resize", size);
    const key = (e: KeyboardEvent) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", key);
    return () => {
      window.removeEventListener("resize", size);
      window.visualViewport?.removeEventListener("resize", size);
      window.removeEventListener("keydown", key);
    };
  }, [onClose]);
  const aspect = posterAspect(design.productId, design.orientation);
  // Leave room for the × and a little margin; account for the frame drawn round the poster.
  const maxW = vp.w - 32;
  const maxH = vp.h - 96;
  // Shrink until the poster plus its frame fits both ways.
  let width = Math.min(maxW, maxH / aspect);
  for (let i = 0; i < 4; i++) {
    const fw = frameWidth(design, width) * 2;
    width = Math.min(maxW - fw, (maxH - fw) / aspect);
  }
  return (
    <div className="fixed inset-0 z-50 bg-[radial-gradient(circle_at_30%_20%,#fff_0%,#f1e8da_75%)] grid place-items-center" role="dialog" aria-label="Full screen preview" onClick={onClose}>
      <button onClick={onClose} aria-label="Back to the editor" title="Back to the editor" className="absolute left-4 top-4 z-10 w-11 h-11 grid place-items-center rounded-full bg-ink text-white text-2xl leading-none shadow-xl">×</button>
      {width > 0 && (
        // The poster is laid out at its design width and scaled down: pin the box to the shown size.
        <div data-fullscreen-poster onClick={(e) => e.stopPropagation()} className="shadow-2xl overflow-hidden" style={{ width: Math.floor(width) + frameWidth(design, width) * 2 }}>
          <FramedPoster design={design} width={Math.floor(width)} />
        </div>
      )}
    </div>
  );
}
