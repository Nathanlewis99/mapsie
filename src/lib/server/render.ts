import path from "path";
import { promises as fs } from "fs";
import type { Design } from "../types";
import { posterAspect, printPixels, PRINT_DPI } from "../products";
import { rendersDir } from "./db";

// How it works: a headless browser lays the poster out at the same CSS width the
// customer designed at, with the pixel density raised to hit 300 dpi.
//
// Two browser limits matter at poster sizes:
//  1. WebGL can't make a canvas much over ~8000 px, so the map layer is drawn at
//     most GL_MAX px and gently upscaled (A1 ≈ 1.3×, invisible in print). Text,
//     stickers and markers are HTML and stay at full 300 dpi.
//     (Exactly 8192 fails in SwiftShader; on a GPU box set PRINT_MAX_PX=16384.)
//  2. A single screenshot taller than ~8192 px wraps around. So we capture the
//     poster in horizontal strips and stitch them together.
const GL_MAX = Number(process.env.PRINT_MAX_PX ?? 7680);
const STRIP_PX = 4000;

export async function renderDesign(design: Design, fileName: string) {
  const { chromium } = await import("playwright");
  const sharp = (await import("sharp")).default;
  const target = printPixels(design.productId, design.orientation);
  const cssW = design.view.refWidth;
  const cssH = Math.round(cssW * posterAspect(design.productId, design.orientation));
  const scale = target.width / cssW;
  const stripCss = Math.max(1, Math.floor(STRIP_PX / scale));

  const browser = await chromium.launch({ args: ["--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"] });
  try {
    // The viewport is only one strip tall; the poster's size doesn't depend on it.
    const page = await browser.newPage({ viewport: { width: cssW, height: stripCss }, deviceScaleFactor: scale });
    await page.addInitScript((max) => (window.__MAPSIE_GLMAX = max), GL_MAX);
    const base = process.env.APP_URL ?? "http://localhost:3000";
    await page.goto(`${base}/print/${design.id}`, { waitUntil: "networkidle", timeout: 180_000 });
    // Poll on a timer: at print density each animation frame is slow.
    await page.waitForFunction(() => window.__MAPSIE_READY === true || !!window.__MAPSIE_ERROR, null, { timeout: 240_000, polling: 1000 });
    const failed = await page.evaluate(() => window.__MAPSIE_ERROR);
    if (failed) throw new Error(`Map failed to render: ${failed}`);

    const width = Math.round(cssW * scale);
    const height = Math.round(cssH * scale);
    const strips: { input: Buffer; top: number; left: 0 }[] = [];
    for (let y = 0; y < cssH; y += stripCss) {
      // Slide the poster up under the viewport instead of scrolling the page.
      await page.evaluate((offset) => {
        const el = document.getElementById("poster")!;
        el.style.transform = `translateY(${-offset}px)`;
        return new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
      }, y);
      const shot = await page.screenshot({ type: "png", timeout: 120_000 });
      const top = Math.round(y * scale);
      const h = Math.min((await sharp(shot).metadata()).height!, height - top);
      if (h <= 0) break;
      strips.push({ input: await sharp(shot).extract({ left: 0, top: 0, width, height: h }).toBuffer(), top, left: 0 });
    }

    const out = path.join(await rendersDir(), fileName);
    await sharp({ create: { width, height, channels: 4, background: "#ffffff" } })
      .composite(strips)
      .withMetadata({ density: PRINT_DPI })
      .png({ compressionLevel: 6 })
      .toFile(out);

    const mapDpi = Math.round(Math.min(1, GL_MAX / Math.max(width, height)) * PRINT_DPI);
    const stat = await fs.stat(out);
    return { file: fileName, width, height, dpi: PRINT_DPI, mapDpi, bytes: stat.size };
  } finally {
    await browser.close();
  }
}
