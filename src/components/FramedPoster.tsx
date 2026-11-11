"use client";
import Poster from "./Poster";
import { FRAMES, posterAspect } from "@/lib/products";
import type { ComponentProps } from "react";

export const frameWidth = (design: { frame: string }, width: number) => (design.frame !== "none" ? Math.max(4, width * 0.035) : 0);

/**
 * The poster with its chosen frame drawn around it (frame sits outside `width`).
 * Read-only previews are laid out at the design's own width and scaled, so a
 * thumbnail shows exactly what the print will.
 */
export default function FramedPoster(props: ComponentProps<typeof Poster> & { shadow?: boolean }) {
  const { shadow = true, ...rest } = props;
  const { design, width, editable } = props;
  const frame = FRAMES.find((f) => f.id === design.frame);
  const fw = frameWidth(design, width);
  const ref = design.view.refWidth;
  const scaled = !editable && Math.abs(width - ref) > 1;
  const h = width * posterAspect(design.productId, design.orientation);

  return (
    <div
      style={{
        padding: fw,
        background: frame?.id === "oak" ? "linear-gradient(135deg, #d4ab7b, #b98a59 40%, #c99e6d 70%, #a97b4c)" : frame?.color,
        boxShadow: shadow ? "0 30px 60px -15px rgba(31,36,48,0.4), 0 6px 12px -4px rgba(31,36,48,0.2)" : undefined,
        borderRadius: fw ? 2 : 0,
      }}
    >
      <div style={{ boxShadow: fw ? "inset 0 0 6px rgba(0,0,0,0.35)" : undefined, lineHeight: 0, width, height: h, overflow: "hidden", position: "relative" }}>
        {scaled ? (
          <div style={{ transform: `scale(${width / ref})`, transformOrigin: "top left", width: ref }}>
            <Poster {...rest} width={ref} />
          </div>
        ) : (
          <Poster {...rest} />
        )}
      </div>
    </div>
  );
}
