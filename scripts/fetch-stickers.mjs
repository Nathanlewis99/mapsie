// Downloads the sticker artwork sets into public/stickers/.
//
//   node scripts/fetch-stickers.mjs
//
// Sets:
//   public/stickers/<name>.svg        Twemoji (CC-BY 4.0)          "cartoon"
//   public/stickers/flat/<name>.svg   Fluent Emoji Flat (MIT)
//   public/stickers/color/<name>.svg  Fluent Emoji Color (MIT)
//   public/stickers/line/<name>.svg   Fluent Emoji High Contrast (MIT)
//
// Fluent Emoji folders are named after the official Unicode (CLDR) emoji names,
// which we look up in Unicode's emoji-test.txt.
import { readFile, writeFile, mkdir, access } from "node:fs/promises";
import path from "node:path";

const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), "..");
const catalog = JSON.parse(await readFile(path.join(root, "src/lib/sticker-catalog.json"), "utf8"));
const extra = [{ name: "potted-plant", code: "1fab4" }]; // used by the wall preview

const FLUENT = "https://cdn.jsdelivr.net/gh/microsoft/fluentui-emoji@main/assets";
const TWEMOJI = "https://cdn.jsdelivr.net/gh/jdecked/twemoji@15.1.0/assets/svg";

const emojiTest = await (await fetch("https://unicode.org/Public/emoji/15.1/emoji-test.txt")).text();
const names = new Map();
for (const line of emojiTest.split("\n")) {
  const m = /^([0-9A-F ]+?)\s*; fully-qualified\s*# \S+ E[\d.]+ (.+)$/.exec(line);
  if (!m) continue;
  const code = m[1].split(" ").filter((c) => c !== "FE0F").join("-").toLowerCase();
  if (!names.has(code)) names.set(code, m[2]);
}

const SETS = [
  { dir: "flat", folder: "Flat", suffix: "flat" },
  { dir: "color", folder: "Color", suffix: "color" },
  { dir: "line", folder: "High Contrast", suffix: "high_contrast" },
];

const exists = (p) => access(p).then(() => true, () => false);
async function get(url) {
  const r = await fetch(url);
  return r.ok ? await r.text() : null;
}

const missing = [];
for (const s of [...catalog, ...extra]) {
  const twPath = path.join(root, "public/stickers", `${s.name}.svg`);
  if (!(await exists(twPath))) {
    const svg = await get(`${TWEMOJI}/${s.code}.svg`);
    if (svg) await writeFile(twPath, svg);
    else missing.push(`twemoji:${s.name}`);
  }

  const cldr = names.get(s.code);
  if (!cldr) {
    missing.push(`name:${s.name}`);
    continue;
  }
  const folder = encodeURIComponent(cldr[0].toUpperCase() + cldr.slice(1));
  const file = cldr.toLowerCase().replace(/[^a-z0-9 -]/g, "").replace(/ /g, "_");

  for (const set of SETS) {
    const out = path.join(root, "public/stickers", set.dir, `${s.name}.svg`);
    if (await exists(out)) continue;
    await mkdir(path.dirname(out), { recursive: true });
    const style = encodeURIComponent(set.folder);
    // People emoji have skin-tone sub-folders; "Default" is the yellow one.
    const svg =
      (await get(`${FLUENT}/${folder}/${style}/${file}_${set.suffix}.svg`)) ??
      (await get(`${FLUENT}/${folder}/Default/${style}/${file}_${set.suffix}_default.svg`));
    if (svg) await writeFile(out, svg);
    else missing.push(`${set.dir}:${s.name} (${cldr})`);
  }
  process.stdout.write(".");
}
// Record which sets each sticker exists in, so the app can fall back gracefully.
const available = {};
for (const s of catalog) {
  available[s.name] = [];
  for (const set of SETS) if (await exists(path.join(root, "public/stickers", set.dir, `${s.name}.svg`))) available[s.name].push(set.dir);
}
await writeFile(path.join(root, "src/lib/sticker-availability.json"), JSON.stringify(available));

console.log(`\ndone. missing: ${missing.length ? missing.join(", ") : "none"}`);
