import { defineConfig } from "vitest/config";
import path from "node:path";

export default defineConfig({
  resolve: { alias: { "@": path.resolve(__dirname, "src") } },
  test: {
    include: ["tests/unit/**/*.test.ts"],
    environment: "node",
    // Each file gets its own throwaway data directory (see tests/unit/setup.ts).
    setupFiles: ["tests/unit/setup.ts"],
    pool: "forks",
  },
});
