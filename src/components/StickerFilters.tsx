import type { ThemeColors } from "@/lib/types";
import type { Finish } from "@/lib/stickers";

/**
 * SVG filters that give stickers their artistic finish, in the poster's colours.
 * Sizes use objectBoundingBox units (fractions of the sticker), so a finish looks
 * the same on a thumbnail, in the editor and in a 300 dpi print.
 *
 * Reference one with CSS: filter: url(#<prefix>-<finish>)
 */
export const filterId = (prefix: string, finish: Finish) => `${prefix}-${finish}`;

const hex = (h: string) => {
  const n = parseInt(h.replace("#", "").padEnd(6, "0").slice(0, 6), 16);
  return [(n >> 16) & 255, (n >> 8) & 255, n & 255].map((v) => +(v / 255).toFixed(3));
};
/** Gradient map: luminance 0..1 → the given colours (for feComponentTransfer tables). */
const tables = (colors: string[]) => {
  const rgb = colors.map(hex);
  return [0, 1, 2].map((i) => rgb.map((c) => c[i]).join(" "));
};

// A line screen for engraving: fine diagonal stripes whose brightness rises and falls
// across each stripe. Where the art is darker than the stripe, ink is laid, so shadows
// get thick lines and highlights thin or none, as in a copperplate engraving.
const HATCH =
  "data:image/svg+xml;utf8," +
  encodeURIComponent(
    `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="400" height="400" preserveAspectRatio="none"><defs><linearGradient id="g" x1="0" x2="1" y1="0" y2="0"><stop offset="0" stop-color="#000"/><stop offset="0.5" stop-color="#fff"/><stop offset="1" stop-color="#000"/></linearGradient><pattern id="p" width="2.6" height="2.6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="2.6" height="2.6" fill="url(#g)"/></pattern></defs><rect x="-50" y="-50" width="200" height="200" fill="url(#p)"/></svg>`,
  );

/** The engraving itself: line-screen shading plus an outline, in ink. `boost` sets how much is shaded. */
function Engrave({ ink, boost, result }: { ink: string; boost: number; result: string }) {
  return (
    <>
      {/* darkness of the art (0 = white, 1 = black), only where the art is */}
      <feColorMatrix in="SourceGraphic" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  -0.2126 -0.7152 -0.0722 0 1" result="dark" />
      <feComposite in="dark" in2="SourceAlpha" operator="in" result="tone" />
      <feImage href={HATCH} x="0" y="0" width="1" height="1" preserveAspectRatio="none" result="screen" />
      <feColorMatrix in="screen" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  1 0 0 0 0" result="screenA" />
      <feComposite in="tone" in2="screenA" operator="arithmetic" k1="0" k2={boost} k3="-1" k4="0" result="diff" />
      <feComponentTransfer in="diff" result="lines">
        <feFuncA type="discrete" tableValues="0 1 1 1 1 1 1 1" />
      </feComponentTransfer>
      {/* a fine outline round every shape */}
      <feMorphology in="SourceAlpha" operator="erode" radius="0.011" result="inner" />
      <feComposite in="SourceAlpha" in2="inner" operator="out" result="edge" />
      <feMerge result="inkMask">
        <feMergeNode in="lines" />
        <feMergeNode in="edge" />
      </feMerge>
      <feFlood floodColor={ink} />
      <feComposite in2="inkMask" operator="in" result={result} />
    </>
  );
}

export default function StickerFilters({ prefix, colors }: { prefix: string; colors: ThemeColors }) {
  const region = { x: "-30%", y: "-30%", width: "160%", height: "160%", primitiveUnits: "objectBoundingBox", colorInterpolationFilters: "sRGB" } as const;
  const [rR, rG, rB] = tables([colors.ink, colors.accent, colors.paper]);
  const [gR, gG, gB] = tables(["#5a3c0e", "#9c6e1e", "#d4a640", "#f6dd8c", "#fff6d4"]);
  const LUM = "0.2126 0.7152 0.0722 0 0  0.2126 0.7152 0.0722 0 0  0.2126 0.7152 0.0722 0 0  0 0 0 1 0";

  return (
    <svg width="0" height="0" style={{ position: "absolute", width: 0, height: 0, overflow: "hidden" }} aria-hidden>
      <defs>
        {/* Die-cut vinyl: thick white edge and a soft shadow */}
        <filter id={filterId(prefix, "diecut")} {...region}>
          <feMorphology in="SourceAlpha" operator="dilate" radius="0.05" result="edge" />
          <feFlood floodColor="#ffffff" />
          <feComposite in2="edge" operator="in" result="white" />
          <feGaussianBlur in="edge" stdDeviation="0.025" result="blur" />
          <feOffset in="blur" dx="0" dy="0.025" result="drop" />
          <feFlood floodColor="#000000" floodOpacity="0.28" />
          <feComposite in2="drop" operator="in" result="shadow" />
          <feMerge>
            <feMergeNode in="shadow" />
            <feMergeNode in="white" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>

        {/* Vintage ink stamp: tonal ink with worn, speckled edges */}
        <filter id={filterId(prefix, "stamp")} {...region}>
          <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="3" result="grain" />
          <feTurbulence type="fractalNoise" baseFrequency="0.06" numOctaves="2" seed="7" result="wobble" />
          <feDisplacementMap in="SourceGraphic" in2="wobble" scale="0.025" xChannelSelector="R" yChannelSelector="G" result="shaky" />
          {/* darker parts of the art = more ink */}
          <feColorMatrix in="shaky" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  -0.22 -0.5 -0.08 0 1.05" result="tone" />
          <feComposite in="tone" in2="shaky" operator="in" result="toneA" />
          <feComponentTransfer in="toneA" result="steps">
            <feFuncA type="discrete" tableValues="0 0.45 0.7 0.9 1" />
          </feComponentTransfer>
          {/* knock speckles out of the ink */}
          <feColorMatrix in="grain" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  1.6 0 0 0 -0.35" result="speck" />
          <feComponentTransfer in="speck" result="mask">
            <feFuncA type="discrete" tableValues="0.15 1 1 1 1 1" />
          </feComponentTransfer>
          <feComposite in="steps" in2="mask" operator="in" result="worn" />
          <feFlood floodColor={colors.ink} />
          <feComposite in2="worn" operator="in" />
        </filter>

        {/* Watercolour: wobbly edges, translucent wash, darker pooled rim, paper grain */}
        <filter id={filterId(prefix, "watercolour")} {...region}>
          <feTurbulence type="fractalNoise" baseFrequency="0.035" numOctaves="3" seed="11" result="flow" />
          <feDisplacementMap in="SourceGraphic" in2="flow" scale="0.11" xChannelSelector="R" yChannelSelector="G" result="bled" />
          <feGaussianBlur in="bled" stdDeviation="0.012" result="soft" />
          {/* flatten detail into broad washes */}
          <feComponentTransfer in="soft" result="poster">
            <feFuncR type="discrete" tableValues="0.1 0.3 0.5 0.7 0.85 1" />
            <feFuncG type="discrete" tableValues="0.1 0.3 0.5 0.7 0.85 1" />
            <feFuncB type="discrete" tableValues="0.1 0.3 0.5 0.7 0.85 1" />
          </feComponentTransfer>
          <feGaussianBlur in="poster" stdDeviation="0.01" result="blended" />
          <feComponentTransfer in="blended" result="wash">
            <feFuncA type="linear" slope="0.92" />
          </feComponentTransfer>
          <feMorphology in="soft" operator="erode" radius="0.025" result="inner" />
          <feComposite in="soft" in2="inner" operator="out" result="rimRaw" />
          <feGaussianBlur in="rimRaw" stdDeviation="0.006" result="rimSoft" />
          <feColorMatrix in="rimSoft" type="matrix" values="0.5 0 0 0 0  0 0.5 0 0 0  0 0 0.5 0 0  0 0 0 0.7 0" result="rim" />
          <feTurbulence type="fractalNoise" baseFrequency="0.45" numOctaves="2" seed="5" result="paper" />
          <feColorMatrix in="paper" type="matrix" values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 -0.55 1.2" result="paperA" />
          <feMerge result="paint">
            <feMergeNode in="wash" />
            <feMergeNode in="rim" />
          </feMerge>
          <feComposite in="paint" in2="paperA" operator="in" />
        </filter>

        {/* Retro two-tone print in the map's own ink / accent / paper colours */}
        <filter id={filterId(prefix, "retro")} {...region}>
          <feColorMatrix in="SourceGraphic" type="matrix" values={LUM} result="lum" />
          <feComponentTransfer in="lum" result="toned">
            <feFuncR type="discrete" tableValues={rR} />
            <feFuncG type="discrete" tableValues={rG} />
            <feFuncB type="discrete" tableValues={rB} />
          </feComponentTransfer>
          {/* a slightly mis-registered accent layer, like a real two-colour print */}
          <feFlood floodColor={colors.accent} floodOpacity="0.85" />
          <feComposite in2="SourceAlpha" operator="in" />
          <feOffset dx="0.03" dy="0.03" result="ghost" />
          <feMerge>
            <feMergeNode in="ghost" />
            <feMergeNode in="toned" />
          </feMerge>
        </filter>

        {/* Gold foil: gradient-mapped gold with a crinkled metallic shine */}
        <filter id={filterId(prefix, "gold")} {...region}>
          <feColorMatrix in="SourceGraphic" type="matrix" values={LUM} result="lum" />
          <feComponentTransfer in="lum" result="gold">
            <feFuncR type="table" tableValues={gR} />
            <feFuncG type="table" tableValues={gG} />
            <feFuncB type="table" tableValues={gB} />
          </feComponentTransfer>
          <feTurbulence type="fractalNoise" baseFrequency="0.03" numOctaves="3" seed="2" result="foil" />
          <feSpecularLighting in="foil" surfaceScale="4" specularConstant="1.1" specularExponent="18" lightingColor="#fff8e0" result="shine">
            <feDistantLight azimuth="225" elevation="40" />
          </feSpecularLighting>
          <feComposite in="shine" in2="SourceAlpha" operator="in" result="shineIn" />
          <feComposite in="gold" in2="shineIn" operator="arithmetic" k1="0" k2="1" k3="0.45" k4="0" result="lit" />
          <feComposite in="lit" in2="SourceAlpha" operator="in" result="foiled" />
          <feGaussianBlur in="SourceAlpha" stdDeviation="0.012" result="sb" />
          <feOffset in="sb" dy="0.012" result="so" />
          <feFlood floodColor="#000" floodOpacity="0.35" />
          <feComposite in2="so" operator="in" result="shadow" />
          <feMerge>
            <feMergeNode in="shadow" />
            <feMergeNode in="foiled" />
          </feMerge>
        </filter>

        {/* Neon: line art glowing in the route colour with a hot white core */}
        <filter id={filterId(prefix, "neon")} {...region}>
          <feFlood floodColor={colors.accent} />
          <feComposite in2="SourceAlpha" operator="in" result="tube" />
          <feGaussianBlur in="tube" stdDeviation="0.05" result="glowWide" />
          <feGaussianBlur in="tube" stdDeviation="0.018" result="glowTight" />
          <feFlood floodColor="#ffffff" floodOpacity="0.85" />
          <feComposite in2="SourceAlpha" operator="in" result="white" />
          <feGaussianBlur in="white" stdDeviation="0.004" result="core" />
          <feMerge>
            <feMergeNode in="glowWide" />
            <feMergeNode in="glowWide" />
            <feMergeNode in="glowTight" />
            <feMergeNode in="tube" />
            <feMergeNode in="core" />
          </feMerge>
        </filter>

        {/* Engraved: a copperplate etching in the poster's ink, on its paper */}
        <filter id={filterId(prefix, "engraved")} {...region}>
          <Engrave ink={colors.ink} boost={1.7} result="inked" />
          <feFlood floodColor={colors.paper} floodOpacity="0.9" />
          <feComposite in2="SourceAlpha" operator="in" result="ground" />
          <feMerge>
            <feMergeNode in="ground" />
            <feMergeNode in="inked" />
          </feMerge>
        </filter>

        {/* Hand-coloured: a pen-and-ink drawing (outline and inner contours, with a slightly wobbly hand)
            tinted with soft, faded watercolour, as on antique maps. Only the deepest shadows get a
            light touch of hatching, so the colour shows through rather than being striped over. */}
        <filter id={filterId(prefix, "handcoloured")} {...region}>
          {/* the watercolour: muted, faded toward the paper, edges bleeding a little */}
          <feColorMatrix in="SourceGraphic" type="saturate" values="0.7" result="muted" />
          <feComponentTransfer in="muted" result="faded">
            <feFuncR type="linear" slope="0.68" intercept="0.3" />
            <feFuncG type="linear" slope="0.68" intercept="0.28" />
            <feFuncB type="linear" slope="0.62" intercept="0.24" />
          </feComponentTransfer>
          <feTurbulence type="fractalNoise" baseFrequency="0.05" numOctaves="2" seed="4" result="flow" />
          <feDisplacementMap in="faded" in2="flow" scale="0.03" xChannelSelector="R" yChannelSelector="G" result="wash" />
          <feComposite in="wash" in2="SourceAlpha" operator="in" result="tint" />
          {/* inner contours: where the art's lightness changes sharply */}
          <feColorMatrix in="SourceGraphic" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0.2126 0.7152 0.0722 0 0" result="lum" />
          <feComposite in="lum" in2="SourceAlpha" operator="in" result="lumIn" />
          <feConvolveMatrix in="lumIn" order="3" kernelMatrix="-1 -1 -1  -1 8 -1  -1 -1 -1" kernelUnitLength="0.008" preserveAlpha="false" result="edges" />
          <feComponentTransfer in="edges" result="contours">
            <feFuncA type="discrete" tableValues="0 1 1 1 1 1 1 1" />
          </feComponentTransfer>
          {/* the outline round each shape */}
          <feMorphology in="SourceAlpha" operator="erode" radius="0.013" result="inner" />
          <feComposite in="SourceAlpha" in2="inner" operator="out" result="edge" />
          {/* a light hatch in the deepest shadows only */}
          <feColorMatrix in="SourceGraphic" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  -0.2126 -0.7152 -0.0722 0 1" result="dark" />
          <feComposite in="dark" in2="SourceAlpha" operator="in" result="tone" />
          <feImage href={HATCH} x="0" y="0" width="1" height="1" preserveAspectRatio="none" result="screen" />
          <feColorMatrix in="screen" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  1 0 0 0 0" result="screenA" />
          <feComposite in="tone" in2="screenA" operator="arithmetic" k1="0" k2="0.85" k3="-1" k4="-0.12" result="deep" />
          <feComponentTransfer in="deep" result="hatch">
            <feFuncA type="discrete" tableValues="0 0.45 0.45 0.45" />
          </feComponentTransfer>
          <feMerge result="lines">
            <feMergeNode in="edge" />
            <feMergeNode in="contours" />
            <feMergeNode in="hatch" />
          </feMerge>
          {/* drawn by hand: the pen line wanders very slightly */}
          <feTurbulence type="fractalNoise" baseFrequency="0.09" numOctaves="2" seed="9" result="jitter" />
          <feDisplacementMap in="lines" in2="jitter" scale="0.018" xChannelSelector="R" yChannelSelector="G" result="penMask" />
          <feFlood floodColor={colors.ink} floodOpacity="0.85" />
          <feComposite in2="penMask" operator="in" result="pen" />
          <feMerge>
            <feMergeNode in="tint" />
            <feMergeNode in="pen" />
          </feMerge>
        </filter>

        {/* Fine line: pen drawing in the poster's ink colour */}
        <filter id={filterId(prefix, "ink")} {...region}>
          <feFlood floodColor={colors.ink} />
          <feComposite in2="SourceAlpha" operator="in" />
        </filter>
      </defs>
    </svg>
  );
}
