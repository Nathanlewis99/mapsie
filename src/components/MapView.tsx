"use client";
import { useEffect, useRef } from "react";
import maplibregl, { Map as MLMap, Marker } from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import type { Design, Sticker, Stop } from "@/lib/types";
import { buildStyle, loadBaseStyle } from "@/lib/themes";
import { buildLegs, routeGeoJSON, stopsBounds, MODES } from "@/lib/geo";
import { loadCountries, visitedCountries } from "@/lib/countries";
import { fontCss } from "@/lib/fonts";
import { getArtStyle, stickerSrc } from "@/lib/stickers";
import { originalSrc, resolvePalette } from "@/lib/originals";
import { filterId } from "./StickerFilters";

export interface MapHandlers {
  onView?: (v: Design["view"]) => void;
  onStopMove?: (id: string, lng: number, lat: number) => void;
  onStickerMove?: (id: string, lng: number, lat: number) => void;
  onStickerChange?: (id: string, patch: Partial<Sticker>) => void;
  onStickerSelect?: (id: string | null) => void;
  onLabelSelect?: (stopId: string | null) => void;
  onLabelChange?: (stopId: string, patch: Partial<Stop>) => void;
  onMapClick?: (lng: number, lat: number) => void;
  onDropSticker?: (src: string, lng: number, lat: number) => void;
  /** The title block or subtitle was dragged to a new spot (% of poster width). */
  onTextMove?: (which: "title" | "subtitle", offset: [number, number]) => void;
}

interface Props {
  design: Design;
  width: number; // poster width in CSS px (sizes are relative to this)
  height: number; // map area height
  mapWidth: number; // map area width
  editable: boolean;
  print?: boolean;
  selectedSticker?: string | null;
  selectedLabel?: string | null;
  fitRequest?: number;
  handlers?: MapHandlers;
  filterPrefix?: string; // id prefix of this poster's sticker filters
  onReady?: () => void;
  /** Editor only: keep the framing fixed (no pan/zoom of the map itself). */
  frozen?: boolean;
}

const ROUTE_SRC = "mapsie-route";
const VISITED_SRC = "mapsie-visited";
const EMPTY: GeoJSON.FeatureCollection = { type: "FeatureCollection", features: [] };

// One line layer per look, because dash patterns can't vary per feature.
const ROUTE_LAYERS: { id: string; dash: string; pattern?: number[]; overlay?: boolean }[] = [
  { id: "mapsie-route-solid", dash: "solid" },
  { id: "mapsie-route-dashed", dash: "dashed", pattern: [2.2, 1.6] },
  { id: "mapsie-route-dotted", dash: "dotted", pattern: [0.01, 2] },
  { id: "mapsie-route-rail", dash: "rail" },
  { id: "mapsie-route-rail-ties", dash: "rail", pattern: [1.2, 1.2], overlay: true },
];

declare global {
  interface Window {
    __MAPSIE_READY?: boolean;
    __MAPSIE_ERROR?: string;
    __MAPSIE_GLMAX?: number;
  }
}
/** Largest map canvas for print renders; the renderer can override it. */
const glMax = () => (typeof window !== "undefined" && window.__MAPSIE_GLMAX) || 7680;

/** Multiply-blending only works on light backgrounds. */
const isLight = (hex: string) => {
  const n = parseInt(hex.replace("#", "").slice(0, 6), 16);
  return 0.2126 * ((n >> 16) & 255) + 0.7152 * ((n >> 8) & 255) + 0.0722 * (n & 255) > 140;
};

const esc = (s: string) => s.replace(/[&<>"']/g, (c) => `&#${c.charCodeAt(0)};`);

function markerSvg(style: Design["markers"]["style"], fill: string, stroke: string) {
  if (style === "pin")
    return `<svg viewBox="0 0 24 32" width="100%" height="100%"><path d="M12 31C12 31 2 19.5 2 12a10 10 0 0 1 20 0c0 7.5-10 19-10 19z" fill="${fill}" stroke="${stroke}" stroke-width="2"/><circle cx="12" cy="12" r="4" fill="${stroke}"/></svg>`;
  if (style === "heart")
    return `<svg viewBox="0 0 24 22" width="100%" height="100%"><path d="M12 21s-9-5.6-9-12a5 5 0 0 1 9-3 5 5 0 0 1 9 3c0 6.4-9 12-9 12z" fill="${fill}" stroke="${stroke}" stroke-width="2"/></svg>`;
  return "";
}

export default function MapView(props: Props) {
  const { design, width, height, mapWidth, editable, print, selectedSticker, selectedLabel, fitRequest, handlers, onReady, filterPrefix = "mapsie", frozen = false } = props;
  const el = useRef<HTMLDivElement>(null);
  const map = useRef<MLMap | null>(null);
  const stopMarkers = useRef<Marker[]>([]);
  const stickerMarkers = useRef<Marker[]>([]);
  const modeMarkers = useRef<Marker[]>([]);
  const h = useRef(handlers);
  h.current = handlers;
  const latest = useRef(design);
  latest.current = design;
  const styleReady = useRef(false);
  const widthRef = useRef(width);
  widthRef.current = width;
  const u = width / 100;

  /** Run once the map exists (markers can be added before the style is loaded). */
  const whenMap = (run: (m: MLMap) => void) => {
    if (map.current) {
      run(map.current);
      return;
    }
    const t = setInterval(() => map.current && (clearInterval(t), run(map.current)), 50);
    return () => clearInterval(t);
  };

  // --- create the map once
  useEffect(() => {
    let cancelled = false;
    loadBaseStyle().then((base) => {
      if (cancelled || !el.current) return;
      const d = latest.current;
      // Keep the same framing if the editor is a different width from when the view was saved.
      const zoom = d.view.zoom + Math.log2(widthRef.current / d.view.refWidth);
      const m = new maplibregl.Map({
        container: el.current,
        style: buildStyle(base, d.theme),
        center: d.view.center,
        zoom,
        bearing: d.view.bearing,
        interactive: editable,
        attributionControl: false,
        dragRotate: false,
        pitchWithRotate: false,
        renderWorldCopies: true,
        fadeDuration: print ? 0 : 300,
        canvasContextAttributes: { preserveDrawingBuffer: !!print, antialias: true },
        // In print mode the page runs at a very high pixel density. WebGL tops out
        // around 8192px, so the map is drawn at most that size and gently upscaled,
        // while text, stickers and markers (HTML) stay at full resolution.
        ...(print ? { maxCanvasSize: [glMax(), glMax()] as [number, number] } : {}),
      });
      if (print) {
        // Tell the renderer straight away if WebGL can't start, rather than hanging.
        m.on("error", (e) => {
          const msg = String((e as { error?: Error }).error?.message ?? e);
          if (/webgl/i.test(msg)) window.__MAPSIE_ERROR = msg;
        });
      }
      // Icons used by the map details (current arrows, ships), drawn on demand.
      m.on("styleimagemissing", (e) => {
        const img = detailIcon(e.id);
        if (img && !m.hasImage(e.id)) m.addImage(e.id, img, { sdf: true, pixelRatio: 2 });
      });
      if (editable) m.touchZoomRotate.disableRotation();
      map.current = m;

      m.on("style.load", () => {
        styleReady.current = true;
        syncRoute();
        syncVisited();
      });
      m.on("moveend", () => {
        const c = m.getCenter();
        h.current?.onView?.({ center: [c.lng, c.lat], zoom: m.getZoom(), bearing: m.getBearing(), refWidth: widthRef.current });
      });
      m.on("click", (e) => {
        h.current?.onStickerSelect?.(null);
        h.current?.onLabelSelect?.(null);
        h.current?.onMapClick?.(e.lngLat.lng, e.lngLat.lat);
      });
      if (onReady) {
        m.once("idle", async () => {
          // the visited-countries layer loads asynchronously
          if (latest.current.visited.show) await loadCountries();
          await new Promise((r) => {
            m.once("idle", r);
            m.triggerRepaint();
          });
          await document.fonts.ready;
          onReady();
        });
      }
    });
    return () => {
      cancelled = true;
      map.current?.remove();
      map.current = null;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // --- lock the framing: markers and labels stay editable, the map itself doesn't move
  useEffect(
    () =>
      whenMap((m) => {
        if (!editable) return;
        const hs = [m.dragPan, m.scrollZoom, m.touchZoomRotate, m.doubleClickZoom, m.keyboard, m.boxZoom];
        hs.forEach((x) => (frozen ? x.disable() : x.enable()));
        if (!frozen) m.touchZoomRotate.disableRotation();
      }),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [frozen],
  );

  // --- restyle when the theme changes
  const themeKey = JSON.stringify(design.theme);
  useEffect(() => {
    const m = map.current;
    if (!m) return;
    loadBaseStyle().then((base) => {
      styleReady.current = false;
      m.setStyle(buildStyle(base, design.theme), { diff: false });
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [themeKey]);

  // --- route lines
  function syncRoute() {
    const m = map.current;
    if (!m || !styleReady.current) return;
    const d = latest.current;
    const data = d.route.show ? routeGeoJSON(buildLegs(d.stops, d.route.curved), d.route.style) : EMPTY;
    const src = m.getSource(ROUTE_SRC) as maplibregl.GeoJSONSource | undefined;
    if (src) src.setData(data);
    else m.addSource(ROUTE_SRC, { type: "geojson", data });
    const lw = Math.max(1, (d.route.width * widthRef.current) / 100);
    for (const l of ROUTE_LAYERS) {
      if (!m.getLayer(l.id)) {
        m.addLayer({
          id: l.id,
          type: "line",
          source: ROUTE_SRC,
          filter: ["==", ["get", "dash"], l.dash],
          layout: { "line-cap": l.dash === "dotted" ? "round" : "butt", "line-join": "round" },
          paint: {},
        });
      }
      m.setPaintProperty(l.id, "line-color", l.overlay ? d.theme.colors.paper : d.theme.colors.accent);
      m.setPaintProperty(l.id, "line-width", l.dash === "rail" ? (l.overlay ? lw * 0.6 : lw * 1.6) : lw);
      if (l.pattern) m.setPaintProperty(l.id, "line-dasharray", l.pattern);
    }
  }
  const routeKey = JSON.stringify([design.stops.map((s) => [s.lng, s.lat, s.arriveBy, s.pathFor, s.path?.length]), design.route, design.theme.colors, width]);
  useEffect(() => {
    syncRoute();
     
  }, [routeKey]);

  // --- travel-mode icons halfway along each leg
  useEffect(
    () =>
      whenMap((mm) => {
        modeMarkers.current.forEach((mk) => mk.remove());
        modeMarkers.current = [];
        if (!design.route.show || !design.route.modeIcons) return;
        const c = design.theme.colors;
        modeMarkers.current = buildLegs(design.stops, design.route.curved).map((leg) => {
          const node = document.createElement("div");
          node.className = "mapsie-mode";
          node.style.cssText = `--u:${u}px;background:${c.paper};border-color:${c.accent}`;
          node.innerHTML = `<img src="${MODES.find((x) => x.id === leg.mode)?.icon}" alt="" />`;
          const a = leg.line[0];
          const b = leg.line[leg.line.length - 1];
          // Only show the icon when the leg is long enough on screen not to crowd the stops.
          const fit = () => {
            const pa = mm.project(a);
            const pb = mm.project(b);
            node.style.visibility = Math.hypot(pa.x - pb.x, pa.y - pb.y) > u * 13 ? "visible" : "hidden";
          };
          fit();
          mm.on("zoom", fit);
          const mk = new maplibregl.Marker({ element: node, anchor: "center" }).setLngLat(leg.mid).addTo(mm);
          const remove = mk.remove.bind(mk);
          mk.remove = () => (mm.off("zoom", fit), remove());
          return mk;
        });
      }),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [routeKey],
  );

  // --- visited countries
  function syncVisited() {
    const m = map.current;
    if (!m || !styleReady.current) return;
    const d = latest.current;
    const apply = (data: GeoJSON.FeatureCollection) => {
      if (!map.current || !styleReady.current) return;
      const src = m.getSource(VISITED_SRC) as maplibregl.GeoJSONSource | undefined;
      if (src) src.setData(data);
      else m.addSource(VISITED_SRC, { type: "geojson", data });
      if (!m.getLayer(VISITED_SRC)) {
        // Below the water layer, so the sea crisply trims the country shapes.
        m.addLayer({ id: VISITED_SRC, type: "fill", source: VISITED_SRC, paint: {} }, m.getLayer("water") ? "water" : undefined);
      }
      m.setPaintProperty(VISITED_SRC, "fill-color", d.theme.colors.accent);
      m.setPaintProperty(VISITED_SRC, "fill-opacity", d.visited.opacity);
    };
    if (!d.visited.show) return apply(EMPTY);
    loadCountries().then((all) => apply(visitedCountries(all, latest.current.stops)));
  }
  const visitedKey = JSON.stringify([design.visited, design.stops.map((s) => [s.lng, s.lat]), design.theme.colors.accent]);
  useEffect(() => {
    syncVisited();
     
  }, [visitedKey]);

  // --- stop markers (HTML, so they can use any font and stay crisp in print)
  const stopsKey = JSON.stringify([design.stops.map(({ path: _p, ...s }) => s), design.markers, design.theme.colors, design.font, width, editable, selectedLabel]); // eslint-disable-line @typescript-eslint/no-unused-vars
  useEffect(
    () =>
      whenMap((mm) => {
        stopMarkers.current.forEach((mk) => mk.remove());
        const c = design.theme.colors;
        const style = design.markers.style;
        stopMarkers.current = design.stops.map((s: Stop, i) => {
          const node = document.createElement("div");
          node.className = `mapsie-stop is-${style}`;
          node.style.setProperty("--u", `${u * design.markers.size}px`);
          if (editable) node.title = "Drag to move this stop";
          const icon =
            style === "number"
              ? `<div class="mapsie-stop-dot" style="background:${c.accent};color:${c.paper};border-color:${c.paper}">${i + 1}</div>`
              : style === "dot"
                ? `<div class="mapsie-stop-dot" style="background:${c.accent};border-color:${c.paper}"></div>`
                : `<div class="mapsie-stop-icon">${markerSvg(style, c.accent, c.paper)}</div>`;
          const date = design.markers.showDates && s.date ? `<small>${esc(s.date)}</small>` : "";
          const label = s.showLabel
            ? `<div class="mapsie-stop-label" style="color:${c.ink};background:${c.paper};font-family:${fontCss(design.font)}">${esc(s.name)}${date}</div>`
            : "";
          node.innerHTML = icon + label;
          const labelEl = node.querySelector<HTMLElement>(".mapsie-stop-label");
          if (labelEl) setupLabel(labelEl, s);
          const mk = new maplibregl.Marker({ element: node, draggable: editable, anchor: style === "pin" ? "bottom" : "center" })
            .setLngLat([s.lng, s.lat])
            .addTo(mm);
          mk.on("dragend", () => {
            const p = mk.getLngLat();
            h.current?.onStopMove?.(s.id, p.lng, p.lat);
          });
          return mk;
        });
      }),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [stopsKey],
  );

  /**
   * A stop's label: its own size and offset from the pin. In the editor it can be
   * selected, dragged (without moving the stop) and resized from its corner.
   */
  function setupLabel(el: HTMLElement, s: Stop) {
    const scale = design.markers.labelSize * (s.labelScale ?? 1);
    const [dx, dy] = s.labelOffset ?? [0, 0];
    el.style.setProperty("--u", `${u * scale}px`);
    // A thin leader line back to the pin when the label has been moved away from it.
    const stop = el.parentElement!;
    const leader = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    leader.setAttribute("class", "mapsie-leader");
    const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
    line.setAttribute("stroke", design.theme.colors.ink);
    line.setAttribute("stroke-width", String(Math.max(1, u * 0.18)));
    line.setAttribute("stroke-linecap", "round");
    leader.appendChild(line);
    stop.insertBefore(leader, stop.firstChild);
    const place = (ox: number, oy: number) => {
      el.style.transform = `translate(${ox * u}px, calc(-50% + ${oy * u}px))`;
      const far = Math.hypot(ox, oy) > 4;
      leader.style.display = far ? "block" : "none";
      if (!far) return;
      // From the pin centre to the nearest point of the label (measured unrotated).
      const cx = stop.offsetWidth / 2, cy = stop.offsetHeight / 2;
      const lx = el.offsetLeft + ox * u, ly = el.offsetTop + oy * u - el.offsetHeight / 2;
      const tx = Math.min(Math.max(cx, lx), lx + el.offsetWidth);
      const ty = Math.min(Math.max(cy, ly), ly + el.offsetHeight);
      // Round markers (numbers, dots): start at the edge of the circle, not its centre.
      let sx = cx, sy = cy;
      const round = design.markers.style === "number" || design.markers.style === "dot";
      const dist = Math.hypot(tx - cx, ty - cy);
      if (round && dist > 0) {
        const r = Math.min(stop.offsetWidth, stop.offsetHeight) / 2 + u * 0.35;
        sx = cx + ((tx - cx) / dist) * r;
        sy = cy + ((ty - cy) / dist) * r;
        if (dist <= r) leader.style.display = "none";
      }
      line.setAttribute("x1", String(sx));
      line.setAttribute("y1", String(sy));
      line.setAttribute("x2", String(tx));
      line.setAttribute("y2", String(ty));
    };
    requestAnimationFrame(() => place(dx, dy));
    if (!editable) return;
    el.classList.add("is-editable");
    el.title = "Drag to move the label · corner handle to resize";
    const selected = s.id === selectedLabel;
    if (selected) el.classList.add("is-selected");
    // Keep the map and the stop's own drag out of it.
    for (const ev of ["mousedown", "touchstart", "click", "dblclick"]) el.addEventListener(ev, (e) => e.stopPropagation(), { passive: true });

    el.addEventListener("pointerdown", (e) => {
      if ((e.target as HTMLElement).classList.contains("mapsie-handle")) return;
      e.preventDefault();
      el.setPointerCapture(e.pointerId);
      const x0 = e.clientX, y0 = e.clientY;
      // The editor can zoom the whole poster with a CSS transform; undo that here.
      const k = el.getBoundingClientRect().width / (el.offsetWidth || 1) || 1;
      let moved = false, ox = dx, oy = dy;
      const move = (ev: PointerEvent) => {
        const mx = (ev.clientX - x0) / u / k, my = (ev.clientY - y0) / u / k;
        if (!moved && Math.hypot(ev.clientX - x0, ev.clientY - y0) < 3) return;
        moved = true;
        ox = Math.round((dx + mx) * 10) / 10;
        oy = Math.round((dy + my) * 10) / 10;
        place(ox, oy);
      };
      const up = () => {
        el.removeEventListener("pointermove", move);
        el.removeEventListener("pointerup", up);
        if (moved) h.current?.onLabelChange?.(s.id, { labelOffset: [ox, oy] });
        h.current?.onLabelSelect?.(s.id);
      };
      el.addEventListener("pointermove", move);
      el.addEventListener("pointerup", up);
    });

    if (!selected) return;
    const handle = document.createElement("div");
    handle.className = "mapsie-handle is-resize";
    handle.title = "Drag to resize";
    el.appendChild(handle);
    handle.addEventListener("pointerdown", (e) => {
      e.stopPropagation();
      e.preventDefault();
      handle.setPointerCapture(e.pointerId);
      const r = el.getBoundingClientRect();
      const x0 = r.left, y0 = r.top + r.height / 2;
      const d0 = Math.hypot(e.clientX - x0, e.clientY - y0) || 1;
      const base = s.labelScale ?? 1;
      let next = base;
      const move = (ev: PointerEvent) => {
        next = Math.max(0.4, Math.min(4, base * (Math.hypot(ev.clientX - x0, ev.clientY - y0) / d0)));
        el.style.setProperty("--u", `${u * design.markers.labelSize * next}px`);
      };
      const up = () => {
        handle.removeEventListener("pointermove", move);
        handle.removeEventListener("pointerup", up);
        h.current?.onLabelChange?.(s.id, { labelScale: Math.round(next * 100) / 100 });
      };
      handle.addEventListener("pointermove", move);
      handle.addEventListener("pointerup", up);
    });
  }

  // --- stickers, photos and text notes, pinned to a place on the map
  const stickersKey = JSON.stringify([design.stickers, selectedSticker, width, editable, design.theme.colors.land, design.theme.presetId]);
  useEffect(
    () =>
      whenMap((mm) => {
        stickerMarkers.current.forEach((mk) => mk.remove());
        stickerMarkers.current = design.stickers.map((st: Sticker) => {
          const selected = st.id === selectedSticker && editable;
          const node = document.createElement("div");
          const art = st.kind === "sticker" ? getArtStyle(st.art) : null;
          node.className = `mapsie-sticker is-${st.kind}` + (selected ? " is-selected" : "") + (art?.blend && isLight(design.theme.colors.land) ? " is-multiply" : "");
          const px = st.size * u;
          let inner: HTMLElement;
          if (st.kind === "text") {
            inner = document.createElement("div");
            inner.className = "mapsie-note";
            inner.textContent = st.text || "Your note";
            inner.style.cssText = `font-family:${fontCss(st.font ?? "caveat")};color:${st.color ?? design.theme.colors.ink};font-size:${px}px`;
          } else {
            node.style.width = `${px}px`;
            node.style.height = `${px}px`;
            const img = document.createElement("img");
            img.src =
              st.kind === "original" && st.name
                ? originalSrc(st.name, st.origStyle ?? "papercut", resolvePalette(st.palette ?? "auto", design.theme.presetId, st.origStyle ?? "papercut"))
                : st.kind === "sticker" && st.name
                  ? stickerSrc(st.name, st.art)
                  : st.src;
            if (art && art.finish !== "none") img.style.filter = `url(#${filterId(filterPrefix, art.finish)})`;
            img.draggable = false;
            img.alt = "";
            if (st.kind === "photo") img.style.borderWidth = `${Math.max(2, px * 0.05)}px`;
            inner = img;
          }
          inner.style.transform = `rotate(${st.rotation}deg)`;
          node.appendChild(inner);
          node.addEventListener("click", (e) => {
            e.stopPropagation();
            h.current?.onStickerSelect?.(st.id);
          });
          if (selected) addHandles(node, inner, st);
          const mk = new maplibregl.Marker({ element: node, draggable: editable, anchor: "center" }).setLngLat([st.lng, st.lat]).addTo(mm);
          mk.on("dragstart", () => h.current?.onStickerSelect?.(st.id));
          mk.on("dragend", () => {
            const p = mk.getLngLat();
            h.current?.onStickerMove?.(st.id, p.lng, p.lat);
          });
          return mk;
        });
      }),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [stickersKey],
  );

  /** Corner handle to resize, top handle to rotate. Updates live, saves on release. */
  function addHandles(node: HTMLElement, inner: HTMLElement, st: Sticker) {
    const make = (cls: string, mode: "size" | "rotate") => {
      const hd = document.createElement("div");
      hd.className = `mapsie-handle ${cls}`;
      const start = (e: PointerEvent) => {
        e.stopPropagation();
        e.preventDefault();
        const r = node.getBoundingClientRect();
        const cx = r.left + r.width / 2;
        const cy = r.top + r.height / 2;
        const d0 = Math.hypot(e.clientX - cx, e.clientY - cy) || 1;
        const a0 = Math.atan2(e.clientY - cy, e.clientX - cx);
        let size = st.size;
        let rotation = st.rotation;
        const move = (ev: PointerEvent) => {
          if (mode === "size") {
            size = Math.max(2, Math.min(60, (st.size * Math.hypot(ev.clientX - cx, ev.clientY - cy)) / d0));
            const px = size * (widthRef.current / 100);
            if (st.kind === "text") inner.style.fontSize = `${px}px`;
            else {
              node.style.width = `${px}px`;
              node.style.height = `${px}px`;
            }
          } else {
            rotation = Math.round(st.rotation + ((Math.atan2(ev.clientY - cy, ev.clientX - cx) - a0) * 180) / Math.PI);
            if (!ev.shiftKey) rotation = Math.round(rotation / 5) * 5;
            inner.style.transform = `rotate(${rotation}deg)`;
          }
        };
        const up = () => {
          window.removeEventListener("pointermove", move);
          window.removeEventListener("pointerup", up);
          h.current?.onStickerChange?.(st.id, mode === "size" ? { size } : { rotation });
        };
        window.addEventListener("pointermove", move);
        window.addEventListener("pointerup", up);
      };
      hd.addEventListener("pointerdown", start);
      // keep the marker's own drag from starting
      hd.addEventListener("mousedown", (e) => e.stopPropagation());
      hd.addEventListener("touchstart", (e) => e.stopPropagation(), { passive: true });
      node.appendChild(hd);
    };
    make("is-resize", "size");
    make("is-rotate", "rotate");
  }

  // --- keep the canvas sized to its box
  useEffect(() => {
    map.current?.resize();
  }, [mapWidth, height]);

  // --- frame all the stops
  useEffect(() => {
    const m = map.current;
    if (!m || !fitRequest) return;
    const stops = latest.current.stops;
    const b = stopsBounds(stops);
    if (!b) return;
    if (stops.length === 1) m.flyTo({ center: [stops[0].lng, stops[0].lat], zoom: Math.max(m.getZoom(), 5) });
    else m.fitBounds(b, { padding: Math.min(mapWidth, height) * 0.16, maxZoom: 10, duration: 900 });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [fitRequest]);

  return (
    <div
      ref={el}
      style={{ width: mapWidth, height }}
      onDragOver={(e) => editable && e.preventDefault()}
      onDrop={(e) => {
        const src = e.dataTransfer.getData("text/mapsie-sticker");
        const m = map.current;
        if (!src || !m || !el.current) return;
        e.preventDefault();
        const r = el.current.getBoundingClientRect();
        const p = m.unproject([e.clientX - r.left, e.clientY - r.top]);
        h.current?.onDropSticker?.(src, p.lng, p.lat);
      }}
    />
  );
}

/** Small single-colour icons (tinted by the style) for current arrows and shipping lanes. */
function detailIcon(id: string): ImageData | null {
  if (id !== "mapsie-arrow" && id !== "mapsie-ship") return null;
  const size = 48;
  const cv = document.createElement("canvas");
  cv.width = cv.height = size;
  const g = cv.getContext("2d")!;
  g.fillStyle = "#000";
  g.beginPath();
  if (id === "mapsie-arrow") {
    // A chevron pointing along the line (to the right).
    g.moveTo(14, 10);
    g.lineTo(38, 24);
    g.lineTo(14, 38);
    g.lineTo(20, 24);
  } else {
    // A little ship: hull and sail.
    g.moveTo(6, 30);
    g.lineTo(42, 30);
    g.lineTo(35, 39);
    g.lineTo(13, 39);
    g.closePath();
    g.moveTo(24, 6);
    g.lineTo(24, 27);
    g.lineTo(37, 27);
    g.closePath();
    g.moveTo(22, 11);
    g.lineTo(22, 27);
    g.lineTo(12, 27);
  }
  g.closePath();
  g.fill();
  return g.getImageData(0, 0, size, size);
}
