import { DIGITAL_PRICE, FRAMES, PRODUCTS, getRegion, itemPrice, type RegionId } from "@/lib/products";
import { SITE } from "@/lib/seo";

// Product feed for Google Merchant Center (Shopping ads) and Pinterest catalogues.
//   /feed/products.xml?country=GB  (or US, AU: prices in that currency)
// Each item links to the designer with that size and frame already chosen, so the
// price on the page matches the feed.
export const dynamic = "force-dynamic";

const FINISHES = [
  { id: "print", frame: "none", mount: "none", label: "Unframed print", image: "south-america" },
  { id: "black", frame: "black", mount: "none", label: "Black frame", image: "sri-lanka" },
  { id: "oak", frame: "oak", mount: "none", label: "Natural wood frame", image: "southeast-asia" },
  { id: "white-mount", frame: "white", mount: "white", label: "White frame with mount", image: "london" },
] as const;
const esc = (s: string) => s.replace(/[<>&'"]/g, (c) => ({ "<": "&lt;", ">": "&gt;", "&": "&amp;", "'": "&apos;", '"': "&quot;" })[c]!);

export function GET(req: Request) {
  const country = (new URL(req.url).searchParams.get("country") ?? "GB").toUpperCase();
  const region = getRegion((["GB", "US", "AU"].includes(country) ? country : "GB") as RegionId);
  const cur = region.currency.toUpperCase();
  const items: string[] = [];
  const item = (f: { id: string; title: string; description: string; link: string; image: string; price: number; size: string; color?: string; type: string }) =>
    `<item>
  <g:id>${esc(f.id)}</g:id>
  <g:item_group_id>MAPSIE-CUSTOM-MAP</g:item_group_id>
  <g:title>${esc(f.title)}</g:title>
  <g:description>${esc(f.description)}</g:description>
  <g:link>${esc(f.link)}</g:link>
  <g:image_link>${SITE}/examples/${f.image}.webp</g:image_link>
  <g:additional_image_link>${SITE}/examples/your-photos.webp</g:additional_image_link>
  <g:availability>in_stock</g:availability>
  <g:condition>new</g:condition>
  <g:price>${f.price.toFixed(2)} ${cur}</g:price>
  <g:brand>Mapsie</g:brand>
  <g:identifier_exists>no</g:identifier_exists>
  <g:google_product_category>500044</g:google_product_category>
  <g:product_type>${esc(f.type)}</g:product_type>
  <g:size>${esc(f.size)}</g:size>${f.color ? `\n  <g:color>${esc(f.color)}</g:color>` : ""}
  <g:shipping><g:country>${region.id}</g:country><g:price>0.00 ${cur}</g:price></g:shipping>
</item>`;
  const desc = "Design your own map print of a trip: every stop, the real route between them, stickers and your own photos, in your choice of style. Printed to order at 300 dpi and delivered free.";
  for (const p of PRODUCTS) {
    for (const f of FINISHES) {
      const price = itemPrice({ productId: p.id, frame: f.frame, paper: "ema", mount: f.mount, glaze: "perspex" } as never, region.id);
      const framed = f.frame !== "none";
      items.push(item({
        id: `MAPSIE-${p.id.toUpperCase()}-${f.id.toUpperCase()}-${region.id}`,
        title: `Custom Travel Map Print, ${p.label}, ${f.label} | Personalised Trip Map`,
        description: framed ? `${desc} ${FRAMES.find((x) => x.id === f.frame)?.label} wooden frame with Perspex, ready to hang.` : `${desc} On thick matte art paper, sent in a sturdy tube.`,
        link: `${SITE}/create?product=${p.id}&frame=${f.frame}&mount=${f.mount}&region=${region.id}`,
        image: f.image,
        price,
        size: p.label,
        color: framed ? f.label.replace(" frame", "").replace(" with mount", "") : undefined,
        type: framed ? "Home & Garden > Decor > Artwork > Framed Prints" : "Home & Garden > Decor > Artwork > Posters & Prints",
      }));
    }
  }
  items.push(item({
    id: `MAPSIE-DIGITAL-${region.id}`,
    title: "Custom Travel Map, Digital Print File (300 dpi) | Personalised Trip Map",
    description: "Design your own map of a trip and download it as a full-resolution 300 dpi file, emailed within minutes. Print it anywhere, any size up to A1.",
    link: `${SITE}/create?format=digital&region=${region.id}`,
    image: "your-photos",
    price: DIGITAL_PRICE[region.id],
    size: "Digital",
    type: "Home & Garden > Decor > Artwork > Digital Prints",
  }));
  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:g="http://base.google.com/ns/1.0">
<channel>
<title>Mapsie custom travel map prints (${region.id})</title>
<link>${SITE}</link>
<description>Personalised map prints of your trips</description>
${items.join("\n")}
</channel>
</rss>`;
  return new Response(xml, { headers: { "content-type": "application/xml; charset=utf-8", "cache-control": "public, max-age=3600" } });
}
