import { Composition, staticFile } from "remotion";
import { RouteReel, REEL_FRAMES, type RouteData } from "./RouteReel";
import { REELS } from "./reels";

// 1080×1920 Reels (Instagram, TikTok, Facebook, Stories), 30 fps, 15 seconds.
export const Root: React.FC = () => (
  <>
    {REELS.map((r) => (
      <Composition
        key={r.id}
        id={r.id}
        component={RouteReel}
        durationInFrames={REEL_FRAMES}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{ reel: r, data: null as RouteData | null }}
        calculateMetadata={async ({ props }) => ({ props: { ...props, data: (await (await fetch(staticFile(`maps/${props.reel.slug}.json`))).json()) as RouteData } })}
      />
    ))}
  </>
);
