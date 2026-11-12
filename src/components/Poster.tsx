"use client";
import dynamic from "next/dynamic";
import { useId } from "react";
import StickerFilters from "./StickerFilters";
import type { Design } from "@/lib/types";
import { posterAspect } from "@/lib/products";
import { fontCss } from "@/lib/fonts";
import type { MapHandlers } from "./MapView";

const MapView = dynamic(() => import("./MapView"), { ssr: false });

interface Props {
  design: Design;
  width: number;
  editable?: boolean;
  print?: boolean;
  selectedSticker?: string | null;
  fitRequest?: number;
  handlers?: MapHandlers;
  onReady?: () => void;
}

/** Everything is sized relative to the poster width, so it scales to any print size. */
export default function Poster({ design, width, editable = false, print, selectedSticker, fitRequest, handlers, onReady }: Props) {
  const height = Math.round(width * posterAspect(design.productId, design.orientation));
  const u = width / 100;
  // Each poster gets its own filter ids, since thumbnails may show different themes.
  const filterPrefix = `mf${useId().replace(/[^a-zA-Z0-9]/g, "")}`;
  const c = design.theme.colors;
  const landscape = design.orientation === "landscape";
  const bandH = design.layout === "overlay" ? 0 : u * (landscape ? 11 : 17);
  const pad = design.layout === "border" ? u * 4.5 : 0;
  const mapW = width - pad * 2;
  const mapH = height - bandH - pad * (design.layout === "border" ? 1 : 0) - pad;
  const font = fontCss(design.font);
  const route = design.stops.map((s) => s.name).join("  ·  ");

  const titleBlock = (
    <>
      <div style={{ fontFamily: font, fontSize: u * (design.font === "bebas" ? 8 : 6.2), lineHeight: 1.05, color: c.ink, fontWeight: 700, letterSpacing: design.font === "bebas" ? u * 0.15 : 0 }}>
        {design.title}
      </div>
      {design.subtitle && (
        <div style={{ fontFamily: "var(--f-montserrat), sans-serif", fontSize: u * 2.1, letterSpacing: u * 0.5, textTransform: "uppercase", color: c.ink, opacity: 0.75, marginTop: u * 1 }}>
          {design.subtitle}
        </div>
      )}
      {route && !landscape && (
        <div style={{ fontFamily: "var(--f-montserrat), sans-serif", fontSize: u * 1.5, color: c.ink, opacity: 0.55, marginTop: u * 0.9, maxWidth: "90%", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
          {route}
        </div>
      )}
    </>
  );

  return (
    <div
      id="poster"
      className="relative overflow-hidden select-none"
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
          fitRequest={fitRequest}
          handlers={handlers}
          onReady={onReady}
          filterPrefix={filterPrefix}
        />
      </div>

      {design.layout !== "overlay" ? (
        <div className="absolute left-0 right-0 bottom-0 flex flex-col items-center justify-center text-center" style={{ height: bandH + (design.layout === "border" ? pad * 0.4 : 0) }}>
          {titleBlock}
        </div>
      ) : (
        <div
          className="absolute left-1/2 -translate-x-1/2 flex flex-col items-center text-center pointer-events-none"
          style={{ bottom: u * 5, background: c.paper + "e6", padding: `${u * 2.2}px ${u * 5}px`, borderRadius: u * 1.5, maxWidth: "86%" }}
        >
          {titleBlock}
        </div>
      )}

      {design.theme.texture && <div className="mapsie-paper pointer-events-none absolute inset-0" />}

    </div>
  );
}
