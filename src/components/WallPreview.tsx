"use client";
import { useLayoutEffect, useRef, useState } from "react";
import FramedPoster from "./FramedPoster";
import type { Design } from "@/lib/types";
import { getProduct } from "@/lib/products";
import { ROOMS, type Room } from "@/lib/rooms";
import { frameWidth } from "./FramedPoster";

const WALLS = [
  { id: "linen", color: "#ebe5db", floor: "#b88b5e" },
  { id: "sage", color: "#c9d3c0", floor: "#a77b52" },
  { id: "navy", color: "#2e3a4f", floor: "#8a6545" },
  { id: "blush", color: "#efd6cf", floor: "#c39a70" },
];

/** The poster hung above a sideboard, at true scale (the wall is ~2.6 m wide). */
export default function WallPreview({ design }: { design: Design }) {
  const box = useRef<HTMLDivElement>(null);
  const [w, setW] = useState(0);
  const [wall, setWall] = useState(WALLS[0]);
  const [room, setRoom] = useState<Room | null>(ROOMS[0] ?? null);
  useLayoutEffect(() => {
    const ro = new ResizeObserver(([e]) => setW(e.contentRect.width));
    if (box.current) ro.observe(box.current);
    return () => ro.disconnect();
  }, [room]);

  const p = getProduct(design.productId);
  const posterCm = design.orientation === "portrait" ? p.widthCm : p.heightCm;
  const posterHCm = design.orientation === "portrait" ? p.heightCm : p.widthCm;
  // Wall is at least 2.6 m wide, and tall enough for floor + sideboard + gap + poster + headroom.
  const ASPECT = 0.62;
  const wallHCm = Math.max(260 * ASPECT, 22 + 62 + 25 + posterHCm + 22);
  const wallWCm = wallHCm / ASPECT;
  const H = w * ASPECT;
  const pxPerCm = w / wallWCm;
  const posterW = Math.round(posterCm * pxPerCm);
  const floorH = 22 * pxPerCm;
  const boardW = 140 * pxPerCm;
  const boardH = 62 * pxPerCm;

  const picker = (
    <span className="flex gap-1.5 flex-wrap justify-end">
      {ROOMS.map((r) => (
        <button key={r.id} onClick={() => setRoom(r)} aria-label={r.label} title={r.label} className={`w-9 h-6 rounded-md border-2 bg-cover bg-center ${room?.id === r.id ? "border-coral" : "border-white"}`} style={{ backgroundImage: `url(${r.src})` }} />
      ))}
      {WALLS.map((x) => (
        <button key={x.id} onClick={() => { setRoom(null); setWall(x); }} aria-label={`${x.id} wall`} className={`w-6 h-6 rounded-full border-2 ${!room && wall.id === x.id ? "border-coral" : "border-white"}`} style={{ background: x.color }} />
      ))}
    </span>
  );

  if (room) {
    // True scale: the room photo shows `wallCm` of wall across its width.
    const H2 = (w * room.height) / room.width;
    const pxCm = w / room.wallCm;
    let pw = posterCm * pxCm;
    const fh = (pwx: number) => (pwx + frameWidth(design, pwx) * 2) * (posterHCm / posterCm);
    if (room.maxHeight && fh(pw) > room.maxHeight * H2) pw *= (room.maxHeight * H2) / fh(pw);
    pw = Math.round(pw);
    return (
      <div className="space-y-3">
        <div ref={box} className="relative w-full overflow-hidden rounded-3xl bg-sand" style={{ height: H2 || 300 }}>
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src={room.src} alt="" className="absolute inset-0 w-full h-full object-cover" draggable={false} />
          {w > 0 && (
            <div
              className="absolute"
              style={
                room.by !== undefined
                  ? { left: w * room.cx, top: H2 * room.by, transform: "translate(-50%, -100%)" }
                  : { left: w * room.cx, top: H2 * (room.cy ?? 0.4), transform: "translate(-50%, -50%)" }
              }
            >
              <FramedPoster realistic key={`${pw}-${design.frame}-${design.mount}`} design={design} width={pw} />
            </div>
          )}
        </div>
        <div className="flex items-center justify-between gap-3 text-xs font-bold text-ink/50">
          <span>Shown to scale: {p.label}</span>
          {picker}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <div ref={box} className="relative w-full overflow-hidden rounded-3xl" style={{ height: H, background: `radial-gradient(ellipse at 40% 20%, #ffffff40, transparent 60%), ${wall.color}` }}>
        {w > 0 && (
          <>
            {/* floor */}
            <div className="absolute left-0 right-0 bottom-0" style={{ height: floorH, background: `repeating-linear-gradient(90deg, ${wall.floor} 0 ${w / 9}px, #00000014 ${w / 9}px ${w / 9 + 2}px)` }} />
            <div className="absolute left-0 right-0" style={{ bottom: floorH, height: 6, background: "#00000018" }} />
            {/* sideboard */}
            <div className="absolute rounded-md" style={{ left: w * 0.5 - boardW / 2, bottom: floorH, width: boardW, height: boardH, background: "linear-gradient(#7a5a3d, #6a4c32)", boxShadow: "0 10px 20px -8px #0006" }}>
              <div className="absolute inset-x-[6%] top-[18%] bottom-[14%] grid grid-cols-3 gap-[4%]">
                {[0, 1, 2].map((i) => <div key={i} className="rounded-sm" style={{ background: "#00000018" }} />)}
              </div>
            </div>
            {/* plant & vase */}
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src="/stickers/potted-plant.svg" alt="" className="absolute" style={{ width: 70 * pxPerCm, left: w * 0.5 + boardW / 2 + 8 * pxPerCm, bottom: floorH - 2 }} />
            <div className="absolute rounded-t-full" style={{ width: 9 * pxPerCm, height: 22 * pxPerCm, left: w * 0.5 - boardW * 0.38, bottom: floorH + boardH, background: "#e8dccb", boxShadow: "inset -4px 0 6px #0002" }} />
            {/* poster: centred about 40 cm above the sideboard */}
            <div className="absolute" style={{ left: w * 0.5, bottom: floorH + boardH + 25 * pxPerCm, transform: "translateX(-50%)" }}>
              <FramedPoster realistic key={`${posterW}-${design.frame}-${design.mount}`} design={design} width={posterW} />
            </div>
          </>
        )}
      </div>
      <div className="flex items-center justify-between text-xs font-bold text-ink/50">
        <span>Shown to scale: {p.label} on a {(wallWCm / 100).toFixed(1)} m wide wall</span>
        {picker}
      </div>
    </div>
  );
}
