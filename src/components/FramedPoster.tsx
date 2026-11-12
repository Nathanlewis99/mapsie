"use client";
import Poster from "./Poster";
import { FRAMES, MOUNTS, getProduct, posterAspect } from "@/lib/products";
import type { PaperId } from "@/lib/types";

/** How strongly each paper's texture shows (a little less in the editor than on the wall). */
const PAPER_OPACITY: Record<PaperId, number> = { ema: 0.22, hpr: 0.4, hge: 0.55, lpp: 0.6 };

/** How the ink sits on each paper: matte papers are a little softer, lustre a little richer. */
const INK: Record<PaperId, string> = {
  ema: "saturate(0.94) contrast(0.96)",
  hpr: "saturate(0.88) contrast(0.93) brightness(0.99)",
  hge: "saturate(0.88) contrast(0.92) brightness(0.99)",
  lpp: "saturate(1.03) contrast(1.02)",
};
import type { CSSProperties, ComponentProps } from "react";

type D = { frame: string; mount?: string; productId: string; orientation: "portrait" | "landscape" };

/** Poster width in real centimetres, so the frame and mount are drawn at true scale. */
const posterCm = (d: D) => {
  const p = getProduct(d.productId);
  return d.orientation === "portrait" ? p.widthCm : p.heightCm;
};
/** Classic frames are about 2 cm wide; the mount border about 5 cm. */
const mouldingWidth = (d: D, width: number) => (d.frame !== "none" ? Math.max(5, (width * 2.1) / posterCm(d)) : 0);
const mountWidth = (d: D, width: number) => (d.frame !== "none" && d.mount && d.mount !== "none" ? (width * 5) / posterCm(d) : 0);
/** Everything drawn outside the poster on each side: frame moulding plus any mount. */
export const frameWidth = (d: D, width: number) => mouldingWidth(d, width) + mountWidth(d, width);

const WOOD = new Set(["oak", "brown"]);

/** One mitred side of the frame, shaded as if lit from the top left. */
function Side({ side, fw, base, wood }: { side: "top" | "bottom" | "left" | "right"; fw: number; base: string; wood: boolean }) {
  const clip = {
    top: `polygon(0 0, 100% 0, calc(100% - ${fw}px) ${fw}px, ${fw}px ${fw}px)`,
    bottom: `polygon(${fw}px calc(100% - ${fw}px), calc(100% - ${fw}px) calc(100% - ${fw}px), 100% 100%, 0 100%)`,
    left: `polygon(0 0, ${fw}px ${fw}px, ${fw}px calc(100% - ${fw}px), 0 100%)`,
    right: `polygon(100% 0, 100% 100%, calc(100% - ${fw}px) calc(100% - ${fw}px), calc(100% - ${fw}px) ${fw}px)`,
  }[side];
  const across = side === "top" ? "to bottom" : side === "bottom" ? "to top" : side === "left" ? "to right" : "to left";
  const along = side === "top" || side === "bottom" ? "to right" : "to bottom";
  // light: top brightest, left next, right darker, bottom darkest
  const light = { top: 0.22, left: 0.1, right: -0.12, bottom: -0.22 }[side];
  const tone = light >= 0 ? `rgba(255,255,255,${light})` : `rgba(0,0,0,${-light})`;
  const layers = [
    // the rounded profile of the moulding: a highlight ridge near the outer edge, darker towards the glass
    `linear-gradient(${across}, rgba(0,0,0,0.22) 0%, rgba(255,255,255,0.18) 18%, rgba(255,255,255,0.06) 45%, rgba(0,0,0,0.08) 80%, rgba(0,0,0,0.35) 100%)`,
    `linear-gradient(${tone}, ${tone})`,
    ...(wood
      ? [`repeating-linear-gradient(${along}, rgba(0,0,0,0.05) 0 1px, transparent 1px 3px, rgba(255,255,255,0.04) 3px 4px, transparent 4px 7px)`]
      : []),
    base,
  ];
  return <div aria-hidden className="absolute inset-0 pointer-events-none" style={{ clipPath: clip, background: layers.join(", ") }} />;
}

/**
 * The poster with its chosen frame drawn around it (the frame sits outside `width`).
 * Frames are drawn as real moulding at true scale: mitred corners, light from the
 * top left, wood grain, the artwork recessed behind Perspex. `realistic` adds the
 * look of an actual print in a room (paper tone, soft light, a wall shadow), for
 * the "On the wall" view.
 * Read-only previews are laid out at the design's own width and scaled, so a
 * thumbnail shows exactly what the print will.
 */
export default function FramedPoster(props: ComponentProps<typeof Poster> & { shadow?: boolean; realistic?: boolean }) {
  const { shadow = true, realistic = false, ...rest } = props;
  const { design, width, editable } = props;
  const frame = FRAMES.find((f) => f.id === design.frame);
  const framed = !!frame && frame.id !== "none";
  const fw = mouldingWidth(design, width);
  const mw = mountWidth(design, width);
  const mount = MOUNTS.find((m) => m.id === design.mount);
  const ref = design.view.refWidth;
  const scaled = !editable && Math.abs(width - ref) > 1;
  const h = width * posterAspect(design.productId, design.orientation);
  const unit = width / 100;
  // Framed prints are always on Matte art (Prodigi's A-size frames use it).
  const paper: PaperId = framed ? "ema" : (design.paper ?? "ema");

  const wallShadow = realistic
    ? // light from the left: a tight contact shadow plus a soft one falling down and right
      `${unit * 0.4}px ${unit * 0.6}px ${unit * 0.8}px rgba(0,0,0,0.28), ${unit * 2.2}px ${unit * 3.4}px ${unit * 5}px -${unit * 0.8}px rgba(0,0,0,0.3)`
    : "0 30px 60px -15px rgba(31,36,48,0.4), 0 6px 12px -4px rgba(31,36,48,0.2)";

  const art = (
    <div
      style={{
        lineHeight: 0,
        width,
        height: h,
        overflow: "hidden",
        position: "relative",
        // printed ink is a little softer than a screen, and differs by paper
        filter: realistic ? `${INK[paper]} brightness(0.98)` : INK[paper],
      }}
    >
      {scaled ? (
        <div style={{ transform: `scale(${width / ref})`, transformOrigin: "top left", width: ref }}>
          <Poster {...rest} width={ref} />
        </div>
      ) : (
        <Poster {...rest} />
      )}
      {/* the paper itself: its tooth, texture or sheen (never part of the print file) */}
      <div aria-hidden className={`mapsie-paper-look paper-${paper}`} style={{ opacity: PAPER_OPACITY[paper] * (realistic ? 1 : 0.7) }} />
    </div>
  );

  // Unframed: a sheet of paper, slightly lifted off the wall.
  if (!framed) {
    return (
      <div style={{ position: "relative", boxShadow: shadow ? wallShadow : undefined, lineHeight: 0 }}>
        {art}
        {realistic && <div aria-hidden className="absolute inset-0 pointer-events-none" style={{ background: "linear-gradient(100deg, rgba(255,250,240,0.10), transparent 45%, rgba(0,0,0,0.08))" }} />}
      </div>
    );
  }

  const base = frame.finish ?? frame.color;
  const recess: CSSProperties = {
    // the frame's inner lip casts a shadow onto whatever sits behind the glass
    boxShadow: `inset ${unit * 0.25}px ${unit * 0.35}px ${unit * 0.6}px rgba(0,0,0,0.35), inset 0 0 0 1px rgba(0,0,0,0.25)`,
  };

  return (
    <div style={{ position: "relative", padding: fw, boxShadow: shadow ? wallShadow : undefined, lineHeight: 0 }}>
      {(["top", "bottom", "left", "right"] as const).map((s) => (
        <Side key={s} side={s} fw={fw} base={base} wood={WOOD.has(frame.id)} />
      ))}
      <div style={{ position: "relative" }}>
        {mw > 0 ? (
          <div style={{ padding: mw, background: mount?.color, position: "relative" }}>
            {/* the bevelled cut edge of the mount around the window */}
            <div style={{ position: "relative", boxShadow: `0 0 0 ${Math.max(1, unit * 0.35)}px rgba(255,255,255,0.9), 0 0 0 ${Math.max(1.5, unit * 0.5)}px rgba(0,0,0,0.12)` }}>{art}</div>
          </div>
        ) : (
          art
        )}
        <div aria-hidden className="absolute inset-0 pointer-events-none" style={recess} />
        {/* glazing: a faint reflection across the Perspex */}
        <div
          aria-hidden
          className="absolute inset-0 pointer-events-none"
          style={{
            background:
              "linear-gradient(115deg, rgba(255,255,255,0.16) 0%, rgba(255,255,255,0.05) 22%, transparent 38%, transparent 58%, rgba(255,255,255,0.07) 64%, transparent 76%)",
          }}
        />
        {realistic && (
          <div aria-hidden className="absolute inset-0 pointer-events-none" style={{ background: "linear-gradient(100deg, rgba(255,250,240,0.08), transparent 45%, rgba(0,0,0,0.08))" }} />
        )}
      </div>
    </div>
  );
}
