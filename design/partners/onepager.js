// Renders mapsie-partners.pdf (the one-page partner pitch): node design/partners/onepager.js <screenshot-dir>
const { chromium } = require('playwright'); const fs = require('fs');
const img = (f) => 'data:image/webp;base64,' + fs.readFileSync('/home/user/mapsie/public/partners/' + f).toString('base64');
const seg = [
  ['travel.webp', 'Tour operators & travel agents', 'Send guests a link to their itinerary, already drawn. They add photos and order; you earn 10%.'],
  ['event.webp', 'Events & challenges', 'A finisher print with every name and time. Sell it as an add-on, or put a code in every pack.'],
  ['wedding.webp', 'Wedding registries & planners', 'Honeymoon maps and gift cards for your couples and their guests.'],
  ['corporate.webp', 'Corporate & client gifts', 'Prepaid codes, invoiced. Each person designs their own map: travels, home town, new home.'],
];
const html = `<!doctype html><html><head><link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@800&family=Nunito:wght@600;800;900&display=swap" rel="stylesheet">
<style>@page{size:A4;margin:0}*{box-sizing:border-box}body{margin:0;width:210mm;height:297mm;background:#fbf6ee;color:#1f2430;font-family:Nunito,sans-serif}
.pf{font-family:'Playfair Display',serif;font-weight:800}.w{padding:11mm 14mm 8mm}.k{color:#e0512f;font-weight:900;letter-spacing:.12em;font-size:9pt;text-transform:uppercase}
h1{font-size:25pt;line-height:1.12;margin:3mm 0 3mm}p{margin:0}.lead{font-size:11pt;color:#1f2430bb;line-height:1.45}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:5mm;margin-top:5mm}.c{background:#fff;border-radius:5mm;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,.06)}
.c img{width:100%;height:36mm;object-fit:cover;object-position:50% 2%;display:block}.c div{padding:3.5mm 4mm 4mm}.c b{font-size:11pt}.c p{font-size:9.2pt;color:#1f2430b0;margin-top:1.2mm;line-height:1.4}
.how{display:grid;grid-template-columns:repeat(3,1fr);gap:4mm;margin-top:5mm}.how div{background:#fff;border-radius:4mm;padding:4mm}.n{display:inline-grid;place-items:center;width:7mm;height:7mm;border-radius:50%;background:#ff6b4a;color:#fff;font-weight:900;font-size:9pt}
.how b{display:block;margin-top:2mm;font-size:10pt}.how p{font-size:8.8pt;color:#1f2430b0;margin-top:1mm;line-height:1.35}
table{width:100%;border-collapse:collapse;margin-top:5mm;font-size:9pt;background:#fff;border-radius:4mm;overflow:hidden}td,th{padding:2.4mm 3mm;text-align:left;border-bottom:1px solid #1f243012;vertical-align:top}th{background:#1f2430;color:#fff;font-size:8.5pt}
.foot{margin-top:5mm;display:flex;justify-content:space-between;align-items:center}.cta{background:#ff6b4a;color:#fff;border-radius:99px;padding:3mm 6mm;font-weight:900;font-size:11pt}.logo{font-size:20pt}.logo i{display:inline-block;width:2.2mm;height:2.2mm;border-radius:50%;background:#ff6b4a;margin-left:.6mm}
</style></head><body><div class="w">
<div class="pf logo">Mapsie<i></i></div>
<div class="k" style="margin-top:5mm">Mapsie for business</div>
<h1 class="pf">Give your customers their journey, as a map for the wall</h1>
<p class="lead">Mapsie turns a route into a personalised print: the real roads, rails and flight paths, the traveller's photos and names, framed and delivered in the UK, US and Australia. We draw your routes once; your customers personalise and order in minutes.</p>
<div class="grid">${seg.map(([i,t,d])=>`<div class="c"><img src="${img(i)}"><div><b>${t}</b><p>${d}</p></div></div>`).join('')}</div>
<div class="how">${[['1','We set up your page','Your routes, drawn and styled, at mapsie.shop/with/you.'],['2','You share the link','In a welcome-home email, finisher pack or welcome letter.'],['3','They design and order','We print, frame and deliver. You earn on every order.']].map(([n,t,d])=>`<div><span class="n">${n}</span><b>${t}</b><p>${d}</p></div>`).join('')}</div>
<table><tr><th></th><th>Commission</th><th>Prepaid codes</th></tr>
<tr><td><b>How</b></td><td>Share your link or discount code</td><td>Buy codes and give them away</td></tr>
<tr><td><b>Cost to you</b></td><td>Nothing</td><td>Trade price: 15% off, 20% off 10+, 25% off 50+</td></tr>
<tr><td><b>You get</b></td><td>10% of every order, paid monthly</td><td>Codes that work like gift cards for any print</td></tr></table>
<div class="foot"><div><b>Prints from £34 · framed from £69 · free delivery</b><p style="font-size:9pt;color:#1f2430a0;margin-top:1mm">hello@mapsie.shop · mapsie.shop/partners</p></div><div class="cta">mapsie.shop/partners →</div></div>
</div></body></html>`;
(async () => { const b = await chromium.launch(); const p = await b.newPage(); await p.setContent(html, { waitUntil: 'networkidle' });
  await p.pdf({ path: '/home/user/mapsie/design/partners/mapsie-partners.pdf', format: 'A4', printBackground: true });
  await p.setViewportSize({ width: 794, height: 1123 }); await p.screenshot({ path: process.argv[2] + '/onepager.png' }); await b.close(); })();
