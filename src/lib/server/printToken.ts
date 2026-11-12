import { createHmac, timingSafeEqual } from "node:crypto";

// The bare /print page shows a design at full quality with no watermark, so only
// our own renderer may open it: it carries a token signed with SESSION_SECRET.
const secret = () => process.env.SESSION_SECRET ?? "dev-only-session-secret-change-me-0123456789";

export const printToken = (designId: string) => createHmac("sha256", secret()).update(`print:${designId}`).digest("base64url");

export function printTokenValid(designId: string, token: string | undefined) {
  if (!token) return false;
  const a = Buffer.from(printToken(designId));
  const b = Buffer.from(token);
  return a.length === b.length && timingSafeEqual(a, b);
}

/** A token for Prodigi's status callbacks about one of our orders. */
export const callbackToken = (orderId: string) => createHmac("sha256", secret()).update(`prodigi:${orderId}`).digest("base64url");
export function callbackTokenValid(orderId: string, token: string | null) {
  if (!token) return false;
  const a = Buffer.from(callbackToken(orderId));
  const b = Buffer.from(token);
  return a.length === b.length && timingSafeEqual(a, b);
}
