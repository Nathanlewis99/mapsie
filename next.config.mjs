/** @type {import('next').NextConfig} */
const nextConfig = {
  serverExternalPackages: ["playwright", "sharp", "better-sqlite3", "pg"],
  devIndicators: false,
  // Sticker artwork rarely changes: let browsers and Render's CDN keep it for a week.
  async headers() {
    return [
      { source: "/stickers/:path*", headers: [{ key: "Cache-Control", value: "public, max-age=604800, stale-while-revalidate=86400" }] },
    ];
  },
};

export default nextConfig;
