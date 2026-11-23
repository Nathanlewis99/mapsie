# Mapsie: Next.js app + headless Chromium for 300 dpi print renders.
# The Playwright image ships Node, Chromium and its system libraries, matched to
# the playwright version in package.json.
FROM mcr.microsoft.com/playwright:v1.63.0-noble

WORKDIR /app
ENV NEXT_TELEMETRY_DISABLED=1 \
    PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1

COPY package.json package-lock.json ./
RUN npm ci

COPY . .
# Render passes the commit being built; Next tags the build with it (skew protection, see next.config).
ARG RENDER_GIT_COMMIT
ENV RENDER_GIT_COMMIT=$RENDER_GIT_COMMIT
RUN npm run build && npm prune --omit=dev

ENV NODE_ENV=production \
    PORT=10000 \
    DATA_DIR=/var/data
EXPOSE 10000
CMD ["npm", "start"]
