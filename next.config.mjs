/** @type {import('next').NextConfig} */
const nextConfig = {
  serverExternalPackages: ["playwright", "sharp"],
  devIndicators: false,
};

export default nextConfig;
