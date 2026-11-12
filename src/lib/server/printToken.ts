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
