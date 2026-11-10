import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  serverExternalPackages: ["playwright"],
  experimental: { serverActions: { bodySizeLimit: "15mb" } },
};

export default nextConfig;
