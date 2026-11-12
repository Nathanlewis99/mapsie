/** @type {import('next').NextConfig} */
const nextConfig = {
  serverExternalPackages: ["playwright", "sharp", "better-sqlite3", "pg"],
  devIndicators: false,
};

export default nextConfig;
