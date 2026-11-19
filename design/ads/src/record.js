// Records Mapsie on a phone-shaped screen (mobile layout, 9:16) with
// Chrome's screencast, for the vertical ad videos. Writes JPEG frames + meta.json
// (frame times and named marks) for compose.py.
//   node design/ads/src/record.js <describe|photos|gift> <out dir> [base url] [gift token]
const { chromium } = require("playwright");
const fs = require("fs");
const path = require("path");

const [scenario, OUT, BASE = "http://localhost:3123", GIFT_TOKEN = ""] = process.argv.slice(2);
const ROOT = path.resolve(__dirname, "../../..");
fs.rmSync(OUT, { recursive: true, force: true });
fs.mkdirSync(OUT, { recursive: true });

// The real Sonnet plan for the Sri Lanka description, as the site turns it into a trip.
// TRIP_JSON / TEXT (env) swap in another trip for the describe scenario, e.g. a template.
const TRIP = process.env.TRIP_JSON ? JSON.parse(process.env.TRIP_JSON) : {
  id: "ai", name: "Your trip", emoji: "✨", title: "Sri Lanka 2026", subtitle: "By train & tuk-tuk · March 2026", preset: "tropical",
  stickers: ["safari-elephant", "surf-van", "tea-pour"],
  stops: [["Colombo", 79.8542, 6.93886, null], ["Kandy", 80.63504, 7.29312, "train"], ["Ella", 81.04899, 6.87361, "train"], ["Mirissa", 80.45581, 5.94936, "tuktuk"], ["Galle", 80.21496, 6.03281, "tuktuk"]],
};
const REPLY = process.env.REPLY || "Here's your Sri Lanka map, from Colombo through the hill country down to the southern coast!";
const TEXT = process.env.TEXT || "Two weeks in Sri Lanka: Colombo, the train from Kandy to Ella, tuk-tuks to Mirissa and Galle";

(async () => {
  const b = await chromium.launch({ args: ["--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"] });
  // Chrome's screencast captures at CSS size, so record a bigger phone-shaped layout at 1x
  // (still the mobile layout): 540x960 inside the phone frame, 900x1600 for the crop layout.
  const vp = scenario === "photos" ? { width: Number(process.env.VPW || 900), height: Number(process.env.VPW || 900) * 16 / 9 } : { width: 540, height: 960 };
  const ctx = await b.newContext({ viewport: vp, deviceScaleFactor: 1, isMobile: true, hasTouch: true });
  const p = await ctx.newPage();
  p.setDefaultTimeout(60000);
  await p.route("**/api/ai/design", async (r) => {
    if (r.request().method() === "GET") return r.fulfill({ json: { enabled: true, turnstileSiteKey: null } });
    await new Promise((x) => setTimeout(x, 1500));
    return r.fulfill({ json: { reply: REPLY, trip: TRIP } });
  });
  const pause = (ms) => p.waitForTimeout(ms);
  const frames = [];
  const marks = {};
  let cdp;
  const mark = (name) => (marks[name] = Date.now() / 1000);
  const start = async () => {
    cdp = await ctx.newCDPSession(p);
    cdp.on("Page.screencastFrame", async (f) => {
      frames.push({ t: f.metadata.timestamp, data: f.data });
      await cdp.send("Page.screencastFrameAck", { sessionId: f.sessionId }).catch(() => {});
    });
    await cdp.send("Page.startScreencast", { format: "jpeg", quality: 90, maxWidth: vp.width, maxHeight: vp.height, everyNthFrame: 1 });
    mark("start");
  };
  const meta = {};
  // Smooth pointer drag (mouse events drive the editor's pointer handlers).
  const drag = async (from, to, ms = 600) => {
    await p.mouse.move(from.x, from.y);
    await p.mouse.down();
    const n = Math.max(8, Math.round(ms / 16));
    for (let i = 1; i <= n; i++) {
      const k = i / n;
      const e = k < 0.5 ? 2 * k * k : 1 - Math.pow(-2 * k + 2, 2) / 2;
      await p.mouse.move(from.x + (to.x - from.x) * e, from.y + (to.y - from.y) * e);
      await pause(16);
    }
    await p.mouse.up();
  };
  const centre = async (loc) => {
    const r = await loc.boundingBox();
    return { x: r.x + r.width / 2, y: r.y + r.height / 2 };
  };

  if (scenario === "describe") {
    // Warm up: compile, cache the map tiles and road routes for the trip.
    for (let i = 0; i < 2; i++) {
      await p.goto(`${BASE}/create?new=1`);
      await p.locator("textarea").first().waitFor();
      await pause(2500);
      await p.locator("textarea").first().fill("Sri Lanka");
      await p.getByRole("button", { name: "Create my map" }).click();
      await p.getByText("Change anything you like").waitFor();
      await pause(6000);
    }
    await p.goto(`${BASE}/create?new=1`);
    await p.locator("textarea").first().waitFor();
    await pause(3500);
    await start();
    await pause(700);
    const box = p.locator("textarea").first();
    await box.click();
    await box.pressSequentially(TEXT, { delay: 28 });
    await pause(450);
    await p.getByRole("button", { name: "Create my map" }).click();
    mark("create");
    await p.getByText("Change anything you like").waitFor();
    mark("map");
    await pause(4200);
    await p.getByTitle("See it on a wall").click();
    mark("wall");
    await pause(3600);
  }

  if (scenario === "styles") {
    // One trip, flicking through the map styles (STYLES env: comma-separated preset names).
    const names = (process.env.STYLES || "Vintage,Minimal,Topographic,Midnight,Blush,Terrain,Atlas,Blueprint,Ink").split(",");
    const pick = (n) => p.getByRole("button", { name: new RegExp(`^${n}`) }).first();
    // Build the trip through "Describe your trip" (TRIP_JSON), so the map is framed on it.
    const setup = async () => {
      await p.goto(`${BASE}/create?new=1`);
      await p.locator("textarea").first().waitFor();
      await pause(2500);
      await p.locator("textarea").first().fill(TEXT);
      await p.getByRole("button", { name: "Create my map" }).click();
      await p.getByText("Change anything you like").waitFor();
      await pause(5000);
    };
    for (let i = 0; i < 2; i++) {
      await setup();
      await p.getByRole("button", { name: /Style/ }).first().click();
      await pause(800);
      for (const n of names) {
        await pick(n).click();
        await pause(2200);
      }
    }
    await pick(names[0]).click();
    await pause(3000);
    await start();
    await pause(900);
    mark("s0");
    for (const n of names.slice(1)) {
      await pick(n).click();
      await pause(Number(process.env.STYLE_MS || 1500));
    }
    mark("s1");
    await pause(500);
  }

  if (scenario === "photos") {
    for (let i = 0; i < 2; i++) {
      await p.goto(`${BASE}/create?d=adsphotos`);
      await pause(6000);
    }
    await p.getByRole("button", { name: /Stickers/ }).first().click();
    await pause(4000); // let the "design loaded" toast go
    const mapBox = await p.locator(".maplibregl-canvas").first().boundingBox();
    meta.map = mapBox;
    const at = (fx, fy) => ({ x: mapBox.x + mapBox.width * fx, y: mapBox.y + mapBox.height * fy });
    await start();
    await pause(600);
    const add = async (file, size, place, set) => {
      await p.setInputFiles('input[type=file][accept="image/*"]', path.join(ROOT, "design/mockups/photos", file));
      await pause(700);
      const st = p.locator(".mapsie-sticker.is-photo").last();
      const h = p.locator(".mapsie-sticker.is-photo").last().locator(".mapsie-handle.is-resize");
      const hc = await centre(h);
      await drag(hc, { x: hc.x + size, y: hc.y + size * 0.75 }, 500);
      await pause(250);
      for (const [title, value] of set) {
        await p.selectOption(`select[title="${title}"]`, value);
        await pause(650);
      }
      await drag(await centre(st), at(...place), 650);
      await pause(500);
    };
    mark("p1");
    await add("ella-train.jpg", 46, [0.72, 0.3], [["Border", "polaroid"]]);
    mark("p2");
    await add("hiriketiya.jpg", 44, [0.66, 0.74], [["Shape", "heart"]]);
    await add("tuktuk.jpg", 40, [0.22, 0.6], [["Shape", "stamp"]]);
    mark("p3");
    // Tap outside the poster to deselect.
    await p.mouse.click(8, mapBox.y + mapBox.height + 30);
    await pause(2600);
  }

  if (scenario === "gift") {
    const card = `${BASE}/gift/card/gc_adsdemo?k=${GIFT_TOKEN}`;
    for (const u of [`${BASE}/gift`, card, `${BASE}/create?template=honeymoon`]) {
      await p.goto(u);
      await pause(4000);
    }
    await p.goto(`${BASE}/gift`);
    await pause(2500);
    await start();
    mark("g1");
    await pause(1600);
    await p.mouse.wheel(0, 560);
    await pause(900);
    mark("g2");
    await p.getByRole("button", { name: /£79/ }).first().click();
    await pause(400);
    await p.getByPlaceholder("Who's it for? (name)").pressSequentially("Sam", { delay: 70 });
    await p.getByPlaceholder("From (your name)").pressSequentially("Alex", { delay: 70 });
    await p.getByPlaceholder(/Your message/).pressSequentially("For all our adventures. Happy Christmas! x", { delay: 26 });
    await pause(700);
    mark("g2end");
    await p.goto(card);
    await p.getByText("GIFT-XMAS-2026").first().waitFor();
    mark("g3");
    await pause(3000);
    mark("g3end");
    await p.goto(`${BASE}/create?template=honeymoon`);
    await p.waitForURL(/\/create$/);
    await pause(900);
    mark("g4");
    await pause(3600);
  }

  await cdp.send("Page.stopScreencast");
  mark("end");
  frames.forEach((f, i) => fs.writeFileSync(`${OUT}/${String(i).padStart(5, "0")}.jpg`, Buffer.from(f.data, "base64")));
  fs.writeFileSync(`${OUT}/meta.json`, JSON.stringify({ frames: frames.map((f, i) => ({ file: `${String(i).padStart(5, "0")}.jpg`, t: f.t })), marks, ...meta }, null, 1));
  console.log(scenario, frames.length, "frames over", (frames[frames.length - 1].t - frames[0].t).toFixed(1), "s; marks", Object.keys(marks).join(","));
  await b.close();
})().catch((e) => {
  console.error("FAILED", e.message);
  process.exit(1);
});
