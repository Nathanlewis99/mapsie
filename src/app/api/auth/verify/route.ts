import { NextResponse } from "next/server";
import { getSession, startSession } from "@/lib/server/auth";
import { getUser, markEmailVerified } from "@/lib/server/db";
import { checkLinkToken } from "@/lib/server/password";
import { publicUrl } from "@/lib/server/urls";

// The link in the "Confirm your email" message.
export async function GET(req: Request) {
  const token = new URL(req.url).searchParams.get("token") ?? "";
  const user = await checkLinkToken("verify", token, getUser);
  if (!user) return NextResponse.redirect(`${publicUrl()}/account?verified=expired`);
  await markEmailVerified(user.id);
  // Refresh the session if it's this person, so it reflects the verified email.
  if ((await getSession())?.sub === user.id) await startSession((await getUser(user.id))!);
  return NextResponse.redirect(`${publicUrl()}/account?verified=1`);
}
