# Mapsie

Turn a trip into a custom map print. Customers add their stops, style the map, decorate it with stickers and photos, then order. Mapsie renders a print-ready file and sends it to a print-on-demand partner, which prints and delivers it.

## Run it

```bash
npm install
npm run dev
```

Open http://localhost:3000. With no keys set, checkout uses a built-in **test checkout** and print orders are logged instead of sent, so the whole flow works locally.

## How it fits together

| Piece | Where | Notes |
|---|---|---|
| Editor | `src/components/editor/` | Stops, style, stickers, text, size. The design autosaves in the browser. |
| Poster | `src/components/Poster.tsx`, `MapView.tsx` | One component for the editor, previews and print. All sizes are relative to poster width. |
| Map styles | `src/lib/themes.ts` | OpenFreeMap base map, recoloured per theme. Terrain from AWS open elevation tiles. |
| Print render | `src/lib/server/render.ts`, `/print/[id]` | Headless Chromium lays the poster out at the customer's on-screen width, then raises pixel density to reach 300 dpi. |
| Payments | `/api/checkout`, `/api/webhooks/stripe` | Stripe Checkout (GBP, UK shipping). |
| Fulfilment | `src/lib/server/fulfil.ts`, `prodigi.ts` | Prodigi v4 API (sandbox by default). |
| Storage | `src/lib/server/db.ts` | JSON files in `./data` for now. Replace before deploying. |

## Environment variables (`.env.local`)

```
APP_URL=http://localhost:3000   # must be public in production: the printer downloads files from it
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
PRODIGI_API_KEY=...             # sandbox key from the Prodigi dashboard
PRODIGI_ENV=sandbox             # or live
PRINT_MAX_PX=8192               # WebGL canvas ceiling for the renderer
```

## Before going live

- Check the Prodigi SKUs in `src/lib/products.ts` against their catalogue, and compare real costs with our prices.
- Move storage to Supabase (Postgres + object storage), and run the renderer as a background worker. Serverless functions are too short-lived for big renders.
- Sizes above about A2 are capped by `PRINT_MAX_PX`, so A1 renders at about 250 dpi today. Tiled rendering would lift this cap.

Credits: map data © OpenStreetMap contributors, tiles by OpenFreeMap, stickers by Twemoji (CC-BY 4.0).
