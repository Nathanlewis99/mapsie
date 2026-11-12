import { NextResponse } from "next/server";
import { cookies } from "next/headers";
import { generateCodeVerifier, generateState } from "arctic";
import { google, googleConfigured, safeNext } from "@/lib/server/auth";

// Step 1 of Google sign-in: send the browser to Google.
export async function GET(req: Request) {
  if (!googleConfigured()) return NextResponse.json({ error: "Google sign-in isn't set up yet" }, { status: 503 });
  const next = safeNext(new URL(req.url).searchParams.get("next"));
  const state = generateState();
  const verifier = generateCodeVerifier();
  const url = google().createAuthorizationURL(state, verifier, ["openid", "email", "profile"]);
  url.searchParams.set("prompt", "select_account");
  const jar = await cookies();
  const opts = { httpOnly: true, sameSite: "lax" as const, secure: process.env.NODE_ENV === "production", path: "/", maxAge: 600 };
  jar.set("g_state", state, opts);
  jar.set("g_verifier", verifier, opts);
  jar.set("g_next", next, opts);
  return NextResponse.redirect(url);
}
