// Renders each built design through Mapsie's own /print page (no preview watermark).
//   DATA_DIR=<db dir> npx tsx design/mockups/render.ts <outDir> [scale] [slug...]
// Needs the site running locally (npx next start) with the same DATA_DIR.
import { readFileSync, readdirSync } from "node:fs";
import { chromium } from "playwright";
import { saveDesign } from "../../src/lib/server/db";
import { printToken } from "../../src/lib/server/printToken";
import { posterAspect } from "../../src/lib/products";
import type { Design } from "../../src/lib/types";

const [out, scaleArg, ...only] = process.argv.slice(2);
const scale = Number(scaleArg ?? 2);
(async () => {
  const files = readdirSync("design/mockups/designs").filter((f) => !only.length || only.includes(f.replace(".json", "")));
  const browser = await chromium.launch({ args: ["--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"] });
  for (const f of files) {
    const d = JSON.parse(readFileSync(`design/mockups/designs/${f}`, "utf8")) as Design;
    await saveDesign(d);
    const w = d.view.refWidth;
    const h = Math.round(w * posterAspect(d.productId, d.orientation));
    const page = await browser.newPage({ viewport: { width: w, height: h }, deviceScaleFactor: scale });
    await page.goto(`http://127.0.0.1:${process.env.PORT ?? 3000}/print/${d.id}?t=${printToken(d.id)}`, { waitUntil: "networkidle", timeout: 180_000 });
    await page.waitForFunction(() => (window as unknown as { __MAPSIE_READY?: boolean }).__MAPSIE_READY === true, null, { timeout: 240_000, polling: 500 }).catch(() => console.log("  (not ready signal)"));
    await page.waitForTimeout(1500);
    await page.screenshot({ path: `${out}/${d.id}.png`, clip: { x: 0, y: 0, width: w, height: h } });
    console.log(f, `${w * scale}x${h * scale}`);
    await page.close();
  }
  await browser.close();
  process.exit(0);
})();
