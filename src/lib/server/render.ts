import path from "path";
import { promises as fs } from "fs";
import type { Design } from "../types";
import { posterAspect, printPixels, PRINT_DPI } from "../products";
import { rendersDir } from "./db";

// WebGL can't draw an infinitely large canvas. 8192px is a safe ceiling for
// headless Chromium; a GPU render box can usually go to 16384.
const MAX_PX = Number(process.env.PRINT_MAX_PX ?? 8192);

export async function renderDesign(design: Design, fileName: string) {
  const { chromium } = await import("playwright");
  const target = printPixels(design.productId, design.orientation);
  const cssW = design.view.refWidth;
  const cssH = Math.round(cssW * posterAspect(design.productId, design.orientation));
  const scale = Math.min(target.width / cssW, MAX_PX / Math.max(cssW, cssH));

  const browser = await chromium.launch({ args: ["--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"] });
  try {
    const page = await browser.newPage({ viewport: { width: cssW, height: cssH }, deviceScaleFactor: scale });
    const base = process.env.APP_URL ?? "http://localhost:3000";
    await page.goto(`${base}/print/${design.id}`, { waitUntil: "networkidle", timeout: 120_000 });
    await page.waitForFunction(() => window.__MAPSIE_READY === true, null, { timeout: 120_000 });
    const out = path.join(await rendersDir(), fileName);
    await page.locator("#poster").screenshot({ path: out, type: "png", timeout: 120_000 });
    const width = Math.round(cssW * scale);
    const dpi = Math.round((width / target.width) * PRINT_DPI);
    const stat = await fs.stat(out);
    return { file: fileName, width, height: Math.round(cssH * scale), dpi, bytes: stat.size };
  } finally {
    await browser.close();
  }
}
