// Instagram graphics (organic posts), rendered like the ad graphics.
//   npx tsx design/ads/src/social.ts   → public/social/how-it-works.jpg
import { readFileSync } from "node:fs";
import path from "node:path";
import { chromium } from "playwright";
import { PRODUCTS } from "../../../src/lib/products";
import { CHRISTMAS } from "../../../src/lib/christmas";

const nm = path.resolve("node_modules");
const img = (p: string) => `data:image/jpeg;base64,${readFileSync(p).toString("base64")}`;
const font = (f: string) => `url(data:font/woff2;base64,${readFileSync(`${nm}/${f}`).toString("base64")}) format("woff2")`;
const FROM = Math.min(...PRODUCTS.map((p) => p.price.GB));
const xmas = new Date(`${CHRISTMAS.lastOrder.GB.standard}T12:00:00Z`).toLocaleDateString("en-GB", { weekday: "short", day: "numeric", month: "short", timeZone: "UTC" });

const css = `
@font-face { font-family: Playfair; src: ${font("@fontsource-variable/playfair-display/files/playfair-display-latin-wght-normal.woff2")}; font-weight: 400 900; }
@font-face { font-family: Nunito; src: ${font("@fontsource-variable/nunito/files/nunito-latin-wght-normal.woff2")}; font-weight: 200 1000; }
* { box-sizing: border-box; margin: 0; padding: 0; }
body { width: 1080px; height: 1350px; background: #fbf6ee; color: #1f2430; font-family: Nunito; overflow: hidden; }
.pf { font-family: Playfair; font-weight: 800; letter-spacing: -0.02em; line-height: 1.05; }
.coral { color: #ff6b4a; }
.logo i { display: inline-block; width: .3em; height: .3em; border-radius: 50% 50% 50% 0; background: #ff6b4a; transform: rotate(-45deg) translate(-.02em, .06em); margin-left: .08em; }
.photo { height: 560px; background: url(${img("design/mockups/etsy/01-southeast-asia.jpg")}) 50% 30% / cover; position: relative; }
.badge { position: absolute; bottom: 30px; right: 36px; background: #1f4d3a; color: #fff; font-weight: 900; font-size: 26px; padding: 14px 26px; border-radius: 999px; }
.brand { position: absolute; top: 36px; left: 36px; background: #fbf6ee; font-size: 34px; padding: 10px 22px; border-radius: 999px; }
.steps { padding: 52px 64px 0; }
h1 { font-size: 76px; margin-bottom: 34px; }
.step { display: flex; gap: 28px; align-items: flex-start; margin-bottom: 30px; }
.n { flex: 0 0 64px; height: 64px; border-radius: 50%; background: #ff6b4a; color: #fff; font-weight: 900; font-size: 32px; display: grid; place-items: center; }
.step b { display: block; font-size: 36px; font-weight: 900; margin-bottom: 4px; }
.step span { font-size: 27px; color: #1f2430b3; line-height: 1.35; }
.foot { position: absolute; left: 64px; right: 64px; bottom: 44px; display: flex; justify-content: space-between; align-items: center; font-size: 28px; font-weight: 800; }
`;

const html = `
<div class="photo"><div class="brand pf logo">Mapsie<i></i></div><div class="badge">Order by ${xmas} for Christmas (UK)</div></div>
<div class="steps">
  <h1 class="pf">Your trip, <span class="coral">on your wall.</span></h1>
  <div class="step"><div class="n">1</div><div><b>Design your map</b><span>Add your stops, or just describe your trip. Pick a style, add stickers and your own photos.</span></div></div>
  <div class="step"><div class="n">2</div><div><b>We print and frame it</b><span>On thick art paper, printed near you in the UK, US or Australia.</span></div></div>
  <div class="step"><div class="n">3</div><div><b>Delivered, ready to hang</b><span>Free standard delivery. Or get the digital file in minutes.</span></div></div>
</div>
<div class="foot"><span>Prints from £${FROM}</span><span class="coral">mapsie.shop</span></div>`;

(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1080, height: 1350 } });
  await p.setContent(`<!doctype html><html><head><meta charset="utf-8"><style>${css}</style></head><body>${html}</body></html>`, { waitUntil: "load" });
  await p.evaluate(() => document.fonts.ready);
  await p.waitForTimeout(300);
  await p.screenshot({ path: "public/social/how-it-works.jpg", type: "jpeg", quality: 92 });
  await b.close();
  console.log("public/social/how-it-works.jpg");
})();
