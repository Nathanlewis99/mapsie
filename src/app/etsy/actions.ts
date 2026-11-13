"use server";
import { headers } from "next/headers";
import { redirect } from "next/navigation";
import { listOrdersByEtsyReceipt } from "@/lib/server/db";
import { etsyToken, samePostcode } from "@/lib/server/etsy";
import { recordFailure, tooManyAttempts } from "@/lib/server/password";

export type LookupState = { error?: string; receipt?: string; postcode?: string } | null;

/** Find an Etsy order by its number and the delivery postcode, then open it. */
export async function findEtsyOrder(_: LookupState, f: FormData): Promise<LookupState> {
  const receipt = String(f.get("receipt") ?? "").replace(/[^\d]/g, "");
  const postcode = String(f.get("postcode") ?? "").trim();
  const ip = (await headers()).get("x-forwarded-for")?.split(",")[0]?.trim() || "unknown";
  if (!receipt || !postcode) return { error: "Enter your Etsy order number and the postcode it's being delivered to.", receipt, postcode };
  if (tooManyAttempts(`etsy:${receipt}`, ip)) return { error: "Too many tries. Please wait 15 minutes, or use the link in your email.", receipt, postcode };
  const found = (await listOrdersByEtsyReceipt(receipt)).filter((o) => o.address && samePostcode(o.address.postcode, postcode));
  if (!found.length) {
    recordFailure(`etsy:${receipt}`, ip);
    return {
      error: "We couldn't find that order. Check the number (it's in your Etsy purchase email) and postcode. New orders can take up to 10 minutes to reach us.",
      receipt,
      postcode,
    };
  }
  // Several prints in one Etsy order: start with the first that still needs designing.
  const next = found.find((o) => o.status === "awaiting_design") ?? found[0];
  redirect(`/etsy/${next.id}?k=${etsyToken(next.id)}`);
}
