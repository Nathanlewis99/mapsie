"use client";
import { useEffect, useRef } from "react";
import maplibregl, { Map as MLMap, Marker } from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import type { Design, Sticker } from "@/lib/types";
import { buildStyle, loadBaseStyle } from "@/lib/themes";
import { routeGeoJSON, stopsBounds } from "@/lib/geo";
import { fontCss } from "@/lib/fonts";

export interface MapHandlers {
  onView?: (v: Design["view"]) => void;
  onStopMove?: (id: string, lng: number, lat: number) => void;
  onStickerMove?: (id: string, lng: number, lat: number) => void;
  onStickerSelect?: (id: string | null) => void;
  onMapClick?: (lng: number, lat: number) => void;
  onDropSticker?: (src: string, lng: number, lat: number) => void;
}

interface Props {
  design: Design;
  width: number; // poster width in CSS px (sizes are relative to this)
  height: number; // map area height
  mapWidth: number; // map area width
  editable: boolean;
  print?: boolean;
  selectedSticker?: string | null;
  fitRequest?: number;
  handlers?: MapHandlers;
  onReady?: () => void;
}

const ROUTE_SRC = "mapsie-route";
const ROUTE_LAYER = "mapsie-route-line";

const dash = (style: Design["route"]["style"]) =>
  style === "dashed" ? [2.2, 1.6] : style === "dotted" ? [0.01, 2] : [1, 0];

export default function MapView(props: Props) {
  const { design, width, height, mapWidth, editable, print, selectedSticker, fitRequest, handlers, onReady } = props;
  const el = useRef<HTMLDivElement>(null);
  const map = useRef<MLMap | null>(null);
  const stopMarkers = useRef<Marker[]>([]);
  const stickerMarkers = useRef<Marker[]>([]);
  const h = useRef(handlers);
  h.current = handlers;
  const latest = useRef(design);
  latest.current = design;
  const styleReady = useRef(false);
  const widthRef = useRef(width);
  widthRef.current = width;
  const u = width / 100;

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
        ...(print ? { maxCanvasSize: [16384, 16384] as [number, number] } : {}),
      });
      if (editable) m.touchZoomRotate.disableRotation();
      map.current = m;

      m.on("style.load", () => {
        styleReady.current = true;
        syncRoute();
      });
      m.on("moveend", () => {
        const c = m.getCenter();
        h.current?.onView?.({ center: [c.lng, c.lat], zoom: m.getZoom(), bearing: m.getBearing(), refWidth: widthRef.current });
      });
      m.on("click", (e) => {
        h.current?.onStickerSelect?.(null);
        h.current?.onMapClick?.(e.lngLat.lng, e.lngLat.lat);
      });
      if (onReady) {
        m.once("idle", async () => {
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

  // --- route line
  function syncRoute() {
    const m = map.current;
    if (!m || !styleReady.current) return;
    const d = latest.current;
    const data = routeGeoJSON(d.route.show ? d.stops : [], d.route.curved);
    const src = m.getSource(ROUTE_SRC) as maplibregl.GeoJSONSource | undefined;
    if (src) src.setData(data);
    else m.addSource(ROUTE_SRC, { type: "geojson", data });
    const lw = Math.max(1, d.route.width * widthRef.current / 100);
    if (!m.getLayer(ROUTE_LAYER)) {
      m.addLayer({ id: ROUTE_LAYER, type: "line", source: ROUTE_SRC, layout: { "line-cap": "round", "line-join": "round" }, paint: {} });
    }
    m.setPaintProperty(ROUTE_LAYER, "line-color", d.theme.colors.accent);
    m.setPaintProperty(ROUTE_LAYER, "line-width", lw);
    m.setPaintProperty(ROUTE_LAYER, "line-dasharray", dash(d.route.style));
  }
  const routeKey = JSON.stringify([design.stops.map((s) => [s.lng, s.lat]), design.route, design.theme.colors.accent, width]);
  useEffect(() => {
    syncRoute();
     
  }, [routeKey]);

  // --- stop markers (DOM, so they can use any font and stay crisp in print)
  const stopsKey = JSON.stringify([design.stops, design.theme.colors, design.font, width, editable]);
  useEffect(() => {
    const m = map.current;
    const run = () => {
      const mm = map.current;
      if (!mm) return;
      stopMarkers.current.forEach((mk) => mk.remove());
      const c = design.theme.colors;
      stopMarkers.current = design.stops.map((s, i) => {
        const node = document.createElement("div");
        node.className = "mapsie-stop";
        node.style.setProperty("--u", `${u}px`);
        node.innerHTML = `
          <div class="mapsie-stop-dot" style="background:${c.accent};color:${c.paper};border-color:${c.paper}">${i + 1}</div>
          ${s.showLabel ? `<div class="mapsie-stop-label" style="color:${c.ink};background:${c.paper};font-family:${fontCss(design.font)}"></div>` : ""}`;
        const label = node.querySelector(".mapsie-stop-label");
        if (label) label.textContent = s.name;
        const mk = new maplibregl.Marker({ element: node, draggable: editable, anchor: "center" }).setLngLat([s.lng, s.lat]).addTo(mm);
        mk.on("dragend", () => {
          const p = mk.getLngLat();
          h.current?.onStopMove?.(s.id, p.lng, p.lat);
        });
        return mk;
      });
    };
    if (m) run();
    else {
      const t = setInterval(() => map.current && (clearInterval(t), run()), 50);
      return () => clearInterval(t);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [stopsKey]);

  // --- stickers & photos, pinned to a place on the map
  const stickersKey = JSON.stringify([design.stickers, selectedSticker, width, editable]);
  useEffect(() => {
    const run = () => {
      const mm = map.current;
      if (!mm) return;
      stickerMarkers.current.forEach((mk) => mk.remove());
      stickerMarkers.current = design.stickers.map((st: Sticker) => {
        const node = document.createElement("div");
        node.className = "mapsie-sticker" + (st.id === selectedSticker && editable ? " is-selected" : "") + (st.kind === "photo" ? " is-photo" : "");
        const px = st.size * u;
        node.style.width = `${px}px`;
        node.style.height = `${px}px`;
        const img = document.createElement("img");
        img.src = st.src;
        img.draggable = false;
        img.alt = "";
        img.style.transform = `rotate(${st.rotation}deg)`;
        if (st.kind === "photo") img.style.borderWidth = `${Math.max(2, px * 0.05)}px`;
        node.appendChild(img);
        node.addEventListener("click", (e) => {
          e.stopPropagation();
          h.current?.onStickerSelect?.(st.id);
        });
        const mk = new maplibregl.Marker({ element: node, draggable: editable, anchor: "center" }).setLngLat([st.lng, st.lat]).addTo(mm);
        mk.on("dragstart", () => h.current?.onStickerSelect?.(st.id));
        mk.on("dragend", () => {
          const p = mk.getLngLat();
          h.current?.onStickerMove?.(st.id, p.lng, p.lat);
        });
        return mk;
      });
    };
    if (map.current) run();
    else {
      const t = setInterval(() => map.current && (clearInterval(t), run()), 50);
      return () => clearInterval(t);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [stickersKey]);

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
