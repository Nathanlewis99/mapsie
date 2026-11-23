/** @type {import('next').NextConfig} */
const nextConfig = {
  serverExternalPackages: ["playwright", "sharp", "better-sqlite3", "pg"],
  devIndicators: false,
  // Skew protection: each build is tagged with its git commit, so a page left open across a deploy
  // does a full load on its next navigation instead of mixing old and new code.
  ...(process.env.RENDER_GIT_COMMIT ? { deploymentId: process.env.RENDER_GIT_COMMIT.slice(0, 12) } : {}),
  // Sticker artwork rarely changes: let browsers and Render's CDN keep it for a week.
  async headers() {
    // Security headers on every page: HTTPS only, no MIME sniffing, no framing by other
    // sites (clickjacking), and only the browser features we use (the microphone, for
    // "Describe your trip").
    const security = [
      { key: "Strict-Transport-Security", value: "max-age=31536000; includeSubDomains" },
      { key: "X-Content-Type-Options", value: "nosniff" },
      { key: "X-Frame-Options", value: "SAMEORIGIN" },
      { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
      { key: "Permissions-Policy", value: "microphone=(self), camera=(), geolocation=(), payment=(), usb=()" },
    ];
    return [
      { source: "/:path*", headers: security },
      { source: "/stickers/:path*", headers: [{ key: "Cache-Control", value: "public, max-age=604800, stale-while-revalidate=86400" }] },
    ];
  },
};

export default nextConfig;
