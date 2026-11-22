import type { MetadataRoute } from "next";
import { publicUrl } from "@/lib/server/urls";
import { OCCASIONS } from "@/lib/occasions";

// Built per request, not at build time: the site address (APP_URL) is only set when the
// server runs, so a build-time file would point search engines at localhost.
export const dynamic = "force-dynamic";

/** Pages search engines should know about. Private pages (orders, account, admin) are left out. */
export default function sitemap(): MetadataRoute.Sitemap {
  const base = publicUrl().replace(/\/$/, "");
  const page = (path: string, priority: number, changeFrequency: "weekly" | "monthly" | "yearly") => ({ url: `${base}${path}`, lastModified: new Date(), changeFrequency, priority });
  return [
    page("/", 1, "weekly"),
    page("/create", 0.9, "weekly"),
    page("/maps", 0.8, "weekly"),
    page("/gift", 0.8, "weekly"),
    page("/partners", 0.5, "monthly"),
    ...OCCASIONS.map((o) => page(`/maps/${o.slug}`, 0.8, "weekly")),
    page("/support", 0.4, "monthly"),
    page("/etsy", 0.3, "monthly"),
    ...["shipping", "refunds", "terms", "privacy", "cookies"].map((p) => page(`/legal/${p}`, 0.2, "yearly")),
  ];
}
