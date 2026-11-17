import type { MetadataRoute } from "next";
import { publicUrl } from "@/lib/server/urls";

// Built per request, not at build time: the site address (APP_URL) is only set when the
// server runs, so a build-time file would point search engines at localhost.
export const dynamic = "force-dynamic";

export default function robots(): MetadataRoute.Robots {
  const base = publicUrl().replace(/\/$/, "");
  return {
    // Private and per-customer pages stay out of search results.
    rules: { userAgent: "*", allow: "/", disallow: ["/admin", "/api/", "/account", "/order/", "/checkout/", "/print/", "/etsy/", "/d/", "/signin"] },
    sitemap: `${base}/sitemap.xml`,
  };
}
