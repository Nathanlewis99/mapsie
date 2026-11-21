"use client";
import dynamic from "next/dynamic";
import { useId } from "react";
import StickerFilters from "./StickerFilters";
import { DEFAULT_TEXT, type CompassStyle, type Design, type TextCase } from "@/lib/types";
import { posterAspect } from "@/lib/products";
import { fontBold, fontCss } from "@/lib/fonts";
import type { MapHandlers } from "./MapView";

const MapView = dynamic(() => import("./MapView"), { ssr: false });

interface Props {
  design: Design;
  width: number;
  editable?: boolean;
  print?: boolean;
  selectedSticker?: string | null;
  selectedLabel?: string | null;
  fitRequest?: number;
  handlers?: MapHandlers;
  onReady?: () => void;
  frozen?: boolean;
}

/** Everything is sized relative to the poster width, so it scales to any print size. */

/** Title fonts whose descenders need extra line height. */
const TALL_TAILS = new Set(["pacifico", "vibes", "satisfy", "lobster", "dancing", "caveat", "kalam", "rocksalt", "marker"]);

export default function Poster({ design, width, editable = false, print, selectedSticker, selectedLabel, fitRequest, handlers, onReady, frozen }: Props) {
  const height = Math.round(width * posterAspect(design.productId, design.orientation));
  const u = width / 100;
  // Each poster gets its own filter ids, since thumbnails may show different themes.
  const filterPrefix = `mf${useId().replace(/[^a-zA-Z0-9]/g, "")}`;
  const c = design.theme.colors;
  const landscape = design.orientation === "landscape";
  const t = design.text ?? DEFAULT_TEXT;
  const mapOnly = design.layout === "none";
  const route = t.showRoute && !mapOnly ? design.stops.map((s) => s.name).join("  ·  ") : "";
  // The title area grows to fit a big title, a subtitle and the list of stops.
  const lines = (chars: number, fontPx: number, boxPx: number) => Math.max(1, Math.ceil((chars * fontPx * 0.55) / boxPx));
  const titleFont = u * (design.font === "bebas" ? 8 : 6.2) * t.titleSize;
  // Script fonts have long tails (g, p, y) that hang well below the line: give them room
  // so they don't run into the subtitle.
  const titleLine = TALL_TAILS.has(design.font) ? 1.42 : 1.05;
  const needed =
    u * 4 +
    lines(design.title.length, titleFont, width * 0.86) * titleFont * (titleLine + 0.03) +
    (design.subtitle ? u * 2.1 * t.subtitleSize * 1.3 + u : 0) +
    (route ? Math.min(2, lines(route.length, u * 1.5, width * 0.78)) * u * 1.5 * 1.35 + u * 0.9 : 0);
  const bandH = design.layout === "overlay" || mapOnly ? 0 : Math.max(u * (landscape ? 11 : 17), needed);
  const pad = design.layout === "border" ? u * 4.5 : 0;
  const mapW = width - pad * 2;
  const mapH = height - bandH - pad * (design.layout === "border" ? 1 : 0) - pad;
  const font = fontCss(design.font);
  const tt = (c: TextCase) => (c === "upper" ? "uppercase" : c === "lower" ? "lowercase" : "none");
  const align = t.align;
  const items = align === "left" ? "flex-start" : align === "right" ? "flex-end" : "center";
  const off = (o?: [number, number]) => (o ? `translate(${o[0] * u}px, ${o[1] * u}px)` : undefined);
  const drag = (which: "title" | "subtitle") => (editable && handlers?.onTextMove ? textDrag(which, which === "title" ? t.titleOffset : t.subtitleOffset, u, handlers.onTextMove) : undefined);
  const movable = editable && handlers?.onTextMove ? "pointer-events-auto cursor-move touch-none hover:outline-dashed hover:outline-2 hover:outline-offset-4 hover:outline-coral/60" : "";

  const subtitle = design.subtitle && (
    <div
      onPointerDown={drag("subtitle")}
      className={movable}
      title={editable ? "Drag to move the subtitle" : undefined}
      style={{
        fontFamily: fontCss(t.subtitleFont),
        fontStyle: t.subtitleItalic ? "italic" : undefined,
        fontWeight: t.subtitleFont === "montserrat" || t.subtitleFont === "josefin" ? 500 : undefined,
        fontSize: u * 2.1 * t.subtitleSize,
        letterSpacing: u * t.subtitleSpacing,
        textTransform: tt(t.subtitleCase),
        color: c.ink,
        opacity: 0.75,
        marginTop: u * 1,
        transform: off(t.subtitleOffset),
      }}
    >
      {design.subtitle}
    </div>
  );

  const cart = t.cartouche && t.cartouche !== "none" ? t.cartouche : null;
  const titleBlock = (box?: React.CSSProperties) => (
    <div
      onPointerDown={drag("title")}
      className={`flex flex-col ${movable}`}
      title={editable ? "Drag to move the title" : undefined}
      style={{
        ...box,
        alignItems: items,
        textAlign: align,
        transform: off(t.titleOffset),
        maxWidth: "100%",
        ...(cart ? { position: "relative", padding: cart === "oval" ? `${u * 2.4}px ${u * 7}px` : `${u * 1.6}px ${u * 5}px`, ...(design.layout === "overlay" ? { background: "transparent" } : {}) } : {}),
      }}
    >
      {cart && <Cartouche kind={cart} u={u} ink={c.ink} paper={c.paper} />}
      <div
        style={{
          fontFamily: font,
          fontSize: titleFont,
          lineHeight: titleLine,
          color: c.ink,
          fontWeight: fontBold(design.font),
          fontStyle: t.titleItalic ? "italic" : undefined,
          textTransform: tt(t.titleCase),
          letterSpacing: u * (t.titleSpacing + (design.font === "bebas" ? 0.15 : 0)),
        }}
      >
        {design.title}
      </div>
      {subtitle}
      {route && (
        <div
          style={{
            fontFamily: "var(--f-montserrat), sans-serif",
            fontSize: u * 1.5,
            lineHeight: 1.35,
            color: c.ink,
            opacity: 0.6,
            marginTop: u * 0.9,
            width: "max-content",
            maxWidth: width * (cart === "oval" ? 0.58 : 0.8),
            display: "-webkit-box",
            WebkitLineClamp: 2,
            WebkitBoxOrient: "vertical",
            overflow: "hidden",
          }}
        >
          {route}
        </div>
      )}
    </div>
  );

  return (
    <div
      id="poster"
      className="relative overflow-hidden select-none"
      onContextMenu={print ? undefined : (e) => e.preventDefault()}
      style={{ width, height, background: c.paper, ["--u" as string]: `${u}px` }}
    >
      <StickerFilters prefix={filterPrefix} colors={c} />
      <div
        className="absolute overflow-hidden"
        style={{
          left: pad,
          top: pad,
          width: mapW,
          height: mapH,
          outline: design.layout === "border" ? `${Math.max(1, u * 0.25)}px solid ${c.ink}` : undefined,
          // Aged paper also gently yellows and softens the map itself.
          filter: design.theme.texture ? "sepia(0.22) saturate(0.88) contrast(0.97)" : undefined,
        }}
      >
        <MapView
          design={design}
          width={width}
          mapWidth={mapW}
          height={mapH}
          editable={editable}
          print={print}
          selectedSticker={selectedSticker}
          selectedLabel={selectedLabel}
          fitRequest={fitRequest}
          handlers={handlers}
          onReady={onReady}
          frozen={frozen}
          filterPrefix={filterPrefix}
        />
        {design.theme.details?.neatline && <Neatline u={u} ink={c.ink} paper={c.paper} />}
        {design.theme.details?.compass && (
          <Compass u={u} ink={c.ink} accent={c.accent} paper={c.paper} variant={design.theme.details.compassStyle} corner={design.theme.details.compassCorner} />
        )}
      </div>

      {mapOnly ? null : design.layout !== "overlay" ? (
        <div
          className="absolute left-0 right-0 bottom-0 flex flex-col justify-center pointer-events-none"
          style={{ height: bandH + (design.layout === "border" ? pad * 0.4 : 0), alignItems: items, padding: `0 ${u * 6}px`, zIndex: 3 }}
        >
          {titleBlock()}
        </div>
      ) : (
        <div
          className="absolute left-1/2 -translate-x-1/2 pointer-events-none"
          style={{ bottom: u * 5, maxWidth: "86%", zIndex: 3 }}
        >
          {titleBlock({ background: c.paper + "e6", padding: `${u * 2.2}px ${u * 5}px`, borderRadius: u * 1.5 })}
        </div>
      )}

      {design.theme.texture && <div className="mapsie-paper pointer-events-none absolute inset-0" style={{ zIndex: 4 }} />}
      {/* Previews carry a watermark; only the paid print file is clean. */}
      {!print && <Watermark u={u} ink={c.ink} />}

    </div>
  );
}

/**
 * An atlas neatline round the map: an outer rule, a band of alternating ink and paper
 * (the degree scale on old maps), and an inner rule.
 */
function Neatline({ u, ink, paper }: { u: number; ink: string; paper: string }) {
  const band = u * 1.1;
  const seg = u * 2.6;
  const rule = Math.max(1, u * 0.18);
  const keys = (dir: "to right" | "to bottom") => `repeating-linear-gradient(${dir}, ${ink} 0 ${seg}px, ${paper} ${seg}px ${seg * 2}px)`;
  const edge = (pos: React.CSSProperties, dir: "to right" | "to bottom") => (
    <div className="absolute" style={{ ...pos, background: keys(dir), boxShadow: `inset 0 0 0 ${rule}px ${ink}` }} />
  );
  return (
    <div className="pointer-events-none absolute inset-0" style={{ zIndex: 2 }}>
      {edge({ left: 0, right: 0, top: 0, height: band }, "to right")}
      {edge({ left: 0, right: 0, bottom: 0, height: band }, "to right")}
      {edge({ top: 0, bottom: 0, left: 0, width: band }, "to bottom")}
      {edge({ top: 0, bottom: 0, right: 0, width: band }, "to bottom")}
      {/* the inner rule, a hair inside the band */}
      <div className="absolute" style={{ inset: band + u * 0.35, border: `${rule}px solid ${ink}` }} />
    </div>
  );
}

/** An ornamental frame round the title, after old-map cartouches. Sits behind the text. */
function Cartouche({ kind, u, ink, paper }: { kind: "plaque" | "scroll" | "oval"; u: number; ink: string; paper: string }) {
  const rule = Math.max(1, u * 0.2);
  const base: React.CSSProperties = { position: "absolute", inset: 0, zIndex: -1, pointerEvents: "none" };
  if (kind === "oval") {
    return (
      <div style={{ ...base, background: paper, borderRadius: "50%", border: `${rule * 3}px double ${ink}`, boxShadow: `0 0 0 ${u * 0.5}px ${paper}, 0 0 0 ${u * 0.5 + rule}px ${ink}` }} />
    );
  }
  // A curl for the ends of the scroll and the plaque's corners (fixed shape, scaled to the block).
  const curl = (flip: boolean, style: React.CSSProperties) => (
    <svg viewBox="0 0 40 100" preserveAspectRatio="xMidYMid meet" style={{ position: "absolute", top: 0, bottom: 0, height: "100%", width: "auto", transform: flip ? "scaleX(-1)" : undefined, overflow: "visible", ...style }}>
      <path d="M38 6 C14 6 4 22 4 40 C4 58 16 66 26 62 C36 58 34 44 24 44 C16 44 14 54 22 56" fill="none" stroke={ink} strokeWidth={2.2} strokeLinecap="round" />
      <path d="M38 94 C14 94 4 78 4 60" fill="none" stroke={ink} strokeWidth={2.2} strokeLinecap="round" />
      <path d="M38 6 C26 18 26 82 38 94" fill={paper} stroke={ink} strokeWidth={1.6} />
    </svg>
  );
  if (kind === "scroll") {
    return (
      <div style={base}>
        <div style={{ position: "absolute", inset: `0 ${u * 2.2}px`, background: paper, borderTop: `${rule * 3}px double ${ink}`, borderBottom: `${rule * 3}px double ${ink}` }} />
        {curl(false, { left: -u * 0.6 })}
        {curl(true, { right: -u * 0.6 })}
      </div>
    );
  }
  // Plaque: a double-ruled panel with small flourishes at the corners.
  const corner = (pos: React.CSSProperties, rot: number) => (
    <svg viewBox="0 0 20 20" style={{ position: "absolute", width: u * 3, height: u * 3, transform: `rotate(${rot}deg)`, ...pos }}>
      <path d="M2 18 C2 8 8 2 18 2 M6 18 C6 11 11 6 18 6 M2 18 C6 14 10 14 12 18" fill="none" stroke={ink} strokeWidth={1.3} strokeLinecap="round" />
    </svg>
  );
  return (
    <div style={{ ...base, background: paper, border: `${rule * 3}px double ${ink}`, outline: `${rule}px solid ${ink}`, outlineOffset: u * 0.5 }}>
      {corner({ left: -u * 1.6, top: -u * 1.6 }, 0)}
      {corner({ right: -u * 1.6, top: -u * 1.6 }, 90)}
      {corner({ right: -u * 1.6, bottom: -u * 1.6 }, 180)}
      {corner({ left: -u * 1.6, bottom: -u * 1.6 }, 270)}
    </div>
  );
}

/** Compass roses for the corner of the map, in a few styles. */
export function Compass({ u, ink, accent, paper, variant = "classic", corner = "br", size = 11, inline = false }: {
  u: number; ink: string; accent: string; paper: string; variant?: CompassStyle; corner?: "br" | "bl" | "tr" | "tl"; size?: number; inline?: boolean;
}) {
  const pos = inline
    ? { width: "100%", height: "100%" }
    : { [corner[1] === "r" ? "right" : "left"]: u * 3, [corner[0] === "b" ? "bottom" : "top"]: u * 3, width: u * size, height: u * size };
  const serif = { fontFamily: "var(--f-playfair), serif" };
  const N = (y: number, fs = 13) => <text y={y} textAnchor="middle" fontSize={fs} fontWeight="700" fill={ink} style={serif}>N</text>;
  const half = (a: number, len: number, w: number, fill: string, op = 1) => (
    <path key={`${a}-${len}`} d={`M0 ${-len} L${w} 0 L0 0 Z`} fill={fill} fillOpacity={op} transform={`rotate(${a})`} />
  );
  const star = (a: number, len: number, w: number, dark: string, light: string) => (
    <g key={`s${a}-${len}`}>
      {half(a, len, w, dark)}
      <path d={`M0 ${-len} L${-w} 0 L0 0 Z`} fill={light} transform={`rotate(${a})`} />
    </g>
  );
  let body: React.ReactNode;
  if (variant === "minimal") {
    body = (
      <>
        <path d="M0 -40 L11 22 L0 12 L-11 22 Z" fill={ink} />
        <path d="M0 -40 L0 12 L-11 22 Z" fill={accent} />
        {N(-46, 15)}
      </>
    );
  } else if (variant === "nautical") {
    // 32-point mariner's rose with a fleur-de-lis north.
    body = (
      <>
        <circle r="40" fill={paper} fillOpacity="0.6" stroke={ink} strokeWidth="1.2" />
        <circle r="36" fill="none" stroke={ink} strokeOpacity="0.5" strokeWidth="0.6" />
        {Array.from({ length: 32 }, (_, i) => i * 11.25).filter((a) => a % 45 !== 0).map((a) => half(a, a % 22.5 === 0 ? 30 : 22, 2.6, ink, 0.45))}
        {[45, 135, 225, 315].map((a) => star(a, 32, 5, ink, paper))}
        {[90, 180, 270].map((a) => star(a, 40, 6.5, ink, accent))}
        {star(0, 40, 6.5, accent, paper)}
        <path d="M0 -58 C-3 -52 -8 -51 -9 -47 C-5 -48 -2 -47 0 -44 C2 -47 5 -48 9 -47 C8 -51 3 -52 0 -58 Z M-6 -44 H6" fill={accent} stroke={accent} strokeWidth="1.2" />
        <circle r="3.5" fill={accent} stroke={paper} strokeWidth="1" />
      </>
    );
  } else if (variant === "vintage") {
    body = (
      <>
        <circle r="44" fill={paper} fillOpacity="0.7" stroke={ink} strokeWidth="1.4" />
        <circle r="39" fill="none" stroke={ink} strokeWidth="0.6" />
        {Array.from({ length: 72 }, (_, i) => i * 5).map((a) => (
          <line key={a} y1={-39} y2={a % 30 === 0 ? -33 : -36} stroke={ink} strokeWidth={a % 30 === 0 ? 1 : 0.5} transform={`rotate(${a})`} />
        ))}
        {[30, 60, 120, 150, 210, 240, 300, 330].map((a) => (
          <text key={a} transform={`rotate(${a}) translate(0 -27)`} textAnchor="middle" fontSize="5" fill={ink} fillOpacity="0.7" style={serif}>{a}</text>
        ))}
        {[45, 135, 225, 315].map((a) => star(a, 22, 4, ink, paper))}
        {[0, 90, 180, 270].map((a) => star(a, 31, 5.5, a === 0 ? accent : ink, paper))}
        <circle r="4" fill={paper} stroke={ink} strokeWidth="1" />
        {[["N", 0], ["E", 90], ["S", 180], ["W", 270]].map(([l, a]) => (
          <text key={l} transform={`rotate(${a}) translate(0 -53) rotate(${-Number(a)})`} textAnchor="middle" dominantBaseline="middle" fontSize="9" fontWeight="700" fill={l === "N" ? accent : ink} style={serif}>{l}</text>
        ))}
      </>
    );
  } else {
    const long = (a: number, fill: string) => <path d="M0 -44 L7 0 L0 0 Z M0 -44 L-7 0 L0 0 Z" fill={fill} transform={`rotate(${a})`} />;
    body = (
      <>
        <circle r="33" fill={paper} fillOpacity="0.55" stroke={ink} strokeOpacity="0.6" strokeWidth="1" />
        <circle r="29" fill="none" stroke={ink} strokeOpacity="0.4" strokeWidth="0.6" strokeDasharray="1.5 2.2" />
        {[45, 135, 225, 315].map((a) => <path key={a} d="M0 -28 L4.5 0 L-4.5 0 Z" fill={ink} fillOpacity="0.55" transform={`rotate(${a})`} />)}
        {[0, 90, 180, 270].map((a) => (
          <g key={a}>
            {long(a, a === 0 ? accent : ink)}
            <path d="M0 -44 L7 0 L0 0 Z" fill={paper} fillOpacity="0.45" transform={`rotate(${a})`} />
          </g>
        ))}
        <circle r="3" fill={paper} stroke={ink} strokeWidth="1" />
        {N(-48)}
      </>
    );
  }
  return (
    <svg viewBox="-60 -62 120 120" className={inline ? "" : "absolute pointer-events-none"} style={pos}>
      {body}
    </svg>
  );
}

/** Pointer drag for the title block or subtitle. Moves live, saves on release. */
function textDrag(which: "title" | "subtitle", start: [number, number] | undefined, u: number, done: (w: "title" | "subtitle", o: [number, number]) => void) {
  return (e: React.PointerEvent<HTMLDivElement>) => {
    e.stopPropagation();
    e.preventDefault();
    const el = e.currentTarget;
    const k = el.getBoundingClientRect().width / (el.offsetWidth || 1) || 1;
    const [sx, sy] = start ?? [0, 0];
    const x0 = e.clientX, y0 = e.clientY;
    let o: [number, number] = [sx, sy];
    let moved = false;
    const move = (ev: PointerEvent) => {
      if (!moved && Math.hypot(ev.clientX - x0, ev.clientY - y0) < 3) return;
      moved = true;
      o = [Math.round((sx + (ev.clientX - x0) / u / k) * 10) / 10, Math.round((sy + (ev.clientY - y0) / u / k) * 10) / 10];
      el.style.transform = `translate(${o[0] * u}px, ${o[1] * u}px)`;
    };
    const up = () => {
      window.removeEventListener("pointermove", move);
      window.removeEventListener("pointerup", up);
      if (moved) done(which, o);
    };
    window.addEventListener("pointermove", move);
    window.addEventListener("pointerup", up);
  };
}

/** Repeating "mapsie.shop · preview" across the poster, faint enough to design with. */
function Watermark({ u, ink }: { u: number; ink: string }) {
  const tile = 34 * u;
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${tile}" height="${tile}"><g transform="rotate(-30 ${tile / 2} ${tile / 2})" fill="${ink}" font-family="Montserrat Variable, Arial, sans-serif" font-weight="800" text-anchor="middle" letter-spacing="${u * 0.3}"><text x="${tile / 2}" y="${tile * 0.42}" font-size="${u * 3}">MAPSIE.SHOP</text><text x="${tile / 2}" y="${tile * 0.42 + u * 3.2}" font-size="${u * 1.9}">PREVIEW</text></g></svg>`;
  return (
    <div
      aria-hidden
      className="pointer-events-none absolute inset-0 select-none"
      style={{ zIndex: 5, opacity: 0.11, backgroundImage: `url("data:image/svg+xml;utf8,${encodeURIComponent(svg)}")`, backgroundSize: `${tile}px ${tile}px` }}
    />
  );
}
