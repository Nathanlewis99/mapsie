// Reviews: a request a few days after the print arrives (or the file is delivered),
// a review page with stars, words and an optional photo, and moderation in admin.
// Etsy buyers are asked to review on Etsy instead, where it helps the shop rank.
import { createHmac, timingSafeEqual } from "node:crypto";
import { getReviewForOrder, isOptedOut, listOrdersByStatus, updateOrder, type Order } from "./db";
import { sendReviewRequestEmail } from "./email";
import { logError } from "./log";
import { publicUrl } from "./urls";

const secret = () => process.env.SESSION_SECRET ?? "dev-only-session-secret-change-me-0123456789";
export const reviewToken = (orderId: string) => createHmac("sha256", secret()).update(`review:${orderId}`).digest("base64url").slice(0, 22);
export function reviewTokenValid(orderId: string, k: string | null | undefined) {
  const want = Buffer.from(reviewToken(orderId));
  const got = Buffer.from(k ?? "");
  return got.length === want.length && timingSafeEqual(got, want);
}
export const reviewUrl = (orderId: string) => `${publicUrl()}/review/${orderId}?k=${reviewToken(orderId)}`;

const DAY = 24 * 3600_000;
/** When to ask: a few days after delivery should have happened. */
export function reviewDueAt(o: Order): number | null {
  if (o.digital) return o.paidAt ? new Date(o.paidAt).getTime() + 3 * DAY : null;
  const shipped = o.shippedAt ?? o.shipments?.find((s) => s.dispatchDate)?.dispatchDate;
  if (!shipped) return null;
  return new Date(shipped).getTime() + (o.region === "GB" ? 6 : 10) * DAY;
}

/** Worker job: send the review requests that are due (once per order). */
export async function sendReviewRequests() {
  const orders = [...(await listOrdersByStatus("shipped")), ...(await listOrdersByStatus("delivered"))];
  const now = Date.now();
  for (const o of orders) {
    if (!o.email || o.emailsSent?.includes("review-request") || o.reprintOf) continue;
    const due = reviewDueAt(o);
    // Not before it's due, and not for very old orders (e.g. when this first goes live).
    if (!due || due > now || now - due > 21 * DAY) continue;
    await updateOrder(o.id, { emailsSent: [...(o.emailsSent ?? []), "review-request"] }); // first, so never twice
    if ((await isOptedOut(o.email)) || (await getReviewForOrder(o.id))) continue;
    try {
      await sendReviewRequestEmail(o, reviewUrl(o.id));
    } catch (e) {
      await logError("reviews.request", e, { orderId: o.id });
    }
  }
}
