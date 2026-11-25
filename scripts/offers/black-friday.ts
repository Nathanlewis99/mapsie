// Create the BLACKFRIDAY10 Stripe code (10% off, expires midnight UK at the end of Mon 30 Nov). Safe to re-run.
// Run as a Render job: npx -y tsx@4.20.3 scripts/offers/black-friday.ts
import { ensureBlackFriday } from "../../src/lib/server/offers";
ensureBlackFriday()
  .then((p) => (console.log("OFFER", p.code, p.active, p.expires_at && new Date(p.expires_at * 1000).toISOString()), process.exit(0)))
  .catch((e) => (console.log("OFFER ERROR", String(e?.message ?? e)), process.exit(1)));
