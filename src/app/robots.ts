import type { MetadataRoute } from "next";
import { publicUrl } from "@/lib/server/urls";

export default function robots(): MetadataRoute.Robots {
  const base = publicUrl().replace(/\/$/, "");
  return {
    // Private and per-customer pages stay out of search results.
    rules: { userAgent: "*", allow: "/", disallow: ["/admin", "/api/", "/account", "/order/", "/checkout/", "/print/", "/etsy/", "/d/", "/signin"] },
    sitemap: `${base}/sitemap.xml`,
  };
}
