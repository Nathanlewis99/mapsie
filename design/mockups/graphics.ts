// Listing graphics in Mapsie's own fonts: all designs together, a detail close-up and
// "how it works". Renders HTML with Playwright at 2400 x 1800.
//   npx tsx design/mockups/graphics.ts <hi-res renders dir> <mockups dir> <out dir>
import { mkdirSync, readFileSync } from "node:fs";
import path from "node:path";
import { chromium } from "playwright";

const [renders, mockups, out] = process.argv.slice(2).map((p) => path.resolve(p));
mkdirSync(out, { recursive: true });
const nm = path.resolve("node_modules");
const img = (p: string) => `data:image/${p.endsWith(".png") ? "png" : "jpeg"};base64,${readFileSync(p).toString("base64")}`;

const font = (f: string) => `url(data:font/woff2;base64,${readFileSync(`${nm}/${f}`).toString("base64")}) format("woff2")`;
const css = `
@font-face { font-family: Playfair; src: ${font("@fontsource-variable/playfair-display/files/playfair-display-latin-wght-normal.woff2")}; font-weight: 400 900; }
@font-face { font-family: Playfair; font-style: italic; src: ${font("@fontsource-variable/playfair-display/files/playfair-display-latin-wght-italic.woff2")}; font-weight: 400 900; }
@font-face { font-family: Nunito; src: ${font("@fontsource-variable/nunito/files/nunito-latin-wght-normal.woff2")}; font-weight: 200 1000; }
* { box-sizing: border-box; margin: 0; }
body { width: 2400px; height: 1800px; background: #fbf6ee; color: #1f2430; font-family: Nunito; overflow: hidden; }
h1 { font-family: Playfair; font-weight: 800; font-size: 96px; letter-spacing: -1px; }
.coral { color: #ff6b4a; }
.pin { display: inline-block; width: .32em; height: .32em; border-radius: 50% 50% 50% 0; background: #ff6b4a; transform: rotate(-45deg); margin-left: 6px; }
`;

const page = async (name: string, html: string) => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 2400, height: 1800 } });
  await p.setContent(`<!doctype html><html><head><style>${css}</style></head><body>${html}</body></html>`, { waitUntil: "load" });
  await p.evaluate(() => document.fonts.ready);
  await p.waitForTimeout(500);
  await p.screenshot({ path: `${out}/${name}.jpg`, type: "jpeg", quality: 92 });
  await b.close();
  console.log(`${out}/${name}.jpg`);
};

(async () => {
  // 1. Seven trips, seven looks
  const shot = (slug: string, style: string, rot: number) =>
    `<img src="${img(`${renders}/${slug}.png`)}" style="position:absolute;${style};box-shadow:0 22px 44px -14px rgba(31,36,48,.5),0 4px 10px rgba(31,36,48,.15);transform:rotate(${rot}deg)">`;
  await page(
    "all-designs",
    `<div style="padding:80px 110px 0;text-align:center">
       <h1>Any trip. Any style.<span class="pin"></span></h1>
       <p style="font-size:40px;margin-top:14px;color:#1f2430b3">12 map styles · your own photos · 1,400 illustrated stickers · routes by plane, train, car, boat, tuk-tuk…</p>
     </div>
     ${shot("southeast-asia", "left:150px;top:330px;height:640px", -3)}
     ${shot("sri-lanka", "left:640px;top:310px;height:640px", 2)}
     ${shot("interrail-europe", "left:1130px;top:330px;height:640px", -1.5)}
     ${shot("africa-safari", "left:1620px;top:315px;height:640px", 2.5)}
     ${shot("london-pub-crawl", "left:300px;top:1030px;height:640px", 2)}
     ${shot("south-america", "left:800px;top:1060px;height:640px", -2)}
     ${shot("route-66", "left:1290px;top:1180px;width:860px", 1.5)}`,
  );

  // 2. Detail close-up (crop of the Sri Lanka print)
  await page(
    "detail",
    `<div style="position:absolute;inset:0;background:url(${img(`${renders}/../detail/sri-lanka.png`)}) no-repeat;background-size:2600px auto;background-position:-100px -1150px"></div>
     <div style="position:absolute;left:70px;top:70px;background:#fbf6eef2;border-radius:36px;padding:44px 56px;max-width:1150px;box-shadow:0 10px 30px rgba(0,0,0,.15)">
       <h1 style="font-size:72px">Add your own photos</h1>
       <p style="font-size:38px;margin-top:14px;line-height:1.35">Upload snaps from your trip and pin them anywhere on the map, next to your route, stickers and real terrain. Printed sharp at 300 dpi on 200gsm matte art paper.</p>
     </div>`,
  );

  // 3. How it works
  const step = (n: number, title: string, body: string) => `
    <div style="flex:1;background:#fff;border-radius:48px;padding:64px 56px;box-shadow:0 10px 30px rgba(31,36,48,.08)">
      <div style="width:110px;height:110px;border-radius:50%;background:#ff6b4a;color:#fff;font:800 60px Nunito;display:grid;place-items:center">${n}</div>
      <h2 style="font:800 60px Playfair;margin-top:40px">${title}</h2>
      <p style="font-size:40px;line-height:1.4;margin-top:22px;color:#1f2430c0">${body}</p>
    </div>`;
  await page(
    "how-it-works",
    `<div style="padding:120px 120px 0">
       <h1 style="text-align:center">How it works<span class="pin"></span></h1>
       <div style="display:flex;gap:56px;margin-top:100px">
         ${step(1, "Order here", "Choose your size and frame. It's personalised after you buy, so there's nothing to type now.")}
         ${step(2, "Design your map", "Go to <b>mapsie.shop/etsy</b> and enter your order number and postcode. Add your places, route, photos from your trip, stickers and a title. About 5 minutes.")}
         ${step(3, "We print & ship", "Check the preview and press Send to print. Printed to order and delivered to your door, framed or rolled.")}
       </div>
       <p style="text-align:center;font-size:40px;margin-top:70px;color:#1f2430a0">Nothing more to pay · you see exactly how it looks before it's printed</p>
     </div>
     ${["london-pub-crawl", "southeast-asia", "sri-lanka", "interrail-europe", "africa-safari"].map((s2, i) => shot(s2, `left:${170 + i * 430}px;top:${1340 + (i % 2) * 30}px;height:520px`, [-4, 3, -2, 2.5, -3][i])).join("")}`,
  );
  process.exit(0);
})();
