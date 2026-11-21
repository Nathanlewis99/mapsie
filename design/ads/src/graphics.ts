// Mapsie ad graphics: static ads (3 sizes per angle) and the overlays used to build
// the vertical videos (phone frame, captions, end card). HTML rendered by Playwright
// with Mapsie's own fonts; prices and Christmas dates come from the site's code.
//   npx tsx design/ads/src/graphics.ts <out dir> [statics|overlays|all]
import { mkdirSync, readFileSync } from "node:fs";
import path from "node:path";
import { chromium, type Browser } from "playwright";
import { DIGITAL_PRICE, PRODUCTS, itemPrice } from "../../../src/lib/products";
import { CHRISTMAS } from "../../../src/lib/christmas";
import { GIFT_MIN } from "../../../src/lib/giftcards";

const out = path.resolve(process.argv[2] ?? "design/ads");
const what = process.argv[3] ?? "all";
const nm = path.resolve("node_modules");
const img = (p: string) => `data:image/${p.endsWith(".png") ? "png" : p.endsWith(".webp") ? "webp" : "jpeg"};base64,${readFileSync(p).toString("base64")}`;
const font = (f: string) => `url(data:font/woff2;base64,${readFileSync(`${nm}/${f}`).toString("base64")}) format("woff2")`;

const FROM = Math.min(...PRODUCTS.map((p) => p.price.GB));
const FRAMED_FROM = Math.min(...PRODUCTS.map((p) => itemPrice({ productId: p.id, frame: "black", paper: "ema", mount: "none", glaze: "perspex" } as never, "GB")));
const DIGITAL = DIGITAL_PRICE.GB;
const xmas = new Date(`${CHRISTMAS.lastOrder.GB.standard}T12:00:00Z`).toLocaleDateString("en-GB", { weekday: "short", day: "numeric", month: "short", timeZone: "UTC" });

const css = `
@font-face { font-family: Playfair; src: ${font("@fontsource-variable/playfair-display/files/playfair-display-latin-wght-normal.woff2")}; font-weight: 400 900; }
@font-face { font-family: Playfair; font-style: italic; src: ${font("@fontsource-variable/playfair-display/files/playfair-display-latin-wght-italic.woff2")}; font-weight: 400 900; }
@font-face { font-family: Nunito; src: ${font("@fontsource-variable/nunito/files/nunito-latin-wght-normal.woff2")}; font-weight: 200 1000; }
* { box-sizing: border-box; margin: 0; padding: 0; }
html, body { background: transparent; }
body { color: #1f2430; font-family: Nunito; overflow: hidden; }
.pf { font-family: Playfair; font-weight: 800; letter-spacing: -0.02em; line-height: 1.04; text-wrap: balance; }
.coral { color: #ff6b4a; }
.logo { font-family: Playfair; font-weight: 800; letter-spacing: -0.02em; }
.logo i { display: inline-block; width: .3em; height: .3em; border-radius: 50% 50% 50% 0; background: #ff6b4a; transform: rotate(-45deg) translate(-.02em, .06em); margin-left: .08em; }
.pill { display: inline-flex; align-items: center; gap: .4em; border-radius: 999px; font-weight: 900; }
`;

let browser: Browser;
async function render(name: string, w: number, h: number, html: string, opts: { transparent?: boolean; jpg?: boolean } = {}) {
  const p = await browser.newPage({ viewport: { width: w, height: h } });
  await p.setContent(`<!doctype html><html><head><meta charset="utf-8"><style>${css} body{width:${w}px;height:${h}px;${opts.transparent ? "" : "background:#fbf6ee;"}}</style></head><body>${html}</body></html>`, { waitUntil: "load" });
  await p.evaluate(() => document.fonts.ready);
  await p.waitForTimeout(250);
  await p.screenshot({ path: `${out}/${name}.png`, omitBackground: !!opts.transparent });
  if (opts.jpg) await p.screenshot({ path: `${out}/${name}.jpg`, type: "jpeg", quality: 90 });
  await p.close();
  console.log(name);
}

// ---------------------------------------------------------------- static ads
const E = (f: string) => img(path.resolve("design/mockups/etsy", f));
type Angle = {
  id: string;
  image: string | null; // null = gift card visual
  pos: Record<string, string>; // object-position per size
  head: string; // HTML allowed
  sub: string;
  cta: string;
  price: string;
  badge?: string;
};
const ANGLES: Angle[] = [
  {
    id: "christmas-gift",
    image: E("01-southeast-asia.jpg"),
    pos: { sq: "50% 30%", p45: "50% 22%", p23: "50% 25%" },
    head: `The gift they'll <span class="coral">actually</span> hang up.`,
    sub: "A custom map of their favourite trip: every stop, the route and the memories. Framed and delivered.",
    cta: "Design theirs",
    price: `Framed from £${FRAMED_FROM}`,
    badge: `Order by ${xmas} for Christmas (UK)`,
  },
  {
    id: "honeymoon",
    image: E("04-sri-lanka.jpg"),
    pos: { sq: "50% 22%", p45: "50% 18%", p23: "50% 20%" },
    head: `Your honeymoon, <span class="coral">on your wall.</span>`,
    sub: "Every stop, the route between them and your own photos, printed and framed.",
    cta: "Design yours",
    price: `From £${FROM} · free delivery`,
  },
  {
    id: "adventure",
    image: E("03-route-66.jpg"),
    pos: { sq: "50% 18%", p45: "50% 14%", p23: "50% 15%" },
    head: `Every stop.<br><span class="coral">Every route.</span>`,
    sub: "Flights, trains, road trips and tuk-tuks, drawn on the real roads. Your trip as a print.",
    cta: "Map your trip",
    price: `From £${FROM} · free delivery`,
  },
  {
    id: "gift-card",
    image: null,
    pos: {},
    head: `Not sure where they went? <span class="coral">Give a gift card.</span>`,
    sub: "They design their own map. Emailed instantly, or on Christmas morning.",
    cta: "Buy a gift card",
    price: `From £${GIFT_MIN}`,
  },
  {
    id: "your-photos",
    image: img(path.resolve("design/ads/assets/sri-lanka-photos.jpg")),
    pos: { sq: "40% 50%", p45: "47% 50%", p23: "50% 50%" },
    head: `Pin your own photos <span class="coral">to the map.</span>`,
    sub: "Add trip photos right where they were taken, as polaroids, stamps or hearts.",
    cta: "Add your photos",
    price: `From £${FROM} · free delivery`,
  },
  // Vintage map styles (Nov 2026)
  {
    id: "vintage-antique",
    image: img(path.resolve("design/ads/vintage/antique-grand-tour-room.jpg")),
    pos: { sq: "50% 12%", p45: "50% 14%", p23: "50% 16%", p916: "50% 0%" },
    head: `Your trip, as an <span class="coral">antique map.</span>`,
    sub: "Hand-coloured borders, sea monsters and a scroll title, like the maps of the 1700s. Plus Victorian, 1920s touring and more.",
    cta: "Design yours",
    price: `Prints from £${FROM}`,
  },
  {
    id: "vintage-heritage",
    image: img(path.resolve("design/ads/vintage/heritage-edinburgh-room.jpg")),
    pos: { sq: "50% 14%", p45: "50% 16%", p23: "50% 18%", p916: "50% 0%" },
    head: `Your city, as a <span class="coral">Victorian map.</span>`,
    sub: "Engraved streets and buildings, like the old town plans, with your route in gold. Any city, any trip.",
    cta: "Design yours",
    price: `Prints from £${FROM}`,
  },
];

const SIZES = [
  { key: "sq", w: 1080, h: 1080, imgH: 560, head: 70, sub: 31 },
  { key: "p45", w: 1080, h: 1350, imgH: 760, head: 88, sub: 36 },
  { key: "p23", w: 1000, h: 1500, imgH: 880, head: 88, sub: 35 },
  { key: "p916", w: 1080, h: 1920, imgH: 720, head: 84, sub: 32 },
] as const;
const SIZE_NAME = { sq: "1080x1080", p45: "1080x1350", p23: "1000x1500", p916: "1080x1920" } as const;
// Stories/Reels: keep the logo, text and button clear of the profile bar (top 14%)
// and the "Shop now" button and caption (bottom ~25%).
const SAFE = { top: 270, bottom: 500 };
const TALL = { top: 330, textH: 560, right: 190, imgTop: 930 };

function giftCardVisual(scale: number) {
  return `<div style="position:absolute;inset:0;background:radial-gradient(circle at 30% 30%,#ffd9cf 0,#fbe3d8 35%,#f6efe4 75%);overflow:hidden">
    <div style="position:absolute;left:50%;top:52%;width:${760 * scale}px;height:${537 * scale}px;transform:translate(-50%,-50%) rotate(-4deg);border-radius:${34 * scale}px;background:#fff;box-shadow:0 ${40 * scale}px ${80 * scale}px -${20 * scale}px rgba(31,36,48,.45);overflow:hidden">
      <img src="${img(path.resolve("public/examples/southeast-asia.webp"))}" style="position:absolute;right:0;top:0;height:100%;width:48%;object-fit:cover;object-position:52% 20%">
      <div style="position:absolute;right:0;top:0;height:100%;width:48%;background:linear-gradient(90deg,#fff,rgba(255,255,255,.2) 40%,transparent)"></div>
      <div style="position:absolute;left:${40 * scale}px;top:${34 * scale}px;bottom:${32 * scale}px;width:60%;display:flex;flex-direction:column">
        <div class="logo" style="font-size:${40 * scale}px">Mapsie<i></i></div>
        <div style="margin-top:auto;font-size:${17 * scale}px;font-weight:900;letter-spacing:.2em;color:#ff6b4a">GIFT CARD</div>
        <div class="pf" style="font-size:${92 * scale}px">£79</div>
        <div style="font-size:${24 * scale}px;font-weight:800;margin-top:${10 * scale}px">For Sam</div>
        <div style="font-size:${20 * scale}px;font-style:italic;color:#1f2430b3;margin-top:${4 * scale}px">“For all our adventures. Happy Christmas! x”</div>
        <div style="margin-top:${18 * scale}px;background:#fbf6ee;border-radius:${16 * scale}px;padding:${10 * scale}px ${16 * scale}px;width:fit-content">
          <div style="font-size:${12 * scale}px;font-weight:900;color:#1f243080">YOUR CODE</div>
          <div style="font-family:monospace;font-weight:900;font-size:${26 * scale}px;letter-spacing:.06em">GIFT-XMAS-2026</div>
        </div>
      </div>
    </div>
  </div>`;
}

async function statics() {
  const only = process.env.ANGLES?.split(",");
  for (const a of ANGLES.filter((x) => !only || only.includes(x.id))) {
    for (const s of SIZES.filter((z) => z.key !== "p916" || a.id.startsWith("vintage"))) {
      const tall = s.key === "p916";
      const pad = s.w > 1000 ? 64 : 58;
      const src = a.id === "your-photos" && s.key === "p23" ? img(path.resolve("design/ads/assets/sri-lanka-photos-tall.jpg")) : a.image;
      const visual = src
        ? `<img src="${src}" style="position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:${a.pos[s.key]}">`
        : giftCardVisual(s.key === "sq" ? 0.9 : s.key === "p45" ? 1.12 : 1.06);
      // 9:16 (Stories/Reels): text and button first, inside the area no overlay covers on Instagram
      // Reels (top 15%, bottom 40%, right 15%); the room photo fills the rest underneath.
      const html = tall ? `
        <div style="position:absolute;inset:0;background:#fbf6ee"></div>
        <div style="position:absolute;left:0;right:0;top:${TALL.imgTop}px;bottom:0;overflow:hidden">${visual}</div>
        <div style="position:absolute;left:0;right:0;top:${TALL.imgTop}px;height:120px;background:linear-gradient(#fbf6ee,#fbf6ee00)"></div>
        <div style="position:absolute;left:${pad}px;right:${TALL.right}px;top:${TALL.top}px;height:${TALL.textH}px;display:flex;flex-direction:column">
          <div class="logo" style="align-self:flex-start;font-size:40px">Mapsie<i></i></div>
          <div class="pf" style="font-size:${s.head}px;margin-top:30px">${a.head}</div>
          <div style="font-size:${s.sub}px;line-height:1.35;color:#1f2430c4;margin-top:22px;font-weight:600;text-wrap:pretty">${a.sub}</div>
          <div style="margin-top:auto;display:flex;align-items:center;gap:36px">
            <div class="pill" style="background:#ff6b4a;color:#fff;font-size:34px;padding:20px 38px;box-shadow:0 12px 26px -8px rgba(255,107,74,.6)">${a.cta} →</div>
            <div><div style="font-size:30px;font-weight:900">${a.price}</div><div style="font-size:24px;font-weight:700;color:#1f243099">mapsie.shop</div></div>
          </div>
        </div>` : `
        ${tall ? `<div style="position:absolute;inset:0;background:${"#fbf6ee"}"></div>` : ""}
        <div style="position:absolute;left:0;top:${tall ? SAFE.top : 0}px;width:${s.w}px;height:${s.imgH}px;overflow:hidden">${visual}
          ${a.image ? `<div class="logo" style="position:absolute;left:${pad - 14}px;top:${pad - 18}px;font-size:40px;background:#fbf6eef0;border-radius:999px;padding:8px 26px 10px;box-shadow:0 6px 18px rgba(31,36,48,.12)">Mapsie<i></i></div>` : ""}
          ${a.badge ? `<div class="pill" style="position:absolute;right:${pad - 14}px;top:${pad - 14}px;background:#1f4d3a;color:#fff;font-size:27px;padding:14px 24px;box-shadow:0 6px 18px rgba(0,0,0,.18)">${a.badge}</div>` : ""}
        </div>
        <div style="position:absolute;left:${pad}px;right:${pad}px;top:${(tall ? SAFE.top : 0) + s.imgH + (s.key === "sq" ? 40 : tall ? 40 : 52)}px;bottom:${tall ? SAFE.bottom : pad - 6}px;display:flex;flex-direction:column">
          <div class="pf" style="font-size:${s.head}px">${a.head}</div>
          <div style="font-size:${s.sub}px;line-height:1.35;color:#1f2430c4;margin-top:${s.key === "sq" ? 14 : 26}px;font-weight:600;text-wrap:pretty">${a.sub}</div>
          <div style="margin-top:auto;display:flex;align-items:center;justify-content:space-between;gap:20px">
            <div class="pill" style="background:#ff6b4a;color:#fff;font-size:34px;padding:20px 38px;box-shadow:0 12px 26px -8px rgba(255,107,74,.6)">${a.cta} →</div>
            <div style="text-align:right"><div style="font-size:30px;font-weight:900">${a.price}</div><div style="font-size:24px;font-weight:700;color:#1f243099">mapsie.shop</div></div>
          </div>
        </div>`;
      await render(`static/${a.id}-${SIZE_NAME[s.key]}`, s.w, s.h, html, { jpg: true });
    }
  }
}

// ---------------------------------------------------------------- video overlays
// Phone screen: 1080x1920 recording shown at 744x1323, centred, with captions above.
export const SCREEN = { x: 168, y: 368, w: 744, h: 1323, r: 58 };
async function overlays() {
  const S = SCREEN;
  // The frame: cream page with a transparent rounded "screen" hole, bezel and shadow.
  await render(
    "overlay/frame",
    1080,
    1920,
    `<div style="position:absolute;left:${S.x - 16}px;top:${S.y - 16}px;width:${S.w + 32}px;height:${S.h + 32}px;border-radius:${S.r + 16}px;border:16px solid #1f2430;box-shadow:0 0 0 2400px #fbf6ee, 0 50px 90px -20px rgba(31,36,48,.5)"></div>
     <div style="position:absolute;left:-200px;top:1712px;width:520px;height:520px;border-radius:50%;background:#ff6b4a22"></div>
     <div style="position:absolute;right:-210px;top:-260px;width:470px;height:470px;border-radius:50%;background:#7fb7c922"></div>
     <div style="position:absolute;left:0;right:0;top:1740px;text-align:center"><span class="logo" style="font-size:58px">Mapsie<i></i></span><span style="font-size:34px;font-weight:800;color:#1f243099;margin-left:22px">mapsie.shop</span></div>`,
    { transparent: true },
  );
  // Background for the cropped (no phone) layout: same page, no screen hole.
  await render(
    "overlay/bg",
    1080,
    1920,
    `<div style="position:absolute;inset:0;background:#fbf6ee"></div>
     <div style="position:absolute;left:-200px;top:1712px;width:520px;height:520px;border-radius:50%;background:#ff6b4a22"></div>
     <div style="position:absolute;right:-210px;top:-260px;width:470px;height:470px;border-radius:50%;background:#7fb7c922"></div>
     <div style="position:absolute;left:0;right:0;top:1740px;text-align:center"><span class="logo" style="font-size:58px">Mapsie<i></i></span><span style="font-size:34px;font-weight:800;color:#1f243099;margin-left:22px">mapsie.shop</span></div>`,
  );
  // Captions sit above the phone (y 70..330).
  const cap = (name: string, html: string, size = 78) =>
    render(`overlay/cap-${name}`, 1080, 360, `<div style="position:absolute;left:60px;right:60px;top:0;bottom:0;display:flex;align-items:center;justify-content:center"><div class="pf" style="text-align:center;font-size:${size}px">${html}</div></div>`, { transparent: true });
  await cap("describe-1", `Describe your trip…`);
  await cap("describe-2", `…and watch it become <span class="coral">a map</span>`);
  await cap("describe-3", `Printed, framed <span class="coral">&amp; delivered</span>`);
  await cap("photos-1", `Add your own <span class="coral">trip photos</span>`);
  await cap("photos-2", `Polaroid, heart <span class="coral">or stamp</span>`);
  await cap("photos-3", `Right where you <span class="coral">took them</span>`);
  await cap("gift-1", `Don't know the <span class="coral">trip details?</span>`);
  await cap("gift-2", `Give a Mapsie <span class="coral">gift card</span>`);
  await cap("gift-3", `Emailed instantly, or on <span class="coral">Christmas morning</span>`, 70);
  await cap("gift-4", `They design <span class="coral">their own map</span>`);
  // Full-bleed captions for the framed-detail video (bottom band over the image).
  const band = (name: string, html: string) =>
    render(`overlay/band-${name}`, 1080, 1920, `<div style="position:absolute;left:0;right:0;bottom:0;height:560px;background:linear-gradient(180deg,rgba(251,246,238,0),rgba(251,246,238,.92) 38%,#fbf6ee 60%)"></div><div class="pf" style="position:absolute;left:70px;right:70px;bottom:150px;text-align:center;font-size:84px">${html}</div>`, { transparent: true });
  await band("detail-1", `Every stop.`);
  await band("detail-2", `Every route.`);
  await band("detail-3", `On <span class="coral">your wall.</span>`);
  await band("describe-3", `Printed, framed <span class="coral">&amp; delivered</span>`);
  await band("gift-4", `They design <span class="coral">their own map</span>`);
  // The gift card as a full-frame still (caption goes above it).
  await render("overlay/still-gift-card", 1080, 1920, `<div style="position:absolute;inset:0;top:300px">${giftCardVisual(1.3)}</div><div style="position:absolute;left:0;right:0;top:0;height:300px;background:#fbf6ee"></div><div style="position:absolute;left:0;right:0;top:300px;height:200px;background:linear-gradient(#fbf6ee,rgba(251,246,238,0))"></div>`);
  await band("photos-4", `Printed with <span class="coral">your memories</span>`);
  // Organic Reels (Instagram / TikTok).
  await cap("japan-1", `Two weeks <span class="coral">in Japan…</span>`);
  await cap("nz-1", `A New Zealand <span class="coral">road trip…</span>`);
  await cap("styles-1", `One trip.`);
  await cap("styles-2", `<span class="coral">12 map styles.</span>`);
  await cap("styles-3", `Which one's <span class="coral">yours?</span>`);
  await band("xmas-1", `For the traveller who <span class="coral">has everything…</span>`);
  await band("xmas-2", `…their trip, <span class="coral">on the wall.</span>`);
  await band("xmas-3", `Every stop. <span class="coral">Every route.</span>`);
  await band("xmas-4", `Framed <span class="coral">&amp; delivered.</span>`);
  // The vintage styles video.
  await cap("vint-0", `Your trip, as a <span class="coral">vintage map</span>`, 70);
  await band("vint-antique", `Antique <span class="coral">· 1700s</span>`);
  await band("vint-heritage", `Victorian <span class="coral">town plan</span>`);
  await band("vint-touring", `1920s <span class="coral">touring map</span>`);
  await band("vint-poster", `Railway <span class="coral">poster</span>`);
  const pill = (name: string, html: string) =>
    render(`overlay/pill-${name}`, 1080, 220, `<div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center"><div class="pf" style="font-size:66px;background:#fbf6eef2;border-radius:999px;padding:22px 54px;box-shadow:0 10px 30px rgba(31,36,48,.18)">${html}</div></div>`, { transparent: true });
  await pill("vint-antique", `Antique <span class="coral">· 1700s</span>`);
  await pill("vint-heritage", `Victorian <span class="coral">town plan</span>`);
  await pill("vint-touring", `1920s <span class="coral">touring map</span>`);
  await pill("vint-poster", `Railway <span class="coral">poster</span>`);
  await pill("vint-watercolour", `<span class="coral">Watercolour</span>`);
  await band("vint-watercolour", `<span class="coral">Watercolour</span>`);
  // End cards.
  const end = (name: string, line: string, cta: string, sub: string) =>
    render(
      `overlay/end-${name}`,
      1080,
      1920,
      `<div style="position:absolute;inset:0;background:#fbf6ee"></div>
       <div style="position:absolute;left:-160px;top:-120px;width:620px;height:620px;border-radius:50%;background:#ff6b4a1f"></div>
       <div style="position:absolute;right:-180px;bottom:-140px;width:640px;height:640px;border-radius:50%;background:#7fb7c926"></div>
       <div style="position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:0 90px">
         <div class="logo" style="font-size:150px">Mapsie<i></i></div>
         <div class="pf" style="font-size:70px;margin-top:40px">${line}</div>
         <div class="pill" style="margin-top:70px;background:#ff6b4a;color:#fff;font-size:46px;padding:28px 56px;box-shadow:0 18px 40px -10px rgba(255,107,74,.6)">${cta} →</div>
         <div style="margin-top:44px;font-size:40px;font-weight:900">mapsie.shop</div>
         <div style="margin-top:12px;font-size:32px;font-weight:700;color:#1f243099">${sub}</div>
       </div>`,
    );
  await end("design", `Your trip, <span class="coral">on your wall.</span>`, "Design yours", `From £${FROM} · free delivery`);
  await end("xmas", `The gift they'll <span class="coral">actually</span> hang up.`, "Design theirs", `Order by ${xmas} for Christmas (UK)`);
  await end("gift", `Give a map of <span class="coral">their favourite trip.</span>`, "Buy a gift card", `From £${GIFT_MIN} · emailed instantly`);
  await end("vintage", `17 map styles. <span class="coral">Your trip.</span>`, "Design yours", `Prints from £${FROM} · free delivery`);
}

(async () => {
  mkdirSync(`${out}/static`, { recursive: true });
  mkdirSync(`${out}/overlay`, { recursive: true });
  browser = await chromium.launch();
  if (what === "all" || what === "statics") await statics();
  if (what === "all" || what === "overlays") await overlays();
  await browser.close();
})();
