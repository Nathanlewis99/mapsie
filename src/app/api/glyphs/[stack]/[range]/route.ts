import { readFile } from "node:fs/promises";
import path from "node:path";

// Map label fonts. Our own (period serif for the Heritage style) are built into
// public/glyphs by fontnik; anything we don't have, such as Japanese place names,
// comes from OpenFreeMap's Noto Sans in the same weight, so no label goes missing.
const UPSTREAM = "https://tiles.openfreemap.org/fonts";
const SAFE = /^[\w .-]+$/;
const notoFor = (font: string) => (/italic/i.test(font) ? "Noto Sans Italic" : /bold/i.test(font) ? "Noto Sans Bold" : "Noto Sans Regular");
const headers = { "content-type": "application/x-protobuf", "cache-control": "public, max-age=31536000, immutable", "access-control-allow-origin": "*" };

export async function GET(_req: Request, { params }: { params: Promise<{ stack: string; range: string }> }) {
  const { stack, range } = await params;
  const fonts = decodeURIComponent(stack).split(",").map((f) => f.trim());
  const file = range.replace(/\.pbf$/, "");
  if (!/^\d+-\d+$/.test(file) || fonts.some((f) => !SAFE.test(f))) return new Response("bad request", { status: 400 });
  for (const font of fonts) {
    try {
      return new Response(new Uint8Array(await readFile(path.join(process.cwd(), "public/glyphs", font, `${file}.pbf`))), { headers });
    } catch {
      /* not one of ours, or not this range: try the next font */
    }
  }
  const r = await fetch(`${UPSTREAM}/${encodeURIComponent(notoFor(fonts[0]))}/${file}.pbf`, { signal: AbortSignal.timeout(15_000) });
  if (!r.ok) return new Response("not found", { status: 404 });
  return new Response(await r.arrayBuffer(), { headers });
}
