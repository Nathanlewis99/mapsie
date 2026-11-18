# Mapsie ad creative

| What | Where |
|---|---|
| Vertical videos (1080×1920, H.264, silent-friendly captions) | `video/` |
| Static ads, 5 angles × 1080×1080 / 1080×1350 / 1000×1500 (PNG + JPG) | `static/` |
| All statics at a glance | `contact-sheet.jpg` |
| Frame sheets for each video | `frames/` |
| Ready-to-paste copy for Meta, Pinterest, Google Search and Etsy Ads | `copy.md` |
| Every ad with platform, placement, file and tagged link | `campaigns.csv` |

Prices and dates come from the site's own code (`src/lib/products.ts`, `src/lib/christmas.ts`, `src/lib/giftcards.ts`),
so regenerate after changing them. Links are tagged `utm_source=<platform>&utm_medium=paid&utm_campaign=<angle>&utm_content=<file>`,
which is what `/admin/channels` uses to credit each sale.

## Regenerating

Needs the site running locally on port 3123 with the mockup database (`DATA_DIR=<mock db> npx next start -p 3123`),
the `adsphotos` design and the `gc_adsdemo` gift card in it (see the recorder for both).

```bash
npx tsx design/ads/src/graphics.ts design/ads statics        # static ads
npx tsx design/ads/src/graphics.ts <scratch>/ads overlays    # video overlays (phone frame, captions, end cards)
node design/ads/src/record.js describe <scratch>/ads/rec-describe
node design/ads/src/record.js photos   <scratch>/ads/rec-photos
node design/ads/src/record.js gift     <scratch>/ads/rec-gift http://localhost:3123 <gift card token>
python3 design/ads/src/compose.py design/ads/src/videos.json <name> <scratch>/ads <scratch>/ads/overlay design/ads/video
python3 design/ads/src/ad_copy.py                             # copy.md (fails if anything is over a platform limit)
python3 design/ads/src/campaigns.py                           # campaigns.csv
```

`assets/` holds crops of a fresh 6.5× render of the Sri Lanka print (with the sea depth lines) used by the
your-photos statics and the framed-detail video.
