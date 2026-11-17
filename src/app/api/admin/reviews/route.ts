import { NextResponse } from "next/server";
import { setReviewStatus, type ReviewStatus } from "@/lib/server/db";
import { publicUrl } from "@/lib/server/urls";

// Admin only (middleware): approve or hide a review.
export async function POST(req: Request) {
  const f = await req.formData();
  const status = String(f.get("status")) as ReviewStatus;
  if (["approved", "hidden", "pending"].includes(status)) await setReviewStatus(String(f.get("id")), status);
  return NextResponse.redirect(`${publicUrl()}/admin/reviews`, { status: 303 });
}
