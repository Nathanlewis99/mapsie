"use client";
import dynamic from "next/dynamic";
import { useId } from "react";
import StickerFilters from "./StickerFilters";
import { DEFAULT_TEXT, type Design, type TextCase } from "@/lib/types";
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
  const needed =
    u * 4 +
    lines(design.title.length, titleFont, width * 0.86) * titleFont * 1.08 +
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

  const titleBlock = (box?: React.CSSProperties) => (
    <div
      onPointerDown={drag("title")}
      className={`flex flex-col ${movable}`}
      title={editable ? "Drag to move the title" : undefined}
      style={{ ...box, alignItems: items, textAlign: align, transform: off(t.titleOffset), maxWidth: "100%" }}
    >
      <div
        style={{
          fontFamily: font,
          fontSize: u * (design.font === "bebas" ? 8 : 6.2) * t.titleSize,
          lineHeight: 1.05,
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
            maxWidth: width * 0.8,
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
        {design.theme.details?.compass && <Compass u={u} ink={c.ink} accent={c.accent} paper={c.paper} />}
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

/** A classic compass rose for the corner of the map. */
function Compass({ u, ink, accent, paper }: { u: number; ink: string; accent: string; paper: string }) {
  const long = (a: number, fill: string) => <path d="M0 -44 L7 0 L0 0 Z M0 -44 L-7 0 L0 0 Z" fill={fill} transform={`rotate(${a})`} />;
  return (
    <svg viewBox="-60 -62 120 120" className="absolute pointer-events-none" style={{ right: u * 3, bottom: u * 3, width: u * 11, height: u * 11 }}>
      <circle r="33" fill={paper} fillOpacity="0.55" stroke={ink} strokeOpacity="0.6" strokeWidth="1" />
      <circle r="29" fill="none" stroke={ink} strokeOpacity="0.4" strokeWidth="0.6" strokeDasharray="1.5 2.2" />
      {[45, 135, 225, 315].map((a) => (
        <path key={a} d="M0 -28 L4.5 0 L-4.5 0 Z" fill={ink} fillOpacity="0.55" transform={`rotate(${a})`} />
      ))}
      {[0, 90, 180, 270].map((a) => (
        <g key={a}>
          {long(a, a === 0 ? accent : ink)}
          <path d="M0 -44 L7 0 L0 0 Z" fill={paper} fillOpacity="0.45" transform={`rotate(${a})`} />
        </g>
      ))}
      <circle r="3" fill={paper} stroke={ink} strokeWidth="1" />
      <text y="-48" textAnchor="middle" fontSize="13" fontWeight="700" fill={ink} style={{ fontFamily: "var(--f-playfair), serif" }}>N</text>
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
