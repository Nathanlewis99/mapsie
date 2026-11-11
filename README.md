# Mapsie

Turn a trip into a custom map print. Customers add their stops, style the map, decorate it with stickers and photos, then order. Mapsie renders a print-ready file and sends it to a print-on-demand partner, which prints and delivers it.

## Run it

```bash
npm install
npm run dev
```

Open http://localhost:3000. With no keys set, checkout uses a built-in **test checkout** and print orders are logged instead of sent, so the whole flow works locally.

## Features

- **Trip building:** search, tap the map, paste a list of places, or start from a template trip. Drag to reorder.
- **Travel modes per leg:** flight (curved arc), drive/bus (follows real roads via OSRM), train, boat, hike. Each has its own line style and an optional icon.
- **Styling:** 6 presets, 9 editable colours, terrain shading, paper texture, place names, and highlighting of visited countries.
- **Markers:** numbers, pins, hearts or dots, with optional dates.
- **Decorations:** 100+ stickers, your own photos and handwritten text notes. Resize and rotate them with handles on the map.
- **Undo/redo** (Ctrl+Z / Ctrl+Shift+Z), with autosave in the browser.
- **Products:** A4 to A1, portrait or landscape, no frame or black/white/oak frames, priced in GBP, USD or AUD.
- **"On the wall" preview:** shows the poster at true scale above a sideboard.
- **Share links** (`/d/<id>`) that others can open and remix.
- **Orders:** test checkout or Stripe, a 300 dpi print file, then hand-off to Prodigi.
- **Admin:** `/admin` lists orders, links each print file, and can re-send failed ones.

## How it fits together

| Piece | Where | Notes |
|---|---|---|
| Editor | `src/components/editor/` | Stops, style, stickers, text, size. The design autosaves in the browser. |
| Poster | `src/components/Poster.tsx`, `MapView.tsx` | One component for the editor, previews and print. All sizes are relative to poster width. |
| Map styles | `src/lib/themes.ts` | OpenFreeMap base map, recoloured per theme. Terrain from AWS open elevation tiles. |
| Print render | `src/lib/server/render.ts`, `/print/[id]` | Headless Chromium lays the poster out at the customer's on-screen width, then raises pixel density to reach 300 dpi. |
| Payments | `/api/checkout`, `/api/webhooks/stripe` | Stripe Checkout (GBP, UK shipping). |
| Fulfilment | `src/lib/server/fulfil.ts`, `prodigi.ts` | Prodigi v4 API (sandbox by default). |
| Road routing | `/api/route` | Proxies OSRM with a cache and a queue. Set `OSRM_URL` for a self-hosted or paid router. |
| Admin | `/admin` | Basic-auth protected with `ADMIN_PASSWORD`. Open without a password in local dev only. |
| Storage | `src/lib/server/db.ts` | JSON files in `./data` for now. Replace before deploying. |

## Environment variables (`.env.local`)

```
APP_URL=http://localhost:3000   # must be public in production: the printer downloads files from it
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
PRODIGI_API_KEY=...             # sandbox key from the Prodigi dashboard
PRODIGI_ENV=sandbox             # or live
PRINT_MAX_PX=7680               # largest map canvas the renderer draws (16384 on a GPU box)
ADMIN_PASSWORD=...              # protects /admin
OSRM_URL=https://router.project-osrm.org   # road routing (public demo server; fine for testing)
```

## Before going live

- Check the Prodigi SKUs in `src/lib/products.ts` against their catalogue, and compare real costs with our prices.
- Move storage to Supabase (Postgres + object storage), and run the renderer as a background worker. Serverless functions are too short-lived for big renders.
- Print files are always full size at 300 dpi. On the largest sizes the map layer underneath is drawn at up to `PRINT_MAX_PX` and gently upscaled (A1 ≈ 230 dpi for the map only). Text, stickers and markers stay at 300 dpi.
- The public OSRM server is for light use only. Self-host it, or switch to a paid router, before launch. The same goes for Photon place search.

Credits: map data © OpenStreetMap contributors, tiles by OpenFreeMap, stickers by Twemoji (CC-BY 4.0).
