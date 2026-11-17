// Moves each stop's label so it doesn't overlap other labels, pins, route icons,
// stickers, the compass, the title or the map edge. Works on the real rendered page,
// then saves the chosen offsets (Stop.labelOffset, % of poster width) into the design.
//   DATA_DIR=<db> npx tsx design/mockups/place-labels.ts [slug...]
// Needs the site running locally (npx next start) with the same DATA_DIR.
import { readFileSync, readdirSync, writeFileSync } from "node:fs";
import { chromium } from "playwright";
import { saveDesign } from "../../src/lib/server/db";
import { printToken } from "../../src/lib/server/printToken";
import { posterAspect } from "../../src/lib/products";
import type { Design } from "../../src/lib/types";
import { TRIPS } from "./trips";

const only = process.argv.slice(2);

(async () => {
  const browser = await chromium.launch({ args: ["--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"] });
  for (const f of readdirSync("design/mockups/designs").filter((x) => !only.length || only.includes(x.replace(".json", "")))) {
    const file = `design/mockups/designs/${f}`;
    const d = JSON.parse(readFileSync(file, "utf8")) as Design;
    d.stops = d.stops.map((s) => ({ ...s, labelOffset: undefined }));
    await saveDesign(d);
    const w = d.view.refWidth;
    const h = Math.round(w * posterAspect(d.productId, d.orientation));
    const page = await browser.newPage({ viewport: { width: w, height: h } });
    // tsx adds a __name() helper to functions it compiles, including ones run in the page.
    await page.addInitScript(() => ((globalThis as unknown as { __name: unknown }).__name = (f: unknown) => f));
    await page.goto(`http://127.0.0.1:${process.env.PORT ?? 3000}/print/${d.id}?t=${printToken(d.id)}`, { waitUntil: "networkidle", timeout: 180_000 });
    await page.waitForFunction(() => (window as unknown as { __MAPSIE_READY?: boolean }).__MAPSIE_READY === true, null, { timeout: 240_000, polling: 500 }).catch(() => {});
    await page.waitForTimeout(1200);

    const fixed = d.stops.map((st) => TRIPS.find((t) => t.slug === d.id)?.labels?.[st.name] ?? null);
    const result = await page.evaluate((fixed) => {
      type R = { l: number; t: number; r: number; b: number };
      const box = (e: Element): R => {
        const x = e.getBoundingClientRect();
        return { l: x.left, t: x.top, r: x.right, b: x.bottom };
      };
      const overlap = (a: R, b: R) => Math.max(0, Math.min(a.r, b.r) - Math.max(a.l, b.l)) * Math.max(0, Math.min(a.b, b.b) - Math.max(a.t, b.t));
      const u = document.documentElement.clientWidth / 100;
      // The map area: the canvas (excludes the title band and border).
      const canvas = document.querySelector("canvas")!;
      const map = box(canvas);
      const inset = { l: map.l + u * 1, t: map.t + u * 1, r: map.r - u * 1, b: map.b - u * 1 };
      const visible = (e: Element) => getComputedStyle(e).visibility !== "hidden" && (e as HTMLElement).offsetParent !== null;
      const obstacles: R[] = [];
      document.querySelectorAll(".mapsie-stop-icon, .mapsie-stop-dot, .mapsie-stop-sticker, .mapsie-mode, .mapsie-sticker, svg[viewBox='-60 -62 120 120']").forEach((e) => {
        if (visible(e)) obstacles.push(box(e));
      });
      document.querySelectorAll(".mapsie-stop").forEach((stop) => {
        // Number markers are the stop element itself.
        if (!stop.querySelector(".mapsie-stop-icon, .mapsie-stop-dot, .mapsie-stop-sticker")) {
          const r = box(stop);
          obstacles.push({ l: r.l, t: r.t, r: r.l + Math.min(r.r - r.l, u * 4), b: r.b });
        }
      });
      const placed: R[] = [];
      const offsets: ([number, number] | null)[] = [];
      document.querySelectorAll(".mapsie-stop").forEach((stop) => {
        const el = stop.querySelector(".mapsie-stop-label") as HTMLElement | null;
        if (!el) return offsets.push(null);
        el.style.transform = "translate(0px, -50%)";
        const r0 = box(el);
        const pinned = fixed[offsets.length];
        if (pinned) {
          el.style.transform = `translate(${pinned[0] * u}px, calc(-50% + ${pinned[1] * u}px))`;
          placed.push(box(el));
          return offsets.push(pinned);
        }
        const lw = (r0.r - r0.l) / u, lh = (r0.b - r0.t) / u;
        const pin = box(stop.querySelector(".mapsie-stop-icon, .mapsie-stop-dot, .mapsie-stop-sticker") ?? stop);
        const pcx = (pin.l + pin.r) / 2 / u, pcy = (pin.t + pin.b) / 2 / u;
        const pw = (pin.r - pin.l) / u, ph = (pin.b - pin.t) / u;
        const l0 = r0.l / u, cy0 = (r0.t + r0.b) / 2 / u;
        // Candidate label centres around the pin (in u), then converted to offsets.
        const cands: [number, number, number][] = []; // [ox, oy, preference cost]
        const at = (cx: number, cy: number, pref: number) => cands.push([cx - lw / 2 - l0, cy - cy0, pref]);
        const gap = 0.6;
        for (const k of [0, 1, 2.5, 4.5]) {
          at(pcx + pw / 2 + gap + lw / 2 + k, pcy, k * 2); // right
          at(pcx - pw / 2 - gap - lw / 2 - k, pcy, 1 + k * 2); // left
          at(pcx, pcy - ph / 2 - gap - lh / 2 - k, 2 + k * 2); // above
          at(pcx, pcy + ph / 2 + gap + lh / 2 + k, 2 + k * 2); // below
          for (const sx of [1, -1]) for (const sy of [1, -1]) at(pcx + sx * (pw / 2 + lw / 2 + k * 0.7), pcy + sy * (ph / 2 + lh / 2 + gap + k * 0.7), 3 + k * 2);
        }
        let best: [number, number] = [0, 0], bestScore = Infinity;
        for (const [ox, oy, pref] of cands) {
          const r = { l: r0.l + ox * u, r: r0.r + ox * u, t: r0.t + oy * u, b: r0.b + oy * u };
          let score = pref * u * u * 0.5;
          for (const o of [...obstacles, ...placed]) score += overlap(r, o) * 4;
          const out = (Math.max(0, inset.l - r.l) + Math.max(0, r.r - inset.r)) * (r.b - r.t) + (Math.max(0, inset.t - r.t) + Math.max(0, r.b - inset.b)) * (r.r - r.l);
          score += out * 12;
          if (score < bestScore) (bestScore = score), (best = [ox, oy]);
        }
        el.style.transform = `translate(${best[0] * u}px, calc(-50% + ${best[1] * u}px))`;
        placed.push(box(el));
        offsets.push([+best[0].toFixed(2), +best[1].toFixed(2)]);
      });
      // Report anything still overlapping.
      let left = 0;
      placed.forEach((a, i) => [...obstacles, ...placed.slice(i + 1)].forEach((b) => (left += overlap(a, b) > u * u * 0.3 ? 1 : 0)));
      return { offsets, left };
    }, fixed);
    d.stops = d.stops.map((s, i) => {
      const o = result.offsets[i];
      return o && (o[0] || o[1]) ? { ...s, labelOffset: o } : s;
    });
    writeFileSync(file, JSON.stringify(d, null, 1));
    await saveDesign(d);
    console.log(f, "labels placed;", result.left ? `${result.left} small overlaps left` : "no overlaps");
    await page.close();
  }
  await browser.close();
  process.exit(0);
})();
