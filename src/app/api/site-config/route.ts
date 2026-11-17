import { NextResponse } from "next/server";

/**
 * Public IDs for the optional tags, read at runtime so they can be set on Render
 * without a rebuild. All empty means no tags and no cookie banner.
 *   META_PIXEL_ID        Meta (Facebook/Instagram) Pixel ID
 *   GA4_MEASUREMENT_ID   Google Analytics 4, G-XXXXXXX
 *   GOOGLE_ADS_ID        Google Ads, AW-XXXXXXX (+ GOOGLE_ADS_PURCHASE_LABEL for the purchase conversion)
 *   PINTEREST_TAG_ID     Pinterest tag ID (Ads Manager > Conversions)
 */
export function GET() {
  const v = (k: string) => process.env[k]?.trim() || null;
  return NextResponse.json(
    { metaPixel: v("META_PIXEL_ID"), ga4: v("GA4_MEASUREMENT_ID"), googleAds: v("GOOGLE_ADS_ID"), adsPurchaseLabel: v("GOOGLE_ADS_PURCHASE_LABEL"), pinterest: v("PINTEREST_TAG_ID") },
    { headers: { "cache-control": "public, max-age=300" } },
  );
}
