// Capture what a route-drawing Reel needs from a real Mapsie design, using the local site:
//   <slug>-base.png   the poster without route, stops, leg icons or stickers
//   <slug>-full.png   the finished poster
//   <slug>.json       the route (pixel coordinates on the poster image) and the stops, in order
// Run from the repo root, with the site running on PORT (e.g. 3123) and DATA_DIR set:
//   DATA_DIR=... PORT=3123 npx -y tsx@4.20.3 design/video/capture.ts touring-nc500 route-66
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { chromium } from "playwright";
import { saveDesign } from "../../src/lib/server/db";
import { printToken } from "../../src/lib/server/printToken";
import { posterAspect } from "../../src/lib/products";
import type { Design } from "../../src/lib/types";

const SCALE = 3; // poster images 1200px wide (designs are laid out 400px wide)
const OUT = "design/video/public/maps";

(async () => {
  mkdirSync(OUT, { recursive: true });
  const browser = await chromium.launch({ args: ["--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"] });
  for (const slug of process.argv.slice(2)) {
    const d = JSON.parse(readFileSync(`design/mockups/designs/${slug}.json`, "utf8")) as Design;
    await saveDesign(d);
    const w = d.view.refWidth;
    const h = Math.round(w * posterAspect(d.productId, d.orientation));
    const page = await browser.newPage({ viewport: { width: w, height: h }, deviceScaleFactor: SCALE });
    await page.goto(`http://127.0.0.1:${process.env.PORT ?? 3000}/print/${d.id}?t=${printToken(d.id)}`, { waitUntil: "networkidle", timeout: 180_000 });
    await page.waitForFunction(() => (window as unknown as { __MAPSIE_READY?: boolean }).__MAPSIE_READY === true, null, { timeout: 240_000, polling: 500 }).catch(() => {});
    await page.waitForTimeout(1500);
    await page.screenshot({ path: `${OUT}/${slug}-full.png`, clip: { x: 0, y: 0, width: w, height: h } });

    // The route and stops in poster pixels (at SCALE).
    const geo = await page.evaluate(async (scale) => {
      const m = (window as unknown as { __MAPSIE_MAP: { getSource: (id: string) => { getData: () => Promise<GeoJSON.FeatureCollection> }; project: (p: [number, number]) => { x: number; y: number }; getContainer: () => HTMLElement } }).__MAPSIE_MAP;
      const poster = document.getElementById("poster")!.getBoundingClientRect();
      const box = m.getContainer().getBoundingClientRect();
      const off = { x: box.left - poster.left, y: box.top - poster.top };
      const fc = await m.getSource("mapsie-route").getData();
      const legs = fc.features.map((f) =>
        (f.geometry as GeoJSON.LineString).coordinates.map((c) => {
          const p = m.project(c as [number, number]);
          return [Math.round((p.x + off.x) * scale * 10) / 10, Math.round((p.y + off.y) * scale * 10) / 10];
        }),
      );
      return { legs };
    }, SCALE);
    const stops = d.stops.map((s) => ({ name: s.name, mode: s.arriveBy ?? "plane" }));

    // The empty map: hide the route layers, stops, icons and stickers.
    await page.evaluate(() => {
      const m = (window as unknown as { __MAPSIE_MAP: { getStyle: () => { layers: { id: string }[] }; setLayoutProperty: (id: string, k: string, v: string) => void } }).__MAPSIE_MAP;
      for (const l of m.getStyle().layers) if (l.id.startsWith("mapsie-route")) m.setLayoutProperty(l.id, "visibility", "none");
      const css = document.createElement("style");
      css.textContent = ".mapsie-stop,.mapsie-mode,.mapsie-sticker,.mapsie-note{display:none!important}";
      document.head.appendChild(css);
    });
    await page.waitForTimeout(1500);
    await page.screenshot({ path: `${OUT}/${slug}-base.png`, clip: { x: 0, y: 0, width: w, height: h } });
    writeFileSync(`${OUT}/${slug}.json`, JSON.stringify({ width: w * SCALE, height: h * SCALE, title: d.title, subtitle: d.subtitle, ...geo, stops }));
    console.log(slug, `${w * SCALE}x${h * SCALE}`, geo.legs.length, "legs");
    await page.close();
  }
  await browser.close();
  process.exit(0);
})();
