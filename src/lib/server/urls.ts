// Public address of the site (what customers and the print company see).
// On Render, RENDER_EXTERNAL_URL is set automatically; APP_URL overrides it (e.g. a custom domain).
export const publicUrl = () => process.env.APP_URL ?? process.env.RENDER_EXTERNAL_URL ?? "http://localhost:3000";

// Address the print renderer uses to reach this same server. Always local, so
// renders never leave the machine.
export const internalUrl = () => `http://127.0.0.1:${process.env.PORT ?? 3000}`;
