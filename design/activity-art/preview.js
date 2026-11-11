// Contact sheet of built concepts, to review drawings by eye.
//
//   node design/activity-art/preview.js <module> [out.png]
//   node design/activity-art/preview.js <module> out.png --big   (one large papercut per concept, for detail)
//
// Rows: concepts. Columns: every papercut palette, then every line colourway.
// Uses the Playwright that ships with this environment.
const { chromium } = require("playwright");
const fs = require("fs");
const path = require("path");

const OUT = path.join(__dirname, "out");
const [mod, file = `/tmp/preview-${mod}.png`] = process.argv.slice(2).filter((a) => !a.startsWith("--"));
const big = process.argv.includes("--big");
const manifest = JSON.parse(fs.readFileSync(path.join(OUT, `manifest-${mod}.json`), "utf8"));
const PC = ["golden", "coastal", "meadow", "blush", "dusk"];
const LN = ["classic", "forest", "ocean", "night"];
let n = 0;
const inline = (f, px) => {
  const p = `s${n++}-`;
  return fs.readFileSync(f, "utf8").replace(/id="/g, `id="${p}`).replace(/url\(#/g, `url(#${p}`).replace('width="200" height="200"', `width="${px}" height="${px}"`);
};

let h = '<body style="margin:0;background:#fbf6ee;font:12px sans-serif"><table cellspacing=4>';
if (big) {
  h += "<tr>";
  manifest.forEach((c, i) => {
    h += `<td style="text-align:center"><div style="font-weight:bold">${c.title}</div>${inline(path.join(OUT, c.id, `papercut-${c.papercut[0]}.svg`), 260)}</td>`;
    if (i % 4 === 3) h += "</tr><tr>";
  });
  h += "</tr>";
} else {
  h += "<tr><td></td>" + PC.map((p) => `<td>${p}</td>`).join("") + LN.map((p) => `<td>line ${p}</td>`).join("") + "</tr>";
  for (const c of manifest) {
    h += `<tr><td style="width:110px"><b>${c.title}</b><br><span style="color:#888">${c.activity}</span></td>`;
    for (const p of PC) {
      const f = path.join(OUT, c.id, `papercut-${p}.svg`);
      h += "<td>" + (fs.existsSync(f) ? inline(f, 110) : "—") + "</td>";
    }
    for (const p of LN) h += `<td style="background:${p === "night" ? "#1F2A44" : "transparent"}">${inline(path.join(OUT, c.id, `line-${p}.svg`), 110)}</td>`;
    h += "</tr>";
  }
}
(async () => {
  const b = await chromium.launch();
  const pg = await b.newPage({ viewport: { width: big ? 1120 : 1180, height: 800 } });
  await pg.setContent(h + "</table>");
  await pg.screenshot({ path: file, fullPage: true });
  await b.close();
  console.log("wrote", file);
})();
