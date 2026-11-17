import { NextResponse } from "next/server";
import { nanoid } from "nanoid";
import { getOrder, getReviewForOrder, saveReview } from "@/lib/server/db";
import { reviewTokenValid } from "@/lib/server/reviews";
import { alertAdmin } from "@/lib/server/email";
import { clientIp, limit, sameOrigin, tooMany } from "@/lib/server/rateLimit";
import { publicUrl } from "@/lib/server/urls";
import { describeOptions } from "@/lib/products";

const clean = (v: unknown, max: number) => (typeof v === "string" ? v.replace(/[\u0000-\u0008\u000b-\u001f]/g, " ").trim().slice(0, max) : "");

/** A customer's review of their order. POST { orderId, k, rating, text, name, photo?, publish } */
export async function POST(req: Request) {
  if (!sameOrigin(req, publicUrl())) return NextResponse.json({ error: "Not allowed" }, { status: 403 });
  if (!limit("review", clientIp(req), 10, 60 * 60_000)) return tooMany();
  const b = (await req.json().catch(() => ({}))) as Record<string, unknown>;
  const orderId = clean(b.orderId, 40);
  if (!reviewTokenValid(orderId, typeof b.k === "string" ? b.k : "")) return NextResponse.json({ error: "This link isn't valid." }, { status: 404 });
  const o = await getOrder(orderId);
  if (!o) return NextResponse.json({ error: "Order not found." }, { status: 404 });
  if (await getReviewForOrder(orderId)) return NextResponse.json({ error: "You've already reviewed this order. Thank you!" }, { status: 409 });
  const rating = Math.round(Number(b.rating));
  if (!(rating >= 1 && rating <= 5)) return NextResponse.json({ error: "Please choose a star rating." }, { status: 400 });
  const photo = typeof b.photo === "string" && /^data:image\/(jpeg|png|webp);base64,[A-Za-z0-9+/=]+$/.test(b.photo) && b.photo.length < 900_000 ? b.photo : undefined;
  const text = clean(b.text, 1500);
  await saveReview({
    id: `rv_${nanoid(10)}`,
    orderId,
    status: "pending",
    rating,
    text,
    name: clean(b.name, 50) || "A Mapsie customer",
    photo,
    publish: b.publish === true,
    product: o.digital ? "Digital file" : undefined,
    source: o.source === "etsy" ? "etsy" : "mapsie",
    createdAt: new Date().toISOString(),
  });
  await alertAdmin(
    `${"★".repeat(rating)}${"☆".repeat(5 - rating)} new review${rating <= 3 ? ": please follow up" : ""}`,
    `${o.email} (order ${orderId}) left a ${rating}-star review${photo ? " with a photo" : ""}:\n\n${text || "(no comment)"}\n\nApprove or hide it at ${publicUrl()}/admin/reviews.${rating <= 3 ? "\nThey weren't happy: reply to them and offer to put it right." : ""}`,
  );
  return NextResponse.json({ ok: true, rating });
}
