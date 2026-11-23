import { AbsoluteFill, Audio, Easing, Img, interpolate, Sequence, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import type { ReelConfig } from "./reels";

export interface RouteData { width: number; height: number; title: string; subtitle: string; legs: number[][][]; stops: { name: string; mode: string }[] }

export const REEL_FRAMES = 450;
const T = { draw: [24, 255], reveal: [255, 300], room: [300, 380], end: [380, 450] } as const;
const CREAM = "#fbf6ee";
const INK = "#1f2430";
const CORAL = "#ff6b4a";
const fonts = `
@font-face { font-family: Playfair; src: url(${staticFile("fonts/playfair.woff2")}) format("woff2"); font-weight: 400 900; }
@font-face { font-family: Nunito; src: url(${staticFile("fonts/nunito.woff2")}) format("woff2"); font-weight: 200 1000; }`;

const len = (pts: number[][]) => pts.slice(1).reduce((a, p, i) => a + Math.hypot(p[0] - pts[i][0], p[1] - pts[i][1]), 0);
/** The first `d` pixels of a polyline. */
function partial(pts: number[][], d: number) {
  const out = [pts[0]];
  let left = d;
  for (let i = 1; i < pts.length && left > 0; i++) {
    const seg = Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]);
    if (seg <= left) {
      out.push(pts[i]);
      left -= seg;
    } else {
      const t = left / seg;
      out.push([pts[i - 1][0] + (pts[i][0] - pts[i - 1][0]) * t, pts[i - 1][1] + (pts[i][1] - pts[i - 1][1]) * t]);
      left = 0;
    }
  }
  return out;
}

export const RouteReel: React.FC<{ reel: ReelConfig; data: RouteData | null }> = ({ reel, data }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  if (!data) return null;

  // Poster placement: as big as fits between the hook and the bottom overlay area.
  const landscape = data.width > data.height;
  const dispW = landscape ? 980 : 780;
  const s = dispW / data.width;
  const dispH = data.height * s;
  const top = landscape ? 640 : 500;
  const left = (1080 - dispW) / 2;

  // Route drawing progress, leg by leg.
  const lens = data.legs.map(len);
  const total = lens.reduce((a, b) => a + b, 0);
  const p = interpolate(frame, [...T.draw], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.inOut(Easing.quad) });
  let budget = p * total;
  const drawn = data.legs.map((leg, i) => {
    const d = Math.min(Math.max(budget, 0), lens[i]);
    budget -= lens[i];
    return partial(leg, d);
  });
  // Stops reached so far: the start, then the end of each finished leg.
  const reachedAt = [0, ...lens.map((_, i) => lens.slice(0, i + 1).reduce((a, b) => a + b, 0) / total)];
  const stopPts = [data.legs[0]?.[0], ...data.legs.map((l) => l[l.length - 1])];
  const current = reachedAt.filter((r) => r <= p + 1e-6).length - 1;

  const hookIn = spring({ frame, fps, config: { damping: 18 } });
  const posterIn = spring({ frame: frame - 4, fps, config: { damping: 20 } });
  const reveal = interpolate(frame, [...T.reveal], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const room = interpolate(frame, [T.room[0], T.room[0] + 14], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const end = interpolate(frame, [T.end[0], T.end[0] + 12], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const stroke = Math.max(3, reel.routeWidth * (data.width / 100) * s * 1.05);

  // When each stop appears: invert the ease-in-out used for the drawing (y -> t).
  const unease = (y: number) => (y < 0.5 ? Math.sqrt(y / 2) : 1 - Math.sqrt((1 - y) / 2));
  const stopFrames = reachedAt.map((r) => Math.round(T.draw[0] + unease(r) * (T.draw[1] - T.draw[0])));

  return (
    <AbsoluteFill style={{ background: CREAM, fontFamily: "Nunito, sans-serif", color: INK }}>
      <style>{fonts}</style>
      {/* Sound: our own music bed (design/video/sound.py), a pop per stop, a whoosh for the reveal */}
      <Audio src={staticFile("audio/music.wav")} volume={0.85} />
      {stopFrames.map((f, i) => (
        <Sequence key={i} from={f} durationInFrames={12}>
          <Audio src={staticFile("audio/pop.wav")} volume={0.55} />
        </Sequence>
      ))}
      <Sequence from={T.reveal[0] - 8} durationInFrames={30}>
        <Audio src={staticFile("audio/whoosh.wav")} volume={0.5} />
      </Sequence>

      {/* Hook, inside the safe area (clear of the top bar) */}
      <div style={{ position: "absolute", top: 285, left: 70, right: 70, textAlign: "center", fontFamily: "Playfair, serif", fontWeight: 800, fontSize: 62, lineHeight: 1.12, opacity: hookIn * (1 - room), transform: `translateY(${(1 - hookIn) * 30}px)` }}>
        {reel.hook}
      </div>

      {/* The poster, with the route drawing itself */}
      <div style={{ position: "absolute", left, top, width: dispW, height: dispH, opacity: posterIn * (1 - room), transform: `scale(${0.94 + 0.06 * posterIn})`, boxShadow: "0 30px 60px -20px rgba(31,36,48,.45)", background: "#fff" }}>
        <Img src={staticFile(`maps/${reel.slug}-base.jpg`)} style={{ position: "absolute", inset: 0, width: "100%", height: "100%" }} />
        <svg width={dispW} height={dispH} viewBox={`0 0 ${data.width} ${data.height}`} style={{ position: "absolute", inset: 0, opacity: 1 - reveal }}>
          {drawn.map((pts, i) => pts.length > 1 && <polyline key={i} points={pts.map((q) => q.join(",")).join(" ")} fill="none" stroke={reel.accent} strokeWidth={stroke / s} strokeLinecap="round" strokeLinejoin="round" />)}
          {stopPts.map((pt, i) => {
            if (!pt) return null;
            const pop = spring({ frame: frame - (T.draw[0] + reachedAt[i] * (T.draw[1] - T.draw[0])), fps, config: { damping: 11, stiffness: 160 } });
            return <circle key={i} cx={pt[0]} cy={pt[1]} r={(stroke * 1.9 * pop) / s} fill={reel.accent} stroke="#fff" strokeWidth={(stroke * 0.55) / s} />;
          })}
        </svg>
        <Img src={staticFile(`maps/${reel.slug}-full.jpg`)} style={{ position: "absolute", inset: 0, width: "100%", height: "100%", opacity: reveal }} />
      </div>

      {/* Where we are on the trip */}
      {frame >= T.draw[0] && frame < T.reveal[1] && data.stops[current] && (
        <div style={{ position: "absolute", top: top + 22, left: 0, right: 0, textAlign: "center", opacity: 1 - reveal }}>
          <span style={{ display: "inline-block", background: INK, color: "#fff", borderRadius: 999, padding: "12px 28px", fontSize: 34, fontWeight: 900 }}>
            📍 {data.stops[current].name}
            {current > 0 ? <span style={{ opacity: 0.6, fontWeight: 700 }}>{`  ·  stop ${current + 1} of ${data.stops.length}`}</span> : null}
          </span>
        </div>
      )}

      {/* On the wall */}
      <AbsoluteFill style={{ opacity: room * (1 - end) }}>
        <Img src={staticFile(`rooms/${reel.slug}.jpg`)} style={{ position: "absolute", top: 400, left: 0, width: 1080, height: 1350, objectFit: "cover", transform: `scale(${1.08 - 0.08 * interpolate(frame, [T.room[0], T.end[0]], [0, 1], { extrapolateRight: "clamp", extrapolateLeft: "clamp" })})` }} />
        <div style={{ position: "absolute", top: 285, left: 0, right: 0, textAlign: "center", fontFamily: "Playfair, serif", fontWeight: 800, fontSize: 58 }}>{reel.roomLine}</div>
      </AbsoluteFill>

      {/* End card */}
      <AbsoluteFill style={{ opacity: end, background: CREAM, alignItems: "center", justifyContent: "center", textAlign: "center", paddingBottom: 300 }}>
        <div style={{ fontFamily: "Playfair, serif", fontWeight: 800, fontSize: 120 }}>
          Mapsie<span style={{ color: CORAL }}>.</span>
        </div>
        <div style={{ fontFamily: "Playfair, serif", fontWeight: 800, fontSize: 64, marginTop: 30, lineHeight: 1.1 }}>Design yours in minutes</div>
        <div style={{ marginTop: 36, background: CORAL, color: "#fff", borderRadius: 999, padding: "22px 54px", fontSize: 46, fontWeight: 900, transform: `scale(${0.9 + 0.1 * spring({ frame: frame - T.end[0], fps, config: { damping: 9 } })})` }}>mapsie.shop</div>
        <div style={{ marginTop: 28, fontSize: 34, fontWeight: 700, opacity: 0.65 }}>{reel.price}</div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
