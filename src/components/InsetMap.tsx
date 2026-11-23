"use client";
import { useEffect, useMemo, useState } from "react";
import { loadCountries } from "@/lib/countries";
import { insetExtent, merc, overlaps, pathFor, polygonsOf, viewBox, type Box, type LngLat } from "@/lib/inset";
import type { Design } from "@/lib/types";

interface Admin1 {
  regions: { n: string; c: string; x: number; y: number; a: number; g: number[][][][] }[];
  countries: { n: string; x: number; y: number; r: number }[];
}
let admin1: Promise<Admin1> | null = null;
/** State/province outlines and label points (Natural Earth; see scripts/build/admin1.py). Loaded only when used. */
const loadAdmin1 = () => (admin1 ??= fetch("/geo/admin1.json").then((r) => r.json()));

/**
 * A small overview map in a corner of the poster: the whole country (or countries) of the trip,
 * the route as a line, and a box marking the area the main map shows. No stickers: it's a guide.
 * Drawn as SVG from the country outlines, so it's crisp in print and needs no second map.
 */
export default function InsetMap({ design, u, mapW, mapH, posterW }: { design: Design; u: number; mapW: number; mapH: number; posterW: number }) {
  const d = design.theme.details;
  const c = design.theme.colors;
  const [world, setWorld] = useState<GeoJSON.FeatureCollection | null>(null);
  const wantAdmin = !!(d?.insetLabels || d?.insetRegions);
  const [admin, setAdmin] = useState<Admin1 | null>(null);
  useEffect(() => {
    if (!wantAdmin || admin) return;
    let done = false;
    const w = window as unknown as { __MAPSIE_WAIT?: Promise<unknown>[] };
    const p = loadAdmin1().then((a) => !done && setAdmin(a)).catch(() => {});
    (w.__MAPSIE_WAIT ??= []).push(p);
    return () => {
      done = true;
    };
  }, [wantAdmin, admin]);
  useEffect(() => {
    let done = false;
    // The print renderer waits for this before taking its picture.
    const w = window as unknown as { __MAPSIE_WAIT?: Promise<unknown>[] };
    const p = loadCountries().then((fc) => !done && setWorld(fc)).catch(() => {});
    (w.__MAPSIE_WAIT ??= []).push(p);
    return () => {
      done = true;
    };
  }, []);

  const drawn = useMemo(() => {
    if (!world || design.stops.length < 1) return null;
    const ext = insetExtent(world, design.stops);
    if (!ext) return null;
    // The box takes the shape of the area (wide for Australia, tall for Chile), within limits.
    const aspect = (ext.y1 - ext.y0) / (ext.x1 - ext.x0);
    const w = Math.min(mapW, mapH) * (d?.insetSize ?? 0.3);
    const h = w * Math.min(1.35, Math.max(0.6, aspect));
    // Re-fit the area to the box's shape, so nothing is squashed.
    const cx = (ext.x0 + ext.x1) / 2;
    const cy = (ext.y0 + ext.y1) / 2;
    let ew = ext.x1 - ext.x0;
    let eh = ext.y1 - ext.y0;
    if (eh / ew > h / w) ew = (eh * w) / h;
    else eh = (ew * h) / w;
    const box: Box = { x0: cx - ew / 2, x1: cx + ew / 2, y0: cy - eh / 2, y1: cy + eh / 2 };
    const land = world.features.filter((f) => overlaps(f.geometry, box)).map((f) => pathFor(polygonsOf(f.geometry), box, w, h)).join("");
    const px = ([lng, lat]: LngLat) => {
      const [x, y] = merc([lng, lat]);
      return [((x - box.x0) / ew) * w, ((y - box.y0) / eh) * h] as const;
    };
    // The route: the roads actually driven where we have them, otherwise straight between stops.
    const legs: string[] = [];
    design.stops.forEach((s, i) => {
      if (i === 0) return;
      const pts: LngLat[] = s.path?.length ? (s.path as LngLat[]) : [[design.stops[i - 1].lng, design.stops[i - 1].lat], [s.lng, s.lat]];
      legs.push(pts.map((p, k) => `${k ? "L" : "M"}${px(p).map((v) => v.toFixed(1)).join(" ")}`).join(""));
    });
    // What the main map shows (its size at this poster width), unless it's turned.
    const zoom = design.view.zoom + Math.log2(posterW / design.view.refWidth);
    const v = viewBox(design.view.center, zoom, mapW, mapH);
    const frame = design.view.bearing ? null : { x: ((v.x0 - box.x0) / ew) * w, y: ((v.y0 - box.y0) / eh) * h, w: ((v.x1 - v.x0) / ew) * w, h: ((v.y1 - v.y0) / eh) * h };
    // Only worth a box if the main map is noticeably smaller than the overview.
    const showFrame = frame && frame.w < w * 0.8 && frame.h < h * 0.8;
    // States and provinces, and names, if asked for.
    const regionLines = d?.insetRegions && admin ? admin.regions.filter((r) => overlaps({ type: "MultiPolygon", coordinates: r.g }, box)).map((r) => pathFor(r.g, box, w, h)).join("") : "";
    const labels: { x: number; y: number; text: string; kind: "country" | "region" }[] = [];
    if (admin) {
      const fs = { country: Math.max(5, u * 1.05), region: Math.max(4.5, u * 0.85) };
      const taken: { x0: number; y0: number; x1: number; y1: number }[] = [];
      const place = (text: string, lng: number, lat: number, kind: "country" | "region") => {
        const [x, y] = px([lng, lat]);
        const size = fs[kind];
        const tw = text.length * size * (kind === "country" ? 0.72 : 0.55);
        const r = { x0: x - tw / 2, y0: y - size * 0.7, x1: x + tw / 2, y1: y + size * 0.5 };
        if (r.x0 < 2 || r.x1 > w - 2 || r.y0 < 2 || r.y1 > h - 2) return;
        if (taken.some((t) => r.x0 < t.x1 && r.x1 > t.x0 && r.y0 < t.y1 && r.y1 > t.y0)) return;
        taken.push(r);
        labels.push({ x, y, text, kind });
      };
      // Country names: the major ones only (Natural Earth label rank), so tiny territories stay quiet.
      if (d?.insetLabels) for (const c of [...admin.countries].filter((c) => c.r <= 4).sort((a, b) => a.r - b.r)) place(c.n, c.x, c.y, "country");
      if (d?.insetRegions) {
        // Only regions big enough on the overview to hold their name.
        const big = admin.regions
          .map((r) => {
            let x0 = 1e9, x1 = -1e9;
            for (const poly of r.g) for (const p of poly[0]) {
              const [x] = px(p as LngLat);
              x0 = Math.min(x0, x);
              x1 = Math.max(x1, x);
            }
            return { r, span: x1 - x0 };
          })
          .filter((o) => o.span > w * 0.12)
          .sort((a, b) => b.span - a.span);
        for (const { r } of big) place(r.n, r.x, r.y, "region");
      }
    }
    return { w, h, land, legs, regionLines, labels, stops: design.stops.map((s) => px([s.lng, s.lat])), frame: showFrame ? frame : null };
  }, [world, admin, design.stops, design.view, d?.insetSize, d?.insetLabels, d?.insetRegions, mapW, mapH, posterW, u]);

  if (!drawn) return null;
  const corner = d?.insetCorner ?? "bl";
  const rule = Math.max(1, u * 0.22);
  return (
    <div
      className="pointer-events-none absolute"
      style={{
        [corner[1] === "r" ? "right" : "left"]: u * 3,
        [corner[0] === "b" ? "bottom" : "top"]: u * 3,
        width: drawn.w,
        height: drawn.h,
        zIndex: 2,
        background: c.water,
        boxShadow: `0 0 0 ${rule}px ${c.ink}, 0 ${u * 0.6}px ${u * 1.6}px rgba(0,0,0,.18)`,
        overflow: "hidden",
      }}
    >
      <svg width={drawn.w} height={drawn.h} viewBox={`0 0 ${drawn.w} ${drawn.h}`} style={{ display: "block" }}>
        <path d={drawn.land} fill={c.land} stroke={c.borders} strokeWidth={Math.max(0.5, u * 0.08)} strokeLinejoin="round" fillRule="evenodd" />
        {drawn.regionLines && (
          <path d={drawn.regionLines} fill="none" stroke={c.borders} strokeOpacity={0.8} strokeWidth={Math.max(0.4, u * 0.06)} strokeDasharray={`${u * 0.5} ${u * 0.3}`} strokeLinejoin="round" />
        )}
        {drawn.frame && (
          <rect x={drawn.frame.x} y={drawn.frame.y} width={drawn.frame.w} height={drawn.frame.h} fill={c.accent} fillOpacity={0.1} stroke={c.ink} strokeWidth={Math.max(0.8, u * 0.15)} strokeDasharray={`${u * 0.6} ${u * 0.4}`} />
        )}
        <path d={drawn.legs.join("")} fill="none" stroke={c.accent} strokeWidth={Math.max(1.2, u * 0.32)} strokeLinecap="round" strokeLinejoin="round" />
        {drawn.labels.map((l) => (
          <text
            key={`${l.kind}-${l.text}`}
            x={l.x}
            y={l.y}
            textAnchor="middle"
            fontSize={l.kind === "country" ? Math.max(5, u * 1.05) : Math.max(4.5, u * 0.85)}
            fontWeight={l.kind === "country" ? 700 : 600}
            fontStyle={l.kind === "region" ? "italic" : undefined}
            letterSpacing={l.kind === "country" ? "0.12em" : undefined}
            fill={c.labels}
            fillOpacity={l.kind === "country" ? 0.85 : 0.7}
            stroke={c.land}
            strokeWidth={Math.max(1, u * 0.25)}
            paintOrder="stroke"
            style={{ fontFamily: "var(--f-playfair), Georgia, serif" }}
          >
            {l.kind === "country" ? l.text.toUpperCase() : l.text}
          </text>
        ))}
        {drawn.stops.map(([x, y], i) => (
          <circle key={i} cx={x} cy={y} r={Math.max(1.2, u * 0.32)} fill={c.paper} stroke={c.accent} strokeWidth={Math.max(0.8, u * 0.16)} />
        ))}
      </svg>
    </div>
  );
}
