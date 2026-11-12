import { NextResponse } from "next/server";
import { cookies } from "next/headers";
import { decodeIdToken } from "arctic";
import { google, isAdminEmail, safeNext, startSession } from "@/lib/server/auth";
import { upsertGoogleUser } from "@/lib/server/db";
import { publicUrl } from "@/lib/server/urls";

// Step 2 of Google sign-in: Google sends the browser back here with a code.
export async function GET(req: Request) {
  const url = new URL(req.url);
  const jar = await cookies();
  const state = jar.get("g_state")?.value;
  const verifier = jar.get("g_verifier")?.value;
  const next = safeNext(jar.get("g_next")?.value);
  for (const c of ["g_state", "g_verifier", "g_next"]) jar.delete(c);
  const fail = (why: string) => NextResponse.redirect(`${publicUrl()}/signin?error=${encodeURIComponent(why)}`);

  if (url.searchParams.get("error")) return fail("cancelled");
  const code = url.searchParams.get("code");
  if (!code || !state || !verifier || url.searchParams.get("state") !== state) return fail("expired");

  try {
    const tokens = await google().validateAuthorizationCode(code, verifier);
    const claims = decodeIdToken(tokens.idToken()) as { sub: string; email?: string; email_verified?: boolean; name?: string; picture?: string };
    if (!claims.email || !claims.email_verified) return fail("unverified");
    const user = await upsertGoogleUser({ sub: claims.sub, email: claims.email, name: claims.name, picture: claims.picture });
    await startSession(user);
    // Admins finish signing in with their authenticator app.
    const dest = isAdminEmail(user.email) && next.startsWith("/admin") ? "/admin/2fa?next=" + encodeURIComponent(next) : next;
    return NextResponse.redirect(`${publicUrl()}${dest}`);
  } catch (e) {
    console.error("[auth] google callback failed", e);
    return fail("failed");
  }
}
