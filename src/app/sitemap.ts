import type { MetadataRoute } from "next";
import { publicUrl } from "@/lib/server/urls";

/** Pages search engines should know about. Private pages (orders, account, admin) are left out. */
export default function sitemap(): MetadataRoute.Sitemap {
  const base = publicUrl().replace(/\/$/, "");
  const page = (path: string, priority: number, changeFrequency: "weekly" | "monthly" | "yearly") => ({ url: `${base}${path}`, lastModified: new Date(), changeFrequency, priority });
  return [
    page("/", 1, "weekly"),
    page("/create", 0.9, "weekly"),
    page("/support", 0.4, "monthly"),
    page("/etsy", 0.3, "monthly"),
    ...["shipping", "refunds", "terms", "privacy", "cookies"].map((p) => page(`/legal/${p}`, 0.2, "yearly")),
  ];
}
